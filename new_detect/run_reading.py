#!/usr/bin/env python3
"""Reading mode for the explicit wm_test/wn experiment manifest.

The old answers identify checkpoints and attacks. Shared TEACHER responses,
not those student answers or their old scores, provide the reading context.
"""
from __future__ import annotations

import argparse
from collections import OrderedDict, defaultdict
from datetime import datetime, timezone
import gc
import hashlib
import importlib.util
import importlib.metadata
import json
from pathlib import Path
import random
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from new_detect.core import roc
from new_detect.reading_core import score_reading, top1_predictions
from new_detect.run_blackbox import digest, inventory, write_json, KEY, GAMMA
from wm_test.grouped_pvalues import tokenizer_signature

VERSION = 'radioactivity-reading-simple1-cuda-v2'
OFFICIAL_COMMIT = '19c6dc90e7a0dddb1a241b73e7fae708b68f024e'
DEFAULT_PROBE = ROOT / 'data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtest.parquet'
DEFAULT_TRAIN = ROOT / 'data/dolly15k_qwen2_5_14b_kgw_gamma0.5_delta3_newtrain.parquet'


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--manifest', type=Path, default=ROOT / 'new_detect/experiments.json')
    p.add_argument('--experiments', nargs='+')
    p.add_argument('--reference', default=None, help='Manifest clean experiment; default base, as in old table')
    p.add_argument('--probe', type=Path, default=DEFAULT_PROBE)
    p.add_argument('--probe-field', default='teacher_response')
    p.add_argument('--probe-split', choices=('heldout', 'supervised'), default='heldout')
    p.add_argument('--training-corpus', type=Path, default=DEFAULT_TRAIN, help='ID overlap audit for original teacher train data')
    p.add_argument('--tokenizer', type=Path, default=Path('/shared/public_models/Qwen2.5-14B-Instruct'))
    p.add_argument('--checkpoint-root', type=Path, default=ROOT / 'checkpoints')
    p.add_argument('--base-model', type=Path, default=Path('/shared/public_models/Qwen2.5-0.5B'))
    p.add_argument('--model-overrides', type=Path, help='JSON object: manifest experiment name -> HF model directory')
    p.add_argument('--rules', type=Path, help='Override WN rule location; content SHA256 must match saved runs')
    p.add_argument('--wn-tokenizer', type=Path, help='Override original WN tokenizer path, with rule identity validation')
    p.add_argument('--protocol', choices=('official', 'documents'), default='official',
                   help='official: shuffled concatenated full chunks and original scoring indices; documents: preserve response boundaries')
    p.add_argument('--probe-seed', type=int, default=0, help='Python Random shuffle seed; official fake_seed defaults to 0')
    p.add_argument('--sequence-length', type=int, default=256, help='Independent attention-span length')
    p.add_argument('--batch-size', type=int, default=1)
    p.add_argument('--dtype', choices=('float32', 'float16', 'bfloat16'), default='float16')
    p.add_argument('--device', default='cuda')
    p.add_argument('--budgets', type=int, nargs='+', default=[1000, 2000, 3000])
    p.add_argument('--limit', type=int, help='First N probe documents; smoke test only')
    p.add_argument('--max-probe-tokens', type=int, help='Optional per-document cap; recorded explicitly, default no cap')
    p.add_argument('--cache-dir', type=Path, default=ROOT / 'new_detect/cache/reading')
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--preflight', action='store_true', help='Audit sources and paths, no tokenizer/model loading')
    p.add_argument('--from-cache-only', action='store_true', help='Summarize validated server prediction caches on CPU')
    args = p.parse_args(argv)
    if args.sequence_length < 2 or args.batch_size < 1 or (args.limit is not None and args.limit < 1):
        p.error('sequence-length >= 2, batch-size/limit >= 1 required')
    if args.protocol == 'official' and args.sequence_length < 3:
        p.error('official protocol needs sequence-length >= 3')
    if args.max_probe_tokens is not None and args.max_probe_tokens < 2:
        p.error('max-probe-tokens must be >= 2')
    if not args.budgets or len(set(args.budgets)) != len(args.budgets) or min(args.budgets) < 1:
        p.error('budgets must be distinct positive integers')
    if args.preflight and args.from_cache_only:
        p.error('--preflight and --from-cache-only are mutually exclusive')
    return args


