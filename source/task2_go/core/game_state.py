from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from .board import EMPTY, Board, BLACK, WHITE
from .move import Move
from .rules import Rules
# Hằng số Ko-mi
KOMI = 6.5 # Điểm bù cho người chơi Trắng
@dataclass(frozen=True)
class GameState:
    board: Board
    to_play: int = BLACK
    move_history: List[Move] = field(default_factory=list)
    hash_history: List[int] = field(default_factory=list)  # <- thêm
    
    captures: Dict[int, int] = field(default_factory=lambda: {BLACK: 0, WHITE: 0}) # {1: Black_Captures, -1: White_Captures}
    
    @staticmethod
    def new_game(size:int=9)->"GameState":
        b = Board(size=size)
        # hash ban đầu
        return GameState(board=b, to_play=BLACK, move_history=[], hash_history=[b.hash_key()])

    def _last_hash(self) -> Optional[int]:
        # simple-ko dùng hash của trạng thái ngay trước đó
        return self.hash_history[-2] if len(self.hash_history) >= 2 else None

    def legal_moves(self)->List[Move]:
        rules = Rules()
        moves = []
        last_hash = self._last_hash()
        for y in range(self.board.size):
            for x in range(self.board.size):
                if rules.is_legal(self.board, self.to_play, x, y, last_hash=last_hash):
                    moves.append(Move.play(x,y))
        moves.append(Move.pass_()); 
        #moves.append(Move.resign())
        return moves

    def is_terminal(self)->bool:
        # kết thúc: 2 PASS liên tiếp hoặc RESIGN
        if len(self.move_history)>=2 and self.move_history[-1].kind=='PASS' and self.move_history[-2].kind=='PASS':
            return True
        if self.move_history and self.move_history[-1].kind=='RESIGN':
            return True
        return False

    def score(self) -> Tuple[float, float, int]:
        """
        Tính điểm cuối cùng theo Territory Scoring (Lãnh thổ + Quân bắt + Komi).
        Trả về: (Black_Final_Score, White_Final_Score, Winner_Color)
        """
        if not self.is_terminal():
            raise ValueError("Không thể tính điểm khi trò chơi chưa kết thúc.")
        
        rules = Rules()
        # 1. Tính Lãnh thổ (Territory) và Quân trên bàn (Area)
        black_territory, white_territory, _ = rules.calculate_territory(self.board)
        
        # 2. Tính điểm thô (Territory + Captures)
        black_score = black_territory + self.captures[BLACK]
        white_score = white_territory + self.captures[WHITE]
        
        # 3. Áp dụng Ko-mi
        white_score_final = white_score + KOMI
        
        # 4. Xác định người chiến thắng
        if black_score > white_score_final:
            winner = BLACK
        elif white_score_final > black_score:
            winner = WHITE
        else:
            winner = EMPTY # Hòa (Jigo)

        return black_score, white_score_final, winner
    
    def apply_move(self, mv:Move)->"GameState":
        rules = Rules()
        
        if mv.kind=='RESIGN':
            # Trường hợp đầu hàng: cập nhật lịch sử, người thắng là đối thủ
            return GameState(board=self.board, to_play=-self.to_play,
                             move_history=self.move_history+[mv],
                             hash_history=self.hash_history + [self.board.hash_key()],
                             captures=self.captures)
            
        elif mv.kind=='PLAY':
            nb = self.board.copy()
            last_hash = self._last_hash()
            
            # play_move trả về danh sách quân bị bắt
            captured_stones = rules.play_move(nb, self.to_play, mv.x, mv.y, last_hash=last_hash)
            
            # Cập nhật số quân đã bắt
            new_captures = self.captures.copy()
            new_captures[self.to_play] += len(captured_stones)
            
            new_hash_history = self.hash_history + [nb.hash_key()]
            return GameState(board=nb, to_play=-self.to_play,
                             move_history=self.move_history+[mv],
                             hash_history=new_hash_history,
                             captures=new_captures)
        else: # PASS
            return GameState(board=self.board, to_play=-self.to_play,
                             move_history=self.move_history+[mv],
                             hash_history=self.hash_history + [self.board.hash_key()],
                             captures=self.captures)