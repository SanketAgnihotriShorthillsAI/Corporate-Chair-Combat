import pygame
import math
import random
from projectile import Projectile

class Chair:
    def __init__(self, x, y, width=40, height=30, speed=5, is_player=True, enemy_type="basic"):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.base_speed = speed
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.enemy_type = enemy_type
        # Adjust stats based on enemy type
        if is_player:
            self.color = (0, 0, 0)  # Black for player
        elif enemy_type == "sniper":
            self.color = (0, 0, 200)  # Blue for sniper
            self.base_shoot_delay = 15  # Faster shooting (0.25s vs 0.83s)
            self.base_speed = 4  # Slightly slower
        elif enemy_type == "tank":
            self.color = (150, 75, 0)  # Brown for tank
            self.width = 50
            self.height = 40
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
            self.base_speed = 3  # Slower movement
            self.lives = 2  # Tougher
        else:  # Basic enemy
            self.color = (200, 0, 0)  # Red for basic
        self.angle = random.randint(0, 359) if not is_player else 0
        self.shoot_cooldown = 0
        self.base_shoot_cooldown = 30  # Default cooldown: 0.5s at 60 FPS
        self.base_shoot_delay = 20 if is_player else 50
        self.shoot_delay = self.base_shoot_delay
        self.is_player = is_player
        self.alive = True
        if is_player:
            self.lives = 3
        elif enemy_type == "tank":
            self.lives = 2
        else:
            self.lives = 1
        self.bounce_offset = 0
        self.bounce_speed = 0.3
        self.hit_timer = 0
        self.moving = False
        self.speed_boost_timer = 0
        self.shield_timer = 0
        self.rapid_fire_timer = 0
        self.crash_timer = 0
        # Name tag for enemies
        self.name = None if is_player else random.choice(["Zed", "Rex", "Gus", "Max", "Leo", "Sam", "Jon"])
        self.font = pygame.font.SysFont(None, 20)
        self.strafe_timer = random.randint(60, 180) # Time to strafe for
        self.strafe_direction = random.choice([-1, 1]) # -1 for left, 1 for right

    def move(self, keys=None, walls=None, target=None, obstacles=None):
        if obstacles is None:
            obstacles = []
        self.moving = False
        if self.is_player and keys:
            dx, dy = 0, 0
            if keys[pygame.K_LEFT]:
                dx = -self.speed
                self.angle = 90
                self.moving = True
            if keys[pygame.K_RIGHT]:
                dx = self.speed
                self.angle = -90
                self.moving = True
            if keys[pygame.K_UP]:
                dy = -self.speed
                self.angle = 0
                self.moving = True
            if keys[pygame.K_DOWN]:
                dy = self.speed
                self.angle = 180
                self.moving = True

            self.x += dx
            self.rect.x = self.x
            if walls or obstacles:
                for obstacle in (walls if walls else []) + obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        if dx > 0:
                            self.x = obstacle.rect.left - self.width
                        elif dx < 0:
                            self.x = obstacle.rect.right
                        self.rect.x = self.x
                        break

            self.y += dy
            self.rect.y = self.y
            if walls or obstacles:
                for obstacle in (walls if walls else []) + obstacles:
                    if self.rect.colliderect(obstacle.rect):
                        if dy > 0:
                            self.y = obstacle.rect.top - self.height
                        elif dy < 0:
                            self.y = obstacle.rect.bottom
                        self.rect.y = self.y
                        break

        elif not self.is_player and target:
            dx = target.x - self.x
            dy = target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)

            min_distance = 200 if self.enemy_type == "sniper" else 60
            if distance > min_distance: # Maintain some distance for strafing
                target_angle = math.degrees(math.atan2(dy, dx))
                angle_diff = (target_angle - self.angle + 180) % 360 - 180
                self.angle += min(max(angle_diff, -10), 10)

                # Implement strafing
                if self.strafe_timer > 0:
                    strafe_offset = self.strafe_direction * self.speed * 0.5
                    move_dx = math.cos(math.radians(self.angle + 90 * self.strafe_direction)) * self.speed * 0.4
                    move_dy = math.sin(math.radians(self.angle + 90 * self.strafe_direction)) * self.speed * 0.4
                    self.strafe_timer -= 1
                    if self.strafe_timer <= 0:
                        self.strafe_timer = random.randint(60, 180)
                        self.strafe_direction *= -1 # Change strafe direction
                else:
                    move_dx = math.cos(math.radians(self.angle)) * self.speed * 0.6
                    move_dy = math.sin(math.radians(self.angle)) * self.speed * 0.6

                self.moving = True

                self.x += move_dx
                self.rect.x = self.x
                if walls or obstacles:
                    for obstacle in (walls if walls else []) + obstacles:
                        if self.rect.colliderect(obstacle.rect):
                            if move_dx > 0:
                                self.x = obstacle.rect.left - self.width
                            elif move_dx < 0:
                                self.x = obstacle.rect.right
                            self.rect.x = self.x
                            self.angle = (self.angle + random.choice([90, -90])) % 360
                            break

                self.y += move_dy
                self.rect.y = self.y
                if walls or obstacles:
                    for obstacle in (walls if walls else []) + obstacles:
                        if self.rect.colliderect(obstacle.rect):
                            if move_dy > 0:
                                self.y = obstacle.rect.top - self.height
                            elif move_dy < 0:
                                self.y = obstacle.rect.bottom
                            self.rect.y = self.y
                            self.angle = (self.angle + random.choice([90, -90])) % 360
                            break
            else:
                self.moving = False # Stop moving if close to the target

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        elif self.shoot_cooldown < 0:
            self.shoot_cooldown = 0  # Prevent negative cooldown   
             
        if self.hit_timer > 0:
            self.hit_timer -= 1

        if self.speed_boost_timer > 0:
            self.speed = self.base_speed * 2
            self.speed_boost_timer -= 1
        else:
            self.speed = self.base_speed

        if self.shield_timer > 0:
            self.shield_timer -= 1

        if self.rapid_fire_timer > 0:
            self.rapid_fire_timer -= 1

        if self.crash_timer > 0:
            self.crash_timer -= 1    

        if self.moving:
            self.bounce_offset = math.sin(pygame.time.get_ticks() * self.bounce_speed) * 2
        else:
            self.bounce_offset *= 0.9

    def shoot(self):
        if self.shoot_cooldown <= 0:  # Changed to <= 0 for reliability
            dx = -math.sin(math.radians(self.angle))
            dy = -math.cos(math.radians(self.angle))
            projectile = Projectile(self.rect.centerx - 5, self.rect.centery - 2.5, (dx, dy), shooter=self)
            self.shoot_cooldown = self.base_shoot_cooldown if self.rapid_fire_timer <= 0 else self.base_shoot_cooldown // 2  # 0.5s or 0.25s with rapid
            return projectile
        return None

    def take_damage(self):
        if self.shield_timer <= 0:
            self.lives -= 1
            self.hit_timer = 10
            if self.lives <= 0:
                self.alive = False

    def apply_powerup(self, powerup_type):
        if powerup_type == "speed":
            self.speed_boost_timer = 300
        elif powerup_type == "shield":
            self.shield_timer = 300
        elif powerup_type == "rapid":
            self.rapid_fire_timer = 300
        elif powerup_type == "crash":
            self.crash_timer = 300  

    def draw(self, surface):
        if self.alive:
            draw_y = self.rect.y + self.bounce_offset
            draw_color = (255, 255, 255) if self.hit_timer > 0 and self.hit_timer % 2 == 0 else self.color
            if self.enemy_type == "tank":
                seat_rect = pygame.Rect(self.rect.x + 5, draw_y + 15, self.width - 10, self.height - 25)
                backrest_rect = pygame.Rect(self.rect.x + 15, draw_y, self.width - 30, self.height - 15)
            else:
                seat_rect = pygame.Rect(self.rect.x + 5, draw_y + 10, self.width - 10, self.height - 20)
                backrest_rect = pygame.Rect(self.rect.x + 15, draw_y, self.width - 30, self.height - 10)
            # seat_rect = pygame.Rect(self.rect.x + 5, draw_y + 10, self.width - 10, self.height - 20)
            pygame.draw.rect(surface, draw_color, seat_rect)
            # backrest_rect = pygame.Rect(self.rect.x + 15, draw_y, self.width - 30, self.height - 10)
            pygame.draw.rect(surface, draw_color, backrest_rect)
            wheel1_pos = (self.rect.x + 10, draw_y + self.height - 5)
            wheel2_pos = (self.rect.x + self.width - 10, draw_y + self.height - 5)
            pygame.draw.circle(surface, (50, 50, 50), wheel1_pos, 5)
            pygame.draw.circle(surface, (50, 50, 50), wheel2_pos, 5)
            front_wheel_x = self.rect.centerx + math.cos(math.radians(self.angle)) * (self.width // 2)
            front_wheel_y = draw_y + self.height // 2 - math.sin(math.radians(self.angle)) * (self.height // 2)
            pygame.draw.circle(surface, (100, 100, 100), (int(front_wheel_x), int(front_wheel_y)), 5)
            if self.shield_timer > 0:
                pygame.draw.circle(surface, (0, 255, 255, 100), self.rect.center, self.width // 2, 2)
            # Draw name tag for enemies
            if self.name:
                name_text = self.font.render(self.name, True, (255, 255, 255))
                name_rect = name_text.get_rect(center=(self.rect.centerx, self.rect.y - 10))
                surface.blit(name_text, name_rect)

    def check_crash_collisions(self, enemies, score_ref):
        if self.is_player and self.alive and self.crash_timer > 0:
            for enemy in enemies[:]:
                if enemy.alive and self.rect.colliderect(enemy.rect):
                    enemy.take_damage()
                    score_ref[0] += 10  # Increment score