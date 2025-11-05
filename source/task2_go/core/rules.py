
from __future__ import annotations
from typing import Optional
from .board import Board, EMPTY

class Rules:
    def is_legal(self, board: Board, player: int, x: int, y: int, last_hash: Optional[int]=None) -> bool:
        if not board.is_on_board(x,y): return False
        if board.get(x,y) != EMPTY: return False
        # TODO: tự sát, ko
        return True

    def play_move(self, board: Board, player: int, x: int, y: int):
        board.place_stone(player, x, y)
        captured = []
        # TODO: phát hiện/bắt nhóm
        return captured
