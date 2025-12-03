# sudoku_main.py
from sudoku_model import Grid
from sudoku_agent import SudokuSATAgent
from sudoku_view import SudokuView

# ----------------- VÍ DỤ ĐỀ MẪU -----------------
PUZZLE: Grid = [
    [0, 0, 0,  2, 6, 0,  7, 0, 1],
    [6, 8, 0,  0, 7, 0,  0, 9, 0],
    [1, 9, 0,  0, 0, 4,  5, 0, 0],
    [8, 2, 0,  1, 0, 0,  0, 4, 0],
    [0, 0, 4,  6, 0, 2,  9, 0, 0],
    [0, 5, 0,  0, 0, 3,  0, 2, 8],
    [0, 0, 9,  3, 0, 0,  0, 7, 4],
    [0, 4, 0,  0, 5, 0,  0, 3, 6],
    [7, 0, 3,  0, 1, 8,  0, 0, 0],
]


class SudokuApp:
    """
    Lớp "ứng dụng" kết hợp:
    - Model (Grid / CNFEncoder)
    - Agent (SudokuSATAgent)
    - View  (SudokuView)
    và điều khiển luồng chạy chính.
    """
    def __init__(self, puzzle: Grid):
        self.puzzle = puzzle
        self.agent = SudokuSATAgent()
        self.view = SudokuView()

    def run(self):
        print("=== SUDOKU ĐỀ BAN ĐẦU ===")
        self.view.print_grid(self.puzzle)

        print("\nĐang giải bằng SAT (Glucose3)...")
        sol = self.agent.solve(self.puzzle)

        if sol is None:
            print("Không tìm được nghiệm (hoặc chưa cài python-sat).")
            return

        print("\n=== NGHIỆM SUDOKU (in console) ===")
        self.view.print_grid(sol)

        print("\nMở cửa sổ trực quan hóa...")
        self.view.visualize(self.puzzle, sol)


def main():
    app = SudokuApp(PUZZLE)
    app.run()


if __name__ == "__main__":
    main()
