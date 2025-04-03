import pygame
import sys
import random
from chair import Chair
from arena import create_arena, Wall
from projectile import Projectile
from powerup import PowerUp
from boss_chair import BossChair
from paper_jam import PaperJam
from conference_table import ConferenceTable

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
high_score = 0
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 191, 255)
PURPLE = (128, 0, 128)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
pygame.display.set_caption("Corporate Chair Combat")
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 74)
small_font = pygame.font.SysFont(None, 36)
input_font = pygame.font.SysFont("Montserrat", 48, bold=False)
tutorial_font = pygame.font.SysFont("Montserrat", 28, bold=True)
tutorial_desc_font = pygame.font.SysFont("Montserrat", 24)

try:
    shoot_sound = pygame.mixer.Sound('assets/shoot.mp3')
    move_sound = pygame.mixer.Sound('assets/move.mp3')
    powerup_sound = pygame.mixer.Sound('assets/powerup.mp3')
    levelup_sound = pygame.mixer.Sound('assets/levelup.mp3')
    gameover_sound = pygame.mixer.Sound('assets/gameover.mp3')
    win_sound = pygame.mixer.Sound('assets/win.mp3')
except FileNotFoundError as e:
    print(f"Sound file missing: {e}. Running without some sounds.")
    shoot_sound = move_sound = powerup_sound = levelup_sound = gameover_sound = win_sound = None

