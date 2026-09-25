#include <iostream>
#include <string>
#include <unordered_map>
#include <vector>

bool reaches_cycle(int node, const std::vector<std::vector<int>>& graph, std::vector<int>& state) {
    if (state[node] == 1) {
        return true;
    }
    if (state[node] == 2) {
        return false;
    }
    state[node] = 1;
    for (const int next : graph[node]) {
        if (reaches_cycle(next, graph, state)) {
            return true;
        }
    }
    state[node] = 2;
    return false;
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int edge_count;
    std::cin >> edge_count;
    std::unordered_map<std::string, int> index;
    std::vector<std::pair<std::string, std::string>> edges;
    auto get_index = [&index](const std::string& name) {
        const auto [iterator, inserted] = index.try_emplace(name, static_cast<int>(index.size()));
        return iterator->second;
    };
    for (int i = 0; i < edge_count; ++i) {
        std::string from, to;
        std::cin >> from >> to;
        get_index(from);
        get_index(to);
        edges.push_back({from, to});
    }
    std::vector<std::vector<int>> graph(index.size());
    for (const auto& [from, to] : edges) {
        graph[index[from]].push_back(index[to]);
    }

    std::string query;
    while (std::cin >> query) {
        const auto found = index.find(query);
        if (found == index.end()) {
            std::cout << query << " trapped\n";
            continue;
        }
        std::vector<int> state(graph.size());
        std::cout << query << (reaches_cycle(found->second, graph, state) ? " safe\n" : " trapped\n");
    }
}

