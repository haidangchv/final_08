import pygame
import os 
from dataclasses import dataclass
from config.settings import DEFAULT_AI_DEPTH, CLOCK_SECONDS_PER_SIDE

# === MÀU CHUẨN CỜ VÂY ===
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (240, 240, 240)

@dataclass
class GameConfig:
    mode: str = "pvp"
    ai_depth: int = DEFAULT_AI_DEPTH
    human_color: int = 1  # 1=Đen, -1=Trắng
    clock_seconds: int = CLOCK_SECONDS_PER_SIDE

class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()

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

            print("Load font Sarabun thành công từ assets/fonts!")
        except Exception as e:
            print("Không tải được font, dùng font hệ thống:", e)
            # fallback nếu thiếu font
            self.title_font = pygame.font.SysFont("arial", 90, bold=True)
            self.item_font  = pygame.font.SysFont("arial", 38, bold=True)
            self.big_font   = pygame.font.SysFont("arial", 35, bold = True)
            self.small_font = pygame.font.SysFont("arial", 26)
            self.medium_font = pygame.font.SysFont("arial", 24, bold = True)

        # === TRẠNG THÁI ===
        self.choice = None
        self.ai_depth = DEFAULT_AI_DEPTH
        self.human_color = 1
        self.active_panel = None  # None | "pvp" | "vsai" -> modal open when set
        self.selectef_color = (240,210,160)

        # === MÀU SẮC ===
        self.bg_color       = (180, 140, 90)
        self.panel_color    = (200, 160, 110)
        self.border_color   = (150, 110, 70)
        self.text_color     = (50, 30, 10)
        self.title_color    = (100, 60, 20)
        self.start_ready    = (80, 140, 80)

        # === TẢI LOGO ===
        try:
            base_dir = os.path.dirname(__file__)  # đường dẫn thư mục chứa file hiện tại
            root = os.path.dirname(base_dir)

            logo_path = os.path.join(root, "assets", "images", "logo.png")

            self.logo = pygame.image.load(logo_path).convert_alpha()
            self.logo = pygame.transform.smoothscale(self.logo, (250, 250))

        except Exception as e:
            print(f"Không tải được logo: {e}")
            self.logo = None

        self.just_opened_modal = False

    def draw_rounded_rect(self, surface, rect, color, radius=15):
        pygame.draw.rect(surface, color, rect, border_radius=radius)

    def draw_glow_text(self, text, font, color, center, glow=True):
        if glow:
            shadow = font.render(text, True, (0, 0, 0, 80))
            shadow_rect = shadow.get_rect(center=(center[0]+3, center[1]+3))
            self.screen.blit(shadow, shadow_rect)
        txt = font.render(text, True, color)
        txt_rect = txt.get_rect(center=center)
        self.screen.blit(txt, txt_rect)
        return txt_rect

    def draw_go_piece(self, center, is_black, size=18):
        x, y = center

        # Bóng đổ
        shadow = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 50), (size//4, size//3, size*1.5, size//2))
        self.screen.blit(shadow, (x - size, y - size + 8))

        # Quân cờ
        color = BLACK_STONE if is_black else WHITE_STONE
        border_color = (0, 0, 0) if is_black else (100, 100, 100)

        pygame.draw.circle(self.screen, border_color, (x, y), size)
        pygame.draw.circle(self.screen, color, (x, y), size - 1)

    def run_once(self, events):
        self.screen.fill(self.bg_color)

        # === TIÊU ĐỀ ===
        self.draw_glow_text("CỜ VÂY", self.title_font, self.title_color, (self.W//2, 140))
                # === HIỂN THỊ LOGO DƯỚI CHỮ "CỜ VÂY" ===
        if self.logo:
            logo_x = self.W // 2
            logo_y = 320  # Dưới chữ 90px
            logo_rect = self.logo.get_rect(center=(logo_x, logo_y))
            self.screen.blit(self.logo, logo_rect)

        # === BẢNG MENU ===
        panel_w, panel_h = 420, 280 
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (self.W//2, self.H//2 + 130)
        pygame.draw.rect(self.screen, (245, 230, 195), panel_rect, border_radius=30)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 6, border_radius=30)

        # === MENU ITEMS ===
        # only two options shown; clicking one opens the modal to choose color / AI depth
        menu_items = [
            ("Người vs Người", "pvp"),
            ("Người vs Máy", "vsai"),
        ]

        button_h = 60
        spacing = 30
        start_y = panel_rect.y + 50
         # reset option rects for this frame
        self._option_rects = []

        mx, my = pygame.mouse.get_pos()
        for i, (text, action) in enumerate(menu_items):
            y = start_y + i * (button_h + spacing)
            rect = pygame.Rect(0, 0, panel_w - 50, button_h)
            rect.centerx = self.W // 2
            rect.y = y

            # keep clickable rects for options
            if i < 2:
                if not hasattr(self, "_option_rects"):
                    self._option_rects = []
                self._option_rects.append((rect.copy(), action))

            is_hovered = rect.collidepoint(mx, my) and self.active_panel is None

            if is_hovered:
                btn_color = (255, 230, 180)   # giống nút Quay lại khi hover
                border_width = 5
            else:
                btn_color = self.panel_color  # màu gốc
                border_width = 4

            # Vẽ nút
            self.draw_rounded_rect(self.screen, rect, btn_color, 15)
            pygame.draw.rect(self.screen, self.border_color, rect, border_width, border_radius=18)

            # Chữ sáng hơn tí khi hover (giống nút Bắt đầu)
            text_color = (255, 255, 255) if is_hovered else self.text_color
            self.draw_glow_text(text, self.item_font, text_color, rect.center, glow=False)

            # MÀU CHỮ
            color = self.text_color 
            if i == 4 and self.choice:
                color = (240, 255, 200) 

            # DÒNG NGƯỜI CHƠI – CĂN GIỮA
            if i == 3:
                full_text = "Người chơi: "
                text_surf = self.small_font.render(full_text, True, color)
                text_rect = text_surf.get_rect()
                total_w = text_rect.width + 12 + 18*2
                start_x = rect.centerx - total_w // 2

                text_rect.left = start_x
                text_rect.centery = rect.centery
                self.screen.blit(text_surf, text_rect)

                piece_x = text_rect.right + 12
                self.draw_go_piece((piece_x, rect.centery), self.human_color == 1, size=18)
                continue

            # CHỮ THƯỜNG
            font = self.small_font if i >= 2 else self.item_font
            self.draw_glow_text(text, font, color, rect.center, glow=False)
        # === XỬ LÝ SỰ KIỆN ===
        for e in events:
            # Mouse click -> open modal for option or handle modal actions
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mx, my = e.pos
                # open modal when clicking an option (only when no modal is already open)
                if not self.active_panel and hasattr(self, "_option_rects"):
                    for r, action in self._option_rects:
                        if r.collidepoint(mx, my):
                            self.active_panel = action  # "pvp" or "vsai"
                            # ensure ai depth is at least 1
                            self.ai_depth = max(1, self.ai_depth)
                            self.just_opened_modal = True 
                            break

            if e.type == pygame.KEYDOWN:
                # keyboard: open modals
                if e.key == pygame.K_1:
                    self.active_panel = "pvp"
                if e.key == pygame.K_2:
                    self.active_panel = "vsai"

                # only adjust ai depth when vsai modal is open
                if self.active_panel == "vsai":
                    if e.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                        self.ai_depth = min (10, self.ai_depth + 1)
                    if e.key == pygame.K_MINUS:
                        self.ai_depth = max(1, self.ai_depth - 1)

                # toggle color only when a modal is open
                if self.active_panel and e.key == pygame.K_c:
                    self.human_color *= -1

                # confirm selection
                if e.key == pygame.K_RETURN and self.active_panel:
                    cfg = GameConfig(self.active_panel, self.ai_depth, self.human_color)
                    self.active_panel = None
                    self.choice = None 
                    return cfg

        # if modal open, draw it on top
        # === ĐỘ KHÓ AI ===
        if self.active_panel:
            modal_w, modal_h = 540, 360
            modal_rect = pygame.Rect(0, 0, modal_w, modal_h)
            modal_rect.center = (self.W//2, self.H//2)

            # --- Tạo tất cả rect trước ---
            stone_size = 38
            btn_size = 88, 88

            black_rect  = pygame.Rect(modal_rect.centerx - 140, modal_rect.y + 85, *btn_size)
            white_rect  = pygame.Rect(modal_rect.centerx + 52,  modal_rect.y + 85, *btn_size)
            black_rect  = black_rect.inflate(10, 10)   # vùng click rộng
            white_rect  = white_rect.inflate(10, 10)

            plus_rect   = pygame.Rect(modal_rect.centerx + 100,  modal_rect.y + 202, 40, 40)
            minus_rect  = pygame.Rect(modal_rect.centerx - 140, modal_rect.y + 202, 40, 40)

            btn_y = modal_rect.bottom - 96
            back_rect   = pygame.Rect(modal_rect.centerx - 210, btn_y, 148, 64)
            start_rect  = pygame.Rect(modal_rect.centerx + 62,  btn_y, 148, 64)

            # --- Xử lý click (duy nhất 1 chỗ) ---
            for e in events:
                if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if black_rect.collidepoint(e.pos):
                        self.human_color = 1
                    elif white_rect.collidepoint(e.pos):
                        self.human_color = -1
                    
                    if self.active_panel == "vsai":
                        if plus_rect.collidepoint(e.pos):
                            self.ai_depth = min (10, self.ai_depth + 1)
                        elif minus_rect.collidepoint(e.pos):
                            self.ai_depth = max(1, self.ai_depth - 1)
                
                    if back_rect.collidepoint(e.pos):
                        self.active_panel = None
                        self.just_opened_modal = False
                    elif start_rect.collidepoint(e.pos) and not self.just_opened_modal:
                        cfg = GameConfig(mode=self.active_panel, ai_depth=self.ai_depth, human_color=self.human_color)
                        self.active_panel = None
                        return cfg

            # --- Vẽ modal ---
            overlay = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 130))
            self.screen.blit(overlay, (0, 0))

            pygame.draw.rect(self.screen, (245, 238, 210), modal_rect, border_radius=20)
            pygame.draw.rect(self.screen, (180, 140, 90), modal_rect, 6, border_radius=20)

            title = "Tham số" if self.active_panel == "pvp" else "Chọn màu & độ khó AI"
            self.draw_glow_text(title, self.item_font, (80, 50, 20), (modal_rect.centerx, modal_rect.y + 44), glow=False)

            mx, my = pygame.mouse.get_pos()
            for rect, is_black, selected in [(black_rect, True, self.human_color == 1),
                                            (white_rect, False, self.human_color == -1)]:
                hovered = rect.collidepoint(mx, my)
                bg = (255, 250, 200) if selected else (248, 240, 200)
                if hovered: bg = (255, 255, 210)
                self.draw_rounded_rect(self.screen, rect, bg, 26)
                if selected:
                    pygame.draw.rect(self.screen, (255, 160, 60), rect, 7, border_radius=26)
                elif hovered:
                    pygame.draw.rect(self.screen, (255, 200, 100), rect, 5, border_radius=26)
                self.draw_go_piece(rect.center, is_black, stone_size)

            if self.active_panel == "vsai":
                self.draw_glow_text(f"Độ khó: {self.ai_depth}", self.medium_font, self.text_color,
                                  (modal_rect.centerx, modal_rect.y + 222), glow=False)
                for r, txt in [(minus_rect, "−"), (plus_rect, "+")]:
                    hov = r.collidepoint(mx, my)
                    col = (255, 235, 170) if hov else (240, 210, 160)
                    self.draw_rounded_rect(self.screen, r, col, 12)
                    pygame.draw.rect(self.screen, self.border_color, r, 3, border_radius=12)
                    self.draw_glow_text(txt, self.big_font, self.text_color, r.center, glow=False)

            back_hov  = back_rect.collidepoint(mx, my)
            start_hov = start_rect.collidepoint(mx, my) and not self.just_opened_modal
            self.draw_rounded_rect(self.screen, back_rect,  (255, 230, 180) if back_hov else (240, 210, 170), 32)
            self.draw_rounded_rect(self.screen, start_rect, (100, 200, 100) if start_hov else (80, 170, 80), 32)
            pygame.draw.rect(self.screen, self.border_color, back_rect,  4, border_radius=32)
            pygame.draw.rect(self.screen, self.border_color, start_rect, 4, border_radius=32)
            self.draw_glow_text("Quay lại", self.medium_font, self.text_color, back_rect.center,  glow=False)
            self.draw_glow_text("Bắt đầu",  self.medium_font, (255,255,255),      start_rect.center, glow=False)

            self.just_opened_modal = False

        return None