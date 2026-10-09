"""Analyze existing direct-KGW outputs only; no generation or GPU use."""
import hashlib
import json
import statistics
import sys
from pathlib import Path

import pyarrow.parquet as pq
from rouge_score import rouge_scorer
from transformers import AutoTokenizer

ROOT = Path('/shared/wwx/EasyGAD')
sys.path.insert(0, str(ROOT / 'wm_test'))
import evaluate_compare_metrics as detection

text_path = ROOT / 'data/dolly15k_qwen2_5_0.5b_kgw_test.parquet'
ref_path = ROOT / 'data/dolly15k_qwen2_5_14b_clean_test.parquet'
positive_path = ROOT / 'data/dolly15k_qwen2_5_0.5b_kgw_test_kgw_scores.jsonl'
negative_path = ROOT / 'data/dolly15k_qwen2_5_0.5b_clean_test_kgw_scores.jsonl'
audit_dir = ROOT / 'wm_test/pvalue_update_20261005'

def by_id(rows):
    result = {str(row['id']): row for row in rows}
    assert len(rows) == len(result), 'duplicate IDs'
    return result

samples = by_id(pq.read_table(text_path).to_pylist())
reference = by_id(pq.read_table(ref_path).to_pylist())
p_rows = by_id([json.loads(line) for line in (audit_dir / 'direct_kgw_05b_test.p_values.jsonl').read_text().splitlines()])
p_summary = json.loads((audit_dir / 'direct_kgw_05b_p_values_summary.json').read_text())
assert set(samples) == set(reference) == set(p_rows) and len(samples) == 500
print('P_SUMMARY_PROVENANCE', json.dumps({k: v for k, v in p_summary.items() if 'sha' in k or 'file' in k}), flush=True)
roc = detection.evaluate(detection.load_scores(negative_path, 'clean', False), detection.load_scores(positive_path, 'kgw', True))
tokenizer = AutoTokenizer.from_pretrained('/shared/public_models/Qwen2.5-0.5B', local_files_only=True)
scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
rows = []
for index, (sample_id, sample) in enumerate(samples.items(), 1):
    assert sample['content'] == reference[sample_id]['content'], sample_id
    answer = sample['teacher_response']
    rouge = scorer.score(reference[sample_id]['teacher_response'], answer)['rougeL'].fmeasure
    tokens = tokenizer.encode(answer, add_special_tokens=False)
    pairs = list(zip(tokens, tokens[1:]))
    ratio = 1 - len(set(pairs)) / len(pairs) if pairs else 0.0
    rows.append({'id': sample_id, 'rouge_l_clean_teacher': rouge,
                 'repeated_bigram_fraction': ratio, 'severe_repetition': ratio > .5,
                 'answer_tokens': len(tokens), **{k: p_rows[sample_id][k] for k in ['p_value_raw', 'p_value_dedup']}})
    if index % 100 == 0:
        print('QUALITY', index, '/500', flush=True)
result = {'model': 'Qwen2.5-0.5B with inference-time KGW', 'n': len(rows),
          'auroc': roc['auroc'], 'tpr_at_fpr': roc['tpr_at_fpr'],
          'rouge_l_clean_teacher_mean': statistics.mean(row['rouge_l_clean_teacher'] for row in rows),
          'severe_repetition_count': sum(row['severe_repetition'] for row in rows),
          'severe_repetition_fraction': statistics.mean(row['severe_repetition'] for row in rows),
          'p_value_raw_mean': statistics.mean(row['p_value_raw'] for row in rows),
          'p_value_dedup_mean': statistics.mean(row['p_value_dedup'] for row in rows),
          'sources_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in [text_path, ref_path, positive_path, negative_path]},
          'rouge_method': "rouge-score RougeScorer(['rougeL'], use_stemmer=True), mean per-answer F1, ID-aligned clean 14B teacher",
          'repetition_method': '1 - unique adjacent token pairs / all adjacent token pairs > 0.5, full answer, Qwen0.5B tokenizer',
          'p_value_method': 'mean per-answer single-sided normal p, saved scored token span, raw and unique context-token pairs'}
(audit_dir / 'direct_kgw_05b_table_metrics.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
with (audit_dir / 'direct_kgw_05b_table_metrics.jsonl').open('w') as handle:
    for row in rows:
        handle.write(json.dumps(row) + '\n')
print('RESULT', json.dumps(result, ensure_ascii=False), flush=True)
