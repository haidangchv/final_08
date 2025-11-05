
from __future__ import annotations
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    def select_move(self, state):
        ...
