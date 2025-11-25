import pygame
from pygame.sprite import Sprite
import time


class Ship(Sprite):
    """A class to manage the ship."""

    def __init__(self, ai_game):
        """Initialize the ship and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the ship image and get its rect.
        # 默认使用更大的飞船尺寸与更高速度
        self.image = pygame.Surface((60, 48))
        self.image.fill((0, 180, 255))
        self.rect = self.image.get_rect()

        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom

        # Store a float for the ship's exact horizontal position.
        self.x = float(self.rect.x)

        # Movement flags; start with a ship that's not moving.
        self.moving_right = False
        self.moving_left = False

        # 自动连发
        self.auto_fire = False
        self.fire_delay = 200  # 毫秒
        self._last_shot = 0

        # 护盾占位
        self.shield = None
        self.health = 3

    def center_ship(self):
        """Center the ship on the screen."""
        self.rect.midbottom = self.screen_rect.midbottom
        self.x = float(self.rect.x)

    def update(self):
        """Update the ship's position based on movement flags."""
        # Update the ship's x value, not the rect.
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.x += self.settings.ship_speed
        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        # Update rect object from self.x.
        self.rect.x = self.x

        if self.moving_left and self.rect.left > 0:
            self.rect.x -= self.speed
        if self.moving_right and self.rect.right < self.screen.get_width():
            self.rect.x += self.speed
        if self.moving_up and self.rect.top > 0:
            self.rect.y -= self.speed
        if self.moving_down and self.rect.bottom < self.screen.get_height():
            self.rect.y += self.speed

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.moving_left = True
            elif event.key == pygame.K_RIGHT:
                self.moving_right = True
            elif event.key == pygame.K_UP:
                self.moving_up = True
            elif event.key == pygame.K_DOWN:
                self.moving_down = True
            elif event.key == pygame.K_SPACE:
                self.auto_fire = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                self.moving_left = False
            elif event.key == pygame.K_RIGHT:
                self.moving_right = False
            elif event.key == pygame.K_UP:
                self.moving_up = False
            elif event.key == pygame.K_DOWN:
                self.moving_down = False
            elif event.key == pygame.K_SPACE:
                self.auto_fire = False

    def can_shoot(self, now_ms):
        return now_ms - self._last_shot >= self.fire_delay

    def shoot(self, bullets_group, now_ms, bullet_factory):
        """bullet_factory(centerx, centery) -> bullet sprite"""
        if self.can_shoot(now_ms):
            self._last_shot = now_ms
            bullets_group.add(bullet_factory(self.rect.centerx, self.rect.top))

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)

    def __init__(self, screen, x, y, speed=5, fire_delay=200):
        super().__init__()
        self.screen = screen

        # 保留原有图片（若有），并在其基础上放大一点；回退到默认 surface
        try:
            # 许多实现会通过加载图片赋值 self.image
            if not hasattr(self, 'image') or self.image is None:
                self.image = pygame.Surface((40, 30))
                self.image.fill((0, 180, 255))
        except Exception:
            self.image = pygame.Surface((40, 30))
            self.image.fill((0, 180, 255))

        # 放大原图（20%），保持中心不变
        try:
            w, h = self.image.get_size()
            scale = 1.2
            new_w, new_h = max(1, int(w * scale)), max(1, int(h * scale))
            self.image = pygame.transform.scale(self.image, (new_w, new_h))
        except Exception:
            pass

        self.rect = self.image.get_rect(center=(x, y))
        # 提高默认移动速度（兼容传入参数）
        self.speed = max(speed, 7)
        self.moving_left = self.moving_right = False
        self.moving_up = self.moving_down = False

        # 自动连发
        self.auto_fire = False
        # 降低连发频率：默认至少 300ms（你可在构造时传入更高值）
        self.fire_delay = max(fire_delay, 300)  # 毫秒
        self._last_shot = 0