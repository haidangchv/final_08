import pygame
from dataclasses import dataclass
from config.settings import DEFAULT_AI_DEPTH

# === MÀU CHUẨN CỜ VÂY ===
BLACK_STONE = (20, 20, 20)
WHITE_STONE = (240, 240, 240)

@dataclass
class GameConfig:
    mode: str = "pvp"
    ai_depth: int = DEFAULT_AI_DEPTH
    human_color: int = 1  # 1=Đen, -1=Trắng

class MenuScene:
    def __init__(self, screen):
        self.screen = screen
        self.W, self.H = screen.get_size()

        # === FONTS ===
        self.title_font = pygame.font.SysFont("arial", 80, bold=True)
        self.item_font = pygame.font.SysFont("arial", 38, bold=True)
        self.small_font = pygame.font.SysFont("verdana", 30)
        self.tiny_font = pygame.font.SysFont("couriernew", 24, bold=True)
        self.font_small = pygame.font.SysFont ("arial", 15)

        # === TRẠNG THÁI ===
        self.choice = None
        self.ai_depth = DEFAULT_AI_DEPTH
        self.human_color = 1
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
            logo_path = "assets/images/logo.png"
            self.logo = pygame.image.load(logo_path).convert_alpha()
            # Resize nhỏ lại (ví dụ: 80x80)
            self.logo = pygame.transform.smoothscale(self.logo, (200, 200))
        except Exception as e:
            print(f"Không tải được logo: {e}")
            self.logo = None

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
        self.draw_glow_text("CỜ VÂY", self.title_font, self.title_color, (self.W//2, 100))
                # === HIỂN THỊ LOGO DƯỚI CHỮ "CỜ VÂY" ===
        if self.logo:
            logo_x = self.W // 2
            logo_y = 100 + 100  # Dưới chữ 90px
            logo_rect = self.logo.get_rect(center=(logo_x, logo_y))
            self.screen.blit(self.logo, logo_rect)

        # === BẢNG MENU ===
        panel_w, panel_h = 560, 420
        panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
        panel_rect.center = (self.W//2, self.H//2 + 30)
        pygame.draw.rect(self.screen, (225, 195, 145, 240), panel_rect, border_radius=22)
        pygame.draw.rect(self.screen, self.border_color, panel_rect, 5, border_radius=22)

        # === MENU ITEMS ===
        menu_items = [
            ("Người vs Người", "pvp"),
            ("Người vs Máy", "vsai"),
            (f"Độ khó AI: {self.ai_depth}", None),
            ("Người chơi:", None),
            ("Bắt đầu", None),
        ]

        button_h = 60
        spacing = 12
        start_y = panel_rect.y + 50

        for i, (text, action) in enumerate(menu_items):
            y = start_y + i * (button_h + spacing)
            rect = pygame.Rect(0, 0, panel_w - 60, button_h)
            rect.centerx = self.W // 2
            rect.y = y

            # MÀU NÚT – ĐÃ SỬA
            btn_color = self.panel_color 
            if i == 0 and self.choice == "pvp":
                btn_color = self.selectef_color
            if i == 1 and self.choice == "vsai":
                btn_color = self.selectef_color
            if i == 4 and self.choice:
                btn_color = self.start_ready 

            self.draw_rounded_rect(self.screen, rect, btn_color, 16)
            border = self.border_color 
            pygame.draw.rect(self.screen, border, rect, 4, border_radius=16)

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

        # === HƯỚNG DẪN ===
        # hint = "1,2 chọn | +/- độ khó | C đổi màu | ENTER"
        # hint_surf = self.tiny_font.render(hint, True, (120, 80, 40))
        # self.screen.blit(hint_surf, (self.W//2 - hint_surf.get_width()//2, self.H - 50))
        line1 = self.font_small.render("Bấm [C] để đổi quân cờ", True, (100, 100, 100))
        line2 = self.font_small.render("Bấm [+/-] để chọn cấp độ khó", True, (100, 100, 100))
        line3 = self.font_small.render("Bấm [ENTER] để bắt đầu", True, (100, 100, 100))
        line4 = self.font_small.render("Bấm [1] chơi với người, [2] chơi với máy", True, (100, 100, 100))

        # Vị trí: cách lề trái 20px, cách đáy 50px
        self.screen.blit(line1, (20, self.screen.get_height() - 200))
        self.screen.blit(line2, (20, self.screen.get_height() - 170))
        self.screen.blit(line3, (20, self.screen.get_height() - 140))
        self.screen.blit(line4, (20, self.screen.get_height() - 110))

        # === XỬ LÝ SỰ KIỆN ===
        for e in events:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_1: self.choice = "pvp"
                if e.key == pygame.K_2: self.choice = "vsai"
                if e.key in (pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS):
                    self.ai_depth += 1
                if e.key == pygame.K_MINUS:
                    self.ai_depth = max(1, self.ai_depth - 1)
                if e.key == pygame.K_c:
                    self.human_color *= -1
                if e.key == pygame.K_RETURN and self.choice:
                    return GameConfig(self.choice, self.ai_depth, self.human_color)

        return None