# --- CẤU HÌNH GAME & AI ---
BOARD_SIZE = 9
DEFAULT_AI_DEPTH = 2

# Thời gian cho AI suy nghĩ mỗi nước (timebox cho MinimaxSearcher)
TIMEBOX_SEC = 3.0
USE_ALPHA_BETA = True

# --- ĐỒNG HỒ VÁN (UI) ---
# Tổng thời gian cho mỗi bên (giây). Ví dụ: 300 = 5 phút
CLOCK_SECONDS_PER_SIDE = 300
# Nếu hết giờ: tự động RESIGN (bên kia thắng)
ON_TIMEOUT_ACTION = "RESIGN" # Hoặc "PASS" để tự động PASS
