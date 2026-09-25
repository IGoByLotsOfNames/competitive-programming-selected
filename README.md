# Selected Competitive Programming Solutions

This repository contains a small, modernized selection from my C++ competitive-programming practice. The collection supports the algorithmic foundation behind my Bronze Medal at the 2023 National Olympiad in Informatics without turning the profile into an undifferentiated archive of submissions.

The solutions were rewritten from my 2023 practice files for consistent C++20 style, safer containers and clearer naming. Problem statements are not redistributed.

## Selected techniques

| Solution | Technique | Time complexity |
|---|---|---:|
| `knight_shortest_path.cpp` | Breadth-first search on an implicit grid graph | O(n²) |
| `connected_components.cpp` | Repeated BFS on an undirected graph | O(V + E) |
| `longest_common_subsequence.cpp` | Two-dimensional dynamic programming | O(nm) |
| `directed_cycle_reachability.cpp` | DFS with three-state cycle detection | O(V + E) per query |
| `letter_transform_palindrome.cpp` | Floyd–Warshall plus two-pointer optimization | O(26³ + 26n) |
| `dijkstra_round_trip.cpp` | Dijkstra's shortest-path algorithm | O((V + E) log V) per run |

## Build

Compile one solution directly:

```bash
g++ -std=c++20 -O2 -Wall -Wextra -pedantic solutions/knight_shortest_path.cpp -o knight_shortest_path
```

Or compile all solutions with CMake:

```bash
cmake -S . -B build
cmake --build build
```

## Notes

- Each file is intentionally self-contained for contest-style input and output.
- Inputs are assumed to satisfy the original problem constraints.
- The collection emphasizes distinct techniques rather than repository size.
- Original problem sources and links should be added before public release when they can be verified.

## Licence

The implementation code is MIT licensed. Original problem statements remain the property of their respective authors and are not included.