def read_table(path):
    if path.suffix == '.parquet':
        import pyarrow.parquet as pq
        return pq.read_table(path).to_pylist()
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def load_probes(args, expected_ids):
    rows = read_table(args.probe)
    by_id = {}
    for row in rows:
        sid, text = row.get('id'), row.get(args.probe_field)
        if not isinstance(sid, str) or not sid or sid in by_id or not isinstance(text, str) or not text.strip():
            raise ValueError('Probe must contain unique nonempty string id and teacher text')
        by_id[sid] = dict(id=sid, text=text)
    # For the default test corpus, exact same IDs/order as the legacy answers.
    if args.probe.resolve() == DEFAULT_PROBE.resolve():
        if set(by_id) != set(expected_ids):
            raise ValueError('Default teacher probe IDs differ from saved wm_test/wn results')
        probes = ([by_id[sid] for sid in expected_ids] if args.protocol == 'documents'
                  else list(by_id.values()))
    else:
        probes = list(by_id.values())
    train_ids = {r['id'] for r in read_table(args.training_corpus)}
    overlap = set(by_id) & train_ids
    if args.probe_split == 'heldout' and overlap:
        raise ValueError(f'Held-out probe overlaps original teacher training IDs: {len(overlap)}; use independent data or --probe-split supervised')
    if args.limit:
        probes = probes[:args.limit]
    return probes, dict(path=str(args.probe), sha256=digest(args.probe), field=args.probe_field,
        split=args.probe_split, documents=len(probes), full_documents=len(rows), limit=args.limit,
        training_corpus=str(args.training_corpus), training_sha256=digest(args.training_corpus),
        overlap_with_original_teacher_train=len(overlap),
        overlap_note='ID audit only; not a near-duplicate or every transformed training-corpus audit',
        selected_text_sha256=hashlib.sha256(json.dumps(probes, ensure_ascii=False, sort_keys=True).encode()).hexdigest())


def resolve_model(saved, spec, args, overrides):
    if spec['name'] in overrides:
        return Path(overrides[spec['name']])
    normalized = saved.replace('\\', '/')
    if '/checkpoints/' in normalized:
        return args.checkpoint_root / normalized.split('/checkpoints/', 1)[1]
    if spec['name'] == 'base':
        return args.base_model
    return Path(saved)


def make_jobs(specs, datasets, sources, reference, args):
    overrides = json.loads(args.model_overrides.read_text(encoding='utf-8')) if args.model_overrides else {}
    if not isinstance(overrides, dict) or set(overrides) - {s['name'] for s in json.loads(args.manifest.read_text(encoding='utf-8'))['experiments']}:
        raise ValueError('model-overrides must map known experiment names to model paths')
    jobs = []
    attacks = {}
    for spec in specs:
        name = spec['name']
        if len(sources[name]['model_paths']) != 1:
            raise ValueError(f'Mixed checkpoint paths in saved results: {name}')
        model = resolve_model(sources[name]['model_paths'][0], spec, args, overrides)
        raw = dict(name=name, family=spec['family'], stage=spec['stage'], model=str(model),
            model_key=str(overrides.get(name, args.base_model.as_posix() if name == 'base' else sources[name]['model_paths'][0])).replace('\\', '/'),
            saved_source=spec['path'], source_sha256=sources[name]['sha256'], mode='intrinsic', strength=0., rules=None)
        jobs.append(raw)
        if 'strength' in spec:
            rows = datasets[name]
            attack = rows[0]['attack']
            signature = lambda r: (r['attack']['rules_sha256'], r['attack']['rules_path'],
                                    json.dumps(r['attack']['tokenizer'], sort_keys=True), r['attack']['strength'])
            if any(signature(row) != signature(rows[0]) for row in rows):
                raise ValueError(f'Mixed WN rule/tokenizer/strength metadata: {name}')
            path = args.rules or ROOT / 'wn' / Path(attack['rules_path'].replace('\\', '/')).name
            raw_hash = digest(path) if path.is_file() else None
            lf_hash = hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest() if path.is_file() else None
            if attack['rules_sha256'] not in (raw_hash, lf_hash):
                raise ValueError(f'WN rules missing or SHA256 differs from saved run: {path}')
            tokenizer_path = args.wn_tokenizer.as_posix() if args.wn_tokenizer else attack['tokenizer']['name_or_path']
            biased = dict(raw, name=name + '_adjusted', mode='wn_adjusted', strength=spec['strength'],
                rules=str(path), rules_sha256=attack['rules_sha256'], wn_tokenizer=tokenizer_path,
                expected_rule_tokenizer=attack['tokenizer'])
            biased['rule_file_check'] = dict(raw_sha256=raw_hash, lf_sha256=lf_hash,
                matches_after_crlf_normalization=raw_hash != attack['rules_sha256'])
            jobs.append(biased)
            attacks[spec['strength']] = biased
    ref_job = next(j for j in jobs if j['name'] == reference)
    # Also measure the same WN transform on the clean control for matched ROC.
    for strength, attack in attacks.items():
        jobs.append(dict(ref_job, name=reference + '_wn_control_' + str(strength).replace('.', '_'),
            mode='wn_control', strength=strength, rules=attack['rules'], rules_sha256=attack['rules_sha256'],
            wn_tokenizer=attack['wn_tokenizer'], expected_rule_tokenizer=attack['expected_rule_tokenizer']))
    for job in jobs:
        if job['mode'] == 'wn_adjusted':
            job['comparison_reference'] = reference + '_wn_control_' + str(job['strength']).replace('.', '_')
        else:
            job['comparison_reference'] = reference
    return jobs


