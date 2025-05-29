import pygame
import sys
from player import Player
from enemy import Enemy
from collectible import Collectible
from boss_enemy import BossEnemy
from constants import *
#Initialize pygame and game window
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Side-Scroller Hero")
clock = pygame.time.Clock()

# Load background image and width
bg_image = pygame.image.load("assets/images/background.jpg").convert()
bg_width = bg_image.get_width()
scroll = 0

# Font for HUD
font = pygame.font.SysFont(None, 30)

# Level tracking
level = 1
level_cleared = False
level_message_timer = 0
transition_delay = 3000  # 3 seconds
boss = None
score = 0  # player Score tracker

def show_end_screen(win, score):
    message = "YOU WIN!" if win else "YOU LOST!"
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    return True

        screen.blit(bg_image, (-scroll, 0))
        screen.blit(bg_image, (-scroll + bg_width, 0))
        msg_text = font.render(message, True, (255, 255, 0))
        score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
        restart_text = font.render("Press R to Restart or ESC to Quit", True, (200, 200, 200))
        screen.blit(msg_text, (SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2 - 40))
        screen.blit(score_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 40))
        pygame.display.flip()

def load_level(level):
    global enemies, collectibles, boss
    boss = None

    if level == 1:
        enemies = [
            Enemy(400, GROUND_LEVEL),
            Enemy(700, GROUND_LEVEL), Enemy(900, GROUND_LEVEL)
        ]
        collectibles = [
            Collectible(600, GROUND_LEVEL - 20, 'health'),
            Collectible(950, GROUND_LEVEL - 20, 'life')
        ]

    elif level == 2:
        enemies = [
            Enemy(1200, GROUND_LEVEL), Enemy(1450, GROUND_LEVEL),Enemy(1700, GROUND_LEVEL),
            Enemy(1850, GROUND_LEVEL)
        ]
        collectibles = [
            Collectible(1250, GROUND_LEVEL - 20, 'health'),
            Collectible(1500, GROUND_LEVEL - 20, 'life'),
            Collectible(1825, GROUND_LEVEL - 20, 'life')
        ]

    elif level == 3:
        enemies = [
           Enemy(2100, GROUND_LEVEL), 
            Enemy(2300, GROUND_LEVEL),Enemy(2500, GROUND_LEVEL),Enemy(2700, GROUND_LEVEL),
            Enemy(2900, GROUND_LEVEL), Enemy(3100, GROUND_LEVEL)
        ]
        collectibles = [
            Collectible(2050, GROUND_LEVEL - 20, 'health'),
            Collectible(3400, GROUND_LEVEL - 20, 'life'),
            Collectible(2700, GROUND_LEVEL - 20, 'health'),
            Collectible(3000, GROUND_LEVEL - 20, 'life')
        ]

    elif level == 4:
        enemies = []
        collectibles = []
        boss = BossEnemy(3250, GROUND_LEVEL)

    else:
        pygame.quit()
        sys.exit()

# Create player and load first level
player = Player(100, GROUND_LEVEL)
load_level(level)

