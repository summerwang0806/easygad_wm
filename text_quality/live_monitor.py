"""Terminal progress, append-only live metrics and resumable SwanLab logging."""
from datetime import datetime, timezone
import inspect
import json
import os
from pathlib import Path
import re
import statistics
import time
import uuid


def live_scores(records, total_samples):
    groups = {}
    for row in records:
        groups.setdefault((row['left'], row['right']), []).append(row)
    values = {}
    for (left, right), rows in groups.items():
        prefix = f"quality/{left}_vs_{right}"
        values[prefix + '/n'] = len(rows)
        values[prefix + '/coverage'] = len(rows) / total_samples
        values[prefix + '/overall'] = statistics.mean(r['left_scores']['overall'] for r in rows)
        values[prefix + '/relative_score'] = statistics.mean(r['left_relative_score'] for r in rows)
        values[prefix + '/overall_difference'] = statistics.mean(
            r['left_scores']['overall']-r['right_scores']['overall'] for r in rows)
        for dimension in rows[0]['left_scores']:
            values[prefix + '/' + dimension] = statistics.mean(r['left_scores'][dimension] for r in rows)
        for winner in ('left', 'tie', 'right'):
            values[prefix + '/' + winner + '_rate'] = sum(r['winner'] == winner for r in rows) / len(rows)
        values[prefix + '/order_agreement'] = sum(r['order_agreement'] for r in rows) / len(rows)
    # Model differences must use the SAME prompts, not independently arriving means.
    by_model = {}
    for row in records:
        if row['right'] == 'reference':
            by_model.setdefault(row['left'], {})[row['id']] = row['left_relative_score']
    for left in by_model:
        for right in by_model:
            if left >= right:
                continue
            shared = set(by_model[left]) & set(by_model[right])
            if shared:
                prefix = f"paired/{left}_minus_{right}"
                values[prefix + '/n'] = len(shared)
                values[prefix + '/relative_score_difference'] = statistics.mean(
                    by_model[left][i]-by_model[right][i] for i in shared)
    return values


