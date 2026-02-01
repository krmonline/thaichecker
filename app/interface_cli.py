"""
interface_cli.py - Interface แบบ Command Line สำหรับเกม Thaichecker
"""

from board import Board, Player
from game_logic import GameLogic, Move
from ai_minimax import get_best_move
from typing import Optional


class CLI:
    """คลาสจัดการ UI แบบ command line"""

    def __init__(self):
        self.board = Board()
        self.current_player = Player.WHITE
        self.game_over = False
        self.winner = None

        # AI settings
        self.ai_enabled = True
        self.ai_player = Player.BLACK
        self.ai_depth = 6

        # แสดงเลขช่อง 1-32
        self.show_square_numbers = True

    def display_board(self):
        """แสดงกระดาน"""
        print("\n" + "=" * 40)
        print(self.board.to_string(self.show_square_numbers))
        print("=" * 40)

    def display_current_player(self):
        """แสดงผู้เล่นปัจจุบัน"""
        player_name = "ขาว (WHITE)" if self.current_player == Player.WHITE else "ดำ (BLACK)"
        print(f"\nตาของผู้เล่น: {player_name}")

    def _square_num_to_pos(self, num: int) -> tuple:
        """แปลงเลขช่อง 1-32 เป็น (row, col)"""
        row = (num - 1) // 4
        pos_in_row = (num - 1) % 4
        if row % 2 == 0:
            col = pos_in_row * 2 + 1
        else:
            col = pos_in_row * 2
        return (row, col)

    def get_position_input(self, prompt: str) -> Optional[tuple]:
        """รับ input เลขช่อง 1-32"""
        try:
            user_input = input(prompt).strip()
            if user_input.lower() in ['q', 'quit', 'exit']:
                return None

            if user_input.lower() == 'n':
                self.show_square_numbers = not self.show_square_numbers
                label = "ตัวเลข" if self.show_square_numbers else "จุด"
                print(f"เลขช่อง: {label}")
                self.display_board()
                return self.get_position_input(prompt)

            num = int(user_input)
            if not 1 <= num <= 32:
                print("เลขช่องไม่ถูกต้อง! ต้องอยู่ระหว่าง 1-32")
                return self.get_position_input(prompt)

            return self._square_num_to_pos(num)

        except ValueError:
            print("กรุณาใส่เลขช่อง 1-32!")
            return self.get_position_input(prompt)

    def select_piece(self) -> Optional[tuple]:
        """เลือกตัวหมากที่จะเดิน"""
        while True:
            pos = self.get_position_input("เลือกตัวหมาก (เลขช่อง 1-32) หรือ 'q' ออก: ")

            if pos is None:
                return None

            row, col = pos
            piece = self.board.get_piece(row, col)

            if piece is None:
                print("ไม่มีตัวหมากที่ตำแหน่งนี้!")
                continue

            if piece.player != self.current_player:
                print("นี่ไม่ใช่ตัวหมากของคุณ!")
                continue

            moves = GameLogic.get_valid_moves(self.board, row, col)

            # เช็คว่าต้องกินหรือไม่
            all_moves = GameLogic.get_all_valid_moves(self.board, self.current_player)
            must_capture = any(m.is_capture() for m in all_moves)

            if must_capture:
                capture_moves = [m for m in moves if m.is_capture()]
                if not capture_moves:
                    print("คุณต้องเลือกตัวหมากที่สามารถกินได้!")
                    continue
                moves = capture_moves

            if not moves:
                print("ตัวหมากนี้ไม่มีการเดินที่ถูกต้อง!")
                continue

            return (row, col), moves

    def display_moves(self, moves: list):
        """แสดง moves ที่เป็นไปได้"""
        print("\nการเดินที่เป็นไปได้:")
        for i, move in enumerate(moves, 1):
            to_num = self.board.get_square_number(*move.to_pos)
            move_type = "กิน" if move.is_capture() else "เดิน"
            if move.is_capture():
                cap_nums = [self.board.get_square_number(r, c) for r, c in move.captured_pieces]
                captures = f" (กิน: {cap_nums})"
            else:
                captures = ""
            print(f"  {i}. {move_type} ไปช่อง {to_num}{captures}")

    def select_move(self, moves: list) -> Optional[Move]:
        """เลือก move จาก list"""
        self.display_moves(moves)

        while True:
            try:
                choice = input("\nเลือกการเดิน (ใส่หหมายเลข) หรือพิมพ์ 'b' เพื่อกลับ: ").strip()

                if choice.lower() in ['b', 'back']:
                    return None

                choice_num = int(choice)
                if 1 <= choice_num <= len(moves):
                    return moves[choice_num - 1]
                else:
                    print(f"กรุณาเลือก 1-{len(moves)}")

            except ValueError:
                print("กรุณาใส่ตัวเลข!")

    def play_ai_turn(self):
        """ให้ AI เดินอัตโนมัติ"""
        self.display_board()
        print("\nAI (ดำ) กำลังคิด...")

        move = get_best_move(self.board, self.ai_player, self.ai_depth)
        if move is None:
            return

        from_num = self.board.get_square_number(*move.from_pos)
        to_num = self.board.get_square_number(*move.to_pos)
        move_type = "กิน" if move.is_capture() else "เดิน"
        captures = f" (กิน: {move.captured_pieces})" if move.is_capture() else ""
        print(f"AI เดิน: {move_type} {from_num} -> {to_num}{captures}")

        GameLogic.execute_move(self.board, move)

        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE

        game_over, winner = GameLogic.is_game_over(self.board)
        if game_over:
            self.game_over = True
            self.winner = winner

    def play_turn(self):
        """เล่นหนึ่งตา"""
        # ถ้าเป็นตา AI ให้เดินอัตโนมัติ
        if self.ai_enabled and self.current_player == self.ai_player:
            self.play_ai_turn()
            return True

        self.display_board()
        self.display_current_player()

        # เลือกตัวหมาก
        result = self.select_piece()
        if result is None:
            return False  # ผู้เล่นต้องการออก

        (row, col), moves = result

        # เลือก move
        selected_move = self.select_move(moves)
        if selected_move is None:
            return self.play_turn()  # กลับไปเลือกใหม่

        # ดำเนินการ move
        GameLogic.execute_move(self.board, selected_move)

        # สลับผู้เล่น
        self.current_player = Player.BLACK if self.current_player == Player.WHITE else Player.WHITE

        # เช็คเกมจบ (หลังจากสลับผู้เล่นแล้ว)
        game_over, winner = GameLogic.is_game_over(self.board)
        if game_over:
            self.game_over = True
            self.winner = winner

        return True

    def display_winner(self):
        """แสดงผู้ชนะ"""
        self.display_board()
        print("\n" + "=" * 40)
        if self.winner:
            winner_name = "ขาว (WHITE)" if self.winner == Player.WHITE else "ดำ (BLACK)"
            print(f"เกมจบ! ผู้ชนะคือ: {winner_name}")
        else:
            print("เกมจบ! เสมอ")
        print("=" * 40)

    def select_game_mode(self):
        """เลือกโหมดเกม"""
        print("\nเลือกโหมดเกม:")
        print("  1. เล่นกับ AI (คุณเป็นขาว, AI เป็นดำ)")
        print("  2. เล่น 2 คน (ผลัดกันเดิน)")
        while True:
            choice = input("เลือก (1/2): ").strip()
            if choice == '1':
                self.ai_enabled = True
                print("โหมด: เล่นกับ AI")
                return
            elif choice == '2':
                self.ai_enabled = False
                print("โหมด: เล่น 2 คน")
                return
            else:
                print("กรุณาเลือก 1 หรือ 2")

    def run(self):
        """เริ่มเกม"""
        print("=" * 40)
        print("ยินดีต้อนรับสู่เกม Thaichecker!")
        print("=" * 40)
        self.select_game_mode()
        print("-" * 40)
        print("วิธีเล่น:")
        print("  - ใส่เลขช่อง 1-32 เพื่อเลือกตัวหมาก (เช่น: 25)")
        print("  - กติกา: MAN เดินหน้า 1 ช่อง, KING เดินได้ไกล")
        print("  - การกินเป็นบังคับ!")
        print("  - พิมพ์ 'n' เพื่อ show/hide เลขช่อง")
        print("  - พิมพ์ 'q' เพื่อออกจากเกม")
        print("=" * 40)

        while not self.game_over:
            if not self.play_turn():
                print("\nออกจากเกม...")
                return

        self.display_winner()


if __name__ == "__main__":
    game = CLI()
    game.run()
