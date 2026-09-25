#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string first, second;
    std::cin >> first >> second;
    std::vector<std::vector<int>> length(first.size() + 1, std::vector<int>(second.size() + 1));
    for (std::size_t i = 1; i <= first.size(); ++i) {
        for (std::size_t j = 1; j <= second.size(); ++j) {
            if (first[i - 1] == second[j - 1]) {
                length[i][j] = length[i - 1][j - 1] + 1;
            } else {
                length[i][j] = std::max(length[i - 1][j], length[i][j - 1]);
            }
        }
    }
    std::cout << length.back().back() << '\n';
}

