import pygame
import random

class PaperJam:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 100
        self.height = 100
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = random.uniform(1, 2)  # Random drift speed
        self.angle = random.randint(0, 359)  # Random direction
        self.active = True

    def update(self, screen_width, screen_height):
        if not self.active:
            return

        # Drift movement
        dx = self.speed * pygame.math.Vector2(1, 0).rotate(self.angle).x
        dy = self.speed * pygame.math.Vector2(1, 0).rotate(self.angle).y
        self.x += dx
        self.y += dy

        # Bounce off screen edges
        if self.x < 0:
            self.x = 0
            self.angle = (180 - self.angle) % 360
        elif self.x + self.width > screen_width:
            self.x = screen_width - self.width
            self.angle = (180 - self.angle) % 360
        if self.y < 0:
            self.y = 0
            self.angle = (-self.angle) % 360
        elif self.y + self.height > screen_height:
            self.y = screen_height - self.height
            self.angle = (-self.angle) % 360

        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface):
        if self.active:
            # Semi-transparent gray cloud
            cloud_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(cloud_surface, (100, 100, 100, 100), (0, 0, self.width, self.height))
            surface.blit(cloud_surface, (self.x, self.y))