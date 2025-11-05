from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
from .board import Board, BLACK, WHITE
from .move import Move
from .rules import Rules

@dataclass(frozen=True)
class GameState:
    board: Board
    to_play: int = BLACK
    move_history: List[Move] = field(default_factory=list)
    hash_history: List[int] = field(default_factory=list)  # <- thêm

    @staticmethod
    def new_game(size:int=9)->"GameState":
        b = Board(size=size)
        # hash ban đầu
        return GameState(board=b, to_play=BLACK, move_history=[], hash_history=[b.hash_key()])

    def _last_hash(self) -> Optional[int]:
        # simple-ko dùng hash của trạng thái ngay trước đó
        return self.hash_history[-2] if len(self.hash_history) >= 2 else None

    def legal_moves(self)->List[Move]:
        rules = Rules()
        moves = []
        last_hash = self._last_hash()
        for y in range(self.board.size):
            for x in range(self.board.size):
                if rules.is_legal(self.board, self.to_play, x, y, last_hash=last_hash):
                    moves.append(Move.play(x,y))
        moves.append(Move.pass_()); moves.append(Move.resign())
        return moves

    def is_terminal(self)->bool:
        # kết thúc đơn giản: 2 PASS liên tiếp hoặc RESIGN
        if len(self.move_history)>=2 and self.move_history[-1].kind=='PASS' and self.move_history[-2].kind=='PASS':
            return True
        if any(m.kind=='RESIGN' for m in self.move_history[-1:]):
            return True
        return False

    def apply_move(self, mv:Move)->"GameState":
        rules = Rules()
        if mv.kind=='PLAY':
            nb = self.board.copy()
            # dùng last_hash để chặn ko
            last_hash = self._last_hash()
            rules.play_move(nb, self.to_play, mv.x, mv.y, last_hash=last_hash)
            new_hash_history = self.hash_history + [nb.hash_key()]
            return GameState(board=nb, to_play=-self.to_play,
                             move_history=self.move_history+[mv],
                             hash_history=new_hash_history)
        else:
            # PASS/RESIGN không đổi bàn cờ → hash giữ nguyên
            return GameState(board=self.board, to_play=-self.to_play,
                             move_history=self.move_history+[mv],
                             hash_history=self.hash_history + [self.board.hash_key()])
