"""
Musou Mini 2D - Top-Down Hack & Slash
by B5 (Boom Fifth)

WASD - Move
Mouse - Aim direction
LMB - Attack (slash)
RMB / Q - Ultimate (screen nuke)
Space - Dash
R - Restart
ESC - Quit
"""

import pygame
import sys
import math
import random

pygame.init()

# ============================================
# Settings
# ============================================
WIDTH, HEIGHT = 1280, 720
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Musou Mini - Hack & Slash")
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (220, 40, 40)
DARK_RED = (150, 20, 20)
GREEN = (40, 200, 40)
BLUE = (40, 40, 220)
YELLOW = (255, 220, 40)
ORANGE = (255, 140, 40)
PURPLE = (150, 40, 220)
CYAN = (40, 220, 220)
GRAY = (60, 60, 60)
DARK_GREEN = (30, 80, 30)
LIGHT_GREEN = (60, 120, 40)
GOLD = (255, 200, 50)

# ============================================
# Camera
# ============================================
class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.shake = 0
        self.shake_x = 0
        self.shake_y = 0

    def update(self, target_x, target_y):
        self.x += (target_x - WIDTH // 2 - self.x) * 0.1
        self.y += (target_y - HEIGHT // 2 - self.y) * 0.1
        if self.shake > 0:
            self.shake_x = random.uniform(-self.shake, self.shake)
            self.shake_y = random.uniform(-self.shake, self.shake)
            self.shake *= 0.9
            if self.shake < 0.5:
                self.shake = 0
                self.shake_x = 0
                self.shake_y = 0

    def apply(self, x, y):
        return (x - self.x + self.shake_x, y - self.y + self.shake_y)

cam = Camera()

# ============================================
# Particles
# ============================================
particles = []

class Particle:
    def __init__(self, x, y, color, vx=None, vy=None, size=None, life=None):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx or random.uniform(-4, 4)
        self.vy = vy or random.uniform(-4, 4)
        self.size = size or random.uniform(2, 6)
        self.life = life or random.uniform(0.3, 0.8)
        self.max_life = self.life

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.life -= dt
        self.size *= 0.96
        return self.life > 0

    def draw(self, surface, cam):
        alpha = max(0, self.life / self.max_life)
        sx, sy = cam.apply(self.x, self.y)
        if 0 <= sx <= WIDTH and 0 <= sy <= HEIGHT:
            r = int(self.color[0] * alpha)
            g = int(self.color[1] * alpha)
            b = int(self.color[2] * alpha)
            pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy)), max(1, int(self.size)))

def spawn_particles(x, y, color, count=10, speed=4):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed)
        particles.append(Particle(x, y, color, math.cos(angle)*spd, math.sin(angle)*spd))

def spawn_hit_particles(x, y):
    for _ in range(6):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(2, 6)
        particles.append(Particle(x, y, YELLOW, math.cos(angle)*spd, math.sin(angle)*spd, random.uniform(3, 8), 0.3))

# ============================================
# Slash Effect
# ============================================
slash_effects = []

class SlashEffect:
    def __init__(self, x, y, angle, radius=60):
        self.x = x
        self.y = y
        self.angle = angle
        self.radius = radius
        self.life = 0.15
        self.max_life = 0.15

    def update(self, dt):
        self.life -= dt
        return self.life > 0

    def draw(self, surface, cam):
        alpha = self.life / self.max_life
        sx, sy = cam.apply(self.x, self.y)
        # Draw arc slash
        start_angle = self.angle - 0.6
        end_angle = self.angle + 0.6
        points = [(sx, sy)]
        r = self.radius * (1 + (1 - alpha) * 0.3)
        for i in range(12):
            a = start_angle + (end_angle - start_angle) * i / 11
            px = sx + math.cos(a) * r
            py = sy + math.sin(a) * r
            points.append((px, py))
        points.append((sx, sy))
        if len(points) > 2:
            c = int(255 * alpha)
            try:
                pygame.draw.polygon(surface, (c, c, int(c * 0.5)), points, 3)
                # Inner bright line
                inner_points = []
                r2 = r * 0.7
                for i in range(12):
                    a = start_angle + (end_angle - start_angle) * i / 11
                    px = sx + math.cos(a) * r2
                    py = sy + math.sin(a) * r2
                    inner_points.append((int(px), int(py)))
                if len(inner_points) > 1:
                    pygame.draw.lines(surface, (c, c, c), False, inner_points, 2)
            except:
                pass

