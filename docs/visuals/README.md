# Documentation figures

These figures explain the existing implementations and the existing recorded benchmark. They do not introduce new benchmark results or change the programs.

| Figure | Source |
|---|---|
| `cycle-reachability.svg` / `.png` | A five-vertex worked example of the algorithm in `solutions/directed_cycle_reachability.cpp` |
| `rolling-row-lcs.svg` / `.png` | A computed DP table for `ABCBDAB` and `BDCABA`, using the recurrence in `solutions/longest_common_subsequence.cpp` |
| `benchmark-comparison.svg` / `.png` | Every sample in `benchmarks/windows-gcc-2026-10-02.json` |

The README uses SVG for crisp labels. PNG copies are available for viewers that cannot display SVG. Both formats include the same information, with an explicit light background for readability in light and dark interfaces.

## Regenerate

Use Python 3.11+ with Matplotlib installed (rendered with Python 3.12.14 and Matplotlib 3.10.8), then run from the repository root:

```bash
python -m pip install matplotlib==3.10.8
python docs/visuals/generate.py
```

The generator computes medians directly from the raw samples, shows all runs, uses a linear zero-based vertical scale and plots seconds separately from MiB. It checks the benchmark's recorded source hashes against the current C++ files, checks memory units, checks repeat counts, and verifies that paired configurations used the same input and produced matching output hashes. A failed check stops chart generation rather than quietly presenting incomparable values.

Regeneration only requires a documentation plotting dependency; the C++ builds and test harness do not depend on Matplotlib. Benchmark collection remains the responsibility of [`tools/benchmark.py`](../../tools/benchmark.py).