def draw_floor(surface):
    tile_size = 40
    for x in range(0, SCREEN_WIDTH, tile_size):
        for y in range(0, SCREEN_HEIGHT, tile_size):
            color = (100, 80, 60) if (x // tile_size + y // tile_size) % 2 == 0 else (120, 100, 80)
            pygame.draw.rect(surface, color, (x, y, tile_size, tile_size))
    for x in range(0, SCREEN_WIDTH, tile_size):
        pygame.draw.line(surface, (80, 60, 40), (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, tile_size):
        pygame.draw.line(surface, (80, 60, 40), (0, y), (SCREEN_WIDTH, y), 1)

def spawn_enemies(level, walls, is_training=False):
    enemy_count = 2 if is_training else {1: 6, 2: 8, 3: 8, 4: 5, 5: 5}.get(level, 5)
    enemies = []
    for _ in range(enemy_count):
        while True:
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            enemy_type = random.choices(["basic", "sniper", "tank"], weights=[60, 20, 20], k=1)[0]
            new_enemy = Chair(x, y, is_player=False, enemy_type=enemy_type)
            # new_enemy = Chair(x, y, is_player=False)
            if not any(new_enemy.rect.colliderect(wall.rect) for wall in walls):
                enemies.append(new_enemy)
                break
    return enemies

def reset_game(walls, player_name, training_mode=False):
    global player, enemies, boss, projectiles, powerups, paper_jams, conference_tables, game_over, player_won, score, level, coffee_spill_timer, paper_jam_timer, table_timer, training_prompt_timer, tutorial_timer, tutorial_text
    player = Chair(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, is_player=True)
    player.name = player_name
    enemies = spawn_enemies(level, walls, is_training=training_mode)
    boss = BossChair(400, 300, is_level_5=(level == 5), is_level_4=(level == 4)) if level in [4, 5] and not training_mode else None
    projectiles = []
    powerups = []
    paper_jams = []
    conference_tables = []
    game_over = False
    player_won = False
    score = 0
    coffee_spill_timer = 0
    paper_jam_timer = 0
    table_timer = 0
    training_prompt_timer = 180 if training_mode else 0
    tutorial_timer = 0
    tutorial_text = None
    if not training_mode:
        if level == 1:
            tutorial_timer = 180  # 3 seconds
            tutorial_text = "Beware of Coffee Spills!"
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            new_spill = Wall(x, y, 50, 50, color=(0, 191, 255, 150), is_hazard=True)
            if not any(new_spill.rect.colliderect(w.rect) for w in walls):
                walls.append(new_spill)

def get_player_name():
    player_name = ""
    input_active = True
    cursor_blink = 0
    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and player_name:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif event.unicode.isalnum() and len(player_name) < 10:
                    player_name += event.unicode

        draw_floor(screen)
        pygame.draw.rect(screen, (200, 200, 200), (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 4, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), border_radius=10)
        prompt_text = input_font.render("Enter Your Name:", True, WHITE)
        shadow_text = input_font.render("Enter Your Name:", True, (50, 50, 50))
        screen.blit(shadow_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 - 70 + 2))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2 - 70))
        pygame.draw.rect(screen, (255, 255, 255), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 10, 300, 60), border_radius=5)
        pygame.draw.rect(screen, (100, 100, 100), (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 10, 300, 60), 2, border_radius=5)
        name_text = input_font.render(player_name, True, (0, 0, 0))
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, SCREEN_HEIGHT // 2))
        cursor_blink = (cursor_blink + 1) % 60
        if cursor_blink < 30:
            cursor_x = SCREEN_WIDTH // 2 + name_text.get_width() // 2 + 5
            pygame.draw.line(screen, (0, 0, 0), (cursor_x, SCREEN_HEIGHT // 2), (cursor_x, SCREEN_HEIGHT // 2 + 40), 2)
        pygame.display.flip()
        clock.tick(FPS)
    return player_name

def show_controls_tutorial():
    tutorial_active = True
    while tutorial_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                tutorial_active = False

        draw_floor(screen)
        pygame.draw.rect(screen, (220, 220, 220), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(screen, (150, 150, 150), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 3)
        header_text = font.render("Corporate Chair Combat", True, (255, 215, 0))
        shadow_text = font.render("Corporate Chair Combat", True, (50, 50, 50))
        screen.blit(shadow_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2 + 3, 33))
        screen.blit(header_text, (SCREEN_WIDTH // 2 - header_text.get_width() // 2, 30))
        controls = [
            ("Move", "Arrow Keys", "Use Up, Down, Left, Right to roll your chair"),
            ("Shoot", "Spacebar", "Fire staples at enemies")
        ]
        for i, (title, key, desc) in enumerate(controls):
            y_pos = 120 + i * 150
            if title == "Move":
                pygame.draw.polygon(screen, (0, 0, 0), [(50, y_pos), (70, y_pos - 20), (90, y_pos)])
                pygame.draw.polygon(screen, (0, 0, 0), [(50, y_pos + 20), (70, y_pos + 40), (90, y_pos + 20)])
                pygame.draw.polygon(screen, (0, 0, 0), [(30, y_pos + 10), (50, y_pos + 30), (30, y_pos + 50)])
                pygame.draw.polygon(screen, (0, 0, 0), [(110, y_pos + 10), (90, y_pos + 30), (110, y_pos + 50)])
            elif title == "Shoot":
                pygame.draw.rect(screen, (0, 0, 0), (60, y_pos, 40, 20))
            title_text = tutorial_font.render(title, True, (0, 0, 0))
            key_text = tutorial_font.render(key, True, (0, 100, 200))
            desc_text = tutorial_desc_font.render(desc, True, (50, 50, 50))
            screen.blit(title_text, (150, y_pos - 20))
            screen.blit(key_text, (150, y_pos + 10))
            screen.blit(desc_text, (150, y_pos + 40))
        powerup_box_y = 420
        pygame.draw.rect(screen, (255, 255, 255), (50, powerup_box_y, SCREEN_WIDTH - 100, 150), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), (50, powerup_box_y, SCREEN_WIDTH - 100, 150), 2, border_radius=10)
        powerup_title = tutorial_font.render("Power-Ups", True, (0, 0, 0))
        screen.blit(powerup_title, (SCREEN_WIDTH // 2 - powerup_title.get_width() // 2, powerup_box_y + 10))
        powerups = [
            ("Speed", (255, 215, 0), "Doubles your speed"),
            ("Shield", (0, 255, 255), "Blocks one hit"),
            ("Spread", (0, 255, 0), "Shoots bullets in all directions"),
            ("Crash", (128, 0, 128), "Kill enemies on touch")
        ]
        for i, (name, color, desc) in enumerate(powerups):
            x_pos = 100 + i * 250
            pygame.draw.circle(screen, color, (x_pos, powerup_box_y + 70), 10)
            name_text = tutorial_desc_font.render(name, True, (0, 0, 0))
            desc_text = tutorial_desc_font.render(desc, True, (50, 50, 50))
            screen.blit(name_text, (x_pos + 20, powerup_box_y + 60))
            screen.blit(desc_text, (x_pos + 20, powerup_box_y + 85))
        # Enemy Types Section
        enemy_box_y = 600
        pygame.draw.rect(screen, (255, 255, 255), (50, enemy_box_y, SCREEN_WIDTH - 100, 150), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 100), (50, enemy_box_y, SCREEN_WIDTH - 100, 150), 2, border_radius=10)
        enemy_title = tutorial_font.render("Enemy Types", True, (0, 0, 0))
        screen.blit(enemy_title, (SCREEN_WIDTH // 2 - enemy_title.get_width() // 2, enemy_box_y + 10))
        enemies = [
            ("Basic", (200, 0, 0), "Standard enemy, chases you"),
            ("Sniper", (0, 0, 200), "Stays back, shoots fast"),
            ("Tank", (150, 75, 0), "Slow, takes 2 hits")
        ]
        for i, (name, color, desc) in enumerate(enemies):
            x_pos = 100 + i * 350
            pygame.draw.rect(screen, color, (x_pos, enemy_box_y + 70, 20, 15))  # Small chair-like shape
            name_text = tutorial_desc_font.render(name, True, (0, 0, 0))
            desc_text = tutorial_desc_font.render(desc, True, (50, 50, 50))
            screen.blit(name_text, (x_pos + 30, enemy_box_y + 60))
            screen.blit(desc_text, (x_pos + 30, enemy_box_y + 85))    
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 50)
        pygame.draw.rect(screen, (0, 255, 0), button_rect, border_radius=10)
        pygame.draw.rect(screen, (0, 100, 0), button_rect, 3, border_radius=10)
        start_text = tutorial_font.render("Press Enter", True, WHITE)
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT - 65))
        pygame.display.flip()
        clock.tick(FPS)

player_name = get_player_name()
show_controls_tutorial()

walls = create_arena(SCREEN_WIDTH, SCREEN_HEIGHT)
player = Chair(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, is_player=True)
player.name = player_name
level = 0
training_mode = True
enemies = spawn_enemies(level, walls, is_training=True)
boss = None
projectiles = []
powerups = []
paper_jams = []
conference_tables = []
coffee_spill_timer = 0
paper_jam_timer = 0
table_timer = 0
training_prompt_timer = 180
tutorial_timer = 0
tutorial_text = None

game_over = False
player_won = False
score = 0
powerup_spawn_timer = 0
move_sound_playing = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                level = 0 if training_mode else 1
                reset_game(walls, player_name, training_mode=training_mode)

    if not game_over:
        keys = pygame.key.get_pressed()
        original_speed = player.speed
        in_paper_jam = False
        for wall in walls:
            if wall.is_hazard and player.rect.colliderect(wall.rect):
                player.speed = original_speed * 0.5
                break
        else:
            player.speed = original_speed
        if not training_mode:
            for jam in paper_jams:
                if player.rect.colliderect(jam.rect):
                    player.speed = original_speed * 0.5
                    in_paper_jam = True
                    break
        player.move(keys, walls + conference_tables)
        player.check_crash_collisions(enemies, [score])

        if player.moving and move_sound and not move_sound_playing:
            move_sound.play(-1)
            move_sound_playing = True
        elif not player.moving and move_sound_playing:
            move_sound.stop()
            move_sound_playing = False

        if keys[pygame.K_SPACE]:
            new_projectiles = player.shoot()
            print(f"Shot: {new_projectiles}")  # Debug
            if new_projectiles:
                if isinstance(new_projectiles, list):
                    projectiles.extend(new_projectiles)
                else:
                    projectiles.append(new_projectiles)
                if shoot_sound:
                    shoot_sound.play()

        for enemy in enemies:
            if enemy.alive:
                enemy.move(None, walls + conference_tables, player)
                if random.random() < 0.05:
                    new_projectile = enemy.shoot()
                    if new_projectile:
                        projectiles.append(new_projectile)
                        if shoot_sound:
                            shoot_sound.play()

        if boss and boss.alive:
            boss.move(player, walls)

        if level == 1 and not training_mode:
            coffee_spill_timer -= 1
            if coffee_spill_timer <= 0:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                new_spill = Wall(x, y, 50, 50, color=(0, 191, 255, 150), is_hazard=True)
                if not any(new_spill.rect.colliderect(w.rect) for w in walls):
                    walls.append(new_spill)
                coffee_spill_timer = 180

        if level == 2 and not training_mode:
            paper_jam_timer -= 1
            if paper_jam_timer <= 0:
                x = random.randint(0, SCREEN_WIDTH - 100)
                y = random.randint(0, SCREEN_HEIGHT - 100)
                new_jam = PaperJam(x, y)
                paper_jams.append(new_jam)
                paper_jam_timer = 300
            for jam in paper_jams[:]:
                jam.update(SCREEN_WIDTH, SCREEN_HEIGHT)

        if level == 3 and not training_mode:
            table_timer -= 1
            if table_timer <= 0 and len(conference_tables) < 3:
                x = random.randint(50, SCREEN_WIDTH - 150)
                y = random.randint(50, SCREEN_HEIGHT - 90)
                direction = random.choice(["horizontal", "vertical"])
                new_table = ConferenceTable(x, y, direction)
                if not any(new_table.rect.colliderect(w.rect) for w in walls):
                    conference_tables.append(new_table)
                table_timer = 120
            for table in conference_tables[:]:
                table.update(SCREEN_WIDTH, SCREEN_HEIGHT, walls)
                for wall in walls:
                    if table.rect.colliderect(player.rect) and player.alive:
                        if any(player.rect.colliderect(w.rect) for w in walls):
                            player.take_damage()
                            score -= 10
                    for enemy in enemies[:]:
                        if table.rect.colliderect(enemy.rect) and enemy.alive:
                            if any(enemy.rect.colliderect(w.rect) for w in walls):
                                enemy.take_damage()
                                score += 5

        if level >= 4 and not training_mode:
            if boss and boss.alive:
                if random.random() < 0.2:
                    new_projectiles = boss.shoot()
                    for proj in new_projectiles:
                        projectiles.append(proj)
                        if shoot_sound:
                            shoot_sound.play()

        if level == 5 and not training_mode:
            coffee_spill_timer -= 1
            if coffee_spill_timer <= 0:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
                new_spill = Wall(x, y, 50, 50, color=(0, 191, 255, 150), is_hazard=True)
                if not any(new_spill.rect.colliderect(w.rect) for w in walls):
                    walls.append(new_spill)
                coffee_spill_timer = 180

            paper_jam_timer -= 1
            if paper_jam_timer <= 0:
                x = random.randint(0, SCREEN_WIDTH - 100)
                y = random.randint(0, SCREEN_HEIGHT - 100)
                new_jam = PaperJam(x, y)
                paper_jams.append(new_jam)
                paper_jam_timer = 300
            for jam in paper_jams[:]:
                jam.update(SCREEN_WIDTH, SCREEN_HEIGHT)

            table_timer -= 1
            if table_timer <= 0 and len(conference_tables) < 3:
                x = random.randint(50, SCREEN_WIDTH - 150)
                y = random.randint(50, SCREEN_HEIGHT - 90)
                direction = random.choice(["horizontal", "vertical"])
                new_table = ConferenceTable(x, y, direction)
                if not any(new_table.rect.colliderect(w.rect) for w in walls):
                    conference_tables.append(new_table)
                table_timer = 120

        powerup_spawn_timer -= 1
        if powerup_spawn_timer <= 0 and random.random() < 0.01:
            powerup_types = ["speed", "shield", "spread", "crash"]
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            powerup = PowerUp(x, y, random.choice(powerup_types))
            if not any(powerup.rect.colliderect(w.rect) for w in walls + conference_tables):
                powerups.append(powerup)
            powerup_spawn_timer = 300

        for powerup in powerups[:]:
            powerup.update()
            if not powerup.active:
                powerups.remove(powerup)
            elif powerup.rect.colliderect(player.rect):
                player.apply_powerup(powerup.type)
                if powerup_sound:
                    powerup_sound.play()
                powerups.remove(powerup)

        for projectile in projectiles[:]:
            projectile.update(walls + conference_tables)
            if projectile.shooter and projectile.shooter.is_player:
                for enemy in enemies[:]:
                    if projectile.rect.colliderect(enemy.rect) and enemy.alive:
                        enemy.take_damage()
                        score += 10
                        projectile.active = False
                if boss and projectile.rect.colliderect(boss.rect) and boss.alive:
                    boss.take_damage()
                    score += 20
                    projectile.active = False
            elif projectile.shooter and not projectile.shooter.is_player:
                if projectile.rect.colliderect(player.rect) and player.alive:
                    player.take_damage()
                    projectile.active = False
            if not projectile.active:
                projectiles.remove(projectile)

        win_condition = all(not e.alive for e in enemies) and (not boss or not boss.alive)
        if player.lives <= 0:
            game_over = True
            player_won = False
            if move_sound_playing:
                move_sound.stop()
                move_sound_playing = False
            if gameover_sound:
                gameover_sound.play()
        elif win_condition and training_mode:
            training_mode = False
            level = 1
            reset_game(walls, player_name, training_mode=False)
            if levelup_sound:
                levelup_sound.play()
        elif win_condition and level < 5 and not training_mode:
            level += 1
            enemies = spawn_enemies(level, walls)
            boss = BossChair(400, 300, is_level_5=(level == 5), is_level_4=(level == 4)) if level in [4, 5] else None
            paper_jams.clear()
            conference_tables.clear()
            score += 50
            powerups.clear()
            if level == 2:
                tutorial_timer = 150  # 2.5 seconds
                tutorial_text = "Paper Jams Slow You Down!"
                x = random.randint(0, SCREEN_WIDTH - 100)
                y = random.randint(0, SCREEN_HEIGHT - 100)
                paper_jams.append(PaperJam(x, y))
            elif level == 3:
                tutorial_timer = 150  # 2.5 seconds
                tutorial_text = "Watch Out for Tables!"
                x = random.randint(50, SCREEN_WIDTH - 150)
                y = random.randint(50, SCREEN_HEIGHT - 90)
                direction = random.choice(["horizontal", "vertical"])
                new_table = ConferenceTable(x, y, direction)
                if not any(new_table.rect.colliderect(w.rect) for w in walls):
                    conference_tables.append(new_table)
            elif level == 4:
                tutorial_timer = 150  # 2.5 seconds
                tutorial_text = "Defeat the Boss!"
            elif level == 5:
                tutorial_timer = 180  # 3 seconds
                tutorial_text = "FINAL LEVEL BEGINS!"
            if levelup_sound:
                levelup_sound.play()
        elif win_condition and level == 5 and not training_mode:
            game_over = True
            player_won = True
            if win_sound:
                win_sound.play()

        # Update high score
        if score > high_score:
            high_score = score        

    draw_floor(screen)
    for wall in walls:
        wall.draw(screen)
    if not training_mode:
        for jam in paper_jams:
            jam.draw(screen)
        for table in conference_tables:
            table.draw(screen)
    if in_paper_jam:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 50))
        screen.blit(overlay, (0, 0))
    for projectile in projectiles:
        projectile.draw(screen)
    for powerup in powerups:
        powerup.draw(screen)
    if player.alive:
        player.draw(screen)
    for enemy in enemies:
        if enemy.alive:
            enemy.draw(screen)
    if boss and boss.alive:
        boss.draw(screen)

    score_text = small_font.render(f"Score: {score}", True, (0, 0, 0))
    lives_text = small_font.render(f"Lives: {player.lives}", True, (0, 0, 0))
    level_text = small_font.render(f"Level: {'Training' if training_mode else level}", True, (0, 0, 0))
    player_name_text = small_font.render(f"Player: {player_name}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    screen.blit(lives_text, (10, 40))
    screen.blit(level_text, (10, 70))
    screen.blit(player_name_text, (10, 100))

    high_score_text = small_font.render(f"High Score: {high_score}", True, (255, 0, 0))
    screen.blit(high_score_text, (10, 130))

    # Display power-up timer
    active_timer = None
    if player.speed_boost_timer > 0:
        active_timer = ("Speed", player.speed_boost_timer, player.powerup_color)
    elif player.shield_timer > 0:
        active_timer = ("Shield", player.shield_timer, player.powerup_color)
    elif player.spread_shot_timer > 0:
        active_timer = ("Spread", player.spread_shot_timer, player.powerup_color)
    elif player.crash_timer > 0:
        active_timer = ("Crash", player.crash_timer, player.powerup_color)

    if active_timer:
        name, frames, color = active_timer
        seconds = frames // 60  # Convert frames to seconds
        timer_text = small_font.render(f"{name}: {seconds}s", True, color)
        screen.blit(timer_text, (1000, 130))

    if training_mode and training_prompt_timer > 0:
        prompt_text = font.render("Training Level - Defeat 2 Enemies", True, WHITE)
        prompt_shadow = font.render("Training Level - Defeat 2 Enemies", True, (50, 50, 50))
        screen.blit(prompt_shadow, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
        screen.blit(prompt_text, (SCREEN_WIDTH // 2 - prompt_text.get_width() // 2, SCREEN_HEIGHT // 2))
        training_prompt_timer -= 1

    # Draw level-specific tutorials with smaller font
    if tutorial_timer > 0 and not training_mode:
        tutorial_timer -= 1
        if tutorial_text:
            text_surface = small_font.render(tutorial_text, True, WHITE)  # Changed from font to small_font
            text_shadow = small_font.render(tutorial_text, True, (50, 50, 50))  # Changed from font to small_font
            if level == 5:  # Center alert for Level 5
                screen.blit(text_shadow, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2 + 2, SCREEN_HEIGHT // 2 + 2))
                screen.blit(text_surface, (SCREEN_WIDTH // 2 - text_surface.get_width() // 2, SCREEN_HEIGHT // 2))
            else:  # Point to object for Levels 1-4
                target_rect = None
                if level == 1:
                    for wall in walls:
                        if wall.is_hazard:
                            target_rect = wall.rect
                            break
                elif level == 2 and paper_jams:
                    target_rect = paper_jams[0].rect
                elif level == 3 and conference_tables:
                    target_rect = conference_tables[0].rect
                elif level == 4 and boss:
                    target_rect = boss.rect

                if target_rect:
                    # Position text above the target
                    text_x = max(0, min(target_rect.centerx - text_surface.get_width() // 2, SCREEN_WIDTH - text_surface.get_width()))
                    text_y = max(0, target_rect.top - text_surface.get_height() - 20)
                    screen.blit(text_shadow, (text_x + 2, text_y + 2))
                    screen.blit(text_surface, (text_x, text_y))
                    # Draw arrow pointing to target
                    arrow_start = (target_rect.centerx, target_rect.top - 10)
                    arrow_end = (target_rect.centerx, target_rect.top)
                    pygame.draw.line(screen, WHITE, arrow_start, arrow_end, 3)
                    pygame.draw.polygon(screen, WHITE, [(arrow_end[0] - 5, arrow_end[1] - 5), 
                                                        (arrow_end[0] + 5, arrow_end[1] - 5), 
                                                        arrow_end])

    if game_over:
        if player_won:
            text = font.render("YOU WIN!", True, GREEN)
        else:
            text = font.render("GAME OVER", True, RED)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_text = small_font.render("Press R to Restart", True, (0, 0, 0))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(text, text_rect)
        screen.blit(restart_text, restart_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()