# ============================================
# Player
# ============================================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.speed = 5
        self.hp = 100
        self.max_hp = 100
        self.angle = 0
        self.attack_cooldown = 0
        self.attack_power = 30
        self.attack_range = 70
        self.attacking = False
        self.attack_timer = 0
        self.dash_cooldown = 0
        self.dashing = False
        self.dash_timer = 0
        self.dash_dx = 0
        self.dash_dy = 0
        self.invincible = 0
        self.ult_ready = True
        self.ult_cooldown = 0
        self.ult_max_cd = 5
        self.flash_timer = 0
        self.trail = []

    def update(self, dt, keys, mx, my):
        # Aim
        sx, sy = cam.apply(self.x, self.y)
        self.angle = math.atan2(my - sy, mx - sx)

        # Dash
        if self.dashing:
            self.dash_timer -= dt
            self.x += self.dash_dx * 12
            self.y += self.dash_dy * 12
            self.trail.append((self.x, self.y, 0.3))
            if self.dash_timer <= 0:
                self.dashing = False
            return

        # Move
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if dx != 0 or dy != 0:
            length = math.sqrt(dx*dx + dy*dy)
            dx /= length
            dy /= length
            self.x += dx * self.speed
            self.y += dy * self.speed

        # Keep in bounds
        self.x = max(50, min(ARENA_W - 50, self.x))
        self.y = max(50, min(ARENA_H - 50, self.y))

        # Cooldowns
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.dash_cooldown > 0:
            self.dash_cooldown -= dt
        if self.invincible > 0:
            self.invincible -= dt
        if self.flash_timer > 0:
            self.flash_timer -= dt
        if not self.ult_ready:
            self.ult_cooldown -= dt
            if self.ult_cooldown <= 0:
                self.ult_ready = True

        # Trail fade
        self.trail = [(x, y, t - dt) for x, y, t in self.trail if t - dt > 0]

    def attack(self, enemies):
        if self.attack_cooldown > 0:
            return
        self.attack_cooldown = 0.25
        self.attacking = True
        self.attack_timer = 0.15

        slash_effects.append(SlashEffect(self.x, self.y, self.angle, self.attack_range))
        cam.shake = 3

        hit = False
        for e in enemies:
            if not e.alive:
                continue
            dist = math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2)
            if dist < self.attack_range + e.radius:
                angle_to = math.atan2(e.y - self.y, e.x - self.x)
                angle_diff = abs(angle_to - self.angle)
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff
                if angle_diff < 1.2:  # Wide arc
                    knockback = 8
                    e.take_damage(self.attack_power, math.cos(self.angle) * knockback, math.sin(self.angle) * knockback)
                    hit = True
                    spawn_hit_particles(e.x, e.y)

        if hit:
            cam.shake = 6

    def dash(self):
        if self.dash_cooldown > 0 or self.dashing:
            return
        self.dashing = True
        self.dash_timer = 0.12
        self.dash_cooldown = 0.8
        self.invincible = 0.2
        self.dash_dx = math.cos(self.angle)
        self.dash_dy = math.sin(self.angle)

    def ultimate(self, enemies):
        if not self.ult_ready:
            return
        self.ult_ready = False
        self.ult_cooldown = self.ult_max_cd
        cam.shake = 15

        # Nuke all nearby enemies
        for e in enemies:
            if not e.alive:
                continue
            dist = math.sqrt((e.x - self.x)**2 + (e.y - self.y)**2)
            if dist < 300:
                angle = math.atan2(e.y - self.y, e.x - self.x)
                e.take_damage(80, math.cos(angle) * 15, math.sin(angle) * 15)
                spawn_particles(e.x, e.y, ORANGE, 15, 6)

        # Big particle explosion
        spawn_particles(self.x, self.y, GOLD, 40, 8)
        spawn_particles(self.x, self.y, RED, 30, 10)

    def take_damage(self, amount):
        if self.invincible > 0 or self.dashing:
            return
        self.hp -= amount
        self.invincible = 0.5
        self.flash_timer = 0.15
        cam.shake = 5
        spawn_particles(self.x, self.y, RED, 8)
        if self.hp <= 0:
            self.hp = 0

    def draw(self, surface, cam):
        # Trail
        for tx, ty, tl in self.trail:
            sx, sy = cam.apply(tx, ty)
            alpha = tl / 0.3
            r = int(self.radius * alpha)
            pygame.draw.circle(surface, (int(100*alpha), int(50*alpha), int(50*alpha)), (int(sx), int(sy)), r)

        sx, sy = cam.apply(self.x, self.y)

        # Body
        body_color = WHITE if self.flash_timer > 0 else RED
        if self.invincible > 0 and int(self.invincible * 20) % 2 == 0:
            body_color = (100, 30, 30)
        pygame.draw.circle(surface, body_color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, DARK_RED, (int(sx), int(sy)), self.radius, 2)

        # Direction indicator (sword line)
        end_x = sx + math.cos(self.angle) * (self.radius + 15)
        end_y = sy + math.sin(self.angle) * (self.radius + 15)
        pygame.draw.line(surface, WHITE, (int(sx), int(sy)), (int(end_x), int(end_y)), 4)
        # Sword tip
        tip_x = sx + math.cos(self.angle) * (self.radius + 22)
        tip_y = sy + math.sin(self.angle) * (self.radius + 22)
        pygame.draw.circle(surface, YELLOW, (int(tip_x), int(tip_y)), 3)

