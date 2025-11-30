import pygame
from typing import Dict
from core.game_state import GameState
from core.move import Move
from core.board import BLACK, WHITE
from core.agents.human_agent import HumanAgent
from core.agents.minimax_agent import MinimaxAgent
from core.search.minimax import MinimaxSearcher
from config.settings import BOARD_SIZE

# Nếu trong settings có ON_TIMEOUT_ACTION thì import, còn không thì dùng fallback:
try:
    from config.settings import ON_TIMEOUT_ACTION
except Exception:
    ON_TIMEOUT_ACTION = "RESIGN"  # "RESIGN" hoặc "PASS"

CELL = 60

def _fmt_time(seconds: float) -> str:
    s = max(0, int(seconds))
    m, s = divmod(s, 60)
    return f"{m:02d}:{s:02d}"

class GameScene:
    def __init__(self, screen, config):
        self.screen=screen
        self.W, self.H = screen.get_size()
        self.state=GameState.new_game(size=BOARD_SIZE)

        # Căn bàn cờ giữa
        self.cell_size = 60
        self.board_pixel_size = self.cell_size * (BOARD_SIZE - 1)
        self.margin_x = (self.W - self.board_pixel_size) // 2
        self.margin_y = (self.H - self.board_pixel_size) // 2

        # Agents
        if config.mode=="pvp":
            self.agents={BLACK:HumanAgent(), WHITE:HumanAgent()}
        else:
            human=HumanAgent()
            ai=MinimaxAgent(MinimaxSearcher(config.ai_depth), player_color=-config.human_color)
            self.agents={config.human_color:human, -config.human_color:ai}

        self.last_play=None
        self.font=pygame.font.SysFont("arial",28)
        self.font_small = pygame.font.SysFont("arial",15)
        self.font_big = pygame.font.SysFont("arial",32, bold=True)

        # ====== ĐỒNG HỒ MỖI BÊN ======
        # tổng thời gian mỗi bên (giây), truyền từ menu qua config.clock_seconds
        total = getattr(config, "clock_seconds", 300)  # fallback 5 phút mỗi bên nếu thiếu
        self.clock_total = {BLACK: float(total), WHITE: float(total)}
        self._last_tick_ms = pygame.time.get_ticks()
        self.time_over = False
        self.time_over_winner = None  # 1 hoặc -1
        self.final_result = None

    # ====== VẼ QUÂN ======
    def draw_stone(self, center, is_black, scale=1.0):
        x, y = center
        r = int((self.cell_size // 2 - 5) * scale)  # Quân to, đầy ô

        # 1) Bóng đổ
        shadow = pygame.Surface((r*2 + 25, r*2 + 25), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (r//2 + 4, r//2 + 8, r + 5, r//2 + 2))
        self.screen.blit(shadow, (x - r - 12, y - r + 5))

        # 2) Mặt quân – gradient mịn
        for i in range(r, 0, -1):
            intensity = 255 - (r - i) * 2.5
            if is_black:
                color = (max(10, intensity//5), max(10, intensity//5), max(10, intensity//5))
            else:
                color = (min(255, intensity + 50), min(255, intensity + 50), min(255, intensity + 50))
            pygame.draw.circle(self.screen, color, (x, y), i)

    # ====== CHUYỂN TỌA ĐỘ ======
    def board_to_screen(self,i,j): 
        return self.margin_x + i * self.cell_size, self.margin_y + j * self.cell_size
    
    def screen_to_board(self,x,y): 
        i=round((x - self.margin_x) / self.cell_size)
        j=round((y - self.margin_y) / self.cell_size)
        return i,j

    # ====== ĐỒNG HỒ: TRỪ THỜI GIAN BÊN ĐANG ĐI ======
    def _tick_clock(self):
        if self.state.is_terminal() or self.time_over:
            self._last_tick_ms = pygame.time.get_ticks()
            return

        now = pygame.time.get_ticks()
        dt = (now - self._last_tick_ms) / 1000.0  # giây
        self._last_tick_ms = now

        player = self.state.to_play
        self.clock_total[player] = max(0.0, self.clock_total[player] - dt)

        # Hết giờ -> hành động
        if self.clock_total[player] <= 0.0 and not self.time_over:
            action = (ON_TIMEOUT_ACTION or "RESIGN").upper()
            if action == "PASS":
                self.state = self.state.apply_move(Move.pass_())
            else:
                self.state = self.state.apply_move(Move.resign())
            self.time_over = True
            self.time_over_winner = -player  # bên kia thắng

    # ====== XỬ LÝ CLICK ======
    def handle_click(self,pos):
        i,j=self.screen_to_board(*pos)
        if 0<=i<self.state.board.size and 0<=j<self.state.board.size:
            player=self.state.to_play; agent=self.agents[player]
            if isinstance(agent, HumanAgent):
                mv=Move.play(i,j)
                if any(m.kind=='PLAY' and m.x==i and m.y==j for m in self.state.legal_moves()):
                    agent.set_pending_move(mv)
        else:
            # Kiểm tra click nút Đầu hàng
            if self.resign_rect.collidepoint(pos):
                player = self.state.to_play
                agent = self.agents[player]
                if isinstance(agent, HumanAgent) and not self.state.is_terminal():
                    agent.set_pending_move(Move.resign())

    # ====== BƯỚC CẬP NHẬT ======
    def step(self):
        # trừ thời gian theo thực
        self._tick_clock()

        # 1. Nếu game đã kết thúc HOẶC đã hết giờ, tính điểm và dừng
        if self.state.is_terminal() or self.time_over:
            if not self.final_result and not self.time_over:
                # Nếu game kết thúc bởi 2 PASS/RESIGN (chứ không phải hết giờ)
                try:
                    # state.score() sẽ tính điểm và xác định người thắng.
                    self.final_result = self.state.score()
                except ValueError:
                    # Nếu state.is_terminal() là True nhưng có lỗi tính điểm (không nên xảy ra)
                    pass
            
            return "done" # Dừng cập nhật logic game

        player=self.state.to_play; agent=self.agents[player]
        mv=agent.select_move(self.state)
        if mv is None: 
            return None
        self.state=self.state.apply_move(mv); self.last_play=mv
        return None

    # ====== VẼ UI ======
    def draw(self):
        self.screen.fill((230, 200, 150))  # Nền gỗ
        size = self.state.board.size
        cell = self.cell_size
        mx, my = self.margin_x, self.margin_y
        board_w = (size - 1) * cell 

        # 1) Khung viền
        padding = 30
        outer = pygame.Rect(mx - padding, my - padding, board_w + 2 * padding, board_w + 2*padding)
        pygame.draw.rect(self.screen, (110, 70, 30), outer, border_radius=28)
        
        inner_padding = 30
        inner = pygame.Rect(mx - inner_padding, my - inner_padding, board_w + 2 * inner_padding, board_w + 2 * inner_padding)
        pygame.draw.rect(self.screen, (220, 180, 120), inner, border_radius=18)

        board_rect = pygame.Rect(mx, my, board_w, board_w)
        pygame.draw.rect(self.screen, (215, 175, 110), board_rect)

        # 2) Lưới
        for k in range(size):
            x0, y0 = mx + 0 * cell, my + k * cell
            x1, y1 = mx + (size-1) * cell, my + k * cell
            pygame.draw.line(self.screen, (20,20,20), (x0, y0), (x1, y1), 1)

            x0, y0 = mx + k * cell, my + 0 * cell
            x1, y1 = mx + k * cell, my + (size-1) * cell
            pygame.draw.line(self.screen, (20,20,20), (x0, y0), (x1, y1), 1)

        # 3) Điểm khí (hoshi)
        stars = [2, 4, 6]
        for i in stars:
            for j in stars:
                cx = mx + i * cell
                cy = my + j * cell
                pygame.draw.circle(self.screen, (60, 60, 60), (cx, cy), 4)

        # 4) Quân cờ
        for y in range(size):
            for x in range(size):
                v = self.state.board.get(x, y)
                if v != 0:
                    center = (mx + x * cell, my + y * cell)
                    self.draw_stone(center, v == 1)

        # 5) Nước đi cuối (khung đỏ bốn góc)
        if self.last_play and self.last_play.kind == 'PLAY':
            x = self.last_play.x
            y = self.last_play.y
            left = mx + x * cell - cell // 2
            top = my + y * cell - cell // 2
            sizepx = cell
            corner_size = cell // 4
            thickness = 3
            red = (220, 20, 20)
            # TL
            pygame.draw.rect(self.screen, red, (left, top, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left, top, thickness, corner_size))
            # TR
            pygame.draw.rect(self.screen, red, (left + sizepx - corner_size, top, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left + sizepx - thickness, top, thickness, corner_size))
            # BL
            pygame.draw.rect(self.screen, red, (left, top + sizepx - thickness, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left, top + sizepx - corner_size, thickness, corner_size))
            # BR
            pygame.draw.rect(self.screen, red, (left + sizepx - corner_size, top + sizepx - thickness, corner_size, thickness))
            pygame.draw.rect(self.screen, red, (left + sizepx - thickness, top + sizepx - corner_size, thickness, corner_size))

        # 6) UI Trên: hai quân to + đồng hồ + lượt
        top_y = my - 120
        black_center = (mx + board_w * 0.25, top_y)
        white_center = (mx + board_w * 0.75, top_y)

        self.draw_stone(black_center, is_black=True, scale=1.3)
        self.draw_stone(white_center, is_black=False, scale=1.3)

        # Đồng hồ
        blk_txt = self.font_big.render(_fmt_time(self.clock_total[BLACK]), True, (15,15,15))
        wht_txt = self.font_big.render(_fmt_time(self.clock_total[WHITE]), True, (15,15,15))
        self.screen.blit(blk_txt, blk_txt.get_rect(center=(black_center[0], top_y + 52)))
        self.screen.blit(wht_txt, wht_txt.get_rect(center=(white_center[0], top_y + 52)))

        # Lượt (đỏ)
        current_player = self.state.to_play
        turn_text = self.font.render("Đen" if current_player==1 else "Trắng", True, (220, 20, 20))
        if current_player == 1:
            self.screen.blit(turn_text, turn_text.get_rect(center=(black_center[0], top_y + 86)))
        else:
            self.screen.blit(turn_text, turn_text.get_rect(center=(white_center[0], top_y + 86)))

        # --- BỔ SUNG: NÚT ĐẦU HÀNG (RESIGN) ---
        btn_w, btn_h = 100, 30
        btn_x = self.W - btn_w - 20 # Góc trên bên phải
        btn_y = 20
        
        # Lưu rect để xử lý click
        self.resign_rect = pygame.Rect(btn_x, btn_y, btn_w, btn_h)
        
        is_human_turn = isinstance(self.agents[current_player], HumanAgent)
        
        # Nút Đầu hàng chỉ khả dụng khi đang là lượt người chơi và game chưa kết thúc
        if is_human_turn and not self.state.is_terminal():
            # Màu nút
            btn_color = (200, 50, 50)
            hover_color = (255, 80, 80)
            
            mx, my = pygame.mouse.get_pos()
            is_hovered = self.resign_rect.collidepoint(mx, my)

            # Vẽ nút (dùng draw.rect đơn giản)
            pygame.draw.rect(self.screen, hover_color if is_hovered else btn_color, self.resign_rect, border_radius=8)
            
            # Vẽ chữ
            resign_text_surf = self.font_small.render("ĐẦU HÀNG", True, (255, 255, 255))
            text_rect = resign_text_surf.get_rect(center=self.resign_rect.center)
            self.screen.blit(resign_text_surf, text_rect)
        else:
            self.resign_rect = pygame.Rect(0, 0, 0, 0) # Vô hiệu hóa click
        
        # Banner HẾT GIỜ / KẾT QUẢ ĐIỂM
        banner_text = None
        banner_color = (220, 30, 30)
        
        # Ưu tiên 1: Hết giờ
        if self.time_over:
            winner_name = 'Đen' if self.time_over_winner == 1 else 'Trắng'
            banner_text = f"HẾT GIỜ! {winner_name} thắng."
            
        # Ưu tiên 2: Kết quả theo điểm
        elif self.final_result:
            b_score, w_score_final, winner = self.final_result
            if winner != 0:
                winner_name = 'Đen' if winner == 1 else 'Trắng'
                score_diff = abs(b_score - w_score_final)
                
                # Làm tròn điểm chênh lệch và hiển thị Ko-mi
                komi_info = f" (+{w_score_final - b_score + score_diff:.1f} Komi)" if winner == -1 else ""
                
                banner_text = f"GAME OVER! {winner_name} thắng {score_diff:.1f} điểm{komi_info}"
                banner_color = (30, 150, 30) # Màu xanh lá cho kết quả điểm
            else:
                banner_text = "HÒA (JIGO)!"
                banner_color = (50, 50, 200)

        if banner_text:
            banner = self.font_big.render(banner_text, True, banner_color)
            rect = banner.get_rect(center=(self.W // 2, max(30, my - 160)))
            self.screen.blit(banner, rect)

        # Hướng dẫn
        line1 = self.font_small.render("Bấm [ESC] để quay lại menu", True, (100, 100, 100))
        line2 = self.font_small.render("Bấm [SPACE] để pass lượt", True, (100, 100, 100))
        self.screen.blit(line1, (20, self.screen.get_height() - 100))
        self.screen.blit(line2, (20, self.screen.get_height() - 70))