def model_signature(path):
    path = Path(path)
    weights = sorted(list(path.glob('*.safetensors')) + list(path.glob('pytorch_model*.bin')))
    if not (path / 'config.json').is_file() or not weights:
        raise FileNotFoundError(f'Local merged Hugging Face checkpoint required: {path}')
    for index_name in ('model.safetensors.index.json', 'pytorch_model.bin.index.json'):
        index = path / index_name
        if index.is_file():
            weight_map = json.loads(index.read_text(encoding='utf-8')).get('weight_map', {})
            required = set(weight_map.values())
            if not required or any(not isinstance(name, str) or Path(name).name != name for name in required):
                raise ValueError(f'Invalid checkpoint shard index: {index}')
            missing = sorted(name for name in required if not (path / name).is_file())
            if missing:
                raise FileNotFoundError(f'Incomplete checkpoint {path}; missing shards: {missing}')
    return dict(path=str(path), config_sha256=digest(path / 'config.json'),
        weights=[dict(name=p.name, bytes=p.stat().st_size, mtime_ns=p.stat().st_mtime_ns) for p in weights],
        weights_fully_hashed=False, identity_note='Config content plus weight file size/mtime manifest; not full weight hashes')


def static_signature(job, probe_info, args):
    # Content-based probe identity and original model locator survive a server ->
    # Windows cache copy. Resolved model assets are checked separately on CUDA.
    probe_identity = {k: v for k, v in probe_info.items() if k not in ('path', 'training_corpus')}
    return dict(version=VERSION, model=job['model_key'], probe=probe_identity, teacher_tokenizer=args.tokenizer.as_posix(),
        sequence_length=args.sequence_length, max_probe_tokens=args.max_probe_tokens, dtype=args.dtype,
        batch_size=args.batch_size, gamma=GAMMA, hash_key=KEY, rng='cuda', topk=1,
        strength=job['strength'], rules_sha256=job.get('rules_sha256'), wn_tokenizer=job.get('wn_tokenizer'),
        protocol=args.protocol, probe_seed=args.probe_seed, official_commit=OFFICIAL_COMMIT,
        input_format='teacher responses; no chat template/BOS/EOS',
        scoring_start=1 if args.protocol == 'official' else 0,
        output_vocabulary=('full model logits; reject predicted IDs outside teacher vocabulary' if args.protocol == 'official'
                           else 'real teacher token IDs; padded model output rows excluded'),
        prediction_selection='torch.topk(k=1)' if args.protocol == 'official' else 'argmax')


def cache_path(signature, args):
    key = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    return args.cache_dir / (key + '.json')


def validate_prediction_cache(payload, signature, probes):
    if payload.get('signature') != signature:
        raise ValueError('Reading cache protocol/source mismatch')
    vocab = payload.get('vocab_size')
    if type(vocab) is not int or vocab <= 1 or payload.get('runtime', {}).get('rng') != 'cuda':
        raise ValueError('Reading cache must record a real CUDA vocabulary/runtime')
    records = payload.get('records', [])
    if signature['protocol'] == 'official':
        if not records or [r.get('id') for r in records] != [f'chunk_{i:06d}' for i in range(len(records))]:
            raise ValueError('Reading cache official chunk IDs/order mismatch')
        probe_ids = {p['id'] for p in probes}
        if any(not r.get('probe_ids') or not set(r['probe_ids']) <= probe_ids or
               r.get('stream_start') != i * signature['sequence_length'] or len(r.get('chunks', [])) != 1
               for i, r in enumerate(records)):
            raise ValueError('Reading cache official chunk source mismatch')
        layout = payload.get('layout', {})
        if layout.get('protocol') != 'official' or layout.get('chunk_count') != len(records):
            raise ValueError('Reading cache official layout mismatch')
    elif [r.get('id') for r in records] != [r['id'] for r in probes]:
        raise ValueError('Reading cache probe IDs/order mismatch')
    if not payload.get('assets', {}).get('model') or not payload['assets'].get('teacher_tokenizer'):
        raise ValueError('Reading cache missing asset identity')
    for record in records:
        if not isinstance(record.get('chunks'), list) or type(record.get('input_tokens')) is not int:
            raise ValueError('Invalid cached reading document')
        combined = 0
        for chunk in record['chunks']:
            tokens, predicted, flags = chunk['input_ids'], chunk['predictions'], chunk['green_flags']
            if not 2 <= len(tokens) <= signature['sequence_length'] or len(predicted) != len(tokens) - 1 or len(flags) != len(predicted):
                raise ValueError('Invalid cached reading chunk lengths')
            if signature['protocol'] == 'official' and len(tokens) != signature['sequence_length']:
                raise ValueError('Official reading cache must contain full chunks only')
            if any(type(t) is not int or not 0 <= t < vocab for t in tokens + predicted):
                raise ValueError('Cached token outside teacher vocabulary')
            if any(type(f) is not int or f not in (0, 1) for f in flags):
                raise ValueError('Invalid cached CUDA green flags')
            combined += len(tokens)
        if not 0 <= record['input_tokens'] - combined <= 1:
            raise ValueError('Cached document/chunk token counts disagree')


