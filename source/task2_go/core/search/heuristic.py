# core/search/heuristic.py
from __future__ import annotations
from typing import Set, Tuple
import numpy as np
from core.board import Board, BLACK, WHITE, EMPTY
from core.game_state import GameState

Coord = Tuple[int, int]

def _collect_group(board: Board, x: int, y: int) -> Set[Coord]:
    """BFS gom nhóm cùng màu với (x,y)."""
    color = board.get(x, y)
    if color == EMPTY: return set()
    q = [(x, y)]
    seen: Set[Coord] = {(x, y)}
    while q:
        cx, cy = q.pop()
        for nx, ny in board.neighbors(cx, cy):
            if (nx, ny) not in seen and board.get(nx, ny) == color:
                seen.add((nx, ny)); q.append((nx, ny))
    return seen

def _group_liberties(board: Board, group: Set[Coord]) -> Set[Coord]:
    libs: Set[Coord] = set()
    for x, y in group:
        for nx, ny in board.neighbors(x, y):
            if board.get(nx, ny) == EMPTY:
                libs.add((nx, ny))
    return libs

def _sum_liberties(board: Board, color: int) -> int:
    """Tổng liberties theo nhóm (không đếm trùng trong cùng nhóm)."""
    seen: Set[Coord] = set()
    total = 0
    for y in range(board.size):
        for x in range(board.size):
            if board.get(x, y) == color and (x, y) not in seen:
                g = _collect_group(board, x, y)
                seen |= g
                total += len(_group_liberties(board, g))
    return total

def _capture_potential(board: Board, color: int) -> int:
    """Số quân đối thủ đang ở thế nguy (nhóm liberties = 1)."""
    opp = -color
    seen: Set[Coord] = set()
    cnt = 0
    for y in range(board.size):
        for x in range(board.size):
            if board.get(x, y) == opp and (x, y) not in seen:
                g = _collect_group(board, x, y)
                seen |= g
                if len(_group_liberties(board, g)) == 1:
                    cnt += len(g)
    return cnt

def stone_diff(state: GameState, player: int) -> float:
    g = state.board.grid
    black = int((g == BLACK).sum())
    white = int((g == WHITE).sum())
    diff = black - white
    return float(diff if player == BLACK else -diff)

def liberty_diff(state: GameState, player: int) -> float:
    b_lib = _sum_liberties(state.board, BLACK)
    w_lib = _sum_liberties(state.board, WHITE)
    diff = b_lib - w_lib
    return float(diff if player == BLACK else -diff)

def capture_threat_balance(state: GameState, player: int) -> float:
    """Dương nếu mình đang đe doạ bắt nhiều hơn đối thủ."""
    mine = _capture_potential(state.board, player)
    opp  = _capture_potential(state.board, -player)
    return float(mine - opp)

def heuristic_score(state: GameState, player: int) -> float:
    """
    Heuristic tổ hợp (có thể chỉnh hệ số):
      - stone_diff: chênh quân
      - liberty_diff: chênh tự do
      - capture_threat_balance: thế bắt/đe doạ
    """
    a, b, c = 1.0, 0.4, 0.8
    return (
        a * stone_diff(state, player)
        + b * liberty_diff(state, player)
        + c * capture_threat_balance(state, player)
    )
