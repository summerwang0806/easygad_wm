"""One private localhost vLLM replica per selected GPU, with deterministic prompt routing."""
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import sys
import threading
import time
from urllib import request, error


def parse_gpu_ids(value):
    ids = [int(x.strip()) for x in value.split(',')]
    if not ids or any(x < 0 for x in ids) or len(ids) != len(set(ids)):
        raise ValueError('GPU IDs must be unique nonnegative integers, e.g. 1,3')
    return ids


def gpu_inventory():
    result = subprocess.run(['nvidia-smi', '--query-gpu=index,uuid,memory.total,memory.used,utilization.gpu',
                             '--format=csv,noheader,nounits'], capture_output=True, text=True, check=True)
    rows = []
    for line in result.stdout.splitlines():
        index, gpu_uuid, total, used, utilization = [v.strip() for v in line.split(',')]
        rows.append({'index': int(index), 'uuid': gpu_uuid, 'total': float(total),
                     'used': float(used), 'utilization': int(utilization)})
    return rows


def select_gpus(args, inventory):
    by_id = {r['index']: r for r in inventory}
    if args.gpus:
        ids = parse_gpu_ids(args.gpus)
        if any(i not in by_id for i in ids):
            raise ValueError('Selected GPU index does not exist')
    else:
        excluded = set(parse_gpu_ids(args.exclude_gpus)) if args.exclude_gpus else set()
        idle = [r for r in inventory if r['index'] not in excluded and r['used'] < 1024 and r['utilization'] == 0]
        idle.sort(key=lambda r: (-r['total'], r['index']))
        count = args.num_gpus or 1
        if len(idle) < count:
            raise ValueError(f'Need {count} idle GPUs; found {len(idle)}. Specify --gpus only for cards you can use.')
        ids = [r['index'] for r in idle[:count]]
    for i in ids:
        row = by_id[i]
        needed = row['total'] * args.gpu_memory_utilization
        if row['total']-row['used'] < needed:
            raise ValueError(f'GPU {i}: free {row["total"]-row["used"]:.0f} MiB < requested {needed:.0f} MiB; '
                             'choose another GPU or reduce --gpu-memory-utilization')
    return [by_id[i] for i in ids]


def make_local_client(args, base_class, fatal_error, digest, dataset, ids):
    class LocalClient(base_class):
        def __init__(self):
            super().__init__(args)
            self.key = 'local-inference'
            # Stable cache identity independent of ephemeral ports/GPU count.
            self.base_url = 'http://local-vllm/v1'
            self.start_lock = threading.Lock()
            self.processes, self.logs, self.endpoints = [], [], []
            self.ready = False
            self.assignment = {digest(dataset[i]['prompt']): n for n, i in enumerate(ids)}

        def payload(self, messages, judging):
            value = super().payload(messages, judging)
            value.pop('store', None)
            value['seed'] = args.seed
            return value

        def start(self):
            with self.start_lock:
                if self.ready:
                    return
                if self.stop.is_set():
                    raise fatal_error('Local initialization stopped')
                try:
                    devices = select_gpus(args, gpu_inventory())
                    self.devices = [r['index'] for r in devices]
                    print(f'Local judge GPU replicas={self.devices}; each replica has tensor_parallel_size=1', flush=True)
                    for row in devices:
                        with socket.socket() as sock:
                            sock.bind(('127.0.0.1', 0))
                            port = sock.getsockname()[1]
                        env = os.environ.copy()
                        # UUID avoids CUDA index-order differences; each child sees exactly one GPU.
                        env['CUDA_VISIBLE_DEVICES'] = row['uuid']
                        env['HF_HUB_OFFLINE'] = '1'
                        env['VLLM_NO_USAGE_STATS'] = '1'
                        env['NO_PROXY'] = env['no_proxy'] = '127.0.0.1,localhost'
                        env['VLLM_WORKER_MULTIPROC_METHOD'] = 'spawn'
                        # Do not propagate external service credentials into the local model server.
                        for name in ('OPENAI_API_KEY', 'SWANLAB_API_KEY'):
                            env.pop(name, None)
                        directory = args.output_dir / 'local_workers'
                        directory.mkdir(exist_ok=True)
                        log = (directory / f'gpu_{row["index"]}.log').open('a', encoding='utf-8')
                        self.logs.append(log)
                        command = [sys.executable, '-m', 'vllm.entrypoints.openai.api_server',
                            '--model', args.judge_model, '--served-model-name', args.judge_model,
                            '--host', '127.0.0.1', '--port', str(port), '--tensor-parallel-size', '1',
                            '--dtype', 'bfloat16', '--gpu-memory-utilization', str(args.gpu_memory_utilization),
                            '--max-model-len', str(args.max_model_len), '--max-num-seqs', str(args.max_num_seqs),
                            '--generation-config', 'vllm', '--disable-log-requests']
                        process = subprocess.Popen(command, env=env, stdout=log, stderr=subprocess.STDOUT,
                                                   start_new_session=True)
                        self.processes.append(process)
                        self.endpoints.append(f'http://127.0.0.1:{port}/v1')
                    opener = request.build_opener(request.ProxyHandler({}))
                    deadline = time.monotonic() + args.local_startup_timeout
                    waiting = set(range(len(devices)))
                    while waiting:
                        if self.stop.is_set() or time.monotonic() > deadline:
                            raise fatal_error('Local model startup stopped/timed out; inspect local_workers/*.log')
                        for n in list(waiting):
                            if self.processes[n].poll() is not None:
                                raise fatal_error(f'GPU {self.devices[n]} judge server exited; inspect local_workers/gpu_{self.devices[n]}.log')
                            try:
                                with opener.open(self.endpoints[n].removesuffix('/v1')+'/health', timeout=1):
                                    waiting.remove(n)
                            except (error.URLError, TimeoutError):
                                pass
                        self.stop.wait(.5)
                    self.ready = True
                    print('All local judge replicas ready; GPU tasks are assigned by input row index.', flush=True)
                except Exception as exc:
                    self.close()
                    if isinstance(exc, fatal_error):
                        raise
                    raise fatal_error(f'Local judge could not initialize: {exc}') from exc

        def request_url(self, payload):
            self.start()
            conversation = json.loads(payload['messages'][-1]['content'])['conversation']
            index = self.assignment[digest(conversation)] % len(self.endpoints)
            return self.endpoints[index] + '/chat/completions'

        def close(self):
            # These process groups were created by this client, never other users' servers.
            for process in self.processes:
                if process.poll() is None:
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait(timeout=5)
                    except ProcessLookupError:
                        pass
            for log in self.logs:
                log.close()
    return LocalClient()
