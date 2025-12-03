# core/agents.py

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

# Cần import từ các module cùng cấp (core)
from core.move import Move 
from core.minimax import MinimaxSearcher # Giữ nguyên đường dẫn này nếu bạn chưa gộp minimax.py

# === 1. BaseAgent ===
class BaseAgent(ABC):
    """
    Lớp cơ sở trừu tượng cho mọi Agent (người hoặc máy).
    """
    def __init__(self, player_color: int):
        self.player_color = player_color

    @abstractmethod
    def select_move(self, state):
        """Trả về Move được chọn hoặc None."""
        ...

# === 2. HumanAgent ===
class HumanAgent(BaseAgent):
    """
    Agent cho người chơi (xử lý input từ UI).
    """
    def __init__(self, player_color: int):
        super().__init__(player_color)
        self._pending_move: Optional[Move] = None

    def set_pending_move(self, move: Move):
        """Đặt nước đi chờ xử lý từ sự kiện click/phím tắt của UI."""
        self._pending_move = move

    def select_move(self, state):
        """Trả về nước đi đã được đặt, sau đó reset."""
        mv = self._pending_move
        self._pending_move = None
        return mv

# === 3. MinimaxAgent ===
class MinimaxAgent(BaseAgent):
    """
    Agent cho Máy tính, sử dụng thuật toán Minimax.
    """
    def __init__(self, searcher: MinimaxSearcher, player_color: int):
        super().__init__(player_color)
        self.searcher = searcher
    
    def select_move(self, state):
        """Thực hiện tìm kiếm Minimax và trả về nước đi tốt nhất."""
        return self.searcher.search(state, self.player_color)