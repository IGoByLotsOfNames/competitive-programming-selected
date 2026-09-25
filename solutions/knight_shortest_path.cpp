#include <array>
#include <iostream>
#include <queue>
#include <utility>
#include <vector>

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);

    int board_size;
    std::cin >> board_size;
    std::pair<int, int> start, target;
    std::cin >> start.first >> start.second >> target.first >> target.second;
    int forbidden_count;
    std::cin >> forbidden_count;

    std::vector blocked(board_size + 1, std::vector<bool>(board_size + 1));
    for (int i = 0; i < forbidden_count; ++i) {
        int row, column;
        std::cin >> row >> column;
        blocked[row][column] = true;
    }

    if (start == target) {
        std::cout << 0 << '\n';
        return 0;
    }

    constexpr std::array<std::pair<int, int>, 8> moves{{
        {-2, -1}, {-2, 1}, {-1, -2}, {-1, 2},
        {1, -2}, {1, 2}, {2, -1}, {2, 1},
    }};
    std::vector distance(board_size + 1, std::vector<int>(board_size + 1, -1));
    std::queue<std::pair<int, int>> queue;
    distance[start.first][start.second] = 0;
    queue.push(start);

    while (!queue.empty()) {
        const auto [row, column] = queue.front();
        queue.pop();
        for (const auto& [row_delta, column_delta] : moves) {
            const int next_row = row + row_delta;
            const int next_column = column + column_delta;
            if (next_row < 1 || next_row > board_size || next_column < 1 || next_column > board_size) {
                continue;
            }
            if (blocked[next_row][next_column] || distance[next_row][next_column] != -1) {
                continue;
            }
            distance[next_row][next_column] = distance[row][column] + 1;
            if (std::pair{next_row, next_column} == target) {
                std::cout << distance[next_row][next_column] << '\n';
                return 0;
            }
            queue.push({next_row, next_column});
        }
    }
    std::cout << -1 << '\n';
}
