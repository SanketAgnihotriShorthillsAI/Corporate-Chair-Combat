import pygame

class Wall:
    def __init__(self, x, y, width, height, color=(150, 150, 150), is_hazard=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.is_hazard = is_hazard

    def draw(self, surface):
        if self.is_hazard:
            pygame.draw.ellipse(surface, self.color, self.rect, 0)
            pygame.draw.ellipse(surface, (0, 150, 200, 100), self.rect, 2)
        else:
            pygame.draw.rect(surface, self.color, self.rect)
            if self.color == (139, 69, 19):
                pygame.draw.rect(surface, (100, 50, 10), self.rect, 2)
            else:
                pygame.draw.rect(surface, (100, 100, 100), self.rect, 1)

def create_arena(screen_width, screen_height):
    walls = [
        # Outer walls
        Wall(0, 0, screen_width, 20),
        Wall(0, screen_height - 20, screen_width, 20),
        Wall(0, 0, 20, screen_height),
        Wall(screen_width - 20, 0, 20, screen_height),
        # Cubicle walls
        Wall(200, 100, 20, 200),
        Wall(400, 300, 200, 20),
        Wall(600, 100, 20, 200),
        Wall(300, 400, 20, 150),  # New vertical wall
        Wall(100, 300, 150, 20),  # New horizontal wall
        # Desks
        Wall(300, 150, 80, 40, color=(139, 69, 19)),
        Wall(500, 350, 60, 60, color=(139, 69, 19)),
        Wall(150, 450, 70, 30, color=(139, 69, 19)),  # New desk
        Wall(650, 50, 50, 50, color=(139, 69, 19)),   # New desk
        # Coffee spills
        Wall(250, 400, 50, 50, color=(0, 191, 255, 150), is_hazard=True),
        Wall(600, 200, 50, 50, color=(0, 191, 255, 150), is_hazard=True),
        Wall(350, 50, 40, 40, color=(0, 191, 255, 150), is_hazard=True)  # New spill
    ]
    return walls