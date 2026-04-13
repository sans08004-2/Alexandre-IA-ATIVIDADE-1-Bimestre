import pygame
from pygame.locals import *
import os

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Classes
class Paddle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((10, 100))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.side = 'left' if x < WIDTH // 2 else 'right'

    def update(self):
        keys = pygame.key.get_pressed()
        if self.side == 'left':
            if keys[K_w] and self.rect.top > 0:
                self.rect.y -= self.speed
            if keys[K_s] and self.rect.bottom < HEIGHT:
                self.rect.y += self.speed
        else:
            if keys[K_UP] and self.rect.top > 0:
                self.rect.y -= self.speed
            if keys[K_DOWN] and self.rect.bottom < HEIGHT:
                self.rect.y += self.speed

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((10, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.speed_x = 5
        self.speed_y = 5

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top <= 0 or self.rect.bottom >= HEIGHT:
            self.speed_y = -self.speed_y
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            return True  # Ball out
        return False

# Functions
def load_leaderboard():
    if os.path.exists('leaderboard.txt'):
        with open('leaderboard.txt', 'r') as f:
            lines = f.readlines()
            return [(line.split(':')[0], int(line.split(':')[1].strip())) for line in lines]
    return []

def save_leaderboard(scores):
    with open('leaderboard.txt', 'w') as f:
        for name, score in scores:
            f.write(f"{name}:{score}\n")

def show_leaderboard(screen, font):
    scores = load_leaderboard()
    scores.sort(key=lambda x: x[1], reverse=True)
    screen.fill(BLACK)
    title = font.render("Leaderboard", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    for i, (name, score) in enumerate(scores[:10]):
        text = font.render(f"{i+1}. {name}: {score}", True, WHITE)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 30))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    waiting = False

def enter_name(screen, font, score):
    name = ""
    input_active = True
    while input_active:
        screen.fill(BLACK)
        prompt = font.render("Enter your name:", True, WHITE)
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 50))
        name_text = font.render(name, True, WHITE)
        screen.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_RETURN and name:
                    input_active = False
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    scores = load_leaderboard()
    scores.append((name, score))
    save_leaderboard(scores)

def main_menu(screen, font):
    screen.fill(BLACK)
    title = font.render("PONG", True, WHITE)
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))
    start = font.render("Press S to Start", True, WHITE)
    screen.blit(start, (WIDTH // 2 - start.get_width() // 2, 300))
    leaderboard = font.render("Press L for Leaderboard", True, WHITE)
    screen.blit(leaderboard, (WIDTH // 2 - leaderboard.get_width() // 2, 350))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_s:
                    waiting = False
                    return 'start'
                if event.key == K_l:
                    waiting = False
                    return 'leaderboard'

def game_loop(screen, font):
    all_sprites = pygame.sprite.Group()
    paddles = pygame.sprite.Group()
    left_paddle = Paddle(20, HEIGHT // 2)
    right_paddle = Paddle(WIDTH - 20, HEIGHT // 2)
    ball = Ball()
    all_sprites.add(left_paddle, right_paddle, ball)
    paddles.add(left_paddle, right_paddle)
    clock = pygame.time.Clock()
    score_left = 0
    score_right = 0
    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
        all_sprites.update()
        # Ball collision with paddles
        if pygame.sprite.spritecollide(ball, paddles, False):
            ball.speed_x = -ball.speed_x
        # Check if ball out
        if ball.update():
            if ball.rect.left <= 0:
                score_right += 1
            else:
                score_left += 1
            ball.rect.center = (WIDTH // 2, HEIGHT // 2)
            ball.speed_x = -ball.speed_x  # Reset direction
        # Draw
        screen.fill(BLACK)
        all_sprites.draw(screen)
        # Scores
        score_text = font.render(f"{score_left} - {score_right}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))
        pygame.display.flip()
        # Check win
        if score_left >= 5 or score_right >= 5:
            running = False
    # Game over, enter name
    winner_score = max(score_left, score_right)
    enter_name(screen, font, winner_score)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pong")
    font = pygame.font.Font(None, 36)
    while True:
        choice = main_menu(screen, font)
        if choice == 'start':
            game_loop(screen, font)
        elif choice == 'leaderboard':
            show_leaderboard(screen, font)

if __name__ == "__main__":
    main()
