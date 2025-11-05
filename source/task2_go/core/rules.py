from __future__ import annotations
from typing import Optional, Tuple, Set, List
from .board import Board, EMPTY, BLACK, WHITE

class Rules:
    # --- Helpers: nhóm & liberties ---
    def _collect_group(self, board: Board, x: int, y: int) -> Set[Tuple[int,int]]:
        """BFS gom nhóm quân cùng màu với (x,y)."""
        color = board.get(x, y)
        if color == EMPTY:
            return set()
        q = [(x, y)]
        seen: Set[Tuple[int,int]] = set()
        seen.add((x, y))
        while q:
            cx, cy = q.pop()
            for nx, ny in board.neighbors(cx, cy):
                if (nx, ny) not in seen and board.get(nx, ny) == color:
                    seen.add((nx, ny))
                    q.append((nx, ny))
        return seen

    def _liberties_of_group(self, board: Board, group: Set[Tuple[int,int]]) -> Set[Tuple[int,int]]:
        libs: Set[Tuple[int,int]] = set()
        for (x, y) in group:
            for nx, ny in board.neighbors(x, y):
                if board.get(nx, ny) == EMPTY:
                    libs.add((nx, ny))
        return libs

    def _remove_group(self, board: Board, group: Set[Tuple[int,int]]) -> None:
        for (x, y) in group:
            board.remove_stone(x, y)

    # --- Kiểm tra hợp lệ (mô phỏng) ---
    def is_legal(self, board: Board, player: int, x: int, y: int, last_hash: Optional[int]=None) -> bool:
        if not board.is_on_board(x, y):
            return False
        if board.get(x, y) != EMPTY:
            return False

        # Mô phỏng trên bản sao
        tmp = board.copy()
        tmp.place_stone(player, x, y)

        # Bắt các nhóm đối thủ không còn liberties
        opp = -player
        captured_any = False
        for nx, ny in tmp.neighbors(x, y):
            if tmp.is_on_board(nx, ny) and tmp.get(nx, ny) == opp:
                grp = self._collect_group(tmp, nx, ny)
                if not self._liberties_of_group(tmp, grp):  # hết liberties
                    self._remove_group(tmp, grp)
                    captured_any = True

        # Nếu không bắt quân, kiểm tra tự sát (nhóm của mình phải còn liberties)
        my_group = self._collect_group(tmp, x, y)
        if not self._liberties_of_group(tmp, my_group) and not captured_any:
            return False

        # Simple-ko: nếu cung cấp last_hash thì trạng thái sau khi đi không được giống hệt last
        if last_hash is not None:
            if tmp.hash_key() == last_hash:
                return False

        return True

    # --- Chơi nước đi thật sự ---
    def play_move(self, board: Board, player: int, x: int, y: int, last_hash: Optional[int]=None) -> List[Tuple[int,int]]:
        if not self.is_legal(board, player, x, y, last_hash=last_hash):
            raise ValueError("Nước đi không hợp lệ (tự sát/ko/đã chiếm/ngoài bàn).")

        board.place_stone(player, x, y)
        opp = -player
        captured: List[Tuple[int,int]] = []

        # Bắt các nhóm đối thủ không còn liberties
        for nx, ny in board.neighbors(x, y):
            if board.is_on_board(nx, ny) and board.get(nx, ny) == opp:
                grp = self._collect_group(board, nx, ny)
                if not self._liberties_of_group(board, grp):
                    for c in grp:
                        captured.append(c)
                    self._remove_group(board, grp)

        # (Tự sát đã tránh ở is_legal; không cần check lại nếu tin vào is_legal)
        return captured