# ============================================
# Enemy
# ============================================
class Enemy:
    def __init__(self, x, y, etype='normal'):
        self.x = x
        self.y = y
        self.etype = etype
        self.alive = True
        self.flash = 0
        self.knockback_x = 0
        self.knockback_y = 0

        if etype == 'normal':
            self.radius = 14
            self.speed = 2
            self.hp = 40
            self.max_hp = 40
            self.power = 8
            self.color = BLUE
            self.score = 100
            self.attack_cd = 1.0
        elif etype == 'fast':
            self.radius = 10
            self.speed = 4.5
            self.hp = 25
            self.max_hp = 25
            self.power = 5
            self.color = YELLOW
            self.score = 150
            self.attack_cd = 0.6
        elif etype == 'tank':
            self.radius = 22
            self.speed = 1.2
            self.hp = 120
            self.max_hp = 120
            self.power = 20
            self.color = PURPLE
            self.score = 300
            self.attack_cd = 1.5
        elif etype == 'boss':
            self.radius = 35
            self.speed = 1.8
            self.hp = 500
            self.max_hp = 500
            self.power = 25
            self.color = (200, 30, 30)
            self.score = 2000
            self.attack_cd = 1.2

        self.base_color = self.color
        self.attack_timer = self.attack_cd

    def update(self, dt, player):
        if not self.alive:
            return

        # Knockback
        if abs(self.knockback_x) > 0.5 or abs(self.knockback_y) > 0.5:
            self.x += self.knockback_x
            self.y += self.knockback_y
            self.knockback_x *= 0.85
            self.knockback_y *= 0.85
        else:
            # Chase player
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > self.radius + player.radius:
                dx /= dist
                dy /= dist
                self.x += dx * self.speed
                self.y += dy * self.speed
            elif self.attack_timer <= 0:
                player.take_damage(self.power)
                self.attack_timer = self.attack_cd

        self.attack_timer -= dt

        # Keep in bounds
        self.x = max(30, min(ARENA_W - 30, self.x))
        self.y = max(30, min(ARENA_H - 30, self.y))

        # Flash recover
        if self.flash > 0:
            self.flash -= dt
            if self.flash <= 0:
                self.color = self.base_color

    def take_damage(self, amount, kx=0, ky=0):
        self.hp -= amount
        self.flash = 0.1
        self.color = WHITE
        self.knockback_x = kx
        self.knockback_y = ky
        if self.hp <= 0:
            self.alive = False
            spawn_particles(self.x, self.y, self.base_color, 15, 5)

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(self.x, self.y)
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, BLACK, (int(sx), int(sy)), self.radius, 2)

            # HP bar
            bar_w = self.radius * 2.5
            bar_h = 4
            bx = sx - bar_w / 2
            by = sy - self.radius - 10
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, BLACK, (int(bx)-1, int(by)-1, int(bar_w)+2, bar_h+2))
            bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
            pygame.draw.rect(surface, bar_color, (int(bx), int(by), int(bar_w * ratio), bar_h))

            # Boss crown
            if self.etype == 'boss':
                pygame.draw.polygon(surface, GOLD, [
                    (int(sx)-10, int(sy)-self.radius-5),
                    (int(sx), int(sy)-self.radius-18),
                    (int(sx)+10, int(sy)-self.radius-5),
                ])

