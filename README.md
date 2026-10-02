# Selected Competitive Programming Solutions

Six self-contained C++20 programs from my competitive-programming practice, with documented contracts, independent correctness checks and measured algorithm improvements. My competition background includes a Bronze Medal at the 2023 National Olympiad in Informatics.

The maintained implementations were rewritten from my 2023 practice files. The tests and engineering notes describe this repository's current behaviour; they do not redistribute original contest statements or claim judge acceptance that has not been verified.

## Algorithms

| Program | Technique | Time | Auxiliary space |
|---|---|---|---|
| [Knight shortest path](solutions/knight_shortest_path.cpp) | BFS on a blocked grid | O(n²) | O(n²) |
| [Connected components](solutions/connected_components.cpp) | Repeated BFS | O(V+E) | O(V+E) |
| [Longest common subsequence](solutions/longest_common_subsequence.cpp) | Rolling-row dynamic programming | O(nm) | O(min(n,m)) DP storage |
| [Directed cycle reachability](solutions/directed_cycle_reachability.cpp) | Iterative reverse sink elimination | O(V+E+Q), expected name lookup | O(V+E) |
| [Letter transformation palindrome](solutions/letter_transform_palindrome.cpp) | Floyd–Warshall and mirrored-pair optimisation | O(26³+26n) | O(26²) |
| [Directed round trip](solutions/dijkstra_round_trip.cpp) | Two Dijkstra runs with a lazy heap | O((V+E) log(V+E)) | O(V+E) |

Input storage is additional where relevant. [Contracts and reasoning](docs/contracts.md) specify indexing, valid inputs, invariants, numeric bounds and each test oracle.

## Build and verify

Requires a C++20 compiler and Python 3.11+ for the test harness. CMake 3.20+ is optional.

```bash
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel
ctest --test-dir build --output-on-failure
```

For a single program:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic solutions/directed_cycle_reachability.cpp -o directed_cycle_reachability
printf '3\na b\nb c\nc b\na\nunknown\n' | ./directed_cycle_reachability
# a safe
# unknown trapped
```

The test runner can also use a directory of directly compiled binaries:

```bash
python tests/check_solutions.py --bin-dir build --cases 80 --seed 20261002
```

There are eight suites: fixed regressions, six algorithm-specific differential suites, and stress tests. The default generators cover 480 small cases; LCS also checks swapped arguments. Oracles use different methods: union-find, exhaustive subsequences, transitive closure, all-pairs shortest paths, explicit graph relaxation and repeated Dijkstra. Stress checks include 100,000-node chains and a 100,000-by-64 LCS case. CI runs ordinary and address/undefined-behaviour sanitizer builds on Linux.

## Two changes worth explaining

**Cycle reachability:** the earlier implementation started recursive DFS for every query. The current implementation removes sinks and their incoming edges once. Removed vertices cannot reach cycles; every surviving vertex has a surviving successor, so repeatedly following successors must reach a cycle. The survivors include vertices leading into cycles, not just cycle members. This removes repeated graph work and recursion-depth dependence.

**LCS:** each DP cell depends only on the previous row and its left neighbour. Keeping two rows and placing the shorter input in columns preserves the recurrence while reducing DP memory from O(nm) to O(min(n,m)). The program returns length only; reconstructing a subsequence would need another design.

Tests also caught boundary cases: blocked knight endpoints and transformation costs beyond the old 32-bit sentinel.

## Measured comparison

Recorded on Windows with GCC 12.2.0, `-O2`, three repetitions, against maintained baseline commit `c45d1b3`. Both versions produced identical outputs for every benchmark input.

| Workload | Baseline median | Current median | Baseline/current median peak process memory |
|---|---:|---:|---:|
| 8,000-vertex chain ending in a self-loop; 5,000 queries | 0.855 s | 0.045 s | 6.34 / 5.78 MiB |
| Two 6,000-character strings | 0.371 s | 0.216 s | 141.92 / 4.36 MiB |

These are local observations, not universal speed claims. Wall time includes process startup and input/output; memory is Windows peak working set, including runtime overhead. See [raw samples and environment](benchmarks/windows-gcc-2026-10-02.json) and [reproduction instructions](benchmarks/README.md). Complexity and correctness matter more than small timing differences.

## Licence

Implementation code is MIT licensed. Original statements remain their authors' property and are not included.
