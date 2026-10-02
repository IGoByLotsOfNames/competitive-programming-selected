#include <algorithm>
#include <iostream>
#include <string>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    std::string first, second;
    if (!(std::cin >> first >> second)) return 0;
    if (second.size() > first.size()) std::swap(first, second);
    // Previous/current rows retain precisely the dependencies of the LCS recurrence.
    // Put the shorter string in the columns: O(min(n,m)) auxiliary memory.
    std::vector<int> previous(second.size() + 1), current(second.size() + 1);
    for (std::size_t i = 1; i <= first.size(); ++i) {
        for (std::size_t j = 1; j <= second.size(); ++j) {
            if (first[i - 1] == second[j - 1]) {
                current[j] = previous[j - 1] + 1;
            } else {
                current[j] = std::max(previous[j], current[j - 1]);
            }
        }
        previous.swap(current);
    }
    std::cout << previous.back() << '\n';
}

