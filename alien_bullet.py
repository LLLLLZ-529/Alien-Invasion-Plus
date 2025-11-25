import pygame

class AlienBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=5, color=(255,0,0)):
        super().__init__()
        self.image = pygame.Surface((4, 12))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

class BossBullet(AlienBullet):
    def __init__(self, x, y, vx=0, vy=6, color=(255,100,0)):
        super().__init__(x, y, vy, color)
        self.vx = vx
        self.speed = vy

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.speed
        h = pygame.display.get_surface().get_height()
        w = pygame.display.get_surface().get_width()
        if self.rect.top > h or self.rect.right < 0 or self.rect.left > w:
            self.kill()