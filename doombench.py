import pygame
import math
import random
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DoomBench")

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PLAYER_COLOR = (50, 150, 255)
BULLET_COLOR = (255, 50, 50)
ENEMY_COLOR = (200, 0, 0)
BUTTON_COLOR = (70, 130, 180)
BUTTON_HOVER_COLOR = (100, 160, 210)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 150)  # Semi-transparent black overlay

player_size = 40
player_speed = 5

font = pygame.font.SysFont(None, 48)
small_font = pygame.font.SysFont(None, 28)

clock = pygame.time.Clock()

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.radius = 5
        self.dx = math.cos(angle) * self.speed
        self.dy = math.sin(angle) * self.speed

    def update(self):
        self.x += self.dx
        self.y += self.dy

    def draw(self, surface):
        pygame.draw.circle(surface, BULLET_COLOR, (int(self.x), int(self.y)), self.radius)

    def off_screen(self):
        return self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

class Enemy:
    def __init__(self):
        self.size = 30
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            self.x = random.randint(0, WIDTH - self.size)
            self.y = -self.size
        elif side == 'bottom':
            self.x = random.randint(0, WIDTH - self.size)
            self.y = HEIGHT + self.size
        elif side == 'left':
            self.x = -self.size
            self.y = random.randint(0, HEIGHT - self.size)
        else:  # right
            self.x = WIDTH + self.size
            self.y = random.randint(0, HEIGHT - self.size)
        self.speed = 2

    def update(self, player_pos):
        px = player_pos[0] + player_size / 2
        py = player_pos[1] + player_size / 2
        ex = self.x + self.size / 2
        ey = self.y + self.size / 2

        dx = px - ex
        dy = py - ey
        dist = math.hypot(dx, dy)
        if dist != 0:
            dx /= dist
            dy /= dist

        self.x += dx * self.speed
        self.y += dy * self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, ENEMY_COLOR, (int(self.x), int(self.y), self.size, self.size))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = BUTTON_COLOR
        self.hover_color = BUTTON_HOVER_COLOR
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, surface):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = self.hover_color
        else:
            color = self.color
        pygame.draw.rect(surface, color, self.rect)
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def game_loop():
    player_pos = [WIDTH // 2, HEIGHT // 2]
    bullets = []
    enemies = []
    spawn_count = 1
    total_enemies_spawned = 0  # Track total enemies created

    spawn_event = pygame.USEREVENT + 1
    pygame.time.set_timer(spawn_event, 2000)

    running = True
    game_over = False
    paused = False

    benchmark_done = False
    benchmark_duration = 30_000  # 30 seconds in milliseconds
    benchmark_start_time = pygame.time.get_ticks()

    play_again_button = Button((WIDTH//2 - 100, HEIGHT//2 + 50, 200, 50), "Play Again")
    pause_button = Button((WIDTH - 110, 10, 100, 40), "Pause")

    spawn_adjust_interval = 1  # 1 millisecond
    last_spawn_adjust_time = pygame.time.get_ticks()
    min_spawn_count = 1

    while running:
        clock.tick(60)

        current_time = pygame.time.get_ticks()
        elapsed = current_time - benchmark_start_time
        fps = clock.get_fps()

        # Benchmark timer check
        if not benchmark_done and elapsed >= benchmark_duration:
            paused = True
            benchmark_done = True
            enemies.clear()  # Clear enemies at benchmark end
            pause_button.text = "Resume"

        # Spawn count adjustment every 1ms
        if current_time - last_spawn_adjust_time > spawn_adjust_interval:
            last_spawn_adjust_time = current_time

            if fps > 1:
                spawn_count += 1000
            else:
                spawn_count = max(min_spawn_count, spawn_count - 450)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if not game_over:
                if pause_button.is_clicked(event):
                    paused = not paused
                    pause_button.text = "Resume" if paused else "Pause"
                    if paused and not benchmark_done:
                        benchmark_start_time = pygame.time.get_ticks() - elapsed
                    if not paused and benchmark_done:
                        benchmark_done = False
                        benchmark_start_time = pygame.time.get_ticks()
                        total_enemies_spawned = 0
                        spawn_count = 1

                if not paused:
                    if event.type == spawn_event:
                        for _ in range(spawn_count):
                            enemies.append(Enemy())
                            total_enemies_spawned += 1

                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            mx, my = pygame.mouse.get_pos()
                            px = player_pos[0] + player_size / 2
                            py = player_pos[1] + player_size / 2
                            angle = math.atan2(my - py, mx - px)
                            bullets.append(Bullet(px, py, angle))

            else:
                if play_again_button.is_clicked(event):
                    return  # Restart game loop by returning

        keys = pygame.key.get_pressed()
        if not game_over and not paused:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player_pos[0] -= player_speed
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player_pos[0] += player_speed
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player_pos[1] -= player_speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player_pos[1] += player_speed

            player_pos[0] = max(0, min(WIDTH - player_size, player_pos[0]))
            player_pos[1] = max(0, min(HEIGHT - player_size, player_pos[1]))

            for bullet in bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    bullets.remove(bullet)

            for enemy in enemies[:]:
                enemy.update(player_pos)
                enemy_rect = enemy.get_rect()

                player_rect = pygame.Rect(*player_pos, player_size, player_size)
                # Player invincible - no damage

                for bullet in bullets[:]:
                    if enemy_rect.colliderect(bullet.get_rect()):
                        enemies.remove(enemy)
                        bullets.remove(bullet)
                        spawn_count += 1
                        break

        screen.fill(BLACK)

        if not game_over:
            pygame.draw.rect(screen, PLAYER_COLOR, (*player_pos, player_size, player_size))

            for bullet in bullets:
                bullet.draw(screen)

            for enemy in enemies:
                enemy.draw(screen)

            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_center = (player_pos[0] + player_size / 2, player_pos[1] + player_size / 2)
            pygame.draw.line(screen, (255, 255, 255), player_center, (mouse_x, mouse_y), 2)

            pause_button.draw(screen)

            if paused:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill(PAUSE_OVERLAY_COLOR)
                screen.blit(overlay, (0, 0))

                if benchmark_done:
                    benchmark_title = font.render("BENCHMARK RESULTS", True, WHITE)
                    title_rect = benchmark_title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100))
                    screen.blit(benchmark_title, title_rect)

                    enemies_text = small_font.render(f"Enemies Spawned: {total_enemies_spawned}", True, WHITE)
                    enemies_rect = enemies_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
                    screen.blit(enemies_text, enemies_rect)

                    points = total_enemies_spawned * 0.5
                    points_text = small_font.render(f"Points: {points:.1f}", True, WHITE)
                    points_rect = points_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 10))
                    screen.blit(points_text, points_rect)
                else:
                    pause_text = font.render("PAUSED", True, WHITE)
                    pause_rect = pause_text.get_rect(center=(WIDTH//2, HEIGHT//2))
                    screen.blit(pause_text, pause_rect)

        else:
            game_over_text = font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(game_over_text, text_rect)

            play_again_button.draw(screen)

        if not benchmark_done:
            enemy_count_text = small_font.render(f"Enemies: {len(enemies)}", True, WHITE)
            screen.blit(enemy_count_text, (10, 10))

        pygame.display.flip()

def main():
    while True:
        game_loop()

if __name__ == "__main__":
    main()
