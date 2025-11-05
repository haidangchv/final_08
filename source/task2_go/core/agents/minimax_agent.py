
from __future__ import annotations
from .base_agent import BaseAgent
from core.search.minimax import MinimaxSearcher

class MinimaxAgent(BaseAgent):
    def __init__(self, searcher: MinimaxSearcher, player_color:int):
        self.searcher=searcher; self.player_color=player_color
    def select_move(self, state):
        return self.searcher.search(state, self.player_color)
