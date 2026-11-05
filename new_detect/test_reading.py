"""CPU fixtures verify the scientific protocol; no real scores are fabricated."""
import copy
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import torch

from new_detect import run_reading as runner
from new_detect.reading_core import attention_eligibility, score_reading, top1_predictions
from new_detect.core import binomial_score


def record(sid, ids, predicted, flags):
    return dict(id=sid, input_tokens=len(ids), chunks=[dict(input_ids=ids, predictions=predicted, green_flags=flags)])


class ReadingProtocolTests(unittest.TestCase):
    def test_official_topk_ties_dtype_and_invalid_padding_prediction(self):
        logits = torch.zeros((3, 7), dtype=torch.float16)
        expected = torch.topk(logits[:-1], 1, dim=-1).indices.squeeze(-1).tolist()
        self.assertEqual(top1_predictions(logits, [1, 2, 3], 7, official=True), expected)
        logits[0, 6] = 9.
        with self.assertRaisesRegex(ValueError, 'padding row'):
            top1_predictions(logits, [1, 2, 3], 6, official=True)

    def test_official_indices_and_tapes_match_original_target_loop(self):
        # Independent transcription of the original k=1 target/outputs loop.
        # Its target starts at x[1]; context x[0] is neither scored nor taped.
        chunks = [([1, 1, 2, 1, 3, 4], [0, 5, 6, 7, 8]),
                  ([0, 1, 2, 1, 3, 4], [9, 5, 7, 8, 8])]
        seen_pairs, reference = set(), []
        rows = []
        for i, (ids, predicted) in enumerate(chunks):
            target, tape = ids[1:], set()
            flags = [p % 2 for p in predicted]
            for j in range(len(target) - 1):
                window, token = target[j], predicted[j + 1]
                if window not in tape:
                    tape.add(window)
                    if (window, token) not in seen_pairs:
                        seen_pairs.add((window, token))
                        reference.append(token % 2)
            rows.append(record(str(i), ids, predicted, flags))
        actual = score_reading(rows, .5, (4,), protocol='official')
        expected = binomial_score(len(reference), sum(reference), .5)
        self.assertEqual(actual['total_candidate_positions'], 8)
        self.assertEqual(actual['corpus']['n'], expected['n'])
        self.assertEqual(actual['corpus']['green'], expected['green'])
        self.assertAlmostEqual(actual['corpus']['p_value'], expected['p_value'])
        self.assertEqual(attention_eligibility(chunks[0][0], start=1), [True, True, False, True])

    def test_binomial_tail_matches_official_maryland_betainc(self):
        from scipy.special import betainc
        for n in (1, 10, 254, 1000):
            for g in sorted({1, max(1, n // 2), n}):
                official = float(betainc(g, 1 + n - g, .5))
                self.assertAlmostEqual(binomial_score(n, g, .5)['log10_p_value'],
                                       __import__('math').log10(official), places=9)
        self.assertEqual(binomial_score(4, 0, .5)['p_value'], 1.)

    def test_attention_window_excludes_prior_occurrences_not_current_one(self):
        self.assertEqual(attention_eligibility([1, 2, 1, 3, 2, 4]), [True, True, False, True, False])

    def test_prediction_alignment_uses_student_prediction_not_teacher_target(self):
        logits = torch.tensor([[0., 1., 5., 99.], [8., 1., 0., 99.], [0., 9., 1., 99.]])
        self.assertEqual(top1_predictions(logits, [0, 1, 2], 3), [2, 0])
        # Last logit has no reference next position; padded vocab column ignored.
        with self.assertRaises(ValueError):
            top1_predictions(logits, [0, 1], 3)

    def test_wn_bias_context_is_teacher_prefix_and_does_not_mutate_raw_logits(self):
        logits = torch.tensor([[0., 1., 5.], [0., 1., 5.], [0., 0., 0.]])
        before = logits.clone()
        seen = []
        def bias(prompt, generated, scores):
            seen.append((list(prompt), list(generated)))
            scores[2] -= 10
        result = top1_predictions(logits, [2, 0, 1], 3, bias)
        self.assertEqual(result, [1, 1])
        self.assertEqual(seen, [([2], []), ([2, 0], [])])
        self.assertTrue(torch.equal(logits, before))

    def test_corpus_dedup_across_documents_and_group_resets(self):
        rows = [record('a', [1, 2, 1, 3], [5, 6, 7], [1, 0, 1]),
                record('b', [1, 4], [5], [1])]
        result = score_reading(rows, .5, (2,))
        self.assertEqual((result['corpus']['n'], result['corpus']['green']), (2, 1))
        self.assertEqual(result['corpus']['attention_repeats_excluded'], 1)
        self.assertEqual(result['corpus']['duplicate_pairs_excluded'], 1)
        self.assertEqual([g['n'] for g in result['budgets']['2']['groups']], [2, 1])
        self.assertEqual([g['n'] for g in result['per_probe']], [2, 1])

    def test_group_boundary_does_not_reset_attention_exclusion(self):
        result = score_reading([record('a', [1, 2, 1, 2, 3], [4, 5, 6, 7], [1, 1, 1, 1])], .5, (2, 3))
        groups = result['budgets']['2']['groups']
        self.assertEqual([g['n'] for g in groups], [2, 0])
        self.assertEqual(result['budgets']['3']['discarded_tail_positions'], 1)
        self.assertIsNone(groups[1]['p_value'])

    def test_chunk_boundary_resets_actual_attention_but_not_corpus_pairs(self):
        row = record('a', [1, 2], [5], [1])
        row['chunks'].append(dict(input_ids=[1, 3], predictions=[6], green_flags=[0]))
        row['input_tokens'] = 4
        result = score_reading([row], .5, (2,))
        self.assertEqual(result['corpus']['n'], 2)
        self.assertEqual(result['total_input_tokens'], 4)
        self.assertEqual(result['total_candidate_positions'], 2)

    def test_real_wn_processor_matches_legacy_hook(self):
        from baseline_acl.inverse_watermark import RuleTable, VLLMInverseWatermarkProcessor
        rules = RuleTable.__new__(RuleTable)
        rules.vocab_size, rules.max_prefix = 3, 1
        rules.global_scores = {2: .5}
        rules.prefix_scores = {(1,): (2., {2: 1.})}
        logits = torch.tensor([[0., 2., 4.], [0., 2., 4.], [0., 0., 0.]])
        processor = VLLMInverseWatermarkProcessor(rules, 2.5, cache_tensors=True)
        self.assertEqual(top1_predictions(logits, [1, 0, 2], 3, processor), [1, 2])


class ReadingRunnerTests(unittest.TestCase):
    def test_default_protocol_matches_official_layout_and_precision(self):
        args = runner.parse_args([])
        self.assertEqual((args.protocol, args.probe_seed, args.sequence_length, args.dtype),
                         ('official', 0, 256, 'float16'))

    def test_official_shuffle_concatenation_tail_and_source_mapping(self):
        import random
        args = SimpleNamespace(protocol='official', probe_seed=7, sequence_length=4, max_probe_tokens=None)
        tok = SimpleNamespace(tokenize=lambda text: text.split(),
                              convert_tokens_to_ids=lambda parts: list(map(int, parts)),
                              encode=lambda text, add_special_tokens: list(map(int, text.split())))
        probes = [dict(id='a', text='1 2 3'), dict(id='b', text='4 5 6'), dict(id='c', text='7 8 9')]
        expected = list(probes)
        random.Random(7).shuffle(expected)
        stream = [int(t) for p in expected for t in p['text'].split()]
        actual = runner.encode_probes(tok, probes, args)
        self.assertEqual([c['input_ids'] for r in actual for c in r['chunks']], [stream[:4], stream[4:8]])
        self.assertEqual(len(actual[0]['probe_ids']), 2)
        self.assertEqual([p['id'] for p in probes], ['a', 'b', 'c'])
        layout = runner.encoding_layout(tok, probes, actual, args)
        self.assertEqual((layout['read_input_tokens'], layout['discarded_input_tokens'], layout['candidate_positions']), (8, 1, 4))

    def test_official_cache_full_cli_and_input_validation(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            root = Path(temp)
            args = runner.parse_args(['--from-cache-only', '--sequence-length', '4', '--budgets', '2',
                                      '--cache-dir', str(root / 'cache'), '--output-dir', str(root / 'output')])
            probes = [dict(id='a', text='teacher')]
            jobs = [dict(name=name, family='kgw', stage='gad', model='missing/' + name, model_key='/server/' + name,
                         mode='intrinsic', strength=0., comparison_reference='base') for name in ('base', 'target')]
            for job in jobs:
                signature = runner.static_signature(job, dict(sha256='abc'), args)
                row = record('chunk_000000', [1, 2, 3, 4], [0, 5, 6], [0, 0, 0] if job['name'] == 'base' else [1, 1, 1])
                row.update(probe_ids=['a'], stream_start=0)
                payload = dict(signature=signature, vocab_size=8, runtime=dict(rng='cuda'),
                    assets=dict(model={'id': 'fixture'}, teacher_tokenizer={'sha': 'fixture'}),
                    layout=dict(protocol='official', chunk_count=1), records=[row])
                runner.write_json(runner.cache_path(signature, args), payload)
                runner.validate_prediction_cache(payload, signature, probes)
                bad = copy.deepcopy(payload)
                bad['records'][0]['stream_start'] = 1
                with self.assertRaisesRegex(ValueError, 'source mismatch'):
                    runner.validate_prediction_cache(bad, signature, probes)
            argv = ['--from-cache-only', '--sequence-length', '4', '--budgets', '2',
                    '--cache-dir', str(root / 'cache'), '--output-dir', str(root / 'output')]
            with patch.object(runner, 'inventory', return_value=([], {'base': [dict(id='a')]}, {}, 'base', None)), \
                 patch.object(runner, 'load_probes', return_value=(probes, dict(sha256='abc'))), \
                 patch.object(runner, 'make_jobs', return_value=jobs):
                summary = runner.main(argv)
            target = next(r for r in summary['rows'] if r['experiment'] == 'target' and r['unit'] == '2')
            self.assertEqual(target['metrics']['auroc'], 1.)
            self.assertAlmostEqual(target['p_statistics']['mean_p_value'], .25)
            self.assertTrue((root / 'output' / 'summary.md').is_file())

    def args(self, directory):
        return runner.parse_args(['--cache-dir', str(directory / 'cache'), '--protocol', 'documents'])

    def test_probe_order_and_heldout_overlap_guard(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            root = Path(temp)
            probe, train = root / 'probe.jsonl', root / 'train.jsonl'
            probe.write_text(json.dumps(dict(id='x', teacher_response='text')) + '\n', encoding='utf-8')
            train.write_text(json.dumps(dict(id='x')) + '\n', encoding='utf-8')
            args = self.args(root)
            args.probe, args.training_corpus = probe, train
            with self.assertRaisesRegex(ValueError, 'overlaps'):
                runner.load_probes(args, ['x'])
            args.probe_split = 'supervised'
            rows, info = runner.load_probes(args, ['x'])
            self.assertEqual(info['overlap_with_original_teacher_train'], 1)
            self.assertEqual(rows[0]['text'], 'text')

    def test_encoding_preserves_documents_and_short_tail(self):
        args = SimpleNamespace(sequence_length=3, max_probe_tokens=None, protocol='documents')
        tok = SimpleNamespace(encode=lambda text, add_special_tokens: list(map(int, text.split())))
        encoded = runner.encode_probes(tok, [dict(id='a', text='1 2 3 4'), dict(id='b', text='5 6')], args)
        self.assertEqual([c['input_ids'] for r in encoded for c in r['chunks']], [[1, 2, 3], [5, 6]])
        self.assertEqual(encoded[0]['input_tokens'], 4)

    def test_infer_right_padding_and_causal_alignment(self):
        class FakeModel:
            def __call__(self, input_ids, attention_mask, use_cache):
                self.mask = attention_mask.clone()
                # Deterministic token prediction dependent on actual teacher IDs.
                logits = torch.nn.functional.one_hot((input_ids + 1) % 8, num_classes=8).float()
                return SimpleNamespace(logits=logits)
        model = FakeModel()
        encoded = [dict(id='a', input_tokens=3, chunks=[dict(input_ids=[1, 4, 6])]),
                   dict(id='b', input_tokens=2, chunks=[dict(input_ids=[2, 3])])]
        args = SimpleNamespace(device='cpu', batch_size=2)
        result = runner.infer(model, encoded, 8, args)
        self.assertEqual(result[0]['chunks'][0]['predictions'], [2, 5])
        self.assertEqual(result[1]['chunks'][0]['predictions'], [3])
        self.assertEqual(model.mask.tolist(), [[1, 1, 1], [1, 1, 0]])

    def test_portable_cache_integrity_and_cpu_summary(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            args = self.args(Path(temp))
            args.from_cache_only = True
            args.budgets = [2]
            probes = [dict(id='a', text='teacher')]
            jobs = [dict(name='base', family='base', stage='base', model='local/base', model_key='/server/base',
                         mode='intrinsic', strength=0., comparison_reference='base'),
                    dict(name='target', family='kgw', stage='gad', model='local/student', model_key='/server/student',
                         mode='intrinsic', strength=0., comparison_reference='base')]
            for job in jobs:
                signature = runner.static_signature(job, dict(path='/server/probe', sha256='abc'), args)
                payload = dict(signature=signature, vocab_size=8, runtime=dict(rng='cuda'),
                    assets=dict(model={'identity': 'fixture'}, teacher_tokenizer={'sha': 'fixture'}),
                    records=[record('a', [1, 2, 3], [4, 5], [0, 0] if job['name'] == 'base' else [1, 1])])
                runner.write_json(runner.cache_path(signature, args), payload)
                bad = copy.deepcopy(payload)
                bad['records'][0]['chunks'][0]['predictions'][0] = 8
                with self.assertRaisesRegex(ValueError, 'outside'):
                    runner.validate_prediction_cache(bad, signature, probes)
            payloads = runner.collect_predictions(jobs, probes, dict(path='C:/local/probe', sha256='abc'), args)
            summary = runner.build_summary(jobs, payloads, 'base', args)
            metric = next(r for r in summary['rows'] if r['experiment'] == 'target' and r['unit'] == '2')
            self.assertEqual(metric['metrics']['auroc'], 1.)
            self.assertAlmostEqual(metric['p_statistics']['mean_p_value'], .25)
            self.assertIn('Reading mode', runner.markdown(summary))

    def test_model_paths_and_override_do_not_choose_latest_checkpoint(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            args = self.args(Path(temp))
            spec = dict(name='target')
            saved = '/shared/wwx/EasyGAD/checkpoints/experiment/gad/global_step_1813/actor/huggingface'
            actual = runner.resolve_model(saved, spec, args, {})
            self.assertEqual(actual, args.checkpoint_root / 'experiment/gad/global_step_1813/actor/huggingface')
            self.assertEqual(runner.resolve_model(saved, spec, args, {'target': '/other/exact'}), Path('/other/exact'))

    def test_model_signature_rejects_missing_weight_shards(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as temp:
            root = Path(temp)
            (root / 'config.json').write_text('{}')
            (root / 'model-00001-of-00002.safetensors').write_bytes(b'fixture')
            (root / 'model.safetensors.index.json').write_text(json.dumps(dict(weight_map={
                'a': 'model-00001-of-00002.safetensors', 'b': 'model-00002-of-00002.safetensors'})))
            with self.assertRaisesRegex(FileNotFoundError, 'missing shards'):
                runner.model_signature(root)

    def test_summary_rejects_mismatched_teacher_inputs(self):
        args = runner.parse_args(['--protocol', 'documents', '--budgets', '2'])
        payloads = {name: dict(vocab_size=8, assets=dict(teacher_tokenizer={'id': 'same'}),
                              records=[record('a', ids, [4, 5], [1, 0])])
                    for name, ids in [('base', [1, 2, 3]), ('target', [1, 2, 4])]}
        with self.assertRaisesRegex(ValueError, 'same teacher input'):
            runner.build_summary([], payloads, 'base', args)

    def test_current_inventory_wn_hash_crlf_and_matched_controls(self):
        args = runner.parse_args([])
        inv = SimpleNamespace(manifest=args.manifest, experiments=None, reference=None, filter_mode='none', teacher_filter=None)
        specs, datasets, sources, reference, _ = runner.inventory(inv)
        jobs = runner.make_jobs(specs, datasets, sources, reference, args)
        self.assertEqual(len(jobs), 17)
        names = {j['name'] for j in jobs}
        self.assertTrue({'wn_2_5_adjusted', 'wn_3_adjusted', 'base_wn_control_2_5', 'base_wn_control_3_0'} <= names)
        raw = next(j for j in jobs if j['name'] == 'wn_2_5')
        kgw = next(j for j in jobs if j['name'] == 'kgw_gad')
        self.assertEqual(raw['model_key'], kgw['model_key'])
        adjusted = next(j for j in jobs if j['name'] == 'wn_2_5_adjusted')
        self.assertEqual(adjusted['comparison_reference'], 'base_wn_control_2_5')
        self.assertEqual(adjusted['rules_sha256'], '52703fa7641438a7f9426de07990395cf3df5df2be1aaf250248fd327f40161d')


if __name__ == '__main__':
    unittest.main()