# Game loop
running = True
while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input handling
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # Scroll background
    scroll += player.direction.x * player.speed
    scroll %= bg_width

    # Update player
    player.update()

    # Draw background
    screen.blit(bg_image, (-scroll, 0))
    screen.blit(bg_image, (-scroll + bg_width, 0))

    # Draw player
    player.draw(screen)

    # Update and draw enemies
    for enemy in enemies:
        if enemy.alive:
            enemy.update()
            enemy.draw(screen, scroll)

    # Update and draw boss
    if boss and boss.is_alive():
        boss.update()
        boss.draw(screen, scroll)

    # Player bullets hit enemies
    for bullet in player.bullets[:]:
        for enemy in enemies:
            if enemy.alive:
                enemy_screen_rect = enemy.rect.copy()
                enemy_screen_rect.x -= scroll
                if bullet.rect.colliderect(enemy_screen_rect):
                    enemy.take_damage(bullet.damage)
                    if not enemy.alive:
                        score += 100  # Score for defeating enemy
                    print(f"Hit enemy at x={enemy.rect.x}! Health left: {enemy.health}")
                    player.bullets.remove(bullet)
                    break

    # Player bullets hit boss
    if boss and boss.is_alive():
        for bullet in player.bullets[:]:
            boss_screen_rect = boss.rect.copy()
            boss_screen_rect.x -= scroll
            if bullet.rect.colliderect(boss_screen_rect):
                boss.take_damage(bullet.damage)
                if not boss.is_alive():
                    score += 1000  # Score for defeating boss
                print(f"Hit BOSS! Health left: {boss.health}")
                player.bullets.remove(bullet)

    # Enemy bullets hit player
    for enemy in enemies:
        for bullet in enemy.bullets:
            player_world_rect = player.rect.copy()
            player_world_rect.x = scroll + 100
            if bullet.rect.colliderect(player_world_rect):
                player.health -= 1
                print("Player hit! Health now:", player.health)

                if player.health <= 0:
                    player.lives -= 1
                    print("Lost a life! Lives left:", player.lives)
                    if player.lives > 0:
                        player.health = player.max_health
                    else:
                        running = show_end_screen(False, score)
                        if running:
                            level = 1
                            player = Player(100, GROUND_LEVEL)
                            load_level(level)
                            score = 0
                        else:
                            sys.exit()
                enemy.bullets.remove(bullet)
                break

    # Boss bullets hit player
    if boss and boss.is_alive():
        for bullet in boss.bullets:
            player_world_rect = player.rect.copy()
            player_world_rect.x = scroll + 100
            if bullet.rect.colliderect(player_world_rect):
                player.health -= 1
                print("Player hit by BOSS! Health now:", player.health)
                if player.health <= 0:
                    player.lives -= 1
                    print("Lost a life! Lives left:", player.lives)
                    if player.lives > 0:
                        player.health = player.max_health
                    else:
                        running = show_end_screen(False, score)
                        if running:
                            level = 1
                            player = Player(100, GROUND_LEVEL)
                            load_level(level)
                            score = 0
                        else:
                            sys.exit()
                boss.bullets.remove(bullet)
                break

    # Draw collectibles and detect collection
    for item in collectibles:
        if not item.collected:
            item.draw(screen, scroll)
            player_world_rect = player.rect.copy()
            player_world_rect.x = scroll + 100
            if player_world_rect.colliderect(item.rect):
                item.collected = True
                if item.type == 'health' and player.health < player.max_health:
                    player.health += 1
                    score += 50
                elif item.type == 'life':
                    player.lives += 1
                    score += 100

    # LEVEL TRANSITION CHECK
    if not level_cleared and all(not e.alive for e in enemies) and (not boss or not boss.is_alive()):
        level_cleared = True
        level_message_timer = pygame.time.get_ticks()

    if level_cleared:
        elapsed = pygame.time.get_ticks() - level_message_timer
        if elapsed < transition_delay:
            if level == 3:
                message = "BOSS LEVEL"
            elif level == 4 and boss and not boss.is_alive():
                message = "YOU WIN"
            elif level < 4:
                message = "NEXT LEVEL"
            else:
                message = ""
            if message:
                level_text = font.render(message, True, (255, 255, 0))
                screen.blit(level_text, (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2 - 20))
        else:
            if level == 4 and boss and not boss.is_alive():
                running = show_end_screen(True, score)
                if running:
                    level = 1
                    player = Player(100, GROUND_LEVEL)
                    load_level(level)
                    score = 0
                else:
                    sys.exit()
            else:
                level += 1
                load_level(level)
                level_cleared = False

    # Draw HUD (bars)
    def draw_bar(screen, x, y, width, height, value, max_value, color):
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        fill_width = int((value / max_value) * width)
        pygame.draw.rect(screen, color, (x, y, fill_width, height))
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height), 2)

    draw_bar(screen, 10, 10, 150, 20, player.health, player.max_health, (0, 255, 0))
    draw_bar(screen, 10, 40, 150, 20, player.lives, 5, (0, 128, 255))

    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (SCREEN_WIDTH - 180, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
