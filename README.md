# final_08
FINAL PROJECT Introduction to Artificial Intelligence
Dự án này triển khai 3 thuật toán AI nền tảng: Hill Climbing (Tối ưu hóa), Minimax (Cờ Vây) và SAT Solver (Sudoku).

## 🛠️ Yêu cầu Hệ thống (Prerequisites)

Bạn cần cài đặt **Python 3.8+** trở lên.

## ⚙️ Hướng dẫn Cài đặt và Chạy

Thực hiện các bước sau để khởi động chương trình:

### 1. Cài đặt các Thư viện cần thiết

Dự án sử dụng `pygame`, `numpy`, `matplotlib`, `sympy` và `pysat`.
```bash
pip install numpy matplotlib pygame sympy pysat
```
### 2. Khởi động Chương trình

# Task 1: mở file task1.ipynb trong thư mục task1_localsearch để xem chi tiết

# Task 2: Trong thư mục task2_go
- Chạy file chính của chương trình(mở menu)

```bash
python main.py
```
- Thử nghiệm Hiệu năng (Benchmark)
+ Phần này dùng để thu thập dữ liệu về Thời gian di chuyển trung bình và Tỷ lệ thắng của AI ở các độ sâu khác nhau
+ Kết quả (thời gian và tỷ lệ thắng) sẽ được hiển thị dưới dạng bảng sau khi thử nghiệm hoàn tất.

```bash
python benchmark.py
```
# Task 3: mở file Sudoku_Task3.ipynb trong thư mục task3_sudoku để xem chi tiết

### Cây thư mục(Tree path)
source/
├── task1_localsearch/
 |          └── task1.ipynb
├── task2_go/
 |          ├── assets/
 |          ├── config/                         # Logic cốt lõi của Game & AI
 |                      └── settings.py
 |          ├── core/
 |           |          ├── agents.py
 |           |          ├── board.py
 |           |          ├── game_state.py
 |           |          ├── minimax.py          # Lớp tìm kiếm
 |           |          ├── move.py
 |           |          └── rules.py
 |          ├── ui/
 |           |          ├── game_scene.py
 |           |          └── menu.py
 |          ├── benchmark.py                    # Đo hiệu suất thời gian và tỷ lệ win của thuật toán theo độ sâu
 |          └── main.py                         # Khởi chạy giao diện game
├── task3_sudoku/
            └── Sudoku_Task3.ipynb