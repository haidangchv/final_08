# sudoku_agent.py
from typing import Optional
from sudoku_model import Grid, CNFEncoder, var_id

# --------- SAT solver (PySAT / Glucose3) ----------
try:
    from pysat.solvers import Glucose3
    HAS_PYSAT = True
except Exception:
    HAS_PYSAT = False


class SudokuSATAgent:
    """
    Agent giải Sudoku bằng SAT.
    Trách nhiệm:
    - Nhận một grid 9x9.
    - Mã hóa bằng CNFEncoder.
    - Gọi SAT solver (Glucose3) để tìm nghiệm.
    """
    def __init__(self):
        if not HAS_PYSAT:
            # Có thể raise hoặc chỉ in cảnh báo tuỳ bạn
            print("Cảnh báo: Chưa cài 'python-sat' (pip install python-sat).")

    def solve(self, grid: Grid) -> Optional[Grid]:
        """
        Giải Sudoku:
        - Input: grid (0 = ô trống, 1..9 = số đã cho)
        - Output: grid nghiệm 9x9 hoặc None nếu không giải được.
        """
        if not HAS_PYSAT:
            print("Lỗi: Cần cài thư viện 'python-sat'.")
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
        for r in range(1, 10):
            for c in range(1, 10):
                for v in range(1, 10):
                    if var_id(r, c, v) in model:
                        out[r - 1][c - 1] = v
                        break

        return out
