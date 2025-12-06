import pygame
from core.game_state import GameState
from core.move import Move
from core.board import BLACK, WHITE
from core.agents import HumanAgent
from core.agents import MinimaxAgent
from core.minimax import MinimaxSearcher
from config.settings import BOARD_SIZE, ON_TIMEOUT_ACTION
import os

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
        # Đảm bảo MinimaxSearcher được import và khởi tạo đúng
        searcher = MinimaxSearcher(depth_limit=config.ai_depth) 

        if config.mode=="pvp":
            self.agents={
                # Cần truyền màu sắc khi khởi tạo HumanAgent
                BLACK: HumanAgent(player_color=BLACK), 
                WHITE: HumanAgent(player_color=WHITE)
            }
        else: # Chế độ vs AI
            human_color = config.human_color
            ai_color = -config.human_color
            
            human_agent = HumanAgent(player_color=human_color)
            
            # Cần truyền searcher và màu sắc cho MinimaxAgent
            ai_agent = MinimaxAgent(searcher=searcher, player_color=ai_color) 
            
            self.agents={
                human_color: human_agent, 
                ai_color: ai_agent
            }

        # === FONTS ===
        try:
            base_dir = os.path.dirname(__file__)
            root = os.path.dirname(base_dir)  # trỏ tới thư mục gốc dự án
            
            bold_path   = os.path.join(root, "assets", "fonts", "bold.ttf")
            regular_path = os.path.join(root, "assets", "fonts", "normal.ttf")
            
            self.title_font = pygame.font.Font(bold_path, 80)      # CỜ VÂY
            self.item_font  = pygame.font.Font(bold_path, 38)      # 2 nút lớn
            self.big_font   = pygame.font.Font(bold_path, 35)
            self.medium_font = pygame.font.Font(bold_path, 24)
            self.small_font  = pygame.font.Font(regular_path, 15)

        except Exception as e:
            # fallback nếu thiếu font
            self.title_font = pygame.font.SysFont("arial", 90, bold=True)
            self.item_font  = pygame.font.SysFont("arial", 38, bold=True)
            self.big_font   = pygame.font.SysFont("arial", 35, bold = True)
            self.small_font = pygame.font.SysFont("arial", 26)
            self.medium_font = pygame.font.SysFont("arial", 24, bold = True)

        # ====== ĐỒNG HỒ MỖI BÊN ======
        # tổng thời gian mỗi bên (giây), truyền từ menu qua config.clock_seconds
        total = getattr(config, "clock_seconds", 300)  # fallback 5 phút mỗi bên nếu thiếu
        self.clock_total = {BLACK: float(total), WHITE: float(total)}
        self._last_tick_ms = pygame.time.get_ticks()
        self.time_over = False
        self.time_over_winner = None  # 1 hoặc -1
        self.final_result = None
        self.last_play = None # <-- BỔ SUNG DÒNG NÀY
        self.show_endgame_popup = False   # để bật popup kết quả cuối

    def draw_glow_text(self, text, font, color, center, glow=True):
        if glow:
            shadow = font.render(text, True, (0, 0, 0, 80))
            shadow_rect = shadow.get_rect(center=(center[0]+3, center[1]+3))
            self.screen.blit(shadow, shadow_rect)
        txt = font.render(text, True, color)
        txt_rect = txt.get_rect(center=center)
        self.screen.blit(txt, txt_rect)
        return txt_rect

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
            self.show_endgame_popup = True   # bật popup kết quả
            if not self.final_result and not self.time_over:
                # Nếu game kết thúc bởi 2 PASS/RESIGN (chứ không phải hết giờ)
                try:
                    self.final_result = self.state.score()
                except ValueError:
                    pass
            
            return "done" # Dừng cập nhật logic game

        player=self.state.to_play; agent=self.agents[player]
        mv=agent.select_move(self.state)
        if mv is None: 
            return None
        self.state=self.state.apply_move(mv); self.last_play=mv
        return None

    # ====== VẼ UI ======
    def draw(self, events=[]):
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
        top_y = my - 125                  
        black_center = (mx + board_w * 0.25, top_y)
        white_center = (mx + board_w * 0.75, top_y)

        current_player = self.state.to_play

        # === Vẽ quân lớn (to hơn một chút khi tới lượt) ===
        black_scale = 1.4 if current_player == 1 else 1.3
        white_scale = 1.4 if current_player == -1 else 1.3
        self.draw_stone(black_center, is_black=True,  scale=black_scale)
        self.draw_stone(white_center, is_black=False, scale=white_scale)

        # === Đồng hồ ===
        blk_time = _fmt_time(self.clock_total[BLACK])
        wht_time = _fmt_time(self.clock_total[WHITE])

        # Đổi màu đồng hồ bên đang đi thành đỏ nhẹ cho dễ nhận biết
        blk_color = (220, 30, 30) if current_player == 1 else (15, 15, 15)
        wht_color = (220, 30, 30) if current_player == -1 else (15, 15, 15)

        blk_txt = self.big_font.render(blk_time, True, blk_color)
        wht_txt = self.big_font.render(wht_time, True, wht_color)

        self.screen.blit(blk_txt, blk_txt.get_rect(center=(black_center[0], top_y + 54)))
        self.screen.blit(wht_txt, wht_txt.get_rect(center=(white_center[0], top_y + 54)))

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
            resign_text_surf = self.small_font.render("ĐẦU HÀNG", True, (255, 255, 255))
            text_rect = resign_text_surf.get_rect(center=self.resign_rect.center)
            self.screen.blit(resign_text_surf, text_rect)
        else:
            self.resign_rect = pygame.Rect(0, 0, 0, 0) # Vô hiệu hóa click
        
        # Banner HẾT GIỜ / KẾT QUẢ ĐIỂM
        banner_text = None
        banner_color = (220, 30, 30)
        
        #POPUP KẾT QUẢ CUỐI (đầu hàng / hết giờ / tính điểm) 
        if self.show_endgame_popup:
            
            # Xác định TÌNH TRẠNG KẾT THÚC
            is_resign = self.state.move_history and self.state.move_history[-1].kind == 'RESIGN'

            if self.time_over:
                title = "Hết giờ!"
                message = f"Hết giờ! {'Đen' if self.time_over_winner==1 else 'Trắng'} thắng."
                title_color = (220, 50, 50)
                
            elif is_resign:
                winner_color = self.state.to_play
                loser_color = -self.state.to_play
                
                winner_name = "Đen" if winner_color == 1 else "Trắng"
                loser_name = "Đen" if loser_color == 1 else "Trắng"

                title = "Đầu hàng!"
                message = f"{winner_name} thắng do {loser_name} đầu hàng!"
                title_color = (220, 50, 50)
                
                
            elif self.final_result:
                b_score, w_score_final, winner = self.final_result
                if winner != 0:
                    winner_name = 'Đen' if winner == 1 else 'Trắng'
                    diff = abs(b_score - w_score_final)
                    komi = f" (+{w_score_final - b_score + diff:.1f} Komi)" if winner == -1 else ""
                    title = "GAME OVER!"
                    message = f"{winner_name} thắng {diff:.1f} điểm{komi}"
                    title_color = (50, 160, 50)
                else:
                    title = "HÒA!"
                    message = "HÒA (JIGO)!"
                    title_color = (70, 100, 200)

            # Vẽ popup
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            box = pygame.Rect(0, 0, 720, 460)
            box.center = (self.W//2, self.H//2)
            pygame.draw.rect(self.screen, (255, 250, 235), box, border_radius=60)
            pygame.draw.rect(self.screen, (190, 130, 80), box, 10, border_radius=60)

            self.draw_glow_text(title, self.title_font, title_color, (box.centerx, box.top + 100))
            self.draw_glow_text(message, self.big_font, (100, 50, 20), (box.centerx, box.centery + 20), glow=False)

            # 2 nút
            btn_w, btn_h = 280, 86
            menu_btn = pygame.Rect(0, 0, btn_w, btn_h)
            menu_btn.center = (box.centerx, box.centery + 100)  # căn chính giữa

            mx, my = pygame.mouse.get_pos()
            hovered = menu_btn.collidepoint(mx, my)

            # Nút Về trang chủ
            pygame.draw.rect(self.screen, 
                             (220, 70, 70) if hovered else (200, 50, 50),
                             menu_btn, border_radius=50)
            pygame.draw.rect(self.screen, (255, 140, 140), menu_btn, 8, border_radius=50)
            self.draw_glow_text("Về trang chủ", self.big_font, "white", menu_btn.center)

            # Xử lý click
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if menu_btn.collidepoint(e.pos):
                        return "menu"
        
        # Hướng dẫn
        # Vị trí 2 nút
        if not self.show_endgame_popup:
            btn_w, btn_h = 180, 68
            spacing = 100 
            center_y = self.H - 100

            back_rect = pygame.Rect(self.W//2 - btn_w - spacing//2, center_y, btn_w, btn_h)
            pass_rect = pygame.Rect(self.W//2 + spacing//2, center_y, btn_w, btn_h)

            mx, my = pygame.mouse.get_pos()

            click_event = None
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    click_event = e
                    break  # chỉ cần 1 click

            # === XỬ LÝ CLICK CHO 2 NÚT ===
            if click_event:
                if pass_rect.collidepoint(click_event.pos):
                    if not self.state.is_terminal():
                        self.state = self.state.apply_move(Move.pass_())
                elif back_rect.collidepoint(click_event.pos):
                    self.show_quit_confirm = True

            # === VẼ 2 NÚT ===
            for rect, text, is_back in [(back_rect, "Quay lại", True), (pass_rect, "Pass lượt", False)]:
                hovered = rect.collidepoint(mx, my)

                # Màu khác nhau cho 2 nút
                if is_back:
                    base = (240, 210, 170)   
                    hover = (255, 235, 200)
                else:
                    base = (240, 210, 170)  
                    hover = (255, 235, 200)

                color = hover if hovered else base

                pygame.draw.rect(self.screen, color, rect, border_radius=36)
                pygame.draw.rect(self.screen, (160, 110, 70), rect, 3, border_radius=36)

                txt_col = (100, 50, 15) if hovered else (70, 35, 10)
                self.draw_glow_text(text, self.big_font, txt_col, rect.center, glow=False)

            # === POPUP XÁC NHẬN THOÁT ===
            if getattr(self, "show_quit_confirm", False):
                overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))

                popup = pygame.Rect(0, 0, 580, 340)
                popup.center = (self.W//2, self.H//2)

                pygame.draw.rect(self.screen, (248, 242, 215), popup, border_radius=40)
                pygame.draw.rect(self.screen, (180, 120, 70), popup, 3, border_radius=40)

                self.draw_glow_text("Bạn có chắc muốn thoát không?", 
                                self.big_font, (140, 50, 20), (self.W//2, popup.centery - 70), glow=False)

                # Nút Không (trái) – Có (phải)
                no_rect  = pygame.Rect(popup.left + 80,  popup.bottom - 130, 180, 80)
                yes_rect = pygame.Rect(popup.right - 260, popup.bottom - 130, 180, 80)

                for rect, text, is_yes in [(no_rect, "Không", False), (yes_rect, "Có", True)]:
                    hovered = rect.collidepoint(mx, my)
                    bg = (240, 210, 170) if not is_yes else (90, 170, 90)
                    if hovered:
                        bg = (255, 230, 190) if not is_yes else (110, 190, 110)

                    pygame.draw.rect(self.screen, bg, rect, border_radius=40)
                    pygame.draw.rect(self.screen, (180, 120, 70), rect, 2, border_radius=40)

                    txt_col = (80, 40, 10) if not is_yes else (255, 255, 255)
                    self.draw_glow_text(text, self.big_font, txt_col, rect.center, glow=False)

                    # Xử lý click trong popup
                    if click_event and rect.collidepoint(click_event.pos):
                        if is_yes:
                            return "menu"                    # về menu
                        else:
                            self.show_quit_confirm = False   # đóng popup
