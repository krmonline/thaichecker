"""
interface_gui.py - Interface แบบ GUI (Pygame) สำหรับเกม Thaichecker
"""

import pygame
import sys
from board import Board, Player, PieceType
from game_logic import GameLogic, Move
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

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.tiny_font = pygame.font.Font(None, 18)

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

                # วาดเลขช่องสำหรับช่องสีดำ (1-32)
                if self.board.is_dark_square(row, col):
                    square_num = self.board.get_square_number(row, col)
                    if square_num:
                        num_text = self.small_font.render(str(square_num), True, self.BLACK)
                        text_rect = num_text.get_rect(topleft=(x + 3, y + 3))
                        self.screen.blit(num_text, text_rect)

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

        # ปุ่ม Save CSV
        button_y = self.WINDOW_HEIGHT - 50
        button_rect = pygame.Rect(log_x + 10, button_y, self.LOG_PANEL_WIDTH - 20, 35)
        pygame.draw.rect(self.screen, self.GREEN, button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)

        save_text = self.small_font.render("Save CSV", True, self.BLACK)
        save_rect = save_text.get_rect(center=button_rect.center)
        self.screen.blit(save_text, save_rect)

        # เก็บ button rect สำหรับ click detection
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
        import csv
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

    def handle_click(self, pos: Tuple[int, int]):
        """จัดการการคลิกเมาส์"""
        # เช็คคลิกปุ่ม Save CSV
        if hasattr(self, 'save_button_rect') and self.save_button_rect.collidepoint(pos):
            self.save_csv()
            return

        if self.game_over:
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

            self.draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = GUI()
    game.run()
