"""
ai_minimax.py - AI สำหรับเกม Thaichecker ใช้ Minimax + Alpha-Beta Pruning
"""

import copy
import math
from board import Board, Player, PieceType
from game_logic import GameLogic, Move


def evaluate(board: Board, ai_player: Player) -> float:
    """ประเมินคะแนนของ board state สำหรับ ai_player

    MAN = 1 คะแนน, KING = 3 คะแนน
    MAN ที่ใกล้เลื่อนขั้น (advance bonus) +0.5 ต่อแถวที่รุกได้
    mobility bonus เล็กน้อย
    คะแนน = ของเรา - ของคู่ต่อสู้
    """
    opponent = Player.BLACK if ai_player == Player.WHITE else Player.WHITE

    ai_score = 0.0
    opp_score = 0.0

    # คำนวณคะแนนตัวหมาก + advance bonus
    for row, col, piece in board.get_all_pieces(ai_player):
        if piece.is_king():
            ai_score += 3.0
        else:
            ai_score += 1.0
            # advance bonus: ยิ่งใกล้ฝั่งตรงข้ามยิ่งได้คะแนนเพิ่ม
            if ai_player == Player.WHITE:
                # WHITE เดินขึ้น row 0 คือเป้าหมาย
                advanced_rows = 7 - row  # row 6-7 เริ่มต้น, row 0 คือเป้าหมาย
            else:
                # BLACK เดินลง row 7 คือเป้าหมาย
                advanced_rows = row  # row 0-1 เริ่มต้น, row 7 คือเป้าหมาย
            ai_score += advanced_rows * 0.5

    for row, col, piece in board.get_all_pieces(opponent):
        if piece.is_king():
            opp_score += 3.0
        else:
            opp_score += 1.0
            if opponent == Player.WHITE:
                advanced_rows = 7 - row
            else:
                advanced_rows = row
            opp_score += advanced_rows * 0.5

    # mobility bonus
    ai_moves = len(GameLogic.get_all_valid_moves(board, ai_player))
    opp_moves = len(GameLogic.get_all_valid_moves(board, opponent))
    mobility = (ai_moves - opp_moves) * 0.1

    return ai_score - opp_score + mobility


def minimax(board: Board, depth: int, alpha: float, beta: float,
            maximizing: bool, ai_player: Player) -> float:
    """Minimax พร้อม Alpha-Beta Pruning

    maximizing=True  → ตา AI (ต้องการคะแนนสูงสุด)
    maximizing=False → ตาคู่ต่อสู้ (ต้องการคะแนนต่ำสุด)
    """
    opponent = Player.BLACK if ai_player == Player.WHITE else Player.WHITE
    current_player = ai_player if maximizing else opponent

    # Base case: ถึง depth หรือเกมจบ
    game_over, winner = GameLogic.is_game_over(board)
    if game_over:
        if winner == ai_player:
            return 1000.0 + depth  # ชนะเร็วยิ่งดี
        elif winner == opponent:
            return -1000.0 - depth  # แพ้ช้ายิ่งดี
        else:
            return 0.0  # เสมอ

    if depth == 0:
        return evaluate(board, ai_player)

    moves = GameLogic.get_all_valid_moves(board, current_player)
    if not moves:
        return evaluate(board, ai_player)

    if maximizing:
        max_eval = -math.inf
        for move in moves:
            child = copy.deepcopy(board)
            GameLogic.execute_move(child, move)
            val = minimax(child, depth - 1, alpha, beta, False, ai_player)
            max_eval = max(max_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in moves:
            child = copy.deepcopy(board)
            GameLogic.execute_move(child, move)
            val = minimax(child, depth - 1, alpha, beta, True, ai_player)
            min_eval = min(min_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_eval


def get_best_move(board: Board, player: Player, depth: int = 6) -> Move:
    """หา move ที่ดีที่สุดสำหรับ player ด้วย minimax

    Returns:
        Move ที่ดีที่สุด หรือ None ถ้าไม่มี move ให้เดิน
    """
    moves = GameLogic.get_all_valid_moves(board, player)
    if not moves:
        return None

    # ถ้ามี move เดียว ไม่ต้องคำนวณ
    if len(moves) == 1:
        return moves[0]

    best_move = None
    best_val = -math.inf

    for move in moves:
        child = copy.deepcopy(board)
        GameLogic.execute_move(child, move)
        val = minimax(child, depth - 1, -math.inf, math.inf, False, player)
        if val > best_val:
            best_val = val
            best_move = move

    return best_move
