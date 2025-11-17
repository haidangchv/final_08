# sudoku_agent.py
from typing import Optional
from sudoku_model import Grid, CNFEncoder

# --------- SAT solver (PySAT / Glucose3) ----------
try:
    from pysat.solvers import Glucose3
    HAS_PYSAT = True
except Exception:
    HAS_PYSAT = False


def solve_by_sat(grid: Grid) -> Optional[Grid]:
    """
    Agent giải Sudoku bằng SAT:
    - Nhận đầu vào: grid 9x9 (0 = ô trống, 1..9 = số đã cho).
    - Build CNF bằng CNFEncoder.
    - Gọi Glucose3 (PySAT) để tìm model thỏa tất cả câu mệnh đề.
    - Trả về nghiệm Sudoku (ma trận 9x9) hoặc None nếu không giải được.
    """
    if not HAS_PYSAT:
        print("Lỗi: Cần cài thư viện 'python-sat' (pip install python-sat).")
        return None

    # Dùng đối tượng OOP CNFEncoder để sinh CNF
    enc = CNFEncoder(grid)
    cnf = enc.build_cnf()

    solver = Glucose3()
    for cl in cnf:
        solver.add_clause(cl)

    if not solver.solve():
        return None

    model = set(solver.get_model())
    out: Grid = [[0] * 9 for _ in range(9)]

    # Giải mã model -> ma trận 9x9
    from sudoku_model import var_id  # import local để tránh vòng lặp import ở đầu file

    for r in range(1, 10):
        for c in range(1, 10):
            for v in range(1, 10):
                if var_id(r, c, v) in model:
                    out[r - 1][c - 1] = v
                    break

    return out
