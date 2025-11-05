
from __future__ import annotations
from typing import Optional
from .base_agent import BaseAgent
from core.move import Move

class HumanAgent(BaseAgent):
    def __init__(self):
        self._pending_move: Optional[Move] = None
    def set_pending_move(self, move: Move):
        self._pending_move = move
    def select_move(self, state):
        mv = self._pending_move
        self._pending_move = None
        return mv
