#include <functional>
#include <iostream>
#include <limits>
#include <queue>
#include <utility>
#include <vector>

using Edge = std::pair<int, int>;

long long shortest_path(const std::vector<std::vector<Edge>>& graph, int start, int target) {
    constexpr long long infinity = std::numeric_limits<long long>::max() / 4;
    std::vector<long long> distance(graph.size(), infinity);
    std::priority_queue<
        std::pair<long long, int>,
        std::vector<std::pair<long long, int>>,
        std::greater<>
    > queue;
    distance[start] = 0;
    queue.push({0, start});
    while (!queue.empty()) {
        const auto [current_distance, current] = queue.top();
        queue.pop();
        if (current_distance != distance[current]) {
            continue;
        }
        for (const auto& [next, weight] : graph[current]) {
            const long long candidate = current_distance + weight;
            if (candidate < distance[next]) {
                distance[next] = candidate;
                queue.push({candidate, next});
            }
        }
    }
    return distance[target];
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int vertex_count, edge_count, home, target;
    std::cin >> vertex_count >> edge_count >> home >> target;
    std::vector<std::vector<Edge>> graph(vertex_count);
    for (int i = 0; i < edge_count; ++i) {
        int from, to, weight;
        std::cin >> from >> to >> weight;
        graph[from].push_back({to, weight});
    }
    constexpr long long infinity = std::numeric_limits<long long>::max() / 4;
    const long long outward = shortest_path(graph, home, target);
    const long long homeward = shortest_path(graph, target, home);
    std::cout << (outward >= infinity || homeward >= infinity ? -1 : outward + homeward) << '\n';
}