def encode_probes(tokenizer, probes, args):
    if args.protocol == 'official':
        ordered = list(probes)
        random.Random(args.probe_seed).shuffle(ordered)
        tokens, origins = [], []
        for probe in ordered:
            # This matches TextDataset.tokenize -> convert_tokens_to_ids;
            # encode(add_special_tokens=False) is checked for equivalence.
            ids = tokenizer.convert_tokens_to_ids(tokenizer.tokenize(probe['text']))
            if ids != tokenizer.encode(probe['text'], add_special_tokens=False):
                raise ValueError(f'Official tokenize/encode mismatch: {probe["id"]}')
            if args.max_probe_tokens:
                ids = ids[:args.max_probe_tokens]
            tokens.extend(ids)
            origins.extend([probe['id']] * len(ids))
        records = []
        end = len(tokens) // args.sequence_length * args.sequence_length
        for i in range(0, end, args.sequence_length):
            chunk_ids = tokens[i:i + args.sequence_length]
            records.append(dict(id=f'chunk_{len(records):06d}', input_tokens=len(chunk_ids),
                                probe_ids=list(dict.fromkeys(origins[i:i + args.sequence_length])),
                                stream_start=i, chunks=[dict(input_ids=chunk_ids)]))
        if not records:
            raise ValueError('Official protocol needs at least one full sequence-length chunk; increase --limit or shorten --sequence-length')
        return records
    records = []
    for probe in probes:
        ids = tokenizer.encode(probe['text'], add_special_tokens=False)
        if args.max_probe_tokens:
            ids = ids[:args.max_probe_tokens]
        chunks = [dict(input_ids=ids[i:i + args.sequence_length])
                  for i in range(0, len(ids), args.sequence_length) if len(ids[i:i + args.sequence_length]) >= 2]
        records.append(dict(id=probe['id'], input_tokens=len(ids), chunks=chunks))
    if not any(r['chunks'] for r in records):
        raise ValueError('No teacher probe has at least two tokens')
    return records


def encoding_layout(tokenizer, probes, encoded, args):
    lengths = [len(tokenizer.encode(p['text'], add_special_tokens=False)) for p in probes]
    selected = sum(min(n, args.max_probe_tokens) if args.max_probe_tokens else n for n in lengths)
    read = sum(len(c['input_ids']) for r in encoded for c in r['chunks'])
    return dict(protocol=args.protocol, probe_seed=args.probe_seed, original_teacher_tokens=sum(lengths),
                selected_teacher_tokens=selected, truncated_teacher_tokens=sum(lengths) - selected,
                read_input_tokens=read, discarded_input_tokens=selected - read,
                chunk_count=sum(len(r['chunks']) for r in encoded),
                attention_span=args.sequence_length,
                candidate_positions=sum(max(0, len(c['input_ids']) - (2 if args.protocol == 'official' else 1))
                                        for r in encoded for c in r['chunks']))


def validate_tokenizer_compatibility(teacher, student, probes, args):
    if len(teacher) != len(student) or teacher.get_vocab() != student.get_vocab():
        raise ValueError('Teacher/student token-ID vocabularies differ; direct Reading mode is invalid')
    # Check actual tokenization, not file hashes (save_pretrained can rewrite files).
    for probe in probes:
        left = teacher.encode(probe['text'], add_special_tokens=False)
        right = student.encode(probe['text'], add_special_tokens=False)
        if args.max_probe_tokens:
            left, right = left[:args.max_probe_tokens], right[:args.max_probe_tokens]
        if left != right:
            raise ValueError(f'Teacher/student probe encoding mismatch: {probe["id"]}')


