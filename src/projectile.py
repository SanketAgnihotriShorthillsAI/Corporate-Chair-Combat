import pygame

class Projectile:
    def __init__(self, x, y, direction, shooter=None, color=(100, 100, 100)):
        self.x = x
        self.y = y
        self.speed = 15
        self.direction = direction
        self.rect = pygame.Rect(self.x, self.y, 10, 5)
        self.active = True
        self.shooter = shooter
        self.color = color
        self.trail = []
        self.timer = 120  # 2 seconds at 60 FPS

    def update(self, walls):
        dx, dy = self.direction
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.rect.x = self.x
        self.rect.y = self.y

        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:
            self.trail.pop(0)

        self.timer -= 1
        if self.timer <= 0:
            self.active = False

        if self.rect.left < 0 or self.rect.right > 1200 or self.rect.top < 0 or self.rect.bottom > 900:
            self.active = False

        for wall in walls:
            if self.rect.colliderect(wall.rect):
                self.active = False
                break

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        if self.active:
            for i, pos in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                pygame.draw.circle(surface, (255, 215, 0, alpha), (int(pos[0]), int(pos[1])), 2)  # Golden trail
            pygame.draw.rect(surface, (255, 215, 0), self.rect)  # Golden bullet