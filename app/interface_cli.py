"""
interface_cli.py - Interface แบบ Command Line สำหรับเกม Thaichecker
"""

from board import Board, Player
from game_logic import GameLogic, Move
from typing import Optional


class CLI:
    """คลาสจัดการ UI แบบ command line"""

    def __init__(self):
        self.board = Board()
        self.current_player = Player.WHITE
        self.game_over = False
        self.winner = None

    def display_board(self):
        """แสดงกระดาน"""
        print("\n" + "=" * 40)
        print(self.board)
        print("=" * 40)

    def display_current_player(self):
        """แสดงผู้เล่นปัจจุบัน"""
        player_name = "ขาว (WHITE)" if self.current_player == Player.WHITE else "ดำ (BLACK)"
        print(f"\nตาของผู้เล่น: {player_name}")

    def get_position_input(self, prompt: str) -> Optional[tuple]:
        """รับ input ตำแหน่ง (row, col)"""
        try:
            user_input = input(prompt).strip()
            if user_input.lower() in ['q', 'quit', 'exit']:
                return None

            parts = user_input.replace(',', ' ').split()
            if len(parts) != 2:
                print("รูปแบบไม่ถูกต้อง! กรุณาใส่ row col (เช่น: 5 2)")
                return self.get_position_input(prompt)

            row, col = int(parts[0]), int(parts[1])

            if not self.board.is_valid_position(row, col):
                print("ตำแหน่งไม่ถูกต้อง! ต้องอยู่ระหว่าง 0-7")
                return self.get_position_input(prompt)

            return (row, col)

        except ValueError:
            print("กรุณาใส่ตัวเลขเท่านั้น!")
            return self.get_position_input(prompt)

    def select_piece(self) -> Optional[tuple]:
        """เลือกตัวหมากที่จะเดิน"""
        while True:
            pos = self.get_position_input("เลือกตัวหมากที่จะเดิน (row col) หรือพิมพ์ 'q' เพื่อออก: ")

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
            to_row, to_col = move.to_pos
            move_type = "กิน" if move.is_capture() else "เดิน"
            captures = f" (กิน: {move.captured_pieces})" if move.is_capture() else ""
            print(f"  {i}. {move_type} ไป ({to_row}, {to_col}){captures}")

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

    def play_turn(self):
        """เล่นหนึ่งตา"""
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

    def run(self):
        """เริ่มเกม"""
        print("=" * 40)
        print("ยินดีต้อนรับสู่เกม Thaichecker!")
        print("=" * 40)
        print("วิธีเล่น:")
        print("  - เลือกตัวหมากโดยใส่ row col (เช่น: 5 2)")
        print("  - กติกา: MAN เดินหน้า 1 ช่อง, KING เดินได้ไกล")
        print("  - การกินเป็นบังคับ!")
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
