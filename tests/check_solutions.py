"""Executable contracts, seeded independent oracles, and recursion/memory stress cases."""
from __future__ import annotations

import argparse
import heapq
import itertools
from pathlib import Path
import random
import subprocess
import sys
import unittest

PARSER = argparse.ArgumentParser()
PARSER.add_argument('--bin-dir', type=Path, default=Path('build'))
PARSER.add_argument('--cases', type=int, default=80)
PARSER.add_argument('--seed', type=int, default=20261002)
ARGS, REST = PARSER.parse_known_args()


def run(name: str, data: str, timeout: int = 10) -> str:
    path = ARGS.bin_dir / (name + ('.exe' if sys.platform == 'win32' else ''))
    result = subprocess.run([str(path.resolve())], input=data, text=True,
                            capture_output=True, timeout=timeout, check=True)
    if result.stderr:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def graph_input(n, edges):
    return f'{n} {len(edges)}\n' + ''.join(f'{a} {b}\n' for a, b in edges)


class Solutions(unittest.TestCase):
    def test_regressions(self):
        fixtures = [
            ('connected_components', '0 0\n', '0'),
            ('connected_components', '4 3\n0 0\n0 1\n0 1\n', '3'),
            ('knight_shortest_path', '1\n1 1 1 1\n0\n', '0'),
            ('knight_shortest_path', '1\n1 1 1 1\n1\n1 1\n', '-1'),
            ('knight_shortest_path', '3\n1 1 2 3\n1\n1 1\n', '-1'),
            ('knight_shortest_path', '2\n1 1 2 2\n0\n', '-1'),
            ('longest_common_subsequence', 'ABCBDAB BDCABA\n', '4'),
            ('longest_common_subsequence', 'aaa bbb\n', '0'),
            ('directed_cycle_reachability', '0\nunknown\n', 'unknown trapped'),
            ('directed_cycle_reachability', '5\na b\na b\nb c\nc c\na dead\na\nb\nc\ndead\nnone\n',
             'a safe\nb safe\nc safe\ndead trapped\nnone trapped'),
            ('dijkstra_round_trip', '3 4 0 2\n0 1 10\n0 1 2\n1 2 0\n2 0 3\n', '5'),
            ('dijkstra_round_trip', '2 1 0 1\n0 1 1\n', '-1'),
            ('dijkstra_round_trip', '1 0 0 0\n', '0'),
            ('letter_transform_palindrome', '2 0 ab\n', '-1'),
            ('letter_transform_palindrome', '1 0 z\n', '0'),
            ('letter_transform_palindrome', '2 2 ab\na c 2000000000\nb c 2000000000\n', '4000000000'),
        ]
        for name, data, expected in fixtures:
            with self.subTest(name=name, data=data):
                self.assertEqual(run(name, data), expected)

    def test_components_against_union_find(self):
        rng = random.Random(ARGS.seed)
        for case in range(ARGS.cases):
            n = rng.randrange(1, 13)
            edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(40))]
            parent = list(range(n))
            def find(a):
                while parent[a] != a:
                    a = parent[a]
                return a
            for a, b in edges:
                parent[find(a)] = find(b)
            with self.subTest(case=case, seed=ARGS.seed):
                self.assertEqual(int(run('connected_components', graph_input(n, edges))), len({find(i) for i in range(n)}))

    def test_lcs_against_exhaustive_subsequences(self):
        rng = random.Random(ARGS.seed + 1)
        for case in range(ARGS.cases):
            a = ''.join(rng.choices('abc', k=rng.randrange(1, 10)))
            b = ''.join(rng.choices('abc', k=rng.randrange(1, 10)))
            expected = 0
            for mask in range(1 << len(a)):
                candidate = ''.join(a[i] for i in range(len(a)) if mask & (1 << i))
                cursor = iter(b)
                if all(any(c == x for x in cursor) for c in candidate):
                    expected = max(expected, len(candidate))
            with self.subTest(case=case, a=a, b=b):
                self.assertEqual(int(run('longest_common_subsequence', f'{a} {b}\n')), expected)
                self.assertEqual(int(run('longest_common_subsequence', f'{b} {a}\n')), expected)

    def test_cycle_against_transitive_closure(self):
        rng = random.Random(ARGS.seed + 2)
        for case in range(ARGS.cases):
            n = rng.randrange(1, 10)
            edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randrange(35))]
            reachable = [[False] * n for _ in range(n)]
            for a, b in edges:
                reachable[a][b] = True
            for k, i, j in itertools.product(range(n), repeat=3):
                reachable[i][j] |= reachable[i][k] and reachable[k][j]
            expected = [f'n{i} ' + ('safe' if any(reachable[i][j] and reachable[j][j] for j in range(n)) else 'trapped') for i in range(n)]
            data = str(len(edges)) + '\n' + ''.join(f'n{a} n{b}\n' for a, b in edges) + ''.join(f'n{i}\n' for i in range(n))
            with self.subTest(case=case):
                self.assertEqual(run('directed_cycle_reachability', data), '\n'.join(expected))

    def test_round_trip_against_floyd_warshall(self):
        rng = random.Random(ARGS.seed + 3)
        for case in range(ARGS.cases):
            n = rng.randrange(1, 9)
            edges = [(rng.randrange(n), rng.randrange(n), rng.randrange(20)) for _ in range(rng.randrange(35))]
            inf = float('inf')
            distance = [[0 if i == j else inf for j in range(n)] for i in range(n)]
            for a, b, w in edges:
                distance[a][b] = min(distance[a][b], w)
            for k, i, j in itertools.product(range(n), repeat=3):
                distance[i][j] = min(distance[i][j], distance[i][k] + distance[k][j])
            home, target = rng.randrange(n), rng.randrange(n)
            total = distance[home][target] + distance[target][home]
            data = f'{n} {len(edges)} {home} {target}\n' + ''.join(f'{a} {b} {w}\n' for a, b, w in edges)
            with self.subTest(case=case):
                self.assertEqual(int(run('dijkstra_round_trip', data)), -1 if total == inf else total)

    def test_knight_against_explicit_graph_relaxation(self):
        rng = random.Random(ARGS.seed + 4)
        for case in range(ARGS.cases):
            n = rng.randrange(1, 7)
            cells = list(itertools.product(range(1, n + 1), repeat=2))
            start, target = rng.choice(cells), rng.choice(cells)
            blocked = set(rng.sample(cells, rng.randrange(len(cells) + 1)))
            active = [x for x in cells if x not in blocked]
            edges = [(a, b) for a in active for b in active if sorted((abs(a[0]-b[0]), abs(a[1]-b[1]))) == [1, 2]]
            dist = {x: float('inf') for x in cells}
            if start not in blocked:
                dist[start] = 0
            for _ in cells:
                for a, b in edges:
                    dist[b] = min(dist[b], dist[a] + 1)
            expected = -1 if dist[target] == float('inf') else dist[target]
            data = f'{n}\n{start[0]} {start[1]} {target[0]} {target[1]}\n{len(blocked)}\n' + ''.join(f'{a} {b}\n' for a, b in sorted(blocked))
            with self.subTest(case=case):
                self.assertEqual(int(run('knight_shortest_path', data)), expected)

    def test_letters_against_repeated_dijkstra(self):
        rng = random.Random(ARGS.seed + 5)
        for case in range(ARGS.cases):
            alphabet = 'abcde'
            word = ''.join(rng.choices(alphabet, k=rng.randrange(1, 13)))
            edges = [(rng.randrange(5), rng.randrange(5), rng.randrange(12)) for _ in range(rng.randrange(25))]
            costs = []
            for start in range(5):
                d = [float('inf')] * 5
                d[start] = 0
                queue = [(0, start)]
                while queue:
                    value, node = heapq.heappop(queue)
                    if value != d[node]: continue
                    for a, b, w in edges:
                        if a == node and value + w < d[b]:
                            d[b] = value + w
                            heapq.heappush(queue, (d[b], b))
                costs.append(d)
            answer = sum(min(costs[alphabet.index(word[i])][c] + costs[alphabet.index(word[-i-1])][c] for c in range(5)) for i in range(len(word)//2))
            data = f'{len(word)} {len(edges)} {word}\n' + ''.join(f'{alphabet[a]} {alphabet[b]} {w}\n' for a, b, w in edges)
            with self.subTest(case=case):
                self.assertEqual(int(run('letter_transform_palindrome', data)), -1 if answer == float('inf') else answer)

    def test_long_graphs_and_unbalanced_lcs(self):
        n = 100_000
        edges = ''.join(f'v{i} v{i+1}\n' for i in range(n-1))
        for tail, suffix, answer in [('', '', 'trapped'), ('v99999 v99999\n', '1', 'safe')]:
            count = n - 1 + bool(suffix)
            self.assertEqual(run('directed_cycle_reachability', f'{count}\n{edges}{tail}v0\nv99999\n', timeout=30), f'v0 {answer}\nv99999 {answer}')
        a, b = 'a' * 100_000, 'a' * 64
        self.assertEqual(run('longest_common_subsequence', f'{a} {b}\n', timeout=30), '64')
        self.assertEqual(run('longest_common_subsequence', f'{b} {a}\n', timeout=30), '64')


if __name__ == '__main__':
    print(f'Differential seed={ARGS.seed}; cases per algorithm={ARGS.cases}', flush=True)
    unittest.main(argv=[sys.argv[0], *REST], verbosity=2)
