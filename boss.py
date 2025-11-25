import pygame
import random
from alien_bullet import BossBullet

class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y, health=100, speed=2):
        super().__init__()
        # 尽量使用更大尺寸默认图片，若有外部图形会被替换
        self.image = pygame.Surface((200, 100))
        self.image.fill((120, 0, 120))
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.speed = speed
        self.direction = 1
        # 默认降低发射频率，允许外部覆盖
        self.shoot_delay = 1200  # 毫秒
        self._last_shot = 0

    def update(self):
        self.rect.x += self.speed * self.direction
        screen_w = pygame.display.get_surface().get_width()
        if self.rect.right >= screen_w - 10 or self.rect.left <= 10:
            self.direction *= -1

    def try_shoot(self, bullets_group, now_ms):
        """基于时间发射多弹道子弹，传入 bullets sprite group 和当前时间（ms）。"""
        if now_ms - self._last_shot >= self.shoot_delay:
            self._last_shot = now_ms
            # 多路发射
            for angle in (-2, 0, 2):
                vx = angle
                bullets_group.add(BossBullet(self.rect.centerx + angle*6, self.rect.bottom, vx=vx, vy=6))