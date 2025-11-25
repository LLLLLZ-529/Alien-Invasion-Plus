import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    """A class to manage bullets fired from the ship."""

    def __init__(self, ai_game):
        """Create a bullet object at the ship's current position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        # 放大子弹尺寸以增强视觉与命中判定
        self.color = (60, 60, 60)
        self.rect = pygame.Rect(0, 0, 8, 28)  # 原来小子弹改为更大尺寸
        self.rect.midtop = ai_game.ship.rect.midtop

        # Store the bullet's position as a float.
        self.y = float(self.rect.y)
        self.speed_factor = ai_game.settings.bullet_speed

    def update(self):
        """Move the bullet up the screen."""
        # Update the exact position of the bullet.
        self.y -= self.speed_factor
        # Update the rect position.
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        # 使用填充矩形绘制更大的子弹
        pygame.draw.rect(self.screen, self.color, self.rect)