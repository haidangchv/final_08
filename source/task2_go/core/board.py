from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np

EMPTY, BLACK, WHITE = 0, 1, -1

@dataclass
class Board:
    size: int = 9
    def __post_init__(self):
        self.grid = np.zeros((self.size, self.size), dtype=int)

    def is_on_board(self, x: int, y: int) -> bool:
        return 0 <= x < self.size and 0 <= y < self.size

    def get(self, x: int, y: int) -> int:
        return self.grid[y, x]

    def place_stone(self, player: int, x: int, y: int) -> None:
        self.grid[y, x] = player

    def remove_stone(self, x: int, y: int) -> None:
        self.grid[y, x] = EMPTY

    def neighbors(self, x: int, y: int) -> List[Tuple[int,int]]:
        cand = [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]
        return [(i,j) for i,j in cand if self.is_on_board(i,j)]

    def copy(self) -> "Board":
        b = Board(self.size)
        b.grid = self.grid.copy()
        return b
