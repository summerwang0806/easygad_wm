"""Teacher-forced top-1 observations and Reading-mode statistical units."""
from __future__ import annotations

from collections import Counter

from new_detect.core import binomial_score, summarize


def attention_eligibility(input_ids, start=0):
    """For k=1, only the first occurrence of a window in this attention span.

    Position j predicts x[j+1] from x[:j+1]. The window is x[j], so the current
    occurrence itself must NOT be included in the set of previous occurrences.
    """
    seen, flags = set(), []
    # Official main_reed_wm.py uses target=x[:, 1:] for its windows, so
    # it starts at x[1] and its attention tape does not contain x[0].
    for context in input_ids[start:-1]:
        flags.append(context not in seen)
        seen.add(context)
    return flags


class ReadingTape:
    def __init__(self):
        self.seen = set()
        self.green = 0
        self.counts = Counter()

    def add(self, context, prediction, green, eligible):
        self.counts['candidate_positions'] += 1
        if not eligible:
            self.counts['attention_repeats_excluded'] += 1
        elif (context, prediction) in self.seen:
            self.counts['duplicate_pairs_excluded'] += 1
        else:
            self.seen.add((context, prediction))
            self.green += green

    def result(self, q):
        return {**dict(self.counts), **binomial_score(len(self.seen), self.green, q)}


def score_reading(records, q, budgets=(1000, 2000, 3000), protocol='documents'):
    """Each chunk is an actual attention span, with no carried KV state.

    Official layout records are fixed chunks of a shuffled concatenated stream;
    document layout records keep individual teacher responses separate.

    A budget counts next-token prediction positions before exclusions. Test
    tapes reset between groups, but the within-attention-span exclusion never
    resets at a statistical group boundary. Corpus tape spans every document.
    """
    if not budgets or len(set(budgets)) != len(budgets) or any(type(b) is not int or b < 1 for b in budgets):
        raise ValueError('Budgets must be distinct positive integers')
    if protocol not in ('documents', 'official'):
        raise ValueError('Unknown reading protocol')
    start = 1 if protocol == 'official' else 0
    corpus = ReadingTape()
    tapes = {b: ReadingTape() for b in budgets}
    groups = {b: [] for b in budgets}
    ids = {b: [] for b in budgets}
    source_ids = {b: [] for b in budgets}
    documents, offset, total_input = [], 0, 0
    for record in records:
        document = ReadingTape()
        for chunk in record['chunks']:
            tokens, predictions, flags = chunk['input_ids'], chunk['predictions'], chunk['green_flags']
            if len(predictions) != max(0, len(tokens) - 1) or len(flags) != len(predictions):
                raise ValueError('Reading input/prediction/green length mismatch')
            total_input += len(tokens)
            for context, predicted, green, eligible in zip(tokens[start:-1], predictions[start:], flags[start:], attention_eligibility(tokens, start)):
                if type(green) is not int or green not in (0, 1):
                    raise ValueError('Green flags must be integer 0/1')
                event = context, predicted, green, eligible
                document.add(*event)
                corpus.add(*event)
                for budget in budgets:
                    tapes[budget].add(*event)
                    if not ids[budget] or ids[budget][-1] != record['id']:
                        ids[budget].append(record['id'])
                        for sid in record.get('probe_ids', [record['id']]):
                            if sid not in source_ids[budget]:
                                source_ids[budget].append(sid)
                    if tapes[budget].counts['candidate_positions'] == budget:
                        groups[budget].append(dict(index=len(groups[budget]), start_position=offset + 1 - budget,
                            end_position=offset + 1, unit_ids=ids[budget], probe_ids=source_ids[budget], **tapes[budget].result(q)))
                        tapes[budget], ids[budget], source_ids[budget] = ReadingTape(), [], []
                offset += 1
        documents.append(dict(id=record['id'], probe_ids=record.get('probe_ids', [record['id']]), **document.result(q)))
    return dict(corpus=corpus.result(q), total_input_tokens=total_input,
                source_teacher_tokens=sum(r['input_tokens'] for r in records),
                dropped_singleton_tokens=sum(r['input_tokens'] for r in records) - total_input,
                protocol=protocol,
                unit_definition='fixed attention-span chunk' if protocol == 'official' else 'teacher response',
                total_candidate_positions=offset, per_probe=documents, per_probe_summary=summarize(documents),
                budgets={str(b): dict(groups=groups[b], summary=summarize(groups[b]),
                    discarded_tail_positions=tapes[b].counts['candidate_positions']) for b in budgets})


def top1_predictions(logits, input_ids, vocab_size, wn_processor=None, official=False):
    """Align logits[j] with x[j+1]; never feed predictions back into the model.

    Document mode excludes padded output rows; official mode preserves original
    topk and stops if the selected ID does not exist in the teacher tokenizer.
    WN uses the same sparse inverse-bias processor as the original generator.
    """
    if len(logits.shape) != 2 or logits.shape[0] != len(input_ids) or logits.shape[1] < vocab_size:
        raise ValueError('Unexpected model logits shape')
    # Official code uses torch.topk(k=1) on the model output, rather than
    # argmax; ties need not select the same ID. Preserve raw dtype for parity.
    scores = logits[:-1] if official else logits[:-1, :vocab_size]
    if wn_processor is not None:
        scores = scores.float().clone()
        for j in range(len(input_ids) - 1):
            wn_processor(input_ids[:j + 1], [], scores[j])
    predicted = (scores.topk(1, dim=-1).indices.squeeze(-1) if official else scores.argmax(dim=-1)).tolist()
    if any(token >= vocab_size for token in predicted):
        raise ValueError('Official top-1 selected an output padding row outside the teacher vocabulary; cannot score this checkpoint with the original protocol')
    return predicted
