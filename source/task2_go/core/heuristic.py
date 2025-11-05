from __future__ import annotations
from .board import BLACK, WHITE
from .game_state import GameState

def heuristic_score(state: GameState, player: int)->float:
    grid = state.board.grid
    black = (grid==BLACK).sum()
    white = (grid==WHITE).sum()
    diff = black - white
    return diff if player==BLACK else -diff
