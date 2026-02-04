"""
五子棋游戏 (Gomoku)
使用 Python + Tkinter 实现
"""

import tkinter as tk
from tkinter import messagebox


class Gomoku:
    def __init__(self, master):
        self.master = master
        self.master.title("五子棋")
        self.master.resizable(False, False)
        
        # 游戏配置
        self.board_size = 15  # 15x15 棋盘
        self.cell_size = 40   # 每个格子的大小
        self.padding = 30     # 边距
        
        # 计算画布大小
        self.canvas_size = self.board_size * self.cell_size + self.padding * 2
        
        # 游戏状态
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        self.current_player = 1  # 1: 黑棋, 2: 白棋
        self.game_over = False
        self.move_history = []
        
        # 颜色配置
        self.colors = {
            'bg': '#E3C16F',      # 棋盘背景色
            'line': '#000000',     # 线条颜色
            'black': '#000000',    # 黑棋
            'white': '#FFFFFF',    # 白棋
            'last_move': '#FF0000' # 最后一手标记
        }
        
        self.create_ui()
        self.draw_board()
        
    def create_ui(self):
        """创建用户界面"""
        # 顶部信息栏
        self.info_frame = tk.Frame(self.master, padx=10, pady=10)
        self.info_frame.pack()
        
        self.status_label = tk.Label(
            self.info_frame, 
            text="黑棋回合", 
            font=('Arial', 14, 'bold')
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 按钮
        tk.Button(
            self.info_frame, 
            text="重新开始", 
            command=self.reset_game,
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            self.info_frame, 
            text="悔棋", 
            command=self.undo_move,
            font=('Arial', 12)
        ).pack(side=tk.LEFT, padx=5)
        
        # 棋盘画布
        self.canvas = tk.Canvas(
            self.master,
            width=self.canvas_size,
            height=self.canvas_size,
            bg=self.colors['bg']
        )
        self.canvas.pack(padx=10, pady=10)
        
        # 绑定点击事件
        self.canvas.bind('<Button-1>', self.on_click)
        
    def draw_board(self):
        """绘制棋盘"""
        self.canvas.delete('all')
        
        # 绘制网格线
        for i in range(self.board_size):
            # 横线
            self.canvas.create_line(
                self.padding, self.padding + i * self.cell_size,
                self.canvas_size - self.padding, self.padding + i * self.cell_size,
                width=1
            )
            # 竖线
            self.canvas.create_line(
                self.padding + i * self.cell_size, self.padding,
                self.padding + i * self.cell_size, self.canvas_size - self.padding,
                width=1
            )
        
        # 绘制星位（天元、小目等）
        star_points = [(3, 3), (3, 7), (3, 11), (7, 3), (7, 7), (7, 11), (11, 3), (11, 7), (11, 11)]
        for x, y in star_points:
            self.draw_star(x, y)
        
        # 绘制已有棋子
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] != 0:
                    self.draw_piece(row, col, self.board[row][col])
        
        # 标记最后一手
        if self.move_history:
            last_row, last_col = self.move_history[-1]
            self.draw_last_move_marker(last_row, last_col)
    
    def draw_star(self, row, col):
        """绘制星位标记"""
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        r = 3
        self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=self.colors['line'], outline='')
    
    def draw_piece(self, row, col, player):
        """绘制棋子"""
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        r = self.cell_size // 2 - 2
        
        color = self.colors['black'] if player == 1 else self.colors['white']
        
        # 棋子阴影效果
        self.canvas.create_oval(
            x - r + 2, y - r + 2,
            x + r + 2, y + r + 2,
            fill='#999999', outline=''
        )
        
        # 棋子本体
        self.canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=color,
            outline='#333333',
            width=1
        )
    
    def draw_last_move_marker(self, row, col):
        """绘制最后一手标记"""
        x = self.padding + col * self.cell_size
        y = self.padding + row * self.cell_size
        r = 4
        self.canvas.create_rectangle(
            x - r, y - r, x + r, y + r,
            fill=self.colors['last_move'],
            outline=''
        )
    
    def on_click(self, event):
        """处理鼠标点击"""
        if self.game_over:
            return
        
        # 计算点击的格子
        col = round((event.x - self.padding) / self.cell_size)
        row = round((event.y - self.padding) / self.cell_size)
        
        # 检查是否在有效范围内
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return
        
        # 检查位置是否已被占用
        if self.board[row][col] != 0:
            return
        
        # 落子
        self.make_move(row, col)
    
    def make_move(self, row, col):
        """执行落子"""
        self.board[row][col] = self.current_player
        self.move_history.append((row, col))
        
        # 重绘棋盘
        self.draw_board()
        
        # 检查胜负
        if self.check_winner(row, col):
            winner = "黑棋" if self.current_player == 1 else "白棋"
            self.game_over = True
            self.status_label.config(text=f"{winner}获胜！")
            messagebox.showinfo("游戏结束", f"{winner}获胜！")
            return
        
        # 检查平局
        if len(self.move_history) == self.board_size * self.board_size:
            self.game_over = True
            self.status_label.config(text="平局！")
            messagebox.showinfo("游戏结束", "平局！")
            return
        
        # 切换玩家
        self.current_player = 3 - self.current_player  # 1->2, 2->1
        player_name = "黑棋" if self.current_player == 1 else "白棋"
        self.status_label.config(text=f"{player_name}回合")
    
    def check_winner(self, row, col):
        """检查是否有玩家获胜"""
        player = self.board[row][col]
        
        # 四个方向：横、竖、左斜、右斜
        directions = [
            [(0, 1), (0, -1)],   # 横向
            [(1, 0), (-1, 0)],   # 纵向
            [(1, 1), (-1, -1)],  # 右斜
            [(1, -1), (-1, 1)]   # 左斜
        ]
        
        for dir_pair in directions:
            count = 1  # 当前棋子
            
            for dr, dc in dir_pair:
                r, c = row + dr, col + dc
                while 0 <= r < self.board_size and 0 <= c < self.board_size:
                    if self.board[r][c] == player:
                        count += 1
                        r += dr
                        c += dc
                    else:
                        break
            
            if count >= 5:
                return True
        
        return False
    
    def undo_move(self):
        """悔棋"""
        if not self.move_history or self.game_over:
            return
        
        row, col = self.move_history.pop()
        self.board[row][col] = 0
        
        # 切换回上一个玩家
        self.current_player = 3 - self.current_player
        player_name = "黑棋" if self.current_player == 1 else "白棋"
        self.status_label.config(text=f"{player_name}回合")
        
        self.game_over = False
        self.draw_board()
    
    def reset_game(self):
        """重新开始游戏"""
        self.board = [[0] * self.board_size for _ in range(self.board_size)]
        self.current_player = 1
        self.game_over = False
        self.move_history = []
        self.status_label.config(text="黑棋回合")
        self.draw_board()


def main():
    root = tk.Tk()
    game = Gomoku(root)
    root.mainloop()


if __name__ == '__main__':
    main()
