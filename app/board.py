"""
board.py - คลาสกระดานและตัวหมากสำหรับเกม Thaichecker
"""

from enum import Enum
from typing import Optional, List, Tuple


class PieceType(Enum):
    """ชนิดของตัวหมาก"""
    MAN = "MAN"    # เบี้ย
    KING = "KING"  # ฮอส


class Player(Enum):
    """ผู้เล่น"""
    WHITE = "WHITE"  # ขาว (เริ่มจากแถวล่าง)
    BLACK = "BLACK"  # ดำ (เริ่มจากแถวบน)


class Piece:
    """คลาสแทนตัวหมาก"""

    def __init__(self, player: Player, piece_type: PieceType = PieceType.MAN):
        self.player = player
        self.piece_type = piece_type

    def promote_to_king(self):
        """เลื่อนขั้นเป็น KING"""
        self.piece_type = PieceType.KING

    def is_king(self) -> bool:
        """เช็คว่าเป็น KING หรือไม่"""
        return self.piece_type == PieceType.KING

    def __repr__(self):
        if self.player == Player.WHITE:
            return "W" if self.piece_type == PieceType.MAN else "WK"
        else:
            return "B" if self.piece_type == PieceType.MAN else "BK"


class Board:
    """คลาสแทนกระดาน 8x8"""

    def __init__(self):
        self.size = 8
        self.board: List[List[Optional[Piece]]] = [[None for _ in range(8)] for _ in range(8)]
        self.setup_initial_position()

    def setup_initial_position(self):
        """จัดตัวหมากเริ่มต้น - ฝั่งละ 8 ตัว"""
        # ฝั่งดำ (แถวบน) - แถว 0-1
        for row in range(2):
            for col in range(8):
                if self.is_dark_square(row, col):
                    self.board[row][col] = Piece(Player.BLACK)

        # ฝั่งขาว (แถวล่าง) - แถว 6-7
        for row in range(6, 8):
            for col in range(8):
                if self.is_dark_square(row, col):
                    self.board[row][col] = Piece(Player.WHITE)

    def is_dark_square(self, row: int, col: int) -> bool:
        """เช็คว่าเป็นช่องสีดำหรือไม่ (เล่นได้เฉพาะช่องสีดำ)"""
        return (row + col) % 2 == 1

    def get_square_number(self, row: int, col: int) -> Optional[int]:
        """แปลง (row, col) เป็นเลขช่อง 1-32 (เฉพาะช่องสีดำ)"""
        if not self.is_dark_square(row, col):
            return None

        # นับจำนวนช่องสีดำจากแถว 0 ถึงแถวปัจจุบัน
        square_num = row * 4  # แต่ละแถวมี 4 ช่องสีดำ

        # นับช่องสีดำในแถวปัจจุบันจากซ้ายไปขวา
        dark_squares_in_row = [c for c in range(8) if self.is_dark_square(row, c)]
        square_num += dark_squares_in_row.index(col) + 1

        return square_num

    def is_valid_position(self, row: int, col: int) -> bool:
        """เช็คว่าตำแหน่งอยู่ในกระดานหรือไม่"""
        return 0 <= row < self.size and 0 <= col < self.size

    def get_piece(self, row: int, col: int) -> Optional[Piece]:
        """ดึงตัวหมากจากตำแหน่งที่กำหนด"""
        if self.is_valid_position(row, col):
            return self.board[row][col]
        return None

    def set_piece(self, row: int, col: int, piece: Optional[Piece]):
        """วางตัวหมากที่ตำแหน่งที่กำหนด"""
        if self.is_valid_position(row, col):
            self.board[row][col] = piece

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int):
        """ย้ายตัวหมากจากตำแหน่งหนึ่งไปยังอีกตำแหน่งหนึ่ง"""
        piece = self.get_piece(from_row, from_col)
        self.set_piece(to_row, to_col, piece)
        self.set_piece(from_row, from_col, None)

        # เช็คการเลื่อนขั้นเป็น KING
        if piece and not piece.is_king():
            if piece.player == Player.WHITE and to_row == 0:
                piece.promote_to_king()
            elif piece.player == Player.BLACK and to_row == 7:
                piece.promote_to_king()

    def remove_piece(self, row: int, col: int):
        """เอาตัวหมากออกจากกระดาน"""
        self.set_piece(row, col, None)

    def get_all_pieces(self, player: Player) -> List[Tuple[int, int, Piece]]:
        """ดึงตัวหมากทั้งหมดของผู้เล่น (row, col, piece)"""
        pieces = []
        for row in range(self.size):
            for col in range(self.size):
                piece = self.get_piece(row, col)
                if piece and piece.player == player:
                    pieces.append((row, col, piece))
        return pieces

    def count_pieces(self, player: Player) -> int:
        """นับจำนวนตัวหมากของผู้เล่น"""
        return len(self.get_all_pieces(player))

    def to_string(self, show_numbers: bool = True) -> str:
        """แสดงกระดานในรูปแบบข้อความ (show_numbers=False จะแสดง . แทนเลขช่อง)"""
        result = "   0  1  2  3  4  5  6  7\n"
        for row in range(self.size):
            result += f"{row} "
            for col in range(self.size):
                piece = self.get_piece(row, col)
                if piece:
                    result += f"{str(piece):>3}"
                elif self.is_dark_square(row, col):
                    if show_numbers:
                        square_num = self.get_square_number(row, col)
                        result += f"{square_num:>3}"
                    else:
                        result += "  ."
                else:
                    result += "   "
            result += "\n"
        return result

    def __repr__(self):
        """แสดงกระดานในรูปแบบข้อความ"""
        return self.to_string(show_numbers=True)
