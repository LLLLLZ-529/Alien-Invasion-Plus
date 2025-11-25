import pygame
import random
from pathlib import Path

POWER_TYPES = ('shield', 'heal')

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind=None):
        super().__init__()
        self.kind = kind or random.choice(POWER_TYPES)
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        if self.kind == 'shield':
            pygame.draw.circle(self.image, (0,150,255), (12,12), 12)
        else:
            pygame.draw.circle(self.image, (0,255,0), (12,12), 12)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()