class GreenFlags:
    def __init__(self, tokenizer, device):
        import torch
        from wm_data.kgw import KGWConfig, KGWLogitsProcessor
        self.torch, self.device = torch, torch.device(device)
        self.processor = KGWLogitsProcessor(len(tokenizer), KGWConfig(gamma=GAMMA, delta=3, hash_key=KEY))
        self.cache = OrderedDict()

    def classify(self, records):
        # Build lists by context for a single device transfer per context.
        needed = defaultdict(list)
        for record in records:
            for chunk in record['chunks']:
                chunk['green_flags'] = [0] * len(chunk['predictions'])
                for j, (context, predicted) in enumerate(zip(chunk['input_ids'][:-1], chunk['predictions'])):
                    needed[context].append((chunk, j, predicted))
        torch = self.torch
        for context, positions in needed.items():
            mask = self.cache.get(context)
            if mask is None:
                mask = torch.zeros(self.processor.vocab_size, dtype=torch.bool, device=self.device)
                mask[self.processor._greenlist(context, self.device)] = True
                self.cache[context] = mask
                if len(self.cache) > 128:
                    self.cache.popitem(last=False)
            else:
                self.cache.move_to_end(context)
            flags = mask[torch.tensor([p[2] for p in positions], device=self.device)].tolist()
            for (chunk, index, _), green in zip(positions, flags):
                chunk['green_flags'][index] = int(green)


def infer(model, encoded, vocab, args, wn_processor=None):
    import torch
    records = [dict(id=r['id'], input_tokens=r['input_tokens'],
                    **{k: r[k] for k in ('probe_ids', 'stream_start') if k in r},
                    chunks=[dict(input_ids=list(c['input_ids'])) for c in r['chunks']]) for r in encoded]
    chunks = [chunk for record in records for chunk in record['chunks']]
    # Right padding, explicit attention mask: real-token logits are unaffected.
    for start in range(0, len(chunks), args.batch_size):
        batch = chunks[start:start + args.batch_size]
        length = max(len(c['input_ids']) for c in batch)
        ids = torch.zeros((len(batch), length), dtype=torch.long, device=args.device)
        mask = torch.zeros_like(ids)
        for i, chunk in enumerate(batch):
            values = chunk['input_ids']
            ids[i, :len(values)] = torch.tensor(values, device=args.device)
            mask[i, :len(values)] = 1
        with torch.inference_mode():
            output = model(input_ids=ids, attention_mask=mask, use_cache=False)
            for i, chunk in enumerate(batch):
                logits = output.logits[i, :len(chunk['input_ids'])]
                if not bool(torch.isfinite(logits[:, :vocab]).all()):
                    raise ValueError('Model produced non-finite logits')
                chunk['predictions'] = top1_predictions(logits, chunk['input_ids'], vocab, wn_processor,
                                                        official=getattr(args, 'protocol', 'documents') == 'official')
            del output
        if start == 0 or start + len(batch) == len(chunks) or start % (50 * args.batch_size) == 0:
            print(f'  Reading chunks {start + len(batch)}/{len(chunks)}', flush=True)
    return records


def asset_identity(job, args):
    result = dict(model=model_signature(job['model']), teacher_tokenizer=tokenizer_signature(args.tokenizer),
                  student_tokenizer=tokenizer_signature(Path(job['model'])))
    if job['strength']:
        result['wn_tokenizer'] = tokenizer_signature(Path(job['wn_tokenizer']))
        result['wn_rules_file_sha256'] = digest(job['rules'])
    return result


