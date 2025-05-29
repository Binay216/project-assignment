import pygame
from constants import *

class EnemyProjectile:
    def __init__(self, x, y, direction):
        self.image = pygame.Surface((10, 5))
        self.image.fill((255, 0, 0))  # Red bullet
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 6
        self.direction = direction
        self.damage = 1

    def update(self):
        self.rect.x += self.speed * self.direction

    def draw(self, screen, scroll):
        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))
