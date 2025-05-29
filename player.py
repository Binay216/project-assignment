import pygame
from constants import *
from projectile import Projectile

class Player:
    def __init__(self, x, y):
        self.idle_image = pygame.transform.scale(
            pygame.image.load("assets/images/player_idle.png").convert_alpha(), (48, 64)
        )
        self.run_image = pygame.transform.scale(
            pygame.image.load("assets/images/player_run.png").convert_alpha(), (48, 64)
        )
        self.image = self.idle_image
        self.rect = self.image.get_rect(midbottom=(x, y))

        # Movement
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 5
        self.is_jumping = False
        self.gravity = 0.9
        self.jump_speed = -18
        self.vel_y = 0

        # Health and lives
        self.max_health = 5
        self.health = 5
        self.lives = 3


        # Shooting
        self.bullets = []
        self.bullet_cooldown = 250
        self.last_shot_time = 0

    def handle_input(self, keys):
        self.direction.x = 0
        if keys[pygame.K_LEFT]:
            self.direction.x = -1
        if keys[pygame.K_RIGHT]:
            self.direction.x = 1

        if keys[pygame.K_SPACE] and not self.is_jumping:
            self.vel_y = self.jump_speed
            self.is_jumping = True

        if keys[pygame.K_f]:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.bullet_cooldown:
                self.shoot()
                self.last_shot_time = current_time

        self.image = self.run_image if self.direction.x != 0 else self.idle_image

    def apply_gravity(self):
        self.vel_y += self.gravity
        self.rect.y += self.vel_y
        if self.rect.bottom >= GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.is_jumping = False

    def shoot(self):
        bullet = Projectile(100 + 30, self.rect.centery, 1)  # Fixed from screen position
        self.bullets.append(bullet)

    def update(self):
        self.apply_gravity()
        for bullet in self.bullets:
            bullet.update()

        self.bullets = [b for b in self.bullets if b.rect.x < 2000]


    def draw(self, screen):
        screen.blit(self.image, (100, self.rect.y))  # Draw at fixed horizontal position
        for bullet in self.bullets:
            bullet.draw(screen)
