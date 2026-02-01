"""
thai_checker_env.py - Gymnasium-style environment สำหรับ RL agent เล่นเกม Thaichecker

ใช้งาน:
    env = ThaiCheckerEnv()
    obs, info = env.reset()
    obs, reward, done, truncated, info = env.step(action_index)
"""

import numpy as np
from typing import List, Tuple, Optional

from board import Board, Piece, PieceType, Player
from game_logic import GameLogic, Move


class ThaiCheckerEnv:
    """Gymnasium-compatible environment สำหรับเกม Thaichecker"""

    # ค่าที่ใช้แทนตัวหมากใน observation array
    EMPTY = 0
    WHITE_MAN = 1
    WHITE_KING = 2
    BLACK_MAN = 3
    BLACK_KING = 4

    def __init__(self, max_actions: int = 128):
        """
        Args:
            max_actions: ขนาดสูงสุดของ action mask (ใช้สำหรับ fixed-size mask)
        """
        self.max_actions = max_actions
        self.board: Optional[Board] = None
        self.current_player: Player = Player.WHITE
        self.done: bool = True
        self._valid_moves: List[Move] = []

    def reset(self) -> Tuple[np.ndarray, dict]:
        """เริ่มเกมใหม่

        Returns:
            obs: np.ndarray shape (8, 8) dtype int8
            info: dict with "current_player"
        """
        self.board = Board()
        self.current_player = Player.WHITE
        self.done = False
        self._valid_moves = GameLogic.get_all_valid_moves(self.board, self.current_player)

        obs = self._get_obs()
        info = self._get_info()
        return obs, info

    def step(self, action_index: int) -> Tuple[np.ndarray, float, bool, bool, dict]:
        """เล่น 1 ตา

        Args:
            action_index: index ใน list จาก get_valid_actions()

        Returns:
            obs, reward, done, truncated, info
        """
        if self.done:
            raise RuntimeError("Game is over. Call reset() to start a new game.")

        if action_index < 0 or action_index >= len(self._valid_moves):
            raise ValueError(
                f"Invalid action_index {action_index}. "
                f"Valid range: 0-{len(self._valid_moves) - 1}"
            )

        move = self._valid_moves[action_index]
        acting_player = self.current_player

        # execute move (จัดการ capture + promotion ให้หมด)
        GameLogic.execute_move(self.board, move)

        # สลับผู้เล่น
        self.current_player = (
            Player.BLACK if self.current_player == Player.WHITE else Player.WHITE
        )

        # เช็คว่าเกมจบหรือไม่
        game_over, winner = GameLogic.is_game_over(self.board)

        if game_over:
            self.done = True
            self._valid_moves = []
            reward = self.compute_reward(acting_player, winner)
        else:
            self._valid_moves = GameLogic.get_all_valid_moves(
                self.board, self.current_player
            )
            reward = 0.0

        obs = self._get_obs()
        info = self._get_info()
        return obs, reward, self.done, False, info

    def get_valid_actions(self) -> List[Move]:
        """Return list ของ Move ที่เลือกได้ในตานี้"""
        return list(self._valid_moves)

    def action_masks(self) -> np.ndarray:
        """Return boolean array shape (max_actions,) สำหรับ action masking

        True ที่ index ที่เลือกได้, False ที่เลือกไม่ได้
        """
        mask = np.zeros(self.max_actions, dtype=bool)
        n = min(len(self._valid_moves), self.max_actions)
        mask[:n] = True
        return mask

    def render(self):
        """Print กระดานปัจจุบัน"""
        if self.board is None:
            print("(no game in progress)")
            return
        print(repr(self.board))
        print(f"Current player: {self.current_player.value}")
        print(f"Valid moves: {len(self._valid_moves)}")

    def compute_reward(self, acting_player: Player, winner: Optional[Player]) -> float:
        """คำนวณ reward สำหรับผู้เล่นที่เพิ่งเดิน

        Subclass สามารถ override ได้ถ้าต้องการ reward scheme อื่น

        Args:
            acting_player: ผู้เล่นที่เพิ่งเดิน
            winner: ผู้ชนะ (None ถ้าเสมอ/ยังไม่จบ)

        Returns:
            +1.0 ถ้าชนะ, -1.0 ถ้าแพ้, 0.0 ถ้าเสมอหรือยังไม่จบ
        """
        if winner is None:
            return 0.0
        return 1.0 if winner == acting_player else -1.0

    # ── internal helpers ──

    def _get_obs(self) -> np.ndarray:
        """สร้าง observation array จากกระดานปัจจุบัน"""
        obs = np.zeros((8, 8), dtype=np.int8)
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece is not None:
                    obs[row, col] = self._piece_to_int(piece)
        return obs

    def _get_info(self) -> dict:
        """สร้าง info dict"""
        return {
            "current_player": self.current_player.value,
            "num_valid_moves": len(self._valid_moves),
        }

    @staticmethod
    def _piece_to_int(piece: Piece) -> int:
        """แปลง Piece เป็น int สำหรับ observation"""
        if piece.player == Player.WHITE:
            return ThaiCheckerEnv.WHITE_KING if piece.is_king() else ThaiCheckerEnv.WHITE_MAN
        else:
            return ThaiCheckerEnv.BLACK_KING if piece.is_king() else ThaiCheckerEnv.BLACK_MAN