class LiveMonitor:
    def __init__(self, args, configuration, total_samples, total_comparisons, total_calls,
                 append, atomic, digest):
        self.args, self.configuration = args, configuration
        self.total_samples, self.total_comparisons, self.total_calls = total_samples, total_comparisons, total_calls
        self.append, self.atomic = append, atomic
        self.directory = args.output_dir
        self.started, self.last = time.monotonic(), 0
        self.session_id = uuid.uuid4().hex
        self.run, self.swanlab, self.state = None, None, None
        self.bar = None
        try:
            from tqdm.auto import tqdm
            self.bar = tqdm(total=total_samples, desc='Quality evaluation', unit='prompt',
                            disable=not args.progress_bar)
        except ImportError:
            print('tqdm unavailable; using periodic text progress', flush=True)
        if args.swanlab_mode != 'disabled':
            try:
                import swanlab
                self.swanlab = swanlab
                key = os.environ.get('SWANLAB_API_KEY', '')
                if args.swanlab_key_file:
                    key = args.swanlab_key_file.read_text(encoding='utf-8').strip()
                elif not key and args.swanlab_key_from_script:
                    text = args.swanlab_key_from_script.read_text(encoding='utf-8')
                    match = re.search(r"export\s+SWANLAB_API_KEY\s*=\s*['\"]([^'\"]+)['\"]", text)
                    if match and not match[1].startswith(('YOUR_', '$')):
                        key = match[1]
                if args.swanlab_mode == 'cloud':
                    if not key:
                        raise ValueError('Configure SWANLAB_API_KEY or a SwanLab key file/script')
                    swanlab.login(api_key=key, save=False)
                state_path = self.directory / 'swanlab_state.json'
                identity = {'configuration': digest(configuration), 'project': args.swanlab_project,
                            'workspace': args.swanlab_workspace, 'mode': args.swanlab_mode}
                if state_path.exists():
                    state = json.loads(state_path.read_text(encoding='utf-8'))
                    if state['identity'] != identity:
                        raise ValueError('SwanLab identity changed; choose a new result directory')
                else:
                    state = {'identity': identity, 'id': uuid.uuid4().hex[:21], 'step': 0}
                mode = args.swanlab_mode
                # Match the SDK installed on the server; newer SDK calls cloud mode online.
                if mode == 'cloud' and 'online' in str(inspect.signature(swanlab.init).parameters['mode']):
                    mode = 'online'
                self.run = swanlab.init(project=args.swanlab_project, workspace=args.swanlab_workspace,
                    experiment_name=args.swanlab_name or self.directory.name,
                    config={**configuration, 'concurrency': args.concurrency, 'task': 'text_quality'},
                    logdir=str(self.directory / 'swanlog'), mode=mode,
                    **({'id': state['id'], 'resume': 'allow'} if args.swanlab_mode == 'cloud' else {}))
                state['id'] = self.run.id or state['id']
                self.state = state
                self.atomic(state_path, json.dumps(state, indent=2))
                print(f"SwanLab {args.swanlab_mode}: project={args.swanlab_project}, experiment_id={state['id']}", flush=True)
            except Exception as exc:
                print(f'WARNING: SwanLab unavailable ({type(exc).__name__}); live metrics remain local.', flush=True)
                self.run = None

    def update(self, records, completed, cache, client, force=False, final=False):
        now = time.monotonic()
        if not force and now-self.last < self.args.live_interval:
            return
        self.last = now
        with cache.lock:
            seconds = list(cache.request_seconds)
            selected = set(self.configuration['inputs'])
            cached = sum(r['id'] in self.selected_ids and
                         (r['kind'] == 'judge' and r['meta'].get('left') in selected or
                          r['kind'] == 'reference' and self.configuration['references_digest'] is None)
                         for r in cache.rows.values())
        average = statistics.mean(seconds) if seconds else None
        remaining = max(0, self.total_calls-cached)
        eta = remaining * average / self.args.concurrency if average else None
        values = {'progress/prompts_finished': completed, 'progress/prompts_total': self.total_samples,
                  'progress/comparisons_complete': len(records), 'progress/comparisons_total': self.total_comparisons,
                  'progress/coverage': len(records)/self.total_comparisons,
                  'progress/api_requests_this_run': client.calls, 'progress/cached_requests': cached,
                  'timing/elapsed_seconds': now-self.started, 'status/final': int(final),
                  'status/complete': int(len(records) == self.total_comparisons), **live_scores(records, self.total_samples)}
        if average is not None:
            values['timing/mean_request_seconds'] = average
            values['timing/estimated_remaining_seconds'] = eta
        row = {'recorded_at_utc': datetime.now(timezone.utc).isoformat(), 'session_id': self.session_id,
               'metrics': values, 'swanlab_connected': self.run is not None}
        self.append(self.directory / 'live_metrics.jsonl', row)
        self.atomic(self.directory / 'live_status.json', json.dumps(row, ensure_ascii=False, indent=2))
        if self.bar is not None:
            self.bar.update(max(0, completed-self.bar.n))
            self.bar.set_postfix(comparisons=f'{len(records)}/{self.total_comparisons}', api=client.calls,
                                 eta_s=round(eta) if eta is not None else '?')
        else:
            print(f'Live: {completed}/{self.total_samples} prompts; {len(records)}/{self.total_comparisons} comparisons', flush=True)
        if self.run is not None:
            try:
                self.state['step'] += 1
                # Reserve monotonic step before upload so restart never reuses a published step.
                self.atomic(self.directory / 'swanlab_state.json', json.dumps(self.state, indent=2))
                self.run.log(values, step=self.state['step'])
            except Exception as exc:
                print(f'WARNING: SwanLab log failed ({type(exc).__name__}); local history saved.', flush=True)

    def close(self):
        if self.bar is not None:
            self.bar.close()
        if self.run is not None:
            try:
                self.swanlab.finish()
            except Exception as exc:
                print(f'WARNING: SwanLab finish failed ({type(exc).__name__}); local history saved.', flush=True)