def collect_predictions(jobs, probes, probe_info, args):
    import torch
    if not args.from_cache_only and (not args.device.startswith('cuda') or not torch.cuda.is_available()):
        raise RuntimeError('Reading inference requires server CUDA; this computer cannot compute the real predictions/green lists')
    results, runtime = {}, dict(torch=torch.__version__, rng='cuda', dtype=args.dtype,
        transformers=importlib.metadata.version('transformers') if importlib.util.find_spec('transformers') else None,
        cuda=torch.version.cuda, device_name=torch.cuda.get_device_name(args.device) if torch.cuda.is_available() else None)
    teacher = green = encoded = layout = None
    by_model = defaultdict(list)
    for job in jobs:
        by_model[job['model']].append(job)
    for model_path, model_jobs in by_model.items():
        pending = []
        for job in model_jobs:
            signature = static_signature(job, probe_info, args)
            path = cache_path(signature, args)
            assets = None if args.from_cache_only else asset_identity(job, args)
            payload = None
            if path.is_file():
                candidate = json.loads(path.read_text(encoding='utf-8'))
                validate_prediction_cache(candidate, signature, probes)
                if args.from_cache_only or (candidate['assets'] == assets and candidate['runtime'] == runtime):
                    payload = candidate
                    print(f'Cache: {job["name"]}', flush=True)
            if payload is None:
                if args.from_cache_only:
                    raise FileNotFoundError(f'Validated server prediction cache required: {path}')
                pending.append((job, signature, path, assets))
            else:
                results[job['name']] = payload
        if not pending:
            continue
        from transformers import AutoModelForCausalLM, AutoTokenizer
        if teacher is None:
            teacher = AutoTokenizer.from_pretrained(str(args.tokenizer), local_files_only=True, trust_remote_code=False)
            encoded = encode_probes(teacher, probes, args)
            layout = encoding_layout(teacher, probes, encoded, args)
            green = GreenFlags(teacher, args.device)
        student = AutoTokenizer.from_pretrained(model_path, local_files_only=True, trust_remote_code=False)
        validate_tokenizer_compatibility(teacher, student, probes, args)
        print(f'Loading checkpoint: {model_path}', flush=True)
        model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True,
            trust_remote_code=False, torch_dtype=getattr(torch, args.dtype), attn_implementation='eager').to(args.device).eval()
        max_context = getattr(model.config, 'max_position_embeddings', args.sequence_length)
        if args.sequence_length > max_context:
            raise ValueError('sequence-length exceeds model context limit')
        try:
            for job, signature, path, assets in pending:
                # Raw WN/intrinsic jobs can point at the exact same checkpoint/cache.
                if path.is_file():
                    candidate = json.loads(path.read_text(encoding='utf-8'))
                    validate_prediction_cache(candidate, signature, probes)
                    if candidate['assets'] == assets and candidate['runtime'] == runtime:
                        results[job['name']] = candidate
                        continue
                processor = None
                if job['strength']:
                    from baseline_acl.inverse_watermark import RuleTable, VLLMInverseWatermarkProcessor, tokenizer_identities_match
                    rules = RuleTable.load(job['rules'])
                    wn_tok = AutoTokenizer.from_pretrained(job['wn_tokenizer'], local_files_only=True, trust_remote_code=False)
                    rules.validate_tokenizer(wn_tok)
                    if not tokenizer_identities_match(job['expected_rule_tokenizer'], rules.tokenizer):
                        raise ValueError('Saved WN tokenizer identity differs from rules')
                    validate_tokenizer_compatibility(teacher, wn_tok, probes, args)
                    processor = VLLMInverseWatermarkProcessor(rules, job['strength'], cache_tensors=True)
                print(f'Predict: {job["name"]} ({job["mode"]}, WN={job["strength"]})', flush=True)
                records = infer(model, encoded, len(teacher), args, processor)
                green.classify(records)
                payload = dict(signature=signature, runtime=runtime, assets=assets,
                               vocab_size=len(teacher), layout=layout, records=records)
                validate_prediction_cache(payload, signature, probes)
                write_json(path, payload)
                results[job['name']] = payload
        finally:
            del model
            gc.collect()
            torch.cuda.empty_cache()
    return results


def build_summary(jobs, payloads, reference, args):
    vocabularies = {p['vocab_size'] for p in payloads.values()}
    teachers = {json.dumps(p['assets']['teacher_tokenizer'], sort_keys=True) for p in payloads.values()}
    if len(vocabularies) != 1 or len(teachers) != 1:
        raise ValueError('Prediction caches disagree on teacher vocabulary/tokenizer identity')
    def input_identity(payload):
        return hashlib.sha256(json.dumps([
            (r['id'], r['input_tokens'], [c['input_ids'] for c in r['chunks']])
            for r in payload['records']], separators=(',', ':')).encode()).hexdigest()
    if len({input_identity(p) for p in payloads.values()}) != 1:
        raise ValueError('Models were not evaluated on exactly the same teacher input chunks')
    vocab = next(iter(vocabularies))
    q = max(1, int(vocab * GAMMA)) / vocab
    results = {name: score_reading(p['records'], q, tuple(args.budgets), args.protocol) for name, p in payloads.items()}
    unit_name = 'per_chunk' if args.protocol == 'official' else 'per_probe'
    rows = []
    for job in jobs:
        name, ref = job['name'], job['comparison_reference']
        for unit in ['per_probe'] + [str(b) for b in args.budgets]:
            get = lambda key: results[key]['per_probe'] if unit == 'per_probe' else results[key]['budgets'][unit]['groups']
            stats = results[name]['per_probe_summary'] if unit == 'per_probe' else results[name]['budgets'][unit]['summary']
            metric = dict(status='reference_only') if name == ref else roc(get(ref), get(name))
            row = dict(experiment=name, family=job['family'], stage=job['stage'], mode=job['mode'],
                       unit=unit_name if unit == 'per_probe' else unit, reference=ref, p_statistics=stats, metrics=metric)
            stage_reference = 'clean_' + job['stage']
            if stage_reference in results and job['mode'] == 'intrinsic' and name != stage_reference:
                row['stage_matched_reference'] = stage_reference
                row['metrics_vs_stage_clean'] = roc(get(stage_reference), get(name))
            if job['mode'] == 'wn_adjusted':
                row['metrics_vs_unmodified_reference'] = roc(get(reference), get(name))
            rows.append(row)
    return dict(version=VERSION, null_probability=q, nominal_gamma=GAMMA, reference=reference,
        budgets=args.budgets, jobs=jobs, rows=rows, protocol=args.protocol,
        unit_definition=unit_name, layouts={name: p.get('layout') for name, p in payloads.items()},
        official_source=dict(commit=OFFICIAL_COMMIT,
            reading=f'https://github.com/facebookresearch/radioactive-watermark/blob/{OFFICIAL_COMMIT}/main_reed_wm.py',
            detector=f'https://github.com/facebookresearch/radioactive-watermark/blob/{OFFICIAL_COMMIT}/wm/detector.py'),
        note='Per-probe/batch ROC for fixed checkpoints; not population model-level detection rates. Thresholds selected on evaluation units.',
        budget_definition='Candidate next-token positions BEFORE exclusions; N is effective positions AFTER attention-window and pair deduplication.',
        wn_note='Intrinsic WN shares unmodified checkpoint. wn_adjusted is a behavioral extension using recorded inverse bias before top-1; matched clean WN control is primary ROC.',
        results=results)


