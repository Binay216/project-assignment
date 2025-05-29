import pygame
from constants import *
from enemy_projectile import EnemyProjectile

class Enemy:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(
            pygame.image.load("assets/images/enemy1.png").convert_alpha(), (48, 64)
        )
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.health = 5
        self.max_health = 5
        self.alive = True

        # Enemy bullet logic
        self.bullets = []
        self.shoot_cooldown = 2000  # Time between shots (in ms)
        self.last_shot = pygame.time.get_ticks()

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

    def update(self):
        if not self.alive:
            return

        # Shooting logic
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.shoot_cooldown:
            self.bullets.append(EnemyProjectile(self.rect.centerx - 10, self.rect.centery, -1))
            self.last_shot = current_time

        # Update bullets
        for bullet in self.bullets:
            bullet.update()

        # Remove off-screen bullets
        self.bullets = [b for b in self.bullets if b.rect.right > 0]

    def draw(self, screen, scroll_offset=0):
        if not self.alive:
            return

        # Draw enemy
        screen.blit(self.image, (self.rect.x - scroll_offset, self.rect.y))

        # Draw health bar
        bar_width = 40
        bar_height = 5
        bar_x = self.rect.x + 4 - scroll_offset
        bar_y = self.rect.top - 10
        health_ratio = self.health / self.max_health
        pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, bar_width * health_ratio, bar_height))

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen, scroll_offset)
