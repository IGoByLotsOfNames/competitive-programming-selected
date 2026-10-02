# Reproducing the measurements

`tools/benchmark.py` generates seeded inputs, checks output hashes and records each raw sample rather than only a selected best time.

```bash
python tools/benchmark.py --bin-dir build --repeats 3 --seed 20261002 --output benchmarks/my-run.json
```

To compare the earlier maintained implementations, build `solutions/directed_cycle_reachability.cpp` and `solutions/longest_common_subsequence.cpp` from commit `c45d1b3edc6ba8fe48281d49f9210d706af74a10` into another directory with the same compiler and flags. Then pass `--baseline-dir PATH --baseline-ref c45d1b3edc6ba8fe48281d49f9210d706af74a10`. Avoid using the legacy private archive as the benchmark baseline.

The recorded run uses GCC `-std=c++20 -O2 -Wall -Wextra -Wpedantic`. Source hashes, platform, compiler version, seed, workload dimensions, input hashes, output hashes and all three samples are in the JSON. CMake users should select Release before benchmarking; sanitizer timings are not comparable.

The graph cases are worst-case repeated reachability walks into a cycle, not a representative distribution of all graphs. The LCS cases use seeded `abcd` strings. No manual warm-up is removed. The host was not isolated from other work; startup, scheduling and pipe IO contribute to wall time. Input generation is excluded. Windows memory uses PeakWorkingSetSize; Linux uses GNU time maximum RSS when available. These are whole-process measurements, and cross-platform numbers should not be compared directly. Unsupported systems report memory as unavailable rather than zero.

Sanitizers run in CI, not in the recorded Windows benchmark. An O(nm) DP still has quadratic time despite its small memory footprint. The large-chain correctness test is separate from the smaller baseline-comparison workload because the old recursive implementation has a platform-dependent stack limit.
