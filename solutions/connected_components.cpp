#include <iostream>
#include <queue>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int vertex_count, edge_count;
    std::cin >> vertex_count >> edge_count;
    std::vector<std::vector<int>> adjacency(vertex_count);
    for (int i = 0; i < edge_count; ++i) {
        int first, second;
        std::cin >> first >> second;
        adjacency[first].push_back(second);
        adjacency[second].push_back(first);
    }

    std::vector<bool> visited(vertex_count);
    int components = 0;
    for (int start = 0; start < vertex_count; ++start) {
        if (visited[start]) {
            continue;
        }
        ++components;
        std::queue<int> queue;
        queue.push(start);
        visited[start] = true;
        while (!queue.empty()) {
            const int current = queue.front();
            queue.pop();
            for (const int neighbour : adjacency[current]) {
                if (!visited[neighbour]) {
                    visited[neighbour] = true;
                    queue.push(neighbour);
                }
            }
        }
    }
    std::cout << components << '\n';
}

