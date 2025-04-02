import pygame
import random
from projectile import Projectile

# Define colors locally
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)  # Chair color

class BossChair:
    def __init__(self, x, y, is_level_5=False, is_level_4=False):
        self.is_level_4 = is_level_4
        self.width = 40 if is_level_4 else (80 if is_level_5 else 60)  # 40x40 for Level 4, 80x80 for Level 5, 60x60 otherwise
        self.height = 40 if is_level_4 else (80 if is_level_5 else 60)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.color = GRAY if is_level_4 else (255, 0, 0)  # Gray for Level 4, red otherwise
        self.speed = 2
        self.health = 5 if not is_level_5 else 10  # 5 health for Level 4, 10 for Level 5
        self.alive = True
        self.shoot_timer = 0
        self.is_player = False

    def move(self, player, walls):
        if not self.alive:
            return
        # Chase player with improved collision handling
        direction = pygame.math.Vector2(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
        if direction.length() > 0:
            direction = direction.normalize()

        # Try moving in X direction
        new_rect_x = self.rect.move(direction.x * self.speed, 0)
        x_collides = False
        for wall in walls:
            if new_rect_x.colliderect(wall.rect):
                x_collides = True
                break
        if not x_collides:
            self.rect = new_rect_x

        # Try moving in Y direction
        new_rect_y = self.rect.move(0, direction.y * self.speed)
        y_collides = False
        for wall in walls:
            if new_rect_y.colliderect(wall.rect):
                y_collides = True
                break
        if not y_collides:
            self.rect = new_rect_y

        # If still stuck, nudge slightly to avoid walls
        if x_collides and y_collides:
            for wall in walls:
                if self.rect.colliderect(wall.rect):
                    # Push away from the wall
                    wall_center = pygame.math.Vector2(wall.rect.center)
                    boss_center = pygame.math.Vector2(self.rect.center)
                    push_direction = (boss_center - wall_center).normalize()
                    self.rect.x += push_direction.x * self.speed
                    self.rect.y += push_direction.y * self.speed
                    break

    def shoot(self):
        if not self.alive:
            return []
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot_timer = 30
            projectiles = []
            for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                dx = -pygame.math.Vector2(1, 0).rotate(angle).x
                dy = -pygame.math.Vector2(1, 0).rotate(angle).y
                proj = Projectile(self.rect.centerx - 5, self.rect.centery - 5, (dx, dy), self)
                projectiles.append(proj)
            return projectiles
        return []

    def take_damage(self):
        if self.alive:
            self.health -= 1
            if self.health <= 0:
                self.alive = False

    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect)
            pygame.draw.rect(surface, BLACK, self.rect, 2)
            if self.is_level_4:  # Draw wheels like a Chair for Level 4
                wheel_radius = 5
                pygame.draw.circle(surface, BLACK, (self.rect.left + 10, self.rect.bottom - 5), wheel_radius)
                pygame.draw.circle(surface, BLACK, (self.rect.right - 10, self.rect.bottom - 5), wheel_radius)
            health_bar_width = (self.health / (10 if self.rect.width == 80 else 5)) * self.width
            pygame.draw.rect(surface, GREEN, (self.rect.x, self.rect.y - 10, health_bar_width, 5))
            pygame.draw.rect(surface, BLACK, (self.rect.x, self.rect.y - 10, self.width, 5), 1)