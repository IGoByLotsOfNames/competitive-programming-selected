#include <algorithm>
#include <array>
#include <iostream>
#include <limits>
#include <string>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int length, rule_count;
    std::string word;
    std::cin >> length >> rule_count >> word;
    constexpr int infinity = std::numeric_limits<int>::max() / 4;
    std::array<std::array<int, 26>, 26> cost{};
    for (int from = 0; from < 26; ++from) {
        cost[from].fill(infinity);
        cost[from][from] = 0;
    }
    for (int i = 0; i < rule_count; ++i) {
        char from, to;
        int price;
        std::cin >> from >> to >> price;
        cost[from - 'a'][to - 'a'] = std::min(cost[from - 'a'][to - 'a'], price);
    }
    for (int through = 0; through < 26; ++through) {
        for (int from = 0; from < 26; ++from) {
            for (int to = 0; to < 26; ++to) {
                cost[from][to] = std::min(cost[from][to], cost[from][through] + cost[through][to]);
            }
        }
    }

    long long answer = 0;
    for (int left = 0, right = length - 1; left < right; ++left, --right) {
        int best = infinity;
        for (int target = 0; target < 26; ++target) {
            best = std::min(best, cost[word[left] - 'a'][target] + cost[word[right] - 'a'][target]);
        }
        if (best >= infinity) {
            std::cout << -1 << '\n';
            return 0;
        }
        answer += best;
    }
    std::cout << answer << '\n';
}

