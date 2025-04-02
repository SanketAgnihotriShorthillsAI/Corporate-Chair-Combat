import pygame
import random

class ConferenceTable:
    def __init__(self, x, y, direction):
        self.width = 100
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = (139, 69, 19)  # Brown for wood
        self.speed = 2
        self.direction = direction  # "horizontal" or "vertical"
        self.active = True

    def update(self, screen_width, screen_height, walls):
        if self.direction == "horizontal":
            self.rect.x += self.speed
            if self.rect.left < 0 or self.rect.right > screen_width:
                self.speed = -self.speed
        elif self.direction == "vertical":
            self.rect.y += self.speed
            if self.rect.top < 0 or self.rect.bottom > screen_height:
                self.speed = -self.speed

        # Bounce off static walls
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.direction == "horizontal":
                    self.speed = -self.speed
                    self.rect.x += self.speed * 2  # Nudge away to prevent sticking
                elif self.direction == "vertical":
                    self.speed = -self.speed
                    self.rect.y += self.speed * 2

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, (100, 50, 10), self.rect, 2)  # Darker outline for wood grain