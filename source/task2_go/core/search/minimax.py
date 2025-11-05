from __future__ import annotations
from typing import Tuple, Optional
from ..game_state import GameState
from ..move import Move
from ..heuristic import heuristic_score

class MinimaxSearcher:
    def __init__(self, depth_limit:int=2):
        self.depth_limit = depth_limit

    def search(self, state:GameState, player:int)->Move:
        score, best = self._alpha_beta(state, self.depth_limit, float('-inf'), float('inf'), player)
        return best or Move.pass_()

    def _alpha_beta(self, state:GameState, depth:int, alpha:float, beta:float, player:int)->Tuple[float, Optional[Move]]:
        if depth==0 or state.is_terminal():
            return heuristic_score(state, player), None
        best_move=None
        if state.to_play==player:
            value=float('-inf')
            for mv in state.legal_moves():
                ns = state.apply_move(mv)
                sc,_ = self._alpha_beta(ns, depth-1, alpha, beta, player)
                if sc>value: value,best_move=sc,mv
                alpha=max(alpha,value)
                if alpha>=beta: break
            return value,best_move
        else:
            value=float('inf')
            for mv in state.legal_moves():
                ns = state.apply_move(mv)
                sc,_ = self._alpha_beta(ns, depth-1, alpha, beta, player)
                if sc<value: value,best_move=sc,mv
                beta=min(beta,value)
                if beta<=alpha: break
            return value,best_move
