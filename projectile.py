import pygame
from constants import *

class Projectile:
    def __init__(self, x, y, direction):
        # Load and scale bullet image properly
        self.image = pygame.transform.scale(
            pygame.image.load("assets/images/bullet.png").convert_alpha(),
            (16, 16)  # You can change to (10, 10) if it's still too big
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.direction = direction  # 1 = right, -1 = left
        self.damage = 1

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, screen):
        screen.blit(self.image, self.rect)