def markdown(summary):
    def fmt(value):
        if value is None:
            return 'N/A'
        return f'{value:.6g}' if isinstance(value, (float, int)) else str(value)
    lines = ['# Reading mode 检测结果', '',
        f"协议：{summary['protocol']}；{summary['unit_definition']} 为单个检测单元。",
        '预算为去重前的下一 token 预测位置数。N 是过滤、去重后的有效数。',
        'WN adjusted 的主 ROC 使用同规则/强度处理后的 clean 对照；另存对原始 clean 的补充 ROC。', '',
        '| 实验 | 单位/预算 | 对照 | AUROC | TPR≤5% (实际FPR) | TPR≤10% (实际FPR) | p中位数 | p算术平均 | 有效组数 | 平均N |',
        '|---|---|---|---:|---|---|---:|---:|---:|---:|']
    for row in summary['rows']:
        metric, stats = row['metrics'], row['p_statistics']
        work = metric.get('tpr_at_fpr', {})
        rate = lambda key: f"{fmt(work.get(key, {}).get('tpr'))} ({fmt(work.get(key, {}).get('fpr'))})"
        lines.append(f"|{row['experiment']}|{row['unit']}|{row['reference']}|{fmt(metric.get('auroc'))}|{rate('5%')}|{rate('10%')}|{fmt(stats['median_p_value'])}|{fmt(stats['mean_p_value'])}|{stats['valid_units']}|{fmt(stats.get('mean_effective_n'))}|")
    lines += ['', '## 与同阶段 clean 训练模型的补充比较', '',
              '| 实验 | 单位/预算 | clean 对照 | AUROC | TPR≤5% | TPR≤10% |',
              '|---|---|---|---:|---:|---:|']
    for row in summary['rows']:
        metric = row.get('metrics_vs_stage_clean')
        if metric:
            work = metric.get('tpr_at_fpr', {})
            lines.append(f"|{row['experiment']}|{row['unit']}|{row['stage_matched_reference']}|{fmt(metric.get('auroc'))}|{fmt(work.get('5%', {}).get('tpr'))}|{fmt(work.get('10%', {}).get('tpr'))}|")
    lines += ['', '## 整体模型的单次检验', '', '| 实验 | 读取token数 | 候选位置数 | 全局去重N | 绿名单命中率 | log10(p) |', '|---|---:|---:|---:|---:|---:|']
    for name, result in summary['results'].items():
        c = result['corpus']
        lines.append(f"|{name}|{result['total_input_tokens']}|{result['total_candidate_positions']}|{c['n']}|{fmt(c['green_fraction'])}|{fmt(c['log10_p_value'])}|")
    lines += ['', '## 理论阈值下的检出比例及 clean 误报检查', '',
              '| 实验 | 单位/预算 | 有效单元数 | p≤0.05 比例 | p≤1e-5 比例 |',
              '|---|---|---:|---:|---:|']
    for row in summary['rows']:
        s = row['p_statistics']
        lines.append(f"|{row['experiment']}|{row['unit']}|{s['valid_units']}|{fmt(s.get('fraction_p_le_0_05'))}|{fmt(s.get('fraction_p_le_1e_5'))}|")
    lines += ['', '小p表示支持存在水印偏好的证据，大p表示本次未检出。p均值/中位数不是合并检验p。',
              '单一checkpoint的多组探测不是多个独立模型；理论二项尾概率仍需clean误报检查。', '']
    return '\n'.join(lines)


