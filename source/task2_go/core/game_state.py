
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from .board import Board, BLACK, WHITE
from .move import Move
from .rules import Rules

@dataclass(frozen=True)
class GameState:
    board: Board
    to_play: int = BLACK
    move_history: List[Move] = field(default_factory=list)

    @staticmethod
    def new_game(size:int=9)->"GameState":
        return GameState(board=Board(size=size), to_play=BLACK, move_history=[])

    def legal_moves(self)->List[Move]:
        rules = Rules()
        moves = []
        for y in range(self.board.size):
            for x in range(self.board.size):
                if rules.is_legal(self.board, self.to_play, x, y):
                    moves.append(Move.play(x,y))
        moves.append(Move.pass_()); moves.append(Move.resign())
        return moves

    def is_terminal(self)->bool:
        if len(self.move_history)>=2 and self.move_history[-1].kind=='PASS' and self.move_history[-2].kind=='PASS':
            return True
        if any(m.kind=='RESIGN' for m in self.move_history[-1:]):
            return True
        return False

    def apply_move(self, mv:Move)->"GameState":
        if mv.kind=='PLAY':
            nb = self.board.copy()
            Rules().play_move(nb, self.to_play, mv.x, mv.y)
            return GameState(board=nb, to_play=-self.to_play, move_history=self.move_history+[mv])
        else:
            return GameState(board=self.board, to_play=-self.to_play, move_history=self.move_history+[mv])
