# Scoring System Summary: Corporate Chair Combat

## Overview

The scoring system in _Corporate Chair Combat_ tracks player performance through a single global variable score, initialized at 0 in the reset_game function and updated dynamically during gameplay. Points are awarded for **combat success** (damaging or killing enemies and the boss), **level progression**, and **environmental interactions**, while penalties are applied for specific player mistakes. The high_score persists across restarts within a session, updating whenever score exceeds it. This system incentivizes aggressive play, strategic power-up use, and level completion, with a minor risk element introduced in Level 3.

----------

## Positive Scoring Metrics

These actions increase the player’s score, reflecting skill in combat and progression.

### 1. Normal Enemy Hit by Projectile

-   **Points**: +10 per hit
-   **Description**: Awarded when a player-fired projectile hits a "basic" enemy (red, 1 life).
-   **Frequency**: Common across all levels (60% spawn chance via random.choices in spawn_enemies).
-   **Example**: Hitting 3 basic enemies in Level 1 yields +30 points.

    

### 2. Sniper Enemy Hit by Projectile

-   **Points**: +15 per hit
-   **Description**: Awarded when a player-fired projectile hits a "sniper" enemy (blue, 1 life, faster shooting).
-   **Frequency**: Less common (20% spawn chance).
-   **Example**: Hitting 1 sniper in Level 2 yields +15 points.

    

### 3. Tank Enemy Hit by Projectile

-   **Points**: +20 per hit
-   **Description**: Awarded when a player-fired projectile hits a "tank" enemy (brown, 2 lives, slower movement).
-   **Frequency**: Less common (20% spawn chance), but yields more points due to requiring 2 hits to kill.
-   **Example**: Killing 1 tank (2 hits) yields +40 points.

    

### 4. Boss Hit by Projectile

-   **Points**: +20 per hit, +50 bonus on kill
-   **Description**: Each projectile hit on the boss (Levels 4 and 5) awards +20, with an additional +50 when the boss’s lives reach 0.
-   **Frequency**: Occurs once per level in Levels 4 and 5.
-   **Example**: 3 hits to kill the boss = 3 × 20 + 50 = +110 points.

    

### 5. Enemy Killed by "Crash" Power-Up

-   **Points**: +10 per enemy killed
-   **Description**: Colliding with an enemy while the "Crash" power-up is active (crash_timer > 0) instantly kills it, awarding points regardless of enemy type.
-   **Frequency**: Depends on "Crash" power-up spawns (1/4 chance every ~5s via powerup_spawn_timer) and enemy proximity.
-   **Example**: Crashing into 2 enemies yields +20 points.

    

### 6. Level Completion (Levels 1-4)

-   **Points**: +30 per level completed
-   **Description**: Awarded when all enemies (and boss, if present) are defeated in Levels 1-4, before advancing to the next level.
-   **Frequency**: Once per level, excluding Level 5 (ends game) and Training Mode (no bonus).
-   **Example**: Completing Level 1 yields +30 points.

    

### 7. Enemy Hit by Conference Table and Wall

-   **Points**: +5 per enemy damaged
-   **Description**: Awarded when a moving conference table in Level 3 pushes an enemy into a wall, damaging it.
-   **Frequency**: Rare and situational in Level 3 (max 3 tables, random movement).
-   **Example**: 2 enemies hit by tables yield +10 points.

----------

## Negative Scoring Metrics

These actions decrease the player’s score, penalizing mistakes.

### 1. Player Hit by Conference Table and Wall

-   **Points**: -10 per hit
-   **Description**: Occurs when a moving conference table in Level 3 pushes the player into a wall, causing damage.
-   **Frequency**: Situational in Level 3, avoidable with careful positioning.
-   **Example**: Getting caught once deducts -10 points.

----------

## No Score Impact

-   **Player Damage**: Taking damage from enemy projectiles or hazards (e.g., coffee spills) reduces lives but does not affect the score.
-   **Power-Up Collection**: Picking up "Speed", "Shield", "Spread", or "Crash" power-ups has no direct score impact (though "Crash" enables scoring via kills).
-   **Level 5 Victory**: Beating Level 5 ends the game with "YOU WIN!" but awards no completion bonus.
-   **Training Mode**: No level bonus applies; only combat scoring (enemy hits) affects the score.

----------

## Theoretical Scoring Breakdown by Level

Assuming optimal play (all enemies hit/killed, no penalties), here’s a potential score progression:

| Level     | Enemies     | Combat Points (Avg)                                      | Other Points                 | Total |
|-----------|------------|-----------------------------------------------------------|------------------------------|-------|
| Training  | 2          | 2 basic = 20                                             | None                         | 20    |
| Level 1   | 6          | 3.6 basic = 36, 1.2 snipers = 18, 1.2 tanks = 24         | +30 (completion)             | 108   |
| Level 2   | 8          | 4.8 basic = 48, 1.6 snipers = 24, 1.6 tanks = 32         | +30 (completion)             | 134   |
| Level 3   | 8          | 4.8 basic = 48, 1.6 snipers = 24, 1.6 tanks = 32         | +10 (tables, est.), +30 (completion) | 144   |
| Level 4   | 5 + Boss   | 3 basic = 30, 1 sniper = 15, 1 tank = 20, Boss (5 hits + kill) = 150 | +30 (completion)             | 245   |
| Level 5   | 5 + Boss   | 3 basic = 30, 1 sniper = 15, 1 tank = 20, Boss (5 hits + kill) = 150 | None                         | 215   |


-   **Grand Total (No Losses)**: 20 + 108 + 134 + 144 + 245 + 215 = 866 points
-   **With "Crash" Power-Up**: Add ~50-100 points if used effectively across levels (e.g., 5-10 extra kills).

> **Note**: Enemy type distribution is averaged based on random.choices(["basic", "sniper", "tank"], weights=[60, 20, 20]). Actual scores vary due to RNG.

----------

## Strategic Implications

1.  **Combat Focus**
    -   Higher points for snipers (+15) and tanks (+20) reward targeting tougher enemies, though their 20% spawn rates balance this with basic enemies (+10, 60%).
2.  **Boss Incentive**
    -   The +50 bonus for killing the boss in Levels 4 and 5 (on top of +20/hit) makes these levels high-value (up to 245/215 points), encouraging persistence.
3.  **"Crash" Power-Up**
    -   +10 per kill incentivizes aggressive play during its 10-second duration, potentially doubling combat points in dense enemy clusters.
4.  **Level Progression**
    -   Reduced completion bonus (+30 vs. old +50) shifts emphasis to combat, though it remains a steady gain for advancing.
5.  **Table Risk/Reward**
    -   Level 3’s +5 (enemy hit) vs. -10 (player hit) mechanic introduces a small gamble—positioning is key to maximize gains and avoid losses.

----------

## Documentation Notes

-   **Maximum Theoretical Score**: Approximately **900-1000 points** with perfect play, effective "Crash" usage, and table bonuses. RNG (enemy types, table hits) introduces variability.
-   **Balance**: Combat accounts for ~70-80% of points, aligning with the game’s action focus, while level bonuses provide a steady baseline.
-   **Adjustability**: Easily tweakable—e.g., increase boss kill bonus to +100 or add a Level 5 completion reward for a rounder total.