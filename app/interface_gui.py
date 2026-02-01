"""
interface_gui.py - Interface แบบ GUI (Pygame) สำหรับเกม Thaichecker
"""

import copy
import csv
import pygame
import sys
from board import Board, Player, PieceType
from game_logic import GameLogic, Move
from ai_minimax import get_best_move
from typing import Optional, List, Tuple


class GUI:
    """คลาสจัดการ UI แบบ Pygame"""

    # สี
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_BROWN = (240, 217, 181)
    DARK_BROWN = (181, 136, 99)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)
    RED = (255, 0, 0)
    LIGHT_RED = (255, 100, 100)  # สีแดงสว่าง
    BLUE = (0, 100, 255)
    ORANGE = (255, 165, 0)  # สีส้ม

    # ขนาด
    SQUARE_SIZE = 80
    BOARD_SIZE = 8
    BOARD_WINDOW_SIZE = SQUARE_SIZE * BOARD_SIZE
    LOG_PANEL_WIDTH = 250
    WINDOW_WIDTH = BOARD_WINDOW_SIZE + LOG_PANEL_WIDTH
    WINDOW_HEIGHT = BOARD_WINDOW_SIZE + 100
    PIECE_RADIUS = 30
    CROWN_SIZE = 15

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption("Thaichecker - หมากฮอสไทย")

        self.board = Board()
        self.current_player = Player.WHITE
        self.selected_pos = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None

        # Move log
        self.move_log = []  # [(white_move, black_move), ...]
        self.current_round_white_move = None

        # Undo history
        self.history = []

        # AI settings
        self.ai_player = Player.BLACK  # AI เล่นฝั่งดำ
        self.ai_depth = 6

        # แสดงเลขช่อง 1-32 (True=ตัวเลข, False=จุด)
        self.show_square_numbers = True

        self.clock = pygame.time.Clock()
        thai_font = "Thonburi"
        self.font = pygame.font.SysFont(thai_font, 28)
        self.small_font = pygame.font.SysFont(thai_font, 20)
        self.tiny_font = pygame.font.SysFont(thai_font, 16)

    def get_square_from_mouse(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """แปลงตำแหน่งเมาส์เป็น (row, col) บนกระดาน"""
        x, y = pos
        if y > self.BOARD_WINDOW_SIZE or x > self.BOARD_WINDOW_SIZE:
            return None

        col = x // self.SQUARE_SIZE
        row = y // self.SQUARE_SIZE

        if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
            return (row, col)
        return None

    def draw_board(self):
        """วาดกระดาน"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                x = col * self.SQUARE_SIZE
                y = row * self.SQUARE_SIZE

                # เลือกสีช่อง
                if self.board.is_dark_square(row, col):
                    color = self.DARK_BROWN
                else:
                    color = self.LIGHT_BROWN

                pygame.draw.rect(self.screen, color, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE))

                # วาดเส้นขอบ
                pygame.draw.rect(self.screen, self.BLACK, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE), 1)

                # วาดเลขช่องหรือจุดสำหรับช่องสีดำ (1-32)
                if self.board.is_dark_square(row, col):
                    if self.show_square_numbers:
                        square_num = self.board.get_square_number(row, col)
                        if square_num:
                            num_text = self.small_font.render(str(square_num), True, self.BLACK)
                            text_rect = num_text.get_rect(topleft=(x + 3, y + 3))
                            self.screen.blit(num_text, text_rect)
                    else:
                        dot_x = x + 6
                        dot_y = y + 6
                        pygame.draw.circle(self.screen, self.BLACK, (dot_x, dot_y), 3)

    def draw_pieces(self):
        """วาดตัวหมาก"""
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                piece = self.board.get_piece(row, col)
                if piece:
                    center_x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    center_y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2

                    # วงกลมตัวหมาก
                    piece_color = self.WHITE if piece.player == Player.WHITE else self.BLACK
                    border_color = self.BLACK if piece.player == Player.WHITE else self.WHITE

                    pygame.draw.circle(self.screen, piece_color, (center_x, center_y), self.PIECE_RADIUS)
                    pygame.draw.circle(self.screen, border_color, (center_x, center_y), self.PIECE_RADIUS, 3)

                    # วาดมงกุฎสำหรับ KING
                    if piece.is_king():
                        self.draw_crown(center_x, center_y, border_color)

    def draw_crown(self, x: int, y: int, color):
        """วาดมงกุฎบนตัวหมาก KING"""
        points = [
            (x - self.CROWN_SIZE, y + 5),
            (x - self.CROWN_SIZE // 2, y - 5),
            (x, y + 5),
            (x + self.CROWN_SIZE // 2, y - 5),
            (x + self.CROWN_SIZE, y + 5),
            (x + self.CROWN_SIZE, y + 8),
            (x - self.CROWN_SIZE, y + 8),
        ]
        pygame.draw.polygon(self.screen, color, points)

    def draw_selected(self):
        """วาดไฮไลท์ตัวหมากที่เลือก"""
        if self.selected_pos:
            row, col = self.selected_pos
            x = col * self.SQUARE_SIZE
            y = row * self.SQUARE_SIZE
            pygame.draw.rect(self.screen, self.YELLOW, (x, y, self.SQUARE_SIZE, self.SQUARE_SIZE), 5)

    def draw_valid_moves(self):
        """วาดจุดที่สามารถเดินได้"""
        for move in self.valid_moves:
            to_row, to_col = move.to_pos
            center_x = to_col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            center_y = to_row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2

            # ใช้สีต่างกันสำหรับการเดินและการกิน
            color = self.RED if move.is_capture() else self.GREEN

            pygame.draw.circle(self.screen, color, (center_x, center_y), 10)

    def draw_status_bar(self):
        """วาดแถบสถานะด้านล่าง"""
        pygame.draw.rect(self.screen, self.GRAY, (0, self.BOARD_WINDOW_SIZE, self.BOARD_WINDOW_SIZE, 100))

        if self.game_over:
            if self.winner:
                winner_name = "ขาว (WHITE)" if self.winner == Player.WHITE else "ดำ (BLACK)"
                text = self.font.render(f"เกมจบ! ผู้ชนะ: {winner_name}", True, self.WHITE)
            else:
                text = self.font.render("เกมจบ! เสมอ", True, self.WHITE)
        else:
            player_name = "ขาว (WHITE)" if self.current_player == Player.WHITE else "ดำ (BLACK)"
            text = self.font.render(f"ตาของผู้เล่น: {player_name}", True, self.WHITE)

        text_rect = text.get_rect(center=(self.BOARD_WINDOW_SIZE // 2, self.BOARD_WINDOW_SIZE + 30))
        self.screen.blit(text, text_rect)

        # แสดงจำนวนตัวหมาก
        white_count = self.board.count_pieces(Player.WHITE)
        black_count = self.board.count_pieces(Player.BLACK)

        count_text = self.small_font.render(
            f"ขาว: {white_count}  |  ดำ: {black_count}",
            True, self.WHITE
        )
        count_rect = count_text.get_rect(center=(self.BOARD_WINDOW_SIZE // 2, self.BOARD_WINDOW_SIZE + 70))
        self.screen.blit(count_text, count_rect)

    def draw_log_panel(self):
        """วาดแผง log ด้านขวา"""
        # พื้นหลัง log panel
        log_x = self.BOARD_WINDOW_SIZE
        pygame.draw.rect(self.screen, self.LIGHT_BROWN, (log_x, 0, self.LOG_PANEL_WIDTH, self.WINDOW_HEIGHT))
        pygame.draw.line(self.screen, self.BLACK, (log_x, 0), (log_x, self.WINDOW_HEIGHT), 2)

        # หัวข้อ
        title = self.small_font.render("Move Log", True, self.BLACK)
        self.screen.blit(title, (log_x + 10, 10))

        # CSV Header
        header_y = 40
        header = self.tiny_font.render("ขาว,ดำ", True, self.BLACK)
        self.screen.blit(header, (log_x + 10, header_y))

        # แสดง moves (แสดงย้อนกลับ 20 รอบล่าสุด)
        y_offset = header_y + 25
        max_display = 25
        start_idx = max(0, len(self.move_log) - max_display)

        for i in range(start_idx, len(self.move_log)):
            white_move, black_move = self.move_log[i]
            if black_move:
                move_text = f"{white_move},{black_move}"
            else:
                move_text = f"{white_move},"

            text = self.tiny_font.render(move_text, True, self.BLACK)
            self.screen.blit(text, (log_x + 10, y_offset))
            y_offset += 20

        # ถ้ามี white move ในรอบปัจจุบัน
        if self.current_round_white_move:
            move_text = f"{self.current_round_white_move},"
            text = self.tiny_font.render(move_text, True, self.BLUE)
            self.screen.blit(text, (log_x + 10, y_offset))

        # ปุ่ม Load CSV (ฟ้า)
        load_y = self.WINDOW_HEIGHT - 140
        load_rect = pygame.Rect(log_x + 10, load_y, self.LOG_PANEL_WIDTH - 20, 35)
        pygame.draw.rect(self.screen, self.BLUE, load_rect)
        pygame.draw.rect(self.screen, self.BLACK, load_rect, 2)

        load_text = self.small_font.render("Load CSV", True, self.WHITE)
        load_text_rect = load_text.get_rect(center=load_rect.center)
        self.screen.blit(load_text, load_text_rect)

        self.load_button_rect = load_rect

        # ปุ่ม Undo (ส้ม)
        undo_y = self.WINDOW_HEIGHT - 95
        undo_rect = pygame.Rect(log_x + 10, undo_y, self.LOG_PANEL_WIDTH - 20, 35)
        undo_color = self.ORANGE if self.history else self.GRAY
        pygame.draw.rect(self.screen, undo_color, undo_rect)
        pygame.draw.rect(self.screen, self.BLACK, undo_rect, 2)

        undo_text = self.small_font.render("Undo (Ctrl+Z)", True, self.BLACK)
        undo_text_rect = undo_text.get_rect(center=undo_rect.center)
        self.screen.blit(undo_text, undo_text_rect)

        self.undo_button_rect = undo_rect

        # ปุ่ม Save CSV (เขียว)
        button_y = self.WINDOW_HEIGHT - 50
        button_rect = pygame.Rect(log_x + 10, button_y, self.LOG_PANEL_WIDTH - 20, 35)
        pygame.draw.rect(self.screen, self.GREEN, button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)

        save_text = self.small_font.render("Save CSV", True, self.BLACK)
        save_rect = save_text.get_rect(center=button_rect.center)
        self.screen.blit(save_text, save_rect)

        self.save_button_rect = button_rect

    def draw(self):
        """วาดทุกอย่างบนหน้าจอ"""
        self.screen.fill(self.WHITE)
        self.draw_board()
        self.draw_selected()
        self.draw_valid_moves()
        self.draw_pieces()
        self.draw_status_bar()
        self.draw_log_panel()
        pygame.display.flip()

    def save_csv(self):
        """บันทึก move log เป็นไฟล์ CSV"""
        from datetime import datetime

        filename = f"thaichecker_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ขาว', 'ดำ'])

            for white_move, black_move in self.move_log:
                writer.writerow([white_move, black_move if black_move else ''])

            # ถ้ามี white move ในรอบปัจจุบัน
            if self.current_round_white_move:
                writer.writerow([self.current_round_white_move, ''])

        print(f"บันทึก move log ไปที่: {filename}")

    def _save_state(self):
        """บันทึก snapshot ของสถานะเกมปัจจุบันลง history stack"""
        self.history.append({
            'board': copy.deepcopy(self.board),
            'current_player': self.current_player,
            'move_log': list(self.move_log),
            'current_round_white_move': self.current_round_white_move,
            'game_over': self.game_over,
            'winner': self.winner,
        })

    def undo(self):
        """ย้อนกลับ 1 ตา โดย pop snapshot จาก history stack"""
        if not self.history:
            return
        state = self.history.pop()
        self.board = state['board']
        self.current_player = state['current_player']
        self.move_log = state['move_log']
        self.current_round_white_move = state['current_round_white_move']
        self.game_over = state['game_over']
        self.winner = state['winner']
        self.selected_pos = None
        self.valid_moves = []

    def _square_num_to_pos(self, num: int) -> Tuple[int, int]:
        """แปลงเลขช่อง 1-32 เป็น (row, col)"""
        row = (num - 1) // 4
        pos_in_row = (num - 1) % 4
        if row % 2 == 0:
            col = pos_in_row * 2 + 1
        else:
            col = pos_in_row * 2
        return (row, col)

    def load_csv(self):
        """โหลดไฟล์ CSV แล้ว replay ตาเดินบนกระดานใหม่"""
        import subprocess
        import platform

        # ใช้ native file dialog ของ macOS เพื่อให้ focus ถูกต้อง
        if platform.system() == 'Darwin':
            result = subprocess.run(
                ['osascript', '-e',
                 'POSIX path of (choose file of type {"csv","CSV"} '
                 'with prompt "เลือกไฟล์ CSV")'],
                capture_output=True, text=True
            )
            filepath = result.stdout.strip()
        else:
            result = subprocess.run(
                [sys.executable, "-c",
                 "import tkinter as tk; from tkinter import filedialog; "
                 "root = tk.Tk(); root.withdraw(); "
                 "path = filedialog.askopenfilename("
                 "title='เลือกไฟล์ CSV', "
                 "filetypes=[('CSV files', '*.csv'), ('All files', '*.*')]); "
                 "print(path); root.destroy()"],
                capture_output=True, text=True
            )
            filepath = result.stdout.strip()

        if not filepath:
            return

        # อ่าน CSV
        moves = []
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # ข้าม header
            for row in reader:
                if len(row) >= 1 and row[0].strip():
                    moves.append(row[0].strip())
                if len(row) >= 2 and row[1].strip():
                    moves.append(row[1].strip())

        # Reset กระดานเป็นสถานะเริ่มต้น
        self.board = Board()
        self.current_player = Player.WHITE
        self.selected_pos = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None
        self.move_log = []
        self.current_round_white_move = None
        self.history = []

        # Replay แต่ละ move
        for notation in moves:
            parts = notation.split('-')
            if len(parts) != 2:
                print(f"Error: รูปแบบ move ไม่ถูกต้อง: {notation}")
                break

            try:
                from_num = int(parts[0])
                to_num = int(parts[1])
            except ValueError:
                print(f"Error: ไม่สามารถแปลงเลขช่อง: {notation}")
                break

            from_pos = self._square_num_to_pos(from_num)
            to_pos = self._square_num_to_pos(to_num)

            # หา matching move จาก valid moves
            all_moves = GameLogic.get_all_valid_moves(self.board, self.current_player)
            matched_move = None
            for m in all_moves:
                if m.from_pos == from_pos and m.to_pos == to_pos:
                    matched_move = m
                    break

            if not matched_move:
                print(f"Error: move ไม่ถูกต้อง: {notation} (ผู้เล่น: {self.current_player.value})")
                break

            # บันทึก move ลง log
            if self.current_player == Player.WHITE:
                self.current_round_white_move = notation
            else:
                self.move_log.append((self.current_round_white_move, notation))
                self.current_round_white_move = None

            # ดำเนินการ move
            GameLogic.execute_move(self.board, matched_move)

            # สลับผู้เล่น
            self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE

        # เช็คเกมจบ
        game_over, winner = GameLogic.is_game_over(self.board)
        if game_over:
            self.game_over = True
            self.winner = winner

        print(f"โหลด CSV สำเร็จ: {len(moves)} ตา จากไฟล์ {filepath}")

    def handle_click(self, pos: Tuple[int, int]):
        """จัดการการคลิกเมาส์"""
        # เช็คคลิกปุ่ม Undo
        if hasattr(self, 'undo_button_rect') and self.undo_button_rect.collidepoint(pos):
            self.undo()
            return

        # เช็คคลิกปุ่ม Load CSV
        if hasattr(self, 'load_button_rect') and self.load_button_rect.collidepoint(pos):
            self.load_csv()
            return

        # เช็คคลิกปุ่ม Save CSV
        if hasattr(self, 'save_button_rect') and self.save_button_rect.collidepoint(pos):
            self.save_csv()
            return

        if self.game_over:
            return

        # ไม่ให้คลิกตอนตา AI
        if self.current_player == self.ai_player:
            return

        square = self.get_square_from_mouse(pos)
        if square is None:
            return

        row, col = square

        # ถ้ายังไม่ได้เลือกตัวหมาก
        if self.selected_pos is None:
            piece = self.board.get_piece(row, col)

            # เช็คว่าเป็นตัวหมากของผู้เล่นปัจจุบันหรือไม่
            if piece and piece.player == self.current_player:
                moves = GameLogic.get_valid_moves(self.board, row, col)

                # เช็คว่าต้องกินหรือไม่
                all_moves = GameLogic.get_all_valid_moves(self.board, self.current_player)
                must_capture = any(m.is_capture() for m in all_moves)

                if must_capture:
                    capture_moves = [m for m in moves if m.is_capture()]
                    if not capture_moves:
                        return  # ต้องเลือกตัวที่กินได้
                    moves = capture_moves

                if moves:
                    self.selected_pos = (row, col)
                    self.valid_moves = moves

        # ถ้าเลือกตัวหมากแล้ว
        else:
            # คลิกที่เดิม = ยกเลิกการเลือก
            if (row, col) == self.selected_pos:
                self.selected_pos = None
                self.valid_moves = []
                return

            # คลิกที่ valid move
            selected_move = None
            for move in self.valid_moves:
                if move.to_pos == (row, col):
                    selected_move = move
                    break

            if selected_move:
                # บันทึก state ก่อนเดิน (สำหรับ undo)
                self._save_state()

                # บันทึก move ลง log
                from_row, from_col = selected_move.from_pos
                to_row, to_col = selected_move.to_pos
                from_num = self.board.get_square_number(from_row, from_col)
                to_num = self.board.get_square_number(to_row, to_col)
                move_notation = f"{from_num}-{to_num}"

                # เช็คว่าเป็นการเดินของใคร
                if self.current_player == Player.WHITE:
                    # WHITE เดิน - เก็บไว้ก่อน
                    self.current_round_white_move = move_notation
                else:
                    # BLACK เดิน - บันทึกทั้งรอบ
                    self.move_log.append((self.current_round_white_move, move_notation))
                    self.current_round_white_move = None

                # ดำเนินการ move
                GameLogic.execute_move(self.board, selected_move)

                # สลับผู้เล่น
                self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE

                # เช็คเกมจบ (หลังจากสลับผู้เล่นแล้ว)
                game_over, winner = GameLogic.is_game_over(self.board)
                if game_over:
                    self.game_over = True
                    self.winner = winner

                # ล้างการเลือก
                self.selected_pos = None
                self.valid_moves = []

            else:
                # คลิกที่ตัวหมากอื่นของตัวเอง
                piece = self.board.get_piece(row, col)
                if piece and piece.player == self.current_player:
                    self.selected_pos = None
                    self.valid_moves = []
                    self.handle_click(pos)  # เลือกใหม่

    def play_ai_turn(self):
        """ให้ AI เดินอัตโนมัติเมื่อถึงตา AI"""
        if self.game_over or self.current_player != self.ai_player:
            return

        move = get_best_move(self.board, self.ai_player, self.ai_depth)
        if move is None:
            return

        # บันทึก state ก่อนเดิน (สำหรับ undo)
        self._save_state()

        # บันทึก move ลง log
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos
        from_num = self.board.get_square_number(from_row, from_col)
        to_num = self.board.get_square_number(to_row, to_col)
        move_notation = f"{from_num}-{to_num}"

        if self.current_player == Player.WHITE:
            self.current_round_white_move = move_notation
        else:
            self.move_log.append((self.current_round_white_move, move_notation))
            self.current_round_white_move = None

        # ดำเนินการ move
        GameLogic.execute_move(self.board, move)

        # สลับผู้เล่น
        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE

        # เช็คเกมจบ
        game_over, winner = GameLogic.is_game_over(self.board)
        if game_over:
            self.game_over = True
            self.winner = winner

        # ล้างการเลือก
        self.selected_pos = None
        self.valid_moves = []

    def run(self):
        """เริ่มเกม"""
        running = True

        while running:
            self.clock.tick(60)  # 60 FPS

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_n:
                        self.show_square_numbers = not self.show_square_numbers
                    elif event.key == pygame.K_z and (event.mod & pygame.KMOD_CTRL or event.mod & pygame.KMOD_META):
                        self.undo()

            # ให้ AI เดินอัตโนมัติเมื่อถึงตา
            if not self.game_over and self.current_player == self.ai_player:
                self.draw()  # วาดก่อนให้เห็นสถานะ
                pygame.event.pump()  # ให้ Pygame ไม่ค้าง
                self.play_ai_turn()

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GUI()
    game.run()
