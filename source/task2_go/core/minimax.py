# core/minimax.py 
from __future__ import annotations
from typing import Tuple, Optional, Callable, List, Set
import time
from core.game_state import GameState
from core.board import EMPTY, BLACK, WHITE, Board 
from core.move import Move
from config.settings import TIMEBOX_SEC, USE_ALPHA_BETA

# EvalFn bây giờ trỏ đến phương thức tĩnh
EvalFn = Callable[[GameState, int], float]

class MinimaxSearcher:
    """
    Minimax + Alpha-Beta + Move Ordering + Timebox.
    Tất cả logic Heuristic đã được đóng gói bên trong class dưới dạng @staticmethod.
    """
    def __init__(
        self,
        depth_limit: int = 2,
        heuristic: EvalFn = None, 
        time_limit_sec: Optional[float] = TIMEBOX_SEC,
        use_iterative_deepening: bool = True,
        use_move_ordering: bool = True,
    ):
        self.depth_limit = depth_limit
        self.heuristic = heuristic if heuristic is not None else MinimaxSearcher.heuristic_score 
        self.time_limit_sec = time_limit_sec
        self.use_iterative_deepening = use_iterative_deepening
        self.use_move_ordering = use_move_ordering
        self._t0 = 0.0
        self._nodes = 0

    # ====================================================================
    # A. LOGIC HEURISTIC
    # ====================================================================

    @staticmethod
    def _collect_group_h(board: Board, x: int, y: int) -> Set[Tuple[int, int]]:
        color = board.get(x, y)
        if color == EMPTY: return set()
        q = [(x, y)]
        seen: Set[Tuple[int, int]] = {(x, y)}
        while q:
            cx, cy = q.pop()
            for nx, ny in board.neighbors(cx, cy):
                if (nx, ny) not in seen and board.get(nx, ny) == color:
                    seen.add((nx, ny)); q.append((nx, ny))
        return seen

    @staticmethod
    def _group_liberties_h(board: Board, group: Set[Tuple[int, int]]) -> Set[Tuple[int, int]]:
        libs: Set[Tuple[int, int]] = set()
        for x, y in group:
            for nx, ny in board.neighbors(x, y):
                if board.get(nx, ny) == EMPTY:
                    libs.add((nx, ny))
        return libs

    @staticmethod
    def _sum_liberties(board: Board, color: int) -> int:
        seen: Set[Tuple[int, int]] = set()
        total = 0
        for y in range(board.size):
            for x in range(board.size):
                if board.get(x, y) == color and (x, y) not in seen:
                    g = MinimaxSearcher._collect_group_h(board, x, y)
                    seen |= g
                    total += len(MinimaxSearcher._group_liberties_h(board, g))
        return total

    @staticmethod
    def _capture_potential(board: Board, color: int) -> int:
        opp = -color
        seen: Set[Tuple[int, int]] = set()
        cnt = 0
        for y in range(board.size):
            for x in range(board.size):
                if board.get(x, y) == opp and (x, y) not in seen:
                    g = MinimaxSearcher._collect_group_h(board, x, y)
                    seen |= g
                    if len(MinimaxSearcher._group_liberties_h(board, g)) == 1:
                        cnt += len(g)
        return cnt

    @staticmethod
    def stone_diff(state: GameState, player: int) -> float:
        g = state.board.grid
        black = int((g == BLACK).sum())
        white = int((g == WHITE).sum())
        diff = black - white
        return float(diff if player == BLACK else -diff)

    @staticmethod
    def liberty_diff(state: GameState, player: int) -> float:
        b_lib = MinimaxSearcher._sum_liberties(state.board, BLACK)
        w_lib = MinimaxSearcher._sum_liberties(state.board, WHITE)
        diff = b_lib - w_lib
        return float(diff if player == BLACK else -diff)

    @staticmethod
    def capture_threat_balance(state: GameState, player: int) -> float:
        mine = MinimaxSearcher._capture_potential(state.board, player)
        opp  = MinimaxSearcher._capture_potential(state.board, -player)
        return float(mine - opp)

    @staticmethod
    def heuristic_score(state: GameState, player: int) -> float:
        """Hàm đánh giá Heuristic chính (được gọi bởi Minimax)."""
        a, b, c = 1.0, 0.4, 0.8 
        return (
            a * MinimaxSearcher.stone_diff(state, player)
            + b * MinimaxSearcher.liberty_diff(state, player)
            + c * MinimaxSearcher.capture_threat_balance(state, player)
        )

    # ====================================================================
    # B. LOGIC MINIMAX
    # ====================================================================
    
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
    # ... (Hàm _alpha_beta_root giữ nguyên) ...
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

    # ... (Hàm _alpha_beta giữ nguyên) ...
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
    # ... (Hàm _ordered_moves giữ nguyên) ...
    def _ordered_moves(self, state: GameState, player: int) -> List[Move]:
        legal = [m for m in state.legal_moves() if m.kind == "PLAY"]
        if not self.use_move_ordering:
            return legal

        def score_move(mv: Move) -> int:
            cap = self._would_capture(state, player, mv.x, mv.y)
            atari = self._would_put_in_atari(state, player, mv.x, mv.y)
            prox = self._proximity_bonus(state, mv.x, mv.y)
            # Trọng số đơn giản
            return cap * 1000 + atari * 50 + prox

        legal.sort(key=score_move, reverse=True)
        trailer = [m for m in state.legal_moves() if m.kind != "PLAY"]
        return legal + trailer

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