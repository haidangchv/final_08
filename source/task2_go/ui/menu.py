
import pygame
from dataclasses import dataclass
from config.settings import DEFAULT_AI_DEPTH

@dataclass
class GameConfig:
    mode: str = "pvp"     # "pvp" | "vsai"
    ai_depth: int = DEFAULT_AI_DEPTH
    human_color: int = 1  # 1=Đen, -1=Trắng

class MenuScene:
    def __init__(self, screen):
        self.screen=screen
        self.font=pygame.font.SysFont(None,36)
        self.choice=None; self.ai_depth=DEFAULT_AI_DEPTH; self.human_color=1

    def run_once(self, events):
        self.screen.fill((30,30,30))
        y=100
        items=[
            ("[1] Man vs Man", "pvp"),
            ("[2] Man vs Machine", "vsai"),
            (f"AI Depth: {self.ai_depth}  (+/-)", None),
            (f"Player: {'Black' if self.human_color==1 else 'White'}  (C to switch)", None),
            ("Press Enter to start", None),
        ]
        for text,_ in items:
            surf=self.font.render(text, True, (220,220,220))
            self.screen.blit(surf,(100,y)); y+=50
        for e in events:
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_1: self.choice="pvp"
                if e.key==pygame.K_2: self.choice="vsai"
                if e.key in (pygame.K_PLUS, pygame.K_EQUALS): self.ai_depth+=1
                if e.key==pygame.K_MINUS: self.ai_depth=max(1,self.ai_depth-1)
                if e.key==pygame.K_c: self.human_color*=-1
                if e.key==pygame.K_RETURN and self.choice:
                    return GameConfig(self.choice, self.ai_depth, self.human_color)
        return None
