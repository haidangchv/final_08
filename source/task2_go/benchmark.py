import time
import random
from core.game_state import GameState
from core.agents import MinimaxAgent, BaseAgent
from core.minimax import MinimaxSearcher
from core.board import BLACK, WHITE

# --- Agent Ngẫu nhiên ---
class RandomAgent(BaseAgent):
    def select_move(self, state):
        valid_moves = state.legal_moves()
        # Ưu tiên nước đi Play hơn Pass/Resign
        play_moves = [m for m in valid_moves if m.kind == 'PLAY']
        if play_moves:
            return random.choice(play_moves)
        return random.choice(valid_moves)

def run_match(depth_limit, match_id):
    """Chạy 1 ván đấu: Minimax (Đen) vs Random (Trắng)"""
    state = GameState.new_game(size=9)
    
    # Minimax (Đen) vs Random (Trắng)
    # Lưu ý: time_limit_sec = None để không giới hạn thời gian
    minimax_searcher = MinimaxSearcher(depth_limit=depth_limit, time_limit_sec=None)
    
    bot_minimax = MinimaxAgent(minimax_searcher, player_color=BLACK)
    bot_random = RandomAgent(player_color=WHITE)
    
    agents = {BLACK: bot_minimax, WHITE: bot_random}
    
    # Thống kê
    minimax_move_times = []
    moves_count = 0
    
    print(f"--- Ván {match_id} (Depth {depth_limit}) ---")
    
    while not state.is_terminal():
        player = state.to_play
        agent = agents[player]
        
        start_time = time.perf_counter()
        move = agent.select_move(state)
        end_time = time.perf_counter()
        
        # Chỉ đo thời gian của Minimax
        if player == BLACK:
            duration = end_time - start_time
            minimax_move_times.append(duration)
        
        state = state.apply_move(move)
        moves_count += 1
        
        # Giới hạn số nước đi để tránh ván quá dài
        if moves_count > 100:
            print("  -> Dừng sớm do quá 100 nước.")
            break

    # Kết thúc ván, tính điểm
    b_score, w_score, winner = state.score()
    avg_time = sum(minimax_move_times) / len(minimax_move_times) if minimax_move_times else 0
    is_win = (winner == BLACK)
    print(f"  Điểm cuối: Đen {b_score} - Trắng {w_score}")
    print(f"  Kết quả: {'Minimax Thắng' if is_win else 'Thua/Hòa'}")
    print(f"  Thời gian TB/nước: {avg_time:.4f}s")
    return is_win, avg_time

def benchmark_suite():
    # Cấu hình thử nghiệm
    depths_to_test = [1, 2, 3] # Thử các độ sâu này
    num_matches = 3            # Số ván đấu cho mỗi độ sâu (tăng lên 10-20 để số liệu chuẩn hơn)
    
    print(f"BẮT ĐẦU BENCHMARK ({num_matches} ván mỗi độ sâu)...")
    print("="*50)
    
    results = {}
    
    for depth in depths_to_test:
        wins = 0
        total_avg_time = 0
        
        for i in range(num_matches):
            is_win, t = run_match(depth, i+1)
            if is_win: wins += 1
            total_avg_time += t
            
        final_avg_time = total_avg_time / num_matches
        win_rate = (wins / num_matches) * 100
        
        results[depth] = {
            'win_rate': win_rate,
            'avg_time': final_avg_time
        }
        print(f">>> TỔNG KẾT DEPTH {depth}: Win Rate {win_rate}%, Avg Time {final_avg_time:.4f}s\n")

    print("="*50)
    print("BẢNG KẾT QUẢ ĐO:")
    print("Depth | Avg Time (s) | Win Rate (%)")
    for d, Res in results.items():
        print(f"  {d}   |    {Res['avg_time']:.4f}    |    {Res['win_rate']:.1f}")
    print("="*50)
if __name__ == "__main__":
    benchmark_suite()