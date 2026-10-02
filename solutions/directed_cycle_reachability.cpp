#include <iostream>
#include <queue>
#include <string>
#include <unordered_map>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int edge_count;
    if (!(std::cin >> edge_count)) return 0;
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
    std::vector<std::vector<int>> predecessors(index.size());
    std::vector<int> remaining_out_degree(index.size());
    for (const auto& [from, to] : edges) {
        predecessors[index[to]].push_back(index[from]);
        ++remaining_out_degree[index[from]];
    }

    // Remove sinks, then vertices whose outgoing edges all lead to removed vertices.
    // Every removed vertex can only reach a finite DAG. Every surviving vertex
    // has a surviving successor; following successors in a finite graph reaches
    // a cycle. This also keeps paths leading INTO cycles, not just cycle members.
    // Parallel edges are counted and removed individually; self-loops survive.
    std::queue<int> sinks;
    for (std::size_t node = 0; node < index.size(); ++node) {
        if (remaining_out_degree[node] == 0) sinks.push(static_cast<int>(node));
    }
    while (!sinks.empty()) {
        const int sink = sinks.front();
        sinks.pop();
        for (const int parent : predecessors[sink]) {
            if (--remaining_out_degree[parent] == 0) sinks.push(parent);
        }
    }

    std::string query;
    while (std::cin >> query) {
        const auto found = index.find(query);
        if (found == index.end()) {
            std::cout << query << " trapped\n";
            continue;
        }
        std::cout << query << (remaining_out_degree[found->second] > 0 ? " safe\n" : " trapped\n");
    }
}

