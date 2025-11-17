# sudoku_main.py
from sudoku_model import Grid
from sudoku_agent import solve_by_sat
from sudoku_view import print_grid, visualize_sudoku

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


def main():
    print("=== SUDOKU ĐỀ BAN ĐẦU ===")
    print_grid(PUZZLE)

    print("\nĐang giải bằng SAT (Glucose3)...")
    sol = solve_by_sat(PUZZLE)

    if sol is None:
        print("Không tìm được nghiệm (hoặc chưa cài python-sat).")
    else:
        print("\n=== NGHIỆM SUDOKU (in console) ===")
        print_grid(sol)

        print("\nMở cửa sổ trực quan hóa...")
        visualize_sudoku(PUZZLE, sol)


if __name__ == "__main__":
    main()