def main(argv=None):
    args = parse_args(argv)
    inv_args = SimpleNamespace(manifest=args.manifest, experiments=args.experiments, reference=args.reference,
                               filter_mode='none', teacher_filter=None)
    specs, datasets, sources, reference, _ = inventory(inv_args)
    probes, probe_info = load_probes(args, [r['id'] for r in datasets[reference]])
    jobs = make_jobs(specs, datasets, sources, reference, args)
    checks = []
    for job in jobs:
        try:
            identity = model_signature(job['model'])
            checks.append(dict(name=job['name'], model=job['model'], weights_available=True, identity=identity))
        except FileNotFoundError as exc:
            checks.append(dict(name=job['name'], model=job['model'], weights_available=False, reason=str(exc)))
    import torch
    preflight = dict(version=VERSION, protocol=args.protocol, official_commit=OFFICIAL_COMMIT,
        protocol_settings=dict(sequence_length=args.sequence_length, probe_seed=args.probe_seed,
                               dtype=args.dtype, batch_size=args.batch_size, budgets=args.budgets),
        probe=probe_info, sources=sources, jobs=jobs, assets=checks,
        environment=dict(torch=torch.__version__, cuda_available=torch.cuda.is_available(),
                         transformers_available=importlib.util.find_spec('transformers') is not None,
                         teacher_tokenizer_available=args.tokenizer.is_dir()),
        can_run_inference=all(c['weights_available'] for c in checks) and torch.cuda.is_available()
                          and importlib.util.find_spec('transformers') is not None and args.tokenizer.is_dir())
    preflight['blockers'] = ([f"Missing checkpoint for {c['name']}: {c['model']}" for c in checks if not c['weights_available']]
        + ([] if torch.cuda.is_available() else ['CUDA PyTorch/device unavailable'])
        + ([] if importlib.util.find_spec('transformers') else ['transformers unavailable'])
        + ([] if args.tokenizer.is_dir() else [f'Teacher tokenizer missing: {args.tokenizer}'])
        + [f"WN tokenizer missing: {j['wn_tokenizer']}" for j in jobs if j.get('wn_tokenizer') and not Path(j['wn_tokenizer']).is_dir()])
    preflight['can_run_inference'] = preflight['can_run_inference'] and not preflight['blockers']
    if args.preflight:
        if args.output_dir:
            args.output_dir.mkdir(parents=True, exist_ok=False)
            write_json(args.output_dir / 'preflight.json', preflight)
        print(json.dumps(dict(probe=probe_info, environment=preflight['environment'],
            can_run_inference=preflight['can_run_inference'], blockers=preflight['blockers'],
            saved_experiments=len(specs), saved_answers=sum(len(rows) for rows in datasets.values()),
            jobs=[dict(name=j['name'], mode=j['mode'], model=j['model'], reference=j['comparison_reference'],
                       weights_available=c['weights_available']) for j, c in zip(jobs, checks)]), ensure_ascii=True, indent=2))
        return preflight
    out = args.output_dir or ROOT / 'new_detect/runs' / ('reading_' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    out.mkdir(parents=True, exist_ok=False)
    write_json(out / 'preflight.json', preflight)
    try:
        if not args.from_cache_only and preflight['blockers']:
            raise RuntimeError('Inference preflight failed:\n' + '\n'.join(preflight['blockers']))
        payloads = collect_predictions(jobs, probes, probe_info, args)
        summary = build_summary(jobs, payloads, reference, args)
        summary.update(probe=probe_info, created_at=datetime.now(timezone.utc).isoformat(),
            cache_only=args.from_cache_only, settings=vars(args).copy())
        summary['settings'] = {key: str(v) if isinstance(v, Path) else v for key, v in summary['settings'].items()}
        summary['provenance'] = {name: dict(signature=p['signature'], runtime=p['runtime'], assets=p['assets']) for name, p in payloads.items()}
        for name, result in summary['results'].items():
            write_json(out / (name + '.json'), dict(version=VERSION, probe=probe_info, result=result,
                provenance=summary['provenance'][name], job=next(j for j in jobs if j['name'] == name)))
        write_json(out / 'summary.json', summary)
        (out / 'summary.md').write_text(markdown(summary), encoding='utf-8')
        print(f'Saved Reading-mode results: {out}', flush=True)
        return summary
    except Exception as exc:
        write_json(out / 'failure.json', dict(error=type(exc).__name__, message=str(exc)))
        raise


if __name__ == '__main__':
    main()
