
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal

MoveKind = Literal["PLAY","PASS","RESIGN"]

@dataclass(frozen=True)
class Move:
    kind: MoveKind
    x: Optional[int]=None
    y: Optional[int]=None

    @staticmethod
    def play(x:int,y:int)->"Move": return Move("PLAY",x,y)
    @staticmethod
    def pass_()->"Move": return Move("PASS")
    @staticmethod
    def resign()->"Move": return Move("RESIGN")
