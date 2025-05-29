import pygame
from constants import *
from enemy_projectile import EnemyProjectile

class BossEnemy:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(
            pygame.image.load("assets/images/enemy1.png").convert_alpha(), (96, 128)  # Placeholder boss sprite
        )
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = 25
        self.max_health = 25
        self.alive = True

        self.bullets = []
        self.shoot_cooldown = 1000  # Faster shooting
        self.last_shot = pygame.time.get_ticks()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

    def update(self):
        if not self.alive:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.bullets.append(EnemyProjectile(self.rect.centerx - 10, self.rect.centery, -1))
            self.last_shot = current_time

        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if b.rect.right > 0]

    def draw(self, screen, scroll):
        if not self.alive:
            return

        screen.blit(self.image, (self.rect.x - scroll, self.rect.y))

        # Health bar centered at top
        bar_width = 300
        bar_height = 20
        bar_x = (SCREEN_WIDTH // 2) - (bar_width // 2)
        bar_y = 20
        health_ratio = self.health / self.max_health

        pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)

        for bullet in self.bullets:
            bullet.draw(screen, scroll)

    def is_alive(self):
        return self.alive
