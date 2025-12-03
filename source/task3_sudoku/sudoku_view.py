# sudoku_view.py
import matplotlib.pyplot as plt
from sudoku_model import Grid


class SudokuView:
    """
    Lớp phụ trách hiển thị Sudoku:
    - In bảng ra console.
    - Vẽ bảng bằng matplotlib.
    """

    def print_grid(self, grid: Grid):
        """In bảng Sudoku 9x9 ra console, có vạch ngăn block 3x3."""
        for r in range(9):
            row_str = []
            for c in range(9):
                v = grid[r][c]
                ch = "." if v == 0 else str(v)
                row_str.append(ch)
                if c in (2, 5):
                    row_str.append("|")
            print(" ".join(row_str))
            if r in (2, 5):
                print("-" * 21)

    def visualize(self, original: Grid, solution: Grid):
        """
        Trực quan hóa Sudoku bằng matplotlib:
        - Số đề gốc (original != 0) màu đen, in đậm.
        - Số do agent SAT điền (original == 0) màu xanh.
        """
        fig, ax = plt.subplots(figsize=(5, 5))

        # Thiết lập trục
        ax.set_xlim(0, 9)
        ax.set_ylim(0, 9)
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels([])
        ax.set_yticklabels([])

        # Vẽ lưới: đường mỏng cho ô, đường đậm cho block 3x3
        for i in range(10):
            lw = 2 if i % 3 == 0 else 0.5
            ax.axhline(i, linewidth=lw, color="black")
            ax.axvline(i, linewidth=lw, color="black")

        # Vẽ số trong từng ô
        for r in range(9):
            for c in range(9):
                v = solution[r][c]
                if v == 0:
                    continue

                if original[r][c] != 0:
                    color = "black"
                    weight = "bold"
                else:
                    color = "blue"
                    weight = "normal"

                # (c + 0.5, 8.5 - r) để hàng 0 nằm trên cùng
                ax.text(
                    c + 0.5,
                    8.5 - r,
                    str(v),
                    ha="center",
                    va="center",
                    color=color,
                    fontsize=14,
                    fontweight=weight,
                )

        ax.set_title("Sudoku solution (đen = đề gốc, xanh = agent SAT)")
        plt.tight_layout()
        plt.show()