# ============================================
# Game
# ============================================
ARENA_W = 2000
ARENA_H = 2000

# Ground decorations
ground_decorations = []
for _ in range(100):
    ground_decorations.append((
        random.randint(50, ARENA_W - 50),
        random.randint(50, ARENA_H - 50),
        random.randint(3, 8),
        (random.randint(40, 70), random.randint(90, 130), random.randint(30, 60))
    ))

def draw_ground(surface, cam):
    # Fill
    offset_x = -cam.x + cam.shake_x
    offset_y = -cam.y + cam.shake_y
    surface.fill(DARK_GREEN)

    # Grid lines
    grid = 100
    start_x = int(cam.x // grid) * grid
    start_y = int(cam.y // grid) * grid
    for gx in range(start_x - grid, start_x + WIDTH + grid * 2, grid):
        sx, _ = cam.apply(gx, 0)
        pygame.draw.line(surface, (35, 75, 35), (int(sx), 0), (int(sx), HEIGHT), 1)
    for gy in range(start_y - grid, start_y + HEIGHT + grid * 2, grid):
        _, sy = cam.apply(0, gy)
        pygame.draw.line(surface, (35, 75, 35), (0, int(sy)), (WIDTH, int(sy)), 1)

    # Decorations
    for dx, dy, dr, dc in ground_decorations:
        sx, sy = cam.apply(dx, dy)
        if -20 < sx < WIDTH + 20 and -20 < sy < HEIGHT + 20:
            pygame.draw.circle(surface, dc, (int(sx), int(sy)), dr)

    # Arena border
    bx1, by1 = cam.apply(20, 20)
    bx2, by2 = cam.apply(ARENA_W - 20, ARENA_H - 20)
    pygame.draw.rect(surface, (100, 100, 100), (int(bx1), int(by1), int(bx2-bx1), int(by2-by1)), 3)

def draw_ui(surface, player, game_state):
    # HP bar
    bar_x, bar_y = 20, 20
    bar_w, bar_h = 250, 25
    pygame.draw.rect(surface, BLACK, (bar_x-2, bar_y-2, bar_w+4, bar_h+4))
    ratio = max(0, player.hp / player.max_hp)
    bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
    pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(surface, WHITE, (bar_x-2, bar_y-2, bar_w+4, bar_h+4), 2)

    font = pygame.font.SysFont('Arial', 18)
    hp_surf = font.render(f'HP: {int(player.hp)}/{player.max_hp}', True, WHITE)
    surface.blit(hp_surf, (bar_x + 5, bar_y + 2))

    # Score
    score_surf = font.render(f'Score: {game_state["score"]}', True, GOLD)
    surface.blit(score_surf, (20, 55))

    # Kills & Wave
    kill_surf = font.render(f'Kills: {game_state["kills"]}  |  Wave: {game_state["wave"]}/5', True, WHITE)
    surface.blit(kill_surf, (20, 80))

    # Combo
    if game_state['combo'] > 1:
        combo_font = pygame.font.SysFont('Arial', 36, bold=True)
        combo_surf = combo_font.render(f'{game_state["combo"]} COMBO!', True, ORANGE)
        rect = combo_surf.get_rect(center=(WIDTH // 2, 80))
        surface.blit(combo_surf, rect)

    # Ultimate
    if player.ult_ready:
        ult_surf = font.render('[Q] Ultimate: READY', True, CYAN)
    else:
        ult_surf = font.render(f'[Q] Ultimate: {player.ult_cooldown:.1f}s', True, GRAY)
    surface.blit(ult_surf, (20, 105))

    # Dash
    if player.dash_cooldown <= 0:
        dash_surf = font.render('[Space] Dash: READY', True, CYAN)
    else:
        dash_surf = font.render(f'[Space] Dash: {player.dash_cooldown:.1f}s', True, GRAY)
    surface.blit(dash_surf, (20, 130))

    # Enemies remaining
    alive_count = sum(1 for e in game_state.get('enemies', []) if e.alive)
    remain_surf = font.render(f'Enemies: {alive_count}', True, WHITE)
    surface.blit(remain_surf, (20, 155))

    # Controls hint
    hint_font = pygame.font.SysFont('Arial', 14)
    hint_surf = hint_font.render('WASD:Move  Mouse:Aim  LMB:Attack  Space:Dash  Q:Ultimate  R:Reset  ESC:Quit', True, (150, 150, 150))
    surface.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 25))

def spawn_wave(wave, px, py):
    enemies = []
    configs = {
        1: [('normal', 8)],
        2: [('normal', 6), ('fast', 5)],
        3: [('normal', 5), ('fast', 5), ('tank', 3)],
        4: [('normal', 8), ('fast', 6), ('tank', 4)],
        5: [('normal', 5), ('fast', 4), ('tank', 3), ('boss', 1)],
    }
    wave_config = configs.get(wave, configs[5])
    for etype, count in wave_config:
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(300, 600)
            ex = px + math.cos(angle) * dist
            ey = py + math.sin(angle) * dist
            ex = max(50, min(ARENA_W - 50, ex))
            ey = max(50, min(ARENA_H - 50, ey))
            enemies.append(Enemy(ex, ey, etype))
    return enemies

def main():
    player = Player(ARENA_W // 2, ARENA_H // 2)
    game_state = {
        'score': 0,
        'combo': 0,
        'combo_timer': 0,
        'max_combo': 0,
        'kills': 0,
        'wave': 1,
        'game_over': False,
        'victory': False,
        'enemies': [],
    }

    enemies = spawn_wave(1, player.x, player.y)
    game_state['enemies'] = enemies

    wave_msg = "Wave 1!"
    wave_msg_timer = 2.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # Reset
                    player = Player(ARENA_W // 2, ARENA_H // 2)
                    game_state = {
                        'score': 0, 'combo': 0, 'combo_timer': 0,
                        'max_combo': 0, 'kills': 0, 'wave': 1,
                        'game_over': False, 'victory': False, 'enemies': [],
                    }
                    enemies = spawn_wave(1, player.x, player.y)
                    game_state['enemies'] = enemies
                    particles.clear()
                    slash_effects.clear()
                    wave_msg = "Wave 1!"
                    wave_msg_timer = 2.0
                    cam.shake = 0
                    continue

                if not game_state['game_over'] and not game_state['victory']:
                    if event.key == pygame.K_SPACE:
                        player.dash()
                    if event.key == pygame.K_q:
                        player.ultimate(enemies)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not game_state['game_over'] and not game_state['victory']:
                    player.attack(enemies)
                if event.button == 3 and not game_state['game_over'] and not game_state['victory']:
                    player.ultimate(enemies)

        if game_state['game_over'] or game_state['victory']:
            # Draw everything frozen
            draw_ground(screen, cam)
            for e in enemies:
                e.draw(screen, cam)
            player.draw(screen, cam)
            for p in particles[:]:
                p.draw(screen, cam)
            draw_ui(screen, player, game_state)

            # Overlay
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))

            big_font = pygame.font.SysFont('Arial', 48, bold=True)
            med_font = pygame.font.SysFont('Arial', 28)

            if game_state['game_over']:
                t1 = big_font.render('YOU DIED!', True, RED)
            else:
                t1 = big_font.render('VICTORY!', True, GOLD)

            t2 = med_font.render(f'Score: {game_state["score"]}  |  Kills: {game_state["kills"]}  |  Max Combo: {game_state["max_combo"]}', True, WHITE)
            t3 = med_font.render('Press R to Restart', True, (200, 200, 200))

            screen.blit(t1, (WIDTH//2 - t1.get_width()//2, HEIGHT//2 - 60))
            screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2))
            screen.blit(t3, (WIDTH//2 - t3.get_width()//2, HEIGHT//2 + 50))

            pygame.display.flip()
            continue

        # Update
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        player.update(dt, keys, mx, my)
        cam.update(player.x, player.y)

        for e in enemies:
            e.update(dt, player)

        # Check deaths
        for e in enemies:
            if not e.alive and e.score > 0:
                game_state['score'] += e.score * max(1, game_state['combo'])
                game_state['kills'] += 1
                game_state['combo'] += 1
                game_state['combo_timer'] = 2.0
                if game_state['combo'] > game_state['max_combo']:
                    game_state['max_combo'] = game_state['combo']
                e.score = 0  # Don't double count

        # Combo decay
        if game_state['combo'] > 0:
            game_state['combo_timer'] -= dt
            if game_state['combo_timer'] <= 0:
                game_state['combo'] = 0

        # Check wave clear
        alive_count = sum(1 for e in enemies if e.alive)
        if alive_count == 0:
            if game_state['wave'] >= 5:
                game_state['victory'] = True
            else:
                game_state['wave'] += 1
                enemies = spawn_wave(game_state['wave'], player.x, player.y)
                game_state['enemies'] = enemies
                wave_msg = f"Wave {game_state['wave']}!"
                wave_msg_timer = 2.0

        # Player death
        if player.hp <= 0:
            game_state['game_over'] = True

        # Update particles
        particles[:] = [p for p in particles if p.update(dt)]
        slash_effects[:] = [s for s in slash_effects if s.update(dt)]

        # Wave message
        if wave_msg_timer > 0:
            wave_msg_timer -= dt

        # ============ DRAW ============
        draw_ground(screen, cam)

        # Enemies
        for e in enemies:
            e.draw(screen, cam)

        # Player
        player.draw(screen, cam)

        # Slash effects
        for s in slash_effects:
            s.draw(screen, cam)

        # Particles
        for p in particles:
            p.draw(screen, cam)

        # UI
        draw_ui(screen, player, game_state)

        # Wave message
        if wave_msg_timer > 0:
            wave_font = pygame.font.SysFont('Arial', 52, bold=True)
            wave_surf = wave_font.render(wave_msg, True, WHITE)
            alpha = min(1, wave_msg_timer / 0.5) if wave_msg_timer < 0.5 else 1
            rect = wave_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(wave_surf, rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
