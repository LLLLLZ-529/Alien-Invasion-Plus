import os
from pathlib import Path


class GameStats:
    """Track statistics for Alien Invasion."""

    def __init__(self, ai_game, high_score_filename='high_score.txt'):
        """Initialize statistics."""
        self.settings = ai_game.settings
        self.reset_stats()
        self._file = Path(high_score_filename)
        self.high_score = self._load_high_score()

    def reset_stats(self):
        """Initialize statistics that can change during the game."""
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def _load_high_score(self):
        try:
            if self._file.exists():
                text = self._file.read_text().strip()
                return int(text) if text else 0
        except Exception:
            pass
        return 0

    def save_high_score(self):
        try:
            # 确保保存当前最高分，而不仅仅是新纪录
            self._file.write_text(str(self.high_score))
        except Exception:
            pass