# core/search/minimax.py
from __future__ import annotations
from typing import Tuple, Optional, Callable, List
import time
from core.game_state import GameState
from core.board import EMPTY
from core.move import Move
from config.settings import TIMEBOX_SEC, USE_ALPHA_BETA

from .heuristic import heuristic_score

EvalFn = Callable[[GameState, int], float]

class MinimaxSearcher:
    """
    Minimax + Alpha-Beta + Move Ordering + Timebox.
    - depth_limit: độ sâu tối đa
    - heuristic: hàm đánh giá trạng thái
    - time_limit_sec: None => không giới hạn; số giây => bật timebox
    - use_iterative_deepening: nếu True sẽ tăng dần độ sâu đến limit/ hết giờ
    """
    def __init__(
        self,
        depth_limit: int = 2,
        heuristic: EvalFn = heuristic_score,
        time_limit_sec: Optional[float] = TIMEBOX_SEC,
        use_iterative_deepening: bool = True,
        use_move_ordering: bool = True,
    ):
        self.depth_limit = depth_limit
        self.heuristic = heuristic
        self.time_limit_sec = time_limit_sec
        self.use_iterative_deepening = use_iterative_deepening
        self.use_move_ordering = use_move_ordering
        self._t0 = 0.0
        self._nodes = 0

    # ------------- Public API -------------
    def search(self, state: GameState, player: int) -> Move:
        self._t0 = time.perf_counter()
        self._nodes = 0

        best_move: Optional[Move] = None
        best_score: float = float("-inf")

        depths = range(1, self.depth_limit + 1) if self.use_iterative_deepening else [self.depth_limit]
        for d in depths:
            score, move = self._alpha_beta_root(state, d, player)
            if move is not None:
                best_score, best_move = score, move
            if self._timed_out():
                break

        return best_move or Move.pass_()

    # ------------- Alpha-Beta -------------
    def _alpha_beta_root(self, state: GameState, depth: int, player: int) -> Tuple[float, Optional[Move]]:
        alpha, beta = float("-inf"), float("inf")
        best_move: Optional[Move] = None
        best_val = float("-inf")

        moves = self._ordered_moves(state, player)

        for mv in moves:
            if self._timed_out(): break
            ns = state.apply_move(mv)
            val = self._alpha_beta(ns, depth - 1, alpha, beta, player)
            if val > best_val:
                best_val, best_move = val, mv
            alpha = max(alpha, best_val)
            if USE_ALPHA_BETA and alpha >= beta:
                break
        return best_val, best_move

    def _alpha_beta(self, state: GameState, depth: int, alpha: float, beta: float, player: int) -> float:
        if self._timed_out():
            # Khi hết giờ, trả về đánh giá tĩnh hiện tại (không mở rộng thêm)
            return self.heuristic(state, player)
        if depth == 0 or state.is_terminal():
            return self.heuristic(state, player)

        self._nodes += 1
        maximizing = (state.to_play == player)
        if maximizing:
            value = float("-inf")
            moves = self._ordered_moves(state, player)
            for mv in moves:
                ns = state.apply_move(mv)
                value = max(value, self._alpha_beta(ns, depth - 1, alpha, beta, player))
                alpha = max(alpha, value)
                if USE_ALPHA_BETA and alpha >= beta:
                    break
            return value
        else:
            value = float("inf")
            moves = self._ordered_moves(state, player)
            for mv in moves:
                ns = state.apply_move(mv)
                value = min(value, self._alpha_beta(ns, depth - 1, alpha, beta, player))
                beta = min(beta, value)
                if USE_ALPHA_BETA and beta <= alpha:
                    break
            return value

    # ------------- Move ordering -------------
    def _ordered_moves(self, state: GameState, player: int) -> List[Move]:
        """Ưu tiên các nước có xác suất tốt: bắt quân, atari, gần cụm quân.
        Để nhanh gọn, chấm điểm nước đi bằng hàm tĩnh nhẹ, KHÔNG dùng minimax ở đây."""
        legal = [m for m in state.legal_moves() if m.kind == "PLAY"]
        if not self.use_move_ordering:
            return legal

        def score_move(mv: Move) -> int:
            # Heuristics thô: capture > atari > proximity
            cap = self._would_capture(state, player, mv.x, mv.y)
            atari = self._would_put_in_atari(state, player, mv.x, mv.y)
            prox = self._proximity_bonus(state, mv.x, mv.y)
            # Trọng số đơn giản
            return cap * 1000 + atari * 50 + prox

        legal.sort(key=score_move, reverse=True)
        # luôn cho phép PASS/RESIGN ở cuối list để không kẹt
        trailer = [m for m in state.legal_moves() if m.kind != "PLAY"]
        return legal + trailer

    # --- Utilities cho ordering (mô phỏng cục bộ, nhẹ hơn gọi Rules từng lần) ---
    def _would_capture(self, state: GameState, player: int, x: int, y: int) -> int:
        """Số quân đối thủ bị bắt nếu đánh (x,y) (xấp xỉ)."""
        b = state.board.copy()
        opp = -player
        # nếu ô không trống thì coi = 0
        if b.get(x, y) != 0:
            return 0
        b.place_stone(player, x, y)
        captured = 0
        # bắt các nhóm đối thủ không còn liberties
        for nx, ny in b.neighbors(x, y):
            if b.get(nx, ny) == opp:
                g = self._collect_group(b, nx, ny)
                if not self._group_liberties(b, g):
                    captured += len(g)
                    for (cx, cy) in g:
                        b.remove_stone(cx, cy)
        return captured

    def _would_put_in_atari(self, state: GameState, player: int, x: int, y: int) -> int:
        """Số nhóm đối thủ bị đưa vào thế atari (liberties = 1) sau nước đi (x,y)."""
        b = state.board.copy()
        opp = -player
        if b.get(x, y) != 0: return 0
        b.place_stone(player, x, y)
        atari_groups = 0
        seen = set()
        for ny in range(b.size):
            for nx in range(b.size):
                if b.get(nx, ny) == opp and (nx, ny) not in seen:
                    g = self._collect_group(b, nx, ny)
                    seen |= g
                    if len(self._group_liberties(b, g)) == 1:
                        atari_groups += 1
        return atari_groups

    def _proximity_bonus(self, state: GameState, x: int, y: int) -> int:
        """Ưu tiên ô gần quân hiện hữu để giảm branching vô nghĩa."""
        b = state.board
        R = 2
        score = 0
        for dy in range(-R, R+1):
            for dx in range(-R, R+1):
                ix, iy = x + dx, y + dy
                if 0 <= ix < b.size and 0 <= iy < b.size:
                    v = b.get(ix, iy)
                    if v != EMPTY:
                        score += 1
        return score

    # --- phiên bản nhẹ của group & liberties (lặp lại để tránh lệ thuộc Rules) ---
    def _collect_group(self, board, x, y):
        color = board.get(x, y)
        if color == 0: return set()
        q = [(x, y)]
        seen = {(x, y)}
        while q:
            cx, cy = q.pop()
            for nx, ny in board.neighbors(cx, cy):
                if (nx, ny) not in seen and board.get(nx, ny) == color:
                    seen.add((nx, ny)); q.append((nx, ny))
        return seen

    def _group_liberties(self, board, group):
        libs = set()
        for x, y in group:
            for nx, ny in board.neighbors(x, y):
                if board.get(nx, ny) == 0:
                    libs.add((nx, ny))
        return libs

    # ------------- timebox -------------
    def _timed_out(self) -> bool:
        if self.time_limit_sec is None:
            return False
        return (time.perf_counter() - self._t0) >= self.time_limit_sec
