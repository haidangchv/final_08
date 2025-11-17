# sudoku_model.py
from typing import List

# Kiểu dữ liệu Sudoku 9x9
Grid = List[List[int]]

def var_id(r: int, c: int, v: int) -> int:
    """
    Ánh xạ (r, c, v) -> id nguyên 1..729
    r, c, v đều chạy 1..9.
    """
    return 81 * (r - 1) + 9 * (c - 1) + v


class CNFEncoder:
    """
    Đối tượng mã hóa Sudoku (CSP) thành danh sách clause CNF.

    Các nhóm ràng buộc:
    - encode_cells  : mỗi ô đúng 1 giá trị
    - encode_rows   : mỗi hàng, mỗi số xuất hiện đúng 1 lần
    - encode_cols   : mỗi cột, mỗi số xuất hiện đúng 1 lần
    - encode_blocks : mỗi block 3x3, mỗi số xuất hiện đúng 1 lần
    - encode_clues  : giữ nguyên các ô cho trước
    """
    def __init__(self, grid: Grid):
        self.grid = grid                      # đề Sudoku đầu vào
        self.clauses: List[List[int]] = []    # danh sách clause CNF

    def add(self, clause):
        """Thêm 1 clause (danh sách literal nguyên) vào CNF."""
        self.clauses.append(list(clause))

    def exactly_one(self, vars_list: List[int]):
        """
        Ràng buộc exactly-one trên 1 tập biến:
        - Ít nhất 1 biến TRUE  : (x1 ∨ x2 ∨ ... ∨ xn)
        - Không quá 1 biến TRUE: (¬xi ∨ ¬xj) cho mọi cặp i<j
        """
        # at least one
        self.add(vars_list)
        # at most one (pairwise)
        for i in range(len(vars_list)):
            for j in range(i + 1, len(vars_list)):
                self.add([-vars_list[i], -vars_list[j]])

    def encode_cells(self):
        """Mỗi ô (r,c) phải nhận đúng 1 giá trị 1..9."""
        for r in range(1, 10):
            for c in range(1, 10):
                self.exactly_one([var_id(r, c, v) for v in range(1, 10)])

    def encode_rows(self):
        """Trên mỗi hàng r, mỗi giá trị v xuất hiện đúng 1 lần."""
        for r in range(1, 10):
            for v in range(1, 10):
                self.exactly_one([var_id(r, c, v) for c in range(1, 10)])

    def encode_cols(self):
        """Trên mỗi cột c, mỗi giá trị v xuất hiện đúng 1 lần."""
        for c in range(1, 10):
            for v in range(1, 10):
                self.exactly_one([var_id(r, c, v) for r in range(1, 10)])

    def encode_blocks(self):
        """Trong mỗi block 3x3, mỗi giá trị v xuất hiện đúng 1 lần."""
        for br in range(0, 3):         # block row index: 0,1,2
            for bc in range(0, 3):     # block col index: 0,1,2
                rows = range(1 + 3 * br, 4 + 3 * br)
                cols = range(1 + 3 * bc, 4 + 3 * bc)
                for v in range(1, 10):
                    self.exactly_one([var_id(r, c, v) for r in rows for c in cols])

    def encode_clues(self):
        """Giữ nguyên các ô đã cho trước trong đề."""
        for r in range(1, 10):
            for c in range(1, 10):
                v = self.grid[r - 1][c - 1]
                if 1 <= v <= 9:
                    self.add([var_id(r, c, v)])

    def build_cnf(self) -> List[List[int]]:
        """Sinh toàn bộ CNF clauses cho Sudoku hiện tại."""
        self.encode_cells()
        self.encode_rows()
        self.encode_cols()
        self.encode_blocks()
        self.encode_clues()
        return self.clauses
