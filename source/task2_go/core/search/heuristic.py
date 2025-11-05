
from __future__ import annotations
from core.board import BLACK, WHITE
from core.game_state import GameState

def stone_diff(state: GameState, player: int) -> float:
    g = state.board.grid
    black = (g == BLACK).sum()
    white = (g == WHITE).sum()
    diff = black - white
    return diff if player == BLACK else -diff

def heuristic_score(state: GameState, player: int) -> float:
    # TODO: bổ sung thêm các thành phần khác (liberties, territory, capture potential,...)
    return stone_diff(state, player)
