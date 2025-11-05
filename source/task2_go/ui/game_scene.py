import pygame
from typing import Dict
from ..core.game_state import GameState
from ..core.move import Move
from ..core.board import BLACK, WHITE
from ..core.agents.human_agent import HumanAgent
from ..core.agents.minimax_agent import MinimaxAgent
from ..core.search.minimax import MinimaxSearcher

CELL=60; MARGIN=60

class GameScene:
    def __init__(self, screen, config):
        self.screen=screen
        self.state=GameState.new_game(size=9)
        if config.mode=="pvp":
            self.agents={BLACK:HumanAgent(), WHITE:HumanAgent()}
        else:
            human=HumanAgent()
            ai=MinimaxAgent(MinimaxSearcher(config.ai_depth), player_color=-config.human_color)
            self.agents={config.human_color:human, -config.human_color:ai}
        self.last_play=None
        self.font=pygame.font.SysFont(None,28)

    def board_to_screen(self,i,j): return MARGIN+i*CELL, MARGIN+j*CELL
    def screen_to_board(self,x,y): 
        i=round((x-MARGIN)/CELL); j=round((y-MARGIN)/CELL); return i,j

    def handle_click(self,pos):
        i,j=self.screen_to_board(*pos)
        if 0<=i<self.state.board.size and 0<=j<self.state.board.size:
            player=self.state.to_play; agent=self.agents[player]
            if isinstance(agent, HumanAgent):
                mv=Move.play(i,j)
                if any(m.kind=='PLAY' and m.x==i and m.y==j for m in self.state.legal_moves()):
                    agent.set_pending_move(mv)

    def step(self):
        if self.state.is_terminal(): return "done"
        player=self.state.to_play; agent=self.agents[player]
        mv=agent.select_move(self.state)
        if mv is None: return None
        self.state=self.state.apply_move(mv); self.last_play=mv; return None

    def draw(self):
        self.screen.fill((230,200,150)); size=self.state.board.size
        for k in range(size):
            x0,y0=self.board_to_screen(0,k); x1,y1=self.board_to_screen(size-1,k)
            pygame.draw.line(self.screen,(0,0,0),(x0,y0),(x1,y1),2)
            x0,y0=self.board_to_screen(k,0); x1,y1=self.board_to_screen(k,size-1)
            pygame.draw.line(self.screen,(0,0,0),(x0,y0),(x1,y1),2)
        for j in range(size):
            for i in range(size):
                v=self.state.board.get(i,j)
                if v!=0:
                    cx,cy=self.board_to_screen(i,j)
                    pygame.draw.circle(self.screen,(20,20,20) if v==1 else (240,240,240),(cx,cy),CELL//2-4)
        if self.last_play and self.last_play.kind=='PLAY':
            cx,cy=self.board_to_screen(self.last_play.x,self.last_play.y)
            pygame.draw.circle(self.screen,(255,0,0),(cx,cy),6)
        turn='Đen' if self.state.to_play==1 else 'Trắng'
        surf=self.font.render(f'Lượt: {turn} | ESC: Menu | SPACE: Pass', True, (10,10,10))
        self.screen.blit(surf,(20,10))
