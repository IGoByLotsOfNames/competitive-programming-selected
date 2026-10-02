"""End-to-end CLI benchmark; optional comparison with binaries from a named old ref."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import platform
import random
import statistics
import subprocess
import sys
import tempfile
import time


def execute(path, data):
    memory, method = None, 'unavailable'
    command = [str(path.resolve())]
    with tempfile.TemporaryDirectory() as directory:
        measurement = Path(directory) / 'rss.txt'
        if sys.platform.startswith('linux') and Path('/usr/bin/time').exists():
            command = ['/usr/bin/time', '-f', '%M', '-o', str(measurement), *command]
            method = 'GNU time maximum resident set, bytes'
        started = time.perf_counter()
        child = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output, error = child.communicate(data, timeout=120)
        elapsed = time.perf_counter() - started
        if child.returncode:
            raise RuntimeError(f'{path.name}: {child.returncode}: {error.decode(errors="replace")}')
        if sys.platform == 'win32':
            from ctypes import wintypes
            class Counters(ctypes.Structure):
                _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                    (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                    'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                    'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
            query = ctypes.WinDLL('psapi').GetProcessMemoryInfo
            query.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            query.restype = wintypes.BOOL
            counters = Counters()
            counters.cb = ctypes.sizeof(counters)
            if query(int(child._handle), ctypes.byref(counters), counters.cb):
                memory = counters.PeakWorkingSetSize
                method = 'Windows PeakWorkingSetSize, bytes'
        elif measurement.exists():
            memory = int(measurement.read_text().strip()) * 1024
        return {'seconds': elapsed, 'peak_memory_bytes': memory, 'memory_method': method,
                'output_sha256': hashlib.sha256(output).hexdigest()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bin-dir', type=Path, default=Path('build'))
    parser.add_argument('--baseline-dir', type=Path)
    parser.add_argument('--baseline-ref', default=None)
    parser.add_argument('--repeats', type=int, default=3)
    parser.add_argument('--seed', type=int, default=20261002)
    parser.add_argument('--output', type=Path, default=Path('benchmarks/latest.json'))
    args = parser.parse_args()
    if args.repeats < 1: parser.error('repeats must be positive')
    rng = random.Random(args.seed)
    workloads = []
    for n in (2000, 8000):
        queries = 5000
        data = (f'{n}\n' + ''.join(f'n{i} n{i+1}\n' for i in range(n-1))
                + f'n{n-1} n{n-1}\n' + 'n0\n' * queries).encode()
        workloads.append(('directed_cycle_reachability', {'vertices': n, 'edges': n, 'queries': queries}, data))
    for n in (1500, 3000, 6000):
        a, b = (''.join(rng.choices('abcd', k=n)) for _ in range(2))
        workloads.append(('longest_common_subsequence', {'first_length': n, 'second_length': n}, f'{a} {b}\n'.encode()))
    records = []
    for name, size, data in workloads:
        expected = None
        for version, directory in [('current', args.bin_dir), ('baseline', args.baseline_dir)]:
            if directory is None: continue
            path = directory / (name + ('.exe' if sys.platform == 'win32' else ''))
            rows = [execute(path, data) for _ in range(args.repeats)]
            hashes = {x['output_sha256'] for x in rows}
            if len(hashes) != 1 or (expected is not None and next(iter(hashes)) != expected):
                raise AssertionError(f'Output mismatch for {name} {size}')
            expected = next(iter(hashes))
            record = {'solution': name, 'version': version, 'size': size,
                      'input_sha256': hashlib.sha256(data).hexdigest(), 'samples': rows,
                      'median_seconds': statistics.median(x['seconds'] for x in rows)}
            records.append(record)
            print(name, version, size, record['median_seconds'], flush=True)
    compiler = subprocess.run(['g++', '--version'], capture_output=True, text=True)
    report = {'schema_version': 1, 'platform': platform.platform(), 'python': platform.python_version(),
              'processor': platform.processor(), 'compiler': compiler.stdout.splitlines()[0],
              'compile_flags': '-std=c++20 -O2 -Wall -Wextra -Wpedantic',
              'baseline_ref': args.baseline_ref, 'seed': args.seed, 'repeats': args.repeats,
              'timing_scope': 'wall clock including process startup and stdin/stdout; input generation excluded',
              'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(Path('solutions').glob('*.cpp'))},
              'records': records}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__': main()
