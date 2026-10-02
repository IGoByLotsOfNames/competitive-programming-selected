# Input contracts and reasoning

These describe the maintained programs' own interfaces. They are not redistributed contest statements, and are not claims that every input accepted by an unknown original judge is represented. All inputs are whitespace-separated. Every program handles an empty stream by exiting without output. Otherwise inputs must obey the contracts below; these are contest programs, not hostile-input parsers.

## Knight shortest path

Input: positive board size `n`, start row/column, target row/column, nonnegative blocked-cell count, then those coordinate pairs. Coordinates are **one-based**, in `1..n`. Duplicate blocked cells are allowed. The board must fit memory. Output the minimum number of knight moves, or `-1` if unreachable. A blocked endpoint is unreachable, even when start equals target; an unblocked start equal to target takes zero moves.

BFS invariant: the first discovered distance is shortest because each move costs one. Marking on insertion prevents duplicate queue entries. Time and auxiliary space are O(n²). Differential oracle: explicit legal-cell graph with repeated edge relaxation, not the queue implementation.

## Connected components

Input: `V E`, then `E` undirected endpoint pairs in `0..V-1`. `V=0, E=0` is allowed. Parallel edges and self-loops are allowed. Output the number of connected components, including isolated vertices.

Each new BFS starts exactly one component; all vertices visited by it are mutually reachable. Time/space O(V+E). Oracle: disjoint-set union, including duplicate-edge cases.

## Longest common subsequence length

Input: two **nonempty, whitespace-free byte strings**. Output their LCS length; this is not longest common substring and does not reconstruct a subsequence. Lengths must fit signed `int`; time must fit the user's available budget. Empty strings cannot be represented by this token interface. Unicode code points are not decoded.

For prefixes of lengths `i,j`, matching last bytes extend `previous[j-1]`; otherwise use `max(previous[j], current[j-1])`. `current[0]` stays zero. Swapping rows retains every dependency while discarding values never needed again. Put the shorter string in columns: O(nm) time, **O(min(n,m)) auxiliary DP space**, plus O(n+m) input storage. Reconstruction would require a different tradeoff. Oracle: exhaustive subsequence enumeration for small inputs; tests also swap arguments and exercise a 100,000-by-64 case.

## Directed cycle reachability

Input: `E`, then `E` directed pairs of nonempty names; remaining tokens are queried names until EOF. Output `name safe` iff some path from it reaches a directed cycle; otherwise `name trapped`. Unknown names are trapped. Duplicate edges, self-loops, zero edges and repeated queries are valid. The number of vertices/edges must fit signed `int` and memory. Name lookup uses `unordered_map`, so the O(V+E+Q) bound assumes expected constant-time hashing and bounded token lengths; string processing is additional.

Store incoming edges and remaining outgoing degree. Repeatedly remove sinks. A removed vertex has only paths that eventually terminate; induction over removal order proves it cannot reach a cycle. Every survivor has a surviving successor. Following successors in a finite graph repeats a vertex, proving reachability of a cycle. Thus survivors include both cycle vertices **and their predecessors**, even when another outgoing branch reaches a dead end. Removing indegree-zero vertices instead would answer a different question.

This iterative reverse sink elimination uses O(V+E) preprocessing and storage and expected O(1) per named query. SCC decomposition also works, but would require condensation/reachability propagation; only this boolean answer is needed. Oracle: transitive closure, looking for reachable positive-length paths from a vertex to itself. Tests include 100,000-node acyclic and cycle-ending chains, avoiding a recursion-depth dependency.

## Directed weighted round trip

Input: `V E home target`, then `E` directed triples `from to weight`. Vertices are zero-based, `V>=1`; weights are integers in `0..2,147,483,647`. Parallel edges/self-loops are valid. Finite simple-path costs and the requested sum must stay below the sentinel `LLONG_MAX/4`. Output the sum of shortest outward/homeward distances, or `-1` if either is unreachable. With home equal to target the result is zero. Negative weights are unsupported.

Dijkstra uses nonnegative weights; outdated heap entries must be popped before being skipped. Distances use `long long`. Two runs cost O((V+E) log(V+E)) time and O(V+E) space with the lazy duplicate-entry heap; for simple graphs this is conventionally O((V+E) log V). The heap can contain O(E) candidates. Oracle: all-pairs Floyd–Warshall on small graphs.

## Letter transformation palindrome

Input: `length rule_count word`, then directed `from_letter to_letter cost` rules. `length` equals the nonempty word's byte length; all letters are lowercase `a..z`. Costs are integers in `0..2,147,483,647`; duplicate rules take the cheaper cost. Output the minimum total cost to transform the word into any palindrome, or `-1`. Multiple transformations are allowed; the middle character need not change. Length and total cost must fit their types (`int` and `long long`).

Floyd–Warshall finds all directed letter costs. Each mirrored pair independently chooses a shared destination letter. Nonnegative cycles cannot improve a shortest path; with 26 vertices the stated cost bound stays safely below the 64-bit sentinel. Time O(26³+26n), auxiliary space O(26²), plus input storage. Oracle: repeated heap-based shortest paths on generated five-letter graphs, followed by pair optimisation. A regression checks a four-billion-cost answer that previously exceeded the 32-bit sentinel.

## Reproduce failures and limits

`python tests/check_solutions.py --bin-dir build --cases 80 --seed 20261002`

The seed and case index identify a generated input; the same seed/case count repeats it on the tested Python version. Fixed regressions complement the generators. Tests do not prove correctness for every legal graph/string. The invariants above explain why the algorithms generalise. CI adds AddressSanitizer/UndefinedBehaviorSanitizer on Linux; local Windows verification uses the actual GCC build and generated cases.
