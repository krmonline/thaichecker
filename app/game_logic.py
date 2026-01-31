"""
game_logic.py - กติกาการเดินและการกินสำหรับเกม Thaichecker
"""

from typing import List, Tuple, Optional
from board import Board, Piece, PieceType, Player


class Move:
    """คลาสแทนการเดินหนึ่งครั้ง"""

    def __init__(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int],
                 captured_pieces: List[Tuple[int, int]] = None):
        self.from_pos = from_pos  # (row, col)
        self.to_pos = to_pos  # (row, col)
        self.captured_pieces = captured_pieces if captured_pieces else []

    def is_capture(self) -> bool:
        """เช็คว่าเป็นการกินหรือไม่"""
        return len(self.captured_pieces) > 0

    def __repr__(self):
        return f"Move({self.from_pos} -> {self.to_pos}, captures={self.captured_pieces})"


class GameLogic:
    """คลาสจัดการกติกาเกม Thaichecker"""

    @staticmethod
    def get_all_valid_moves(board: Board, player: Player) -> List[Move]:
        """ดึง moves ที่เป็นไปได้ทั้งหมดของผู้เล่น"""
        all_moves = []
        pieces = board.get_all_pieces(player)

        for row, col, piece in pieces:
            moves = GameLogic.get_valid_moves(board, row, col)
            all_moves.extend(moves)

        # ถ้ามีการกินได้ ต้องกินเท่านั้น (บังคับ)
        capture_moves = [m for m in all_moves if m.is_capture()]
        if capture_moves:
            return capture_moves

        return all_moves

    @staticmethod
    def get_valid_moves(board: Board, row: int, col: int) -> List[Move]:
        """ดึง moves ที่เป็นไปได้ทั้งหมดจากตำแหน่งที่กำหนด"""
        piece = board.get_piece(row, col)
        if not piece:
            return []

        if piece.is_king():
            return GameLogic._get_king_moves(board, row, col, piece)
        else:
            return GameLogic._get_man_moves(board, row, col, piece)

    @staticmethod
    def _get_man_moves(board: Board, row: int, col: int, piece: Piece) -> List[Move]:
        """ดึง moves สำหรับ MAN"""
        moves = []

        # ทิศทางการเดิน (เฉียง)
        # WHITE เดินขึ้น (row ลด), BLACK เดินลง (row เพิ่ม)
        direction = -1 if piece.player == Player.WHITE else 1

        # เช็คการกินก่อน (capture moves)
        capture_moves = GameLogic._get_man_capture_moves(board, row, col, piece, direction)
        if capture_moves:
            return capture_moves

        # ถ้าไม่มีการกิน เช็คการเดินปกติ
        for dc in [-1, 1]:  # ซ้ายและขวา
            new_row = row + direction
            new_col = col + dc

            if board.is_valid_position(new_row, new_col):
                target = board.get_piece(new_row, new_col)
                if target is None:  # ช่องว่าง
                    moves.append(Move((row, col), (new_row, new_col)))

        return moves

    @staticmethod
    def _get_man_capture_moves(board: Board, row: int, col: int, piece: Piece,
                                direction: int, captured_so_far: List[Tuple[int, int]] = None,
                                original_pos: Tuple[int, int] = None) -> List[Move]:
        """ดึง capture moves สำหรับ MAN (รองรับ multi-jump)"""
        if captured_so_far is None:
            captured_so_far = []

        # เก็บตำแหน่งเริ่มต้น
        if original_pos is None:
            original_pos = (row, col)

        moves = []

        # MAN กินได้เฉพาะไปข้างหน้า (ตาม direction) แต่กินได้ทั้งซ้ายและขวา
        for dc in [-1, 1]:  # ซ้ายและขวา
            dr = direction  # ใช้เฉพาะทิศทางหน้า (ไม่ย้อนกลับหลัง)

            enemy_row = row + dr
            enemy_col = col + dc
            land_row = row + 2 * dr
            land_col = col + 2 * dc

            if not board.is_valid_position(enemy_row, enemy_col):
                continue
            if not board.is_valid_position(land_row, land_col):
                continue

            enemy = board.get_piece(enemy_row, enemy_col)
            land = board.get_piece(land_row, land_col)

            # เช็คว่ากินได้หรือไม่
            if (enemy and enemy.player != piece.player and
                    land is None and
                    (enemy_row, enemy_col) not in captured_so_far):

                # ทำการกินชั่วคราว
                new_captured = captured_so_far + [(enemy_row, enemy_col)]

                # เช็ค multi-jump
                next_captures = GameLogic._get_man_capture_moves(
                    board, land_row, land_col, piece, direction, new_captured, original_pos
                )

                if next_captures:
                    # มี multi-jump ต่อ - ใช้ moves จาก recursive call
                    for next_move in next_captures:
                        moves.append(next_move)
                else:
                    # ไม่มี multi-jump ต่อ - สร้าง Move จากตำแหน่งเริ่มต้นไปตำแหน่งสุดท้าย
                    moves.append(Move(original_pos, (land_row, land_col), new_captured))

        return moves

    @staticmethod
    def _get_king_moves(board: Board, row: int, col: int, piece: Piece) -> List[Move]:
        """ดึง moves สำหรับ KING (flying king)"""
        moves = []

        # เช็คการกินก่อน
        capture_moves = GameLogic._get_king_capture_moves(board, row, col, piece)
        if capture_moves:
            return capture_moves

        # ถ้าไม่มีการกิน เดินได้ไกลในแนวทแยง
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                for distance in range(1, board.size):
                    new_row = row + dr * distance
                    new_col = col + dc * distance

                    if not board.is_valid_position(new_row, new_col):
                        break

                    target = board.get_piece(new_row, new_col)
                    if target is None:
                        moves.append(Move((row, col), (new_row, new_col)))
                    else:
                        break  # ถ้าเจอตัวหมาก หยุด

        return moves

    @staticmethod
    def _get_king_capture_moves(board: Board, row: int, col: int, piece: Piece,
                                 captured_so_far: List[Tuple[int, int]] = None,
                                 original_pos: Tuple[int, int] = None) -> List[Move]:
        """ดึง capture moves สำหรับ KING (flying king with multi-capture)"""
        if captured_so_far is None:
            captured_so_far = []

        # เก็บตำแหน่งเริ่มต้น
        if original_pos is None:
            original_pos = (row, col)

        moves = []

        # ลองทั้ง 4 ทิศทางแนวทแยง
        for dr in [-1, 1]:
            for dc in [-1, 1]:
                enemy_pos = None
                enemy_distance = 0

                # หาศัตรูในแนวทแยงนี้
                for distance in range(1, board.size):
                    check_row = row + dr * distance
                    check_col = col + dc * distance

                    if not board.is_valid_position(check_row, check_col):
                        break

                    target = board.get_piece(check_row, check_col)

                    if target:
                        if target.player != piece.player and (check_row, check_col) not in captured_so_far:
                            # เจอศัตรูที่ยังไม่ได้กิน
                            enemy_pos = (check_row, check_col)
                            enemy_distance = distance
                            break
                        elif (check_row, check_col) in captured_so_far:
                            # เจอตัวที่กินไปแล้ว - ข้ามไปมองต่อ
                            continue
                        else:
                            # เจอตัวเอง - หยุด
                            break

                # ถ้าเจอศัตรู ลงจอดที่ช่องถัดจากศัตรูทันที (ไม่ใช่ทุกช่อง)
                if enemy_pos:
                    land_distance = enemy_distance + 1
                    land_row = row + dr * land_distance
                    land_col = col + dc * land_distance

                    if board.is_valid_position(land_row, land_col):
                        land = board.get_piece(land_row, land_col)

                        if land is None:
                            # ลงจอดได้
                            new_captured = captured_so_far + [enemy_pos]

                            # เช็ค multi-capture
                            next_captures = GameLogic._get_king_capture_moves(
                                board, land_row, land_col, piece, new_captured, original_pos
                            )

                            if next_captures:
                                # มี multi-capture ต่อ - ใช้ moves จาก recursive call
                                for next_move in next_captures:
                                    moves.append(next_move)
                            else:
                                # ไม่มี multi-capture ต่อ - สร้าง Move จากตำแหน่งเริ่มต้นไปตำแหน่งสุดท้าย
                                moves.append(Move(original_pos, (land_row, land_col), new_captured))

        return moves

    @staticmethod
    def execute_move(board: Board, move: Move) -> bool:
        """ดำเนินการ move บนกระดาน"""
        from_row, from_col = move.from_pos
        to_row, to_col = move.to_pos

        # ย้ายตัวหมาก
        board.move_piece(from_row, from_col, to_row, to_col)

        # ลบตัวที่ถูกกิน
        for captured_row, captured_col in move.captured_pieces:
            board.remove_piece(captured_row, captured_col)

        return True

    @staticmethod
    def is_game_over(board: Board) -> Tuple[bool, Optional[Player]]:
        """เช็คว่าเกมจบหรือไม่ และใครชนะ"""
        white_pieces = board.count_pieces(Player.WHITE)
        black_pieces = board.count_pieces(Player.BLACK)

        if white_pieces == 0:
            return True, Player.BLACK
        elif black_pieces == 0:
            return True, Player.WHITE

        # เช็คว่ามีการเดินได้หรือไม่
        white_moves = GameLogic.get_all_valid_moves(board, Player.WHITE)
        black_moves = GameLogic.get_all_valid_moves(board, Player.BLACK)

        if not white_moves:
            return True, Player.BLACK
        elif not black_moves:
            return True, Player.WHITE

        return False, None
