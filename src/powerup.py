import pygame
import random

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type  # "speed", "shield", "rapid"
        self.rect = pygame.Rect(self.x, self.y, 20, 20)
        self.color = {
            "speed": (255, 215, 0),   # Gold
            "shield": (0, 255, 255),  # Cyan
            "rapid": (255, 0, 255),   # Magenta
            "crash": (128, 0, 128)    # Purple
        }[type]
        self.timer = 300  # 5 seconds at 60 FPS
        self.active = True

    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

    def draw(self, surface):
        if self.active:
            pygame.draw.rect(surface, self.color, self.rect)
            # Add a small symbol
            if self.type == "speed":
                pygame.draw.line(surface, (0, 0, 0), (self.x + 5, self.y + 15), (self.x + 15, self.y + 5), 2)
            elif self.type == "shield":
                pygame.draw.circle(surface, (0, 0, 0), (self.x + 10, self.y + 10), 8, 2)
            elif self.type == "rapid":
                pygame.draw.rect(surface, (0, 0, 0), (self.x + 8, self.y + 8, 4, 4))
            elif self.type == "crash":
                pygame.draw.line(surface, (0, 0, 0), (self.x + 5, self.y + 5), (self.x + 15, self.y + 15), 2)
                pygame.draw.line(surface, (0, 0, 0), (self.x + 15, self.y + 5), (self.x + 5, self.y + 15), 2)