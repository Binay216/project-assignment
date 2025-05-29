import pygame
from constants import *

class Collectible:
    def __init__(self, x, y, type):
        self.type = type  # 'health' or 'life'
        if self.type == 'health':
            self.image = pygame.transform.scale(
                pygame.image.load("assets/images/green_heart.png").convert_alpha(), (24, 24)
            )
        elif self.type == 'life':
            self.image = pygame.transform.scale(
                pygame.image.load("assets/images/blue_heart.png").convert_alpha(), (24, 24)
            )
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False

    def draw(self, screen, scroll):
        if not self.collected:
            screen.blit(self.image, (self.rect.x - scroll, self.rect.y))
