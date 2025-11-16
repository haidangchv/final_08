
import pygame
from typing import Dict
from core.game_state import GameState
from core.move import Move
from core.board import BLACK, WHITE
from core.agents.human_agent import HumanAgent
from core.agents.minimax_agent import MinimaxAgent
from core.search.minimax import MinimaxSearcher
from config.settings import BOARD_SIZE

CELL = 60

class GameScene:
    def __init__(self, screen, config):
        self.screen=screen
        self.W, self.H = screen.get_size()
        self.state=GameState.new_game(size=BOARD_SIZE)

        #Căn bàn cờ giữa
        self.cell_size = 60
        self.board_pixel_size = self.cell_size * (BOARD_SIZE - 1)
        self.margin_x = (self.W - self.board_pixel_size) // 2
        self.margin_y = (self.H - self.board_pixel_size) // 2

        if config.mode=="pvp":
            self.agents={BLACK:HumanAgent(), WHITE:HumanAgent()}
        else:
            human=HumanAgent()
            ai=MinimaxAgent(MinimaxSearcher(config.ai_depth), player_color=-config.human_color)
            self.agents={config.human_color:human, -config.human_color:ai}
        self.last_play=None
        self.font=pygame.font.SysFont("arial",28)
        self.font_small = pygame.font.SysFont ("arial",15)

    def draw_stone(self, center, is_black, scale=1.0):
        x, y = center
        r = int((self.cell_size // 2 - 5) * scale)  # Quân to, đầy ô

        # === 1. BÓNG ĐỔ (dưới, lệch nhẹ) ===
        shadow = pygame.Surface((r*2 + 25, r*2 + 25), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (r//2 + 4, r//2 + 8, r + 5, r//2 + 2))
        self.screen.blit(shadow, (x - r - 12, y - r + 5))

        # === 2. MẶT QUÂN – GRADIENT MỊN ===
        for i in range(r, 0, -1):
            intensity = 255 - (r - i) * 2.5
            if is_black:
                color = (max(10, intensity//5), max(10, intensity//5), max(10, intensity//5))
            else:
                color = (min(255, intensity + 50), min(255, intensity + 50), min(255, intensity + 50))
            pygame.draw.circle(self.screen, color, (x, y), i)

        

    def board_to_screen(self,i,j): 
        return self.margin_x + i * self.cell_size, self.margin_y + j * self.cell_size
    
    def screen_to_board(self,x,y): 
        i=round((x - self.margin_x) / self.cell_size); 
        j=round((y - self.margin_y) / self.cell_size); 
        return i,j

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
        self.state=self.state.apply_move(mv); self.last_play=mv
        return None

    def draw(self):
        self.screen.fill((230, 200, 150))  # Nền gỗ
        size = self.state.board.size
        cell = self.cell_size
        mx, my = self.margin_x, self.margin_y
        board_w = (size - 1) * cell 

       # === VIỀN CÂN ĐỐI (vuông hoàn hảo) ===
        padding = 30
        outer = pygame.Rect(mx - padding, my - padding, board_w + 2 * padding, board_w + 2*padding)
        pygame.draw.rect(self.screen, (110, 70, 30), outer, border_radius=28)
        
        inner_padding = 30
        inner = pygame.Rect(mx - inner_padding, my - inner_padding, board_w + 2 * inner_padding, board_w + 2 * inner_padding)
        pygame.draw.rect(self.screen, (220, 180, 120), inner, border_radius=18)

        board_rect = pygame.Rect(mx, my, board_w, board_w)
        pygame.draw.rect(self.screen, (215, 175, 110), board_rect)

        # === 2. LƯỚI MẢNH ===
        for k in range(size):
            x0, y0 = mx + 0 * cell, my + k * cell
            x1, y1 = mx + (size-1) * cell, my + k * cell
            pygame.draw.line(self.screen, (20,20,20), (x0, y0), (x1, y1), 1)

            x0, y0 = mx + k * cell, my + 0 * cell
            x1, y1 = mx + k * cell, my + (size-1) * cell
            pygame.draw.line(self.screen, (20,20,20), (x0, y0), (x1, y1), 1)

        #điểm khí 
        stars = [2, 4, 6]
        for i in stars:
            for j in stars:
                cx = mx + i * cell
                cy = my + j * cell
                pygame.draw.circle(self.screen, (60, 60, 60), (cx, cy), 4)

        # === 4. VẼ QUÂN CỜ ===
        for y in range(size):
            for x in range(size):
                v = self.state.board.get(x, y)
                if v != 0:
                    center = (mx + x * cell, my + y * cell)
                    self.draw_stone(center, v == 1)


        # Nước đi cuối
        if self.last_play and self.last_play.kind == 'PLAY':
            x = self.last_play.x
            y = self.last_play.y
            left = mx + x * cell - cell // 2
            top = my + y * cell - cell // 2
            size = cell

            # Vẽ 4 góc khung đỏ (giống hình bạn gửi)
            corner_size = cell // 4
            thickness = 3
            red = (220, 20, 20)

            # Góc trên-trái
            pygame.draw.rect(self.screen, red, (left, top, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left, top, thickness, corner_size))

            # Góc trên-phải
            pygame.draw.rect(self.screen, red, (left + size - corner_size, top, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left + size - thickness, top, thickness, corner_size))

            # Góc dưới-trái
            pygame.draw.rect(self.screen, red, (left, top + size - thickness, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left, top + size - corner_size, thickness, corner_size))

            # Góc dưới-phải
            pygame.draw.rect(self.screen, red, (left + size - corner_size, top + size - thickness, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left + size - thickness, top + size - corner_size, thickness, corner_size))

        # === 6. UI ===
        board_w = (self.state.board.size - 1) * cell
        top_y = my - 120  # Cách bàn cờ 90px

        # === QUÂN ĐEN (bên trái) ===
        black_center = (mx + board_w * 0.25, top_y)
        self.draw_stone(black_center, is_black=True, scale=1.3)
        

        # === QUÂN TRẮNG (bên phải) ===
        white_center = (mx + board_w * 0.75, top_y)
        self.draw_stone(white_center, is_black=False, scale=1.3)
        

        # === HIỂN THỊ CHỮ "LƯỢT" DƯỚI BÊN ĐANG ĐI ===
        current_player = self.state.to_play
        if current_player == 1:  # Đen
            turn_text = self.font.render("Đen", True, (220, 20, 20))
            text_y = top_y - 30
            self.screen.blit(turn_text, turn_text.get_rect(center=(black_center[0], top_y + 50)))
        else:  # Trắng
            turn_text = self.font.render("Trắng", True, (220, 20, 20))
            text_y = top_y - 30
            self.screen.blit(turn_text, turn_text.get_rect(center=(white_center[0], top_y + 50)))

        # === HƯỚNG DẪN GÓC DƯỚI TRÁI ===
        line1 = self.font_small.render("Bấm [ESC] để quay lại menu", True, (100, 100, 100))
        line2 = self.font_small.render("Bấm [SPACE] để pass lượt", True, (100, 100, 100))

        # Vị trí: cách lề trái 20px, cách đáy 50px
        self.screen.blit(line1, (20, self.screen.get_height() - 100))
        self.screen.blit(line2, (20, self.screen.get_height() - 70))

