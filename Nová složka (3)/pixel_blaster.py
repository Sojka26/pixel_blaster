import pygame
import random
import sys

# Inicializace
pygame.init()
WIDTH, HEIGHT = 600, 800
FPS = 60

# Barvy
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
STAR_COLORS = [(255, 255, 255), (200, 200, 255), (255, 200, 200)]

# Herní okno
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pixel Blaster - OOP Edition")
clock = pygame.time.Clock()

# Zvuky
laser_sound = pygame.mixer.Sound("laser.wav")
explode_sound = pygame.mixer.Sound("explode.wav")
lose_sound = pygame.mixer.Sound("lose.wav")

# Fonty
font = pygame.font.SysFont("Courier", 24)

# Hvězdy pro dynamické pozadí
stars = [
    {
        "rect": pygame.Rect(random.randint(0, WIDTH), random.randint(0, HEIGHT), size := random.randint(1, 3), size),
        "color": random.choice(STAR_COLORS),
        "speed": random.randint(1, 3)
    }
    for _ in range(100)
]

# Realistické planety (poloprůhledné a vrstvené pro efekt)
class Planet:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(-HEIGHT, 0)
        self.radius = random.randint(30, 60)
        self.color = random.choice([(180, 180, 255), (255, 180, 180), (180, 255, 180), (200, 200, 100)])
        self.alpha = random.randint(100, 180)
        self.speed = random.uniform(0.1, 0.4)
        self.surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.surface, (*self.color, self.alpha), (self.radius, self.radius), self.radius)

    def update(self):
        self.y += self.speed
        if self.y - self.radius > HEIGHT:
            self.y = -self.radius * 2
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        surface.blit(self.surface, (self.x - self.radius, self.y - self.radius))

planets = [Planet() for _ in range(3)]

class Player:
    def __init__(self):
        self.original_image = pygame.image.load("player.png")
        self.image = pygame.transform.scale(self.original_image, (40, 40))
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 60))
        self.bullets = []

    def move_to_mouse(self, pos):
        self.rect.center = pos

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullets.append(bullet)
        laser_sound.play()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(surface)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.rect.bottom < 0:
                self.bullets.remove(bullet)


class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 2, y, 4, 10)
        self.color = WHITE
        self.speed = -10

    def update(self):
        self.rect.y += self.speed

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Meteorite:
    def __init__(self):
        self.image = pygame.image.load("meteorite.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 300)))

    def update(self):
        pass

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Enemy:
    def __init__(self):
        self.image = pygame.image.load("enemy.png")
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect(center=(random.randint(0, WIDTH - 50), -50))
        self.speed = random.randint(2, 4)
        self.bullets = []
        self.shoot_timer = random.randint(60, 120)

    def update(self):
        self.rect.y += self.speed
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.bullets.append(Bullet(self.rect.centerx, self.rect.bottom))
            self.shoot_timer = random.randint(60, 120)

        for bullet in self.bullets[:]:
            bullet.rect.y += 5
            if bullet.rect.top > HEIGHT:
                self.bullets.remove(bullet)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw(surface)


class Game:
    def __init__(self):
        self.player = Player()
        self.running = True
        self.meteorites = [Meteorite() for _ in range(5)]
        self.enemies = [Enemy() for _ in range(3)]
        self.game_over = False
        self.score = 0
        self.level = 1
        self.kills_to_level_up = 10

    def run(self):
        while self.running:
            clock.tick(FPS)
            self.handle_events()
            if not self.game_over:
                self.update()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_over:
                self.player.shoot()
            if event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.__init__()

    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.player.move_to_mouse(mouse_pos)
        self.player.update_bullets()

        for s in stars:
            s["rect"].y += s["speed"]
            if s["rect"].y > HEIGHT:
                s["rect"].y = 0
                s["rect"].x = random.randint(0, WIDTH)

        for planet in planets:
            planet.update()

        for meteor in self.meteorites[:]:
            meteor.update()
            if meteor.rect.colliderect(self.player.rect):
                lose_sound.play()
                self.game_over = True
            for bullet in self.player.bullets[:]:
                if bullet.rect.colliderect(meteor.rect):
                    explode_sound.play()
                    self.player.bullets.remove(bullet)
                    self.meteorites.remove(meteor)
                    self.meteorites.append(Meteorite())
                    self.score += 1
                    break

        for enemy in self.enemies[:]:
            enemy.update()
            if enemy.rect.top > HEIGHT:
                self.enemies.remove(enemy)
                self.enemies.append(Enemy())
            if enemy.rect.colliderect(self.player.rect):
                lose_sound.play()
                self.game_over = True
            for bullet in enemy.bullets:
                if bullet.rect.colliderect(self.player.rect):
                    lose_sound.play()
                    self.game_over = True
            for bullet in self.player.bullets[:]:
                if bullet.rect.colliderect(enemy.rect):
                    explode_sound.play()
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.enemies.append(Enemy())
                    self.score += 2
                    break

        if self.score >= self.level * self.kills_to_level_up:
            self.level += 1
            self.meteorites.append(Meteorite())
            self.enemies.append(Enemy())

    def draw(self):
        win.fill(BLACK)
        for s in stars:
            pygame.draw.rect(win, s["color"], s["rect"])

        for planet in planets:
            planet.draw(win)

        for meteor in self.meteorites:
            meteor.draw(win)
        self.player.draw(win)
        for enemy in self.enemies:
            enemy.draw(win)

        score_text = font.render(f"Score: {self.score}  Level: {self.level}", True, WHITE)
        win.blit(score_text, (10, 10))

        if self.game_over:
            text = font.render("You lose! Press R to retry.", True, WHITE)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))

        pygame.display.flip()


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()