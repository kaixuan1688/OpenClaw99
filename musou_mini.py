"""
Musou Mini 2D - Top-Down Hack & Slash v3
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
import struct
import io

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

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
# Sound Generator (no external files needed)
# ============================================
def make_wav(samples, sample_rate=44100):
    """Convert raw samples to a WAV byte buffer."""
    n = len(samples)
    data = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + n * 2, b'WAVE',
        b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
        b'data', n * 2)
    raw = b''.join(struct.pack('<h', max(-32768, min(32767, int(s)))) for s in samples)
    return io.BytesIO(data + raw)

def gen_slash_sound():
    sr = 44100
    dur = 0.15
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        noise = random.uniform(-1, 1)
        sweep = math.sin(2 * math.pi * (800 - t * 4000) * t)
        samples.append((noise * 0.4 + sweep * 0.6) * env * 20000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_hit_sound():
    sr = 44100
    dur = 0.1
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        val = math.sin(2 * math.pi * 200 * t) * env
        val += random.uniform(-0.3, 0.3) * env
        samples.append(val * 25000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_kill_sound():
    sr = 44100
    dur = 0.25
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        freq = 400 + t * 1200
        val = math.sin(2 * math.pi * freq * t) * env
        samples.append(val * 22000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_ult_sound():
    sr = 44100
    dur = 0.5
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        val = math.sin(2 * math.pi * 80 * t) * env
        val += math.sin(2 * math.pi * 160 * t) * env * 0.5
        val += random.uniform(-0.3, 0.3) * env * 0.5
        samples.append(val * 28000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dash_sound():
    sr = 44100
    dur = 0.12
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        freq = 300 + t * 2000
        val = random.uniform(-1, 1) * 0.5 + math.sin(2 * math.pi * freq * t) * 0.5
        samples.append(val * env * 18000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_hurt_sound():
    sr = 44100
    dur = 0.2
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        val = math.sin(2 * math.pi * 150 * t) * env
        val += random.uniform(-0.5, 0.5) * env
        samples.append(val * 20000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_wave_sound():
    sr = 44100
    dur = 0.4
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = min(1, t / 0.05) * max(0, 1 - (t - 0.05) / (dur - 0.05))
        freq = 500 + math.sin(t * 10) * 100
        val = math.sin(2 * math.pi * freq * t) * env
        samples.append(val * 22000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_victory_sound():
    sr = 44100
    dur = 0.8
    samples = []
    notes = [523, 659, 784, 1047]  # C E G C
    for i in range(int(sr * dur)):
        t = i / sr
        note_idx = min(int(t / dur * len(notes)), len(notes) - 1)
        freq = notes[note_idx]
        env = max(0, 1 - (t % (dur / len(notes))) / (dur / len(notes)) * 0.5)
        val = math.sin(2 * math.pi * freq * t) * env
        samples.append(val * 20000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_death_sound():
    sr = 44100
    dur = 0.6
    samples = []
    for i in range(int(sr * dur)):
        t = i / sr
        env = max(0, 1 - t / dur)
        freq = 300 - t * 400
        val = math.sin(2 * math.pi * max(50, freq) * t) * env
        val += random.uniform(-0.3, 0.3) * env
        samples.append(val * 22000)
    return pygame.mixer.Sound(make_wav(samples))

# Generate all sounds
try:
    snd_slash = gen_slash_sound()
    snd_hit = gen_hit_sound()
    snd_kill = gen_kill_sound()
    snd_ult = gen_ult_sound()
    snd_dash = gen_dash_sound()
    snd_hurt = gen_hurt_sound()
    snd_wave = gen_wave_sound()
    snd_victory = gen_victory_sound()
    snd_death = gen_death_sound()
    SOUND_ON = True
except:
    SOUND_ON = False

def play(snd):
    if SOUND_ON:
        snd.play()

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
            self.shake *= 0.88
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
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= dt
        self.size *= 0.97
        return self.life > 0

    def draw(self, surface, cam):
        alpha = max(0, self.life / self.max_life)
        sx, sy = cam.apply(self.x, self.y)
        if 0 <= sx <= WIDTH and 0 <= sy <= HEIGHT:
            r = max(0, min(255, int(self.color[0] * alpha)))
            g = max(0, min(255, int(self.color[1] * alpha)))
            b = max(0, min(255, int(self.color[2] * alpha)))
            pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy)), max(1, int(self.size)))

def spawn_particles(x, y, color, count=10, speed=4):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed)
        particles.append(Particle(x, y, color, math.cos(angle)*spd, math.sin(angle)*spd))

def spawn_hit_particles(x, y):
    for _ in range(8):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(2, 7)
        particles.append(Particle(x, y, YELLOW, math.cos(angle)*spd, math.sin(angle)*spd, random.uniform(3, 8), 0.3))
    for _ in range(4):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, 3)
        particles.append(Particle(x, y, WHITE, math.cos(angle)*spd, math.sin(angle)*spd, random.uniform(2, 4), 0.2))

# ============================================
# Slash Effect
# ============================================
slash_effects = []

class SlashEffect:
    def __init__(self, x, y, angle, radius=65):
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
        start_angle = self.angle - 0.7
        end_angle = self.angle + 0.7
        r = self.radius * (1 + (1 - alpha) * 0.3)

        # Outer arc
        points = []
        for i in range(15):
            a = start_angle + (end_angle - start_angle) * i / 14
            px = sx + math.cos(a) * r
            py = sy + math.sin(a) * r
            points.append((int(px), int(py)))
        if len(points) > 1:
            c = int(255 * alpha)
            pygame.draw.lines(surface, (c, c, int(c * 0.3)), False, points, max(1, int(4 * alpha)))

        # Inner arc
        r2 = r * 0.6
        points2 = []
        for i in range(15):
            a = start_angle + (end_angle - start_angle) * i / 14
            px = sx + math.cos(a) * r2
            py = sy + math.sin(a) * r2
            points2.append((int(px), int(py)))
        if len(points2) > 1:
            c2 = int(200 * alpha)
            pygame.draw.lines(surface, (c2, c2, c2), False, points2, max(1, int(2 * alpha)))

# ============================================
# Ultimate Effect
# ============================================
ult_effects = []

class UltEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0.5
        self.max_life = 0.5
        self.radius = 0

    def update(self, dt):
        self.life -= dt
        progress = 1 - self.life / self.max_life
        self.radius = progress * 320
        return self.life > 0

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        alpha = self.life / self.max_life
        r = int(self.radius)
        if r > 0:
            c = max(0, min(255, int(255 * alpha * 0.5)))
            pygame.draw.circle(surface, (c, int(c * 0.4), 0), (int(sx), int(sy)), r, max(1, int(5 * alpha)))
            pygame.draw.circle(surface, (c, int(c * 0.6), 0), (int(sx), int(sy)), int(r * 0.7), max(1, int(3 * alpha)))

# ============================================
# Player
# ============================================
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 18
        self.speed = 5.5
        self.hp = 100
        self.max_hp = 100
        self.angle = 0
        self.attack_cooldown = 0
        self.attack_power = 30
        self.attack_range = 75
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
        self.move_dx = 0
        self.move_dy = 0

    def update(self, dt, keys, mx, my):
        # Aim toward mouse
        sx, sy = cam.apply(self.x, self.y)
        self.angle = math.atan2(my - sy, mx - sx)

        # Dash movement
        if self.dashing:
            self.dash_timer -= dt
            self.x += self.dash_dx * 14
            self.y += self.dash_dy * 14
            self.trail.append((self.x, self.y, 0.3))
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            # Normal movement — WASD independent of mouse aim
            dx, dy = 0, 0
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                dx /= length
                dy /= length
                self.move_dx = dx
                self.move_dy = dy
                self.x += dx * self.speed
                self.y += dy * self.speed
            else:
                self.move_dx = 0
                self.move_dy = 0

        # Keep in arena
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
        self.attack_cooldown = 0.22
        self.attacking = True
        self.attack_timer = 0.15

        slash_effects.append(SlashEffect(self.x, self.y, self.angle, self.attack_range))
        play(snd_slash)
        cam.shake = 3

        hit = False
        for e in enemies:
            if not e.alive:
                continue
            dist = math.sqrt((e.x - self.x) ** 2 + (e.y - self.y) ** 2)
            if dist < self.attack_range + e.radius:
                angle_to = math.atan2(e.y - self.y, e.x - self.x)
                angle_diff = abs(angle_to - self.angle)
                if angle_diff > math.pi:
                    angle_diff = 2 * math.pi - angle_diff
                if angle_diff < 1.2:
                    knockback = 10
                    e.take_damage(self.attack_power,
                                  math.cos(self.angle) * knockback,
                                  math.sin(self.angle) * knockback)
                    hit = True
                    spawn_hit_particles(e.x, e.y)

        if hit:
            cam.shake = 8
            play(snd_hit)

    def dash(self):
        if self.dash_cooldown > 0 or self.dashing:
            return
        self.dashing = True
        self.dash_timer = 0.12
        self.dash_cooldown = 0.6
        self.invincible = 0.2
        # Dash toward mouse aim direction
        self.dash_dx = math.cos(self.angle)
        self.dash_dy = math.sin(self.angle)
        play(snd_dash)

    def ultimate(self, enemies):
        if not self.ult_ready:
            return
        self.ult_ready = False
        self.ult_cooldown = self.ult_max_cd
        cam.shake = 18
        play(snd_ult)

        ult_effects.append(UltEffect(self.x, self.y))

        for e in enemies:
            if not e.alive:
                continue
            dist = math.sqrt((e.x - self.x) ** 2 + (e.y - self.y) ** 2)
            if dist < 300:
                angle = math.atan2(e.y - self.y, e.x - self.x)
                e.take_damage(80, math.cos(angle) * 18, math.sin(angle) * 18)
                spawn_particles(e.x, e.y, ORANGE, 15, 6)

        spawn_particles(self.x, self.y, GOLD, 50, 10)
        spawn_particles(self.x, self.y, RED, 30, 8)

    def take_damage(self, amount):
        if self.invincible > 0 or self.dashing:
            return
        self.hp -= amount
        self.invincible = 0.5
        self.flash_timer = 0.15
        cam.shake = 5
        spawn_particles(self.x, self.y, RED, 8)
        play(snd_hurt)
        if self.hp <= 0:
            self.hp = 0

    def draw(self, surface, cam):
        # Trail
        for tx, ty, tl in self.trail:
            sx, sy = cam.apply(tx, ty)
            alpha = tl / 0.3
            r = int(self.radius * alpha)
            if r > 0:
                pygame.draw.circle(surface, (int(100 * alpha), int(50 * alpha), int(50 * alpha)),
                                   (int(sx), int(sy)), r)

        sx, sy = cam.apply(self.x, self.y)

        # Body shadow
        pygame.draw.circle(surface, (15, 40, 15), (int(sx) + 3, int(sy) + 3), self.radius)

        # Body
        body_color = WHITE if self.flash_timer > 0 else RED
        if self.invincible > 0 and int(self.invincible * 20) % 2 == 0:
            body_color = (100, 30, 30)
        pygame.draw.circle(surface, body_color, (int(sx), int(sy)), self.radius)
        pygame.draw.circle(surface, DARK_RED, (int(sx), int(sy)), self.radius, 2)

        # Eyes (face mouse direction)
        eye_dist = 7
        eye_angle_l = self.angle + 0.35
        eye_angle_r = self.angle - 0.35
        for ea in [eye_angle_l, eye_angle_r]:
            ex = sx + math.cos(ea) * eye_dist
            ey = sy + math.sin(ea) * eye_dist
            pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), 4)
            pex = ex + math.cos(self.angle) * 2
            pey = ey + math.sin(self.angle) * 2
            pygame.draw.circle(surface, BLACK, (int(pex), int(pey)), 2)

        # Sword
        sword_len = 28
        sword_x = sx + math.cos(self.angle) * (self.radius + 2)
        sword_y = sy + math.sin(self.angle) * (self.radius + 2)
        tip_x = sx + math.cos(self.angle) * (self.radius + sword_len)
        tip_y = sy + math.sin(self.angle) * (self.radius + sword_len)
        pygame.draw.line(surface, (180, 180, 200), (int(sword_x), int(sword_y)), (int(tip_x), int(tip_y)), 4)
        pygame.draw.circle(surface, YELLOW, (int(tip_x), int(tip_y)), 3)

        # Sword guard
        guard_x = sx + math.cos(self.angle) * (self.radius + 4)
        guard_y = sy + math.sin(self.angle) * (self.radius + 4)
        perp = self.angle + math.pi / 2
        g1x = guard_x + math.cos(perp) * 6
        g1y = guard_y + math.sin(perp) * 6
        g2x = guard_x - math.cos(perp) * 6
        g2y = guard_y - math.sin(perp) * 6
        pygame.draw.line(surface, GOLD, (int(g1x), int(g1y)), (int(g2x), int(g2y)), 3)

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
        self.scored = False

        if etype == 'normal':
            self.radius = 14
            self.speed = 2.2
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
            self.color = (220, 40, 40)
            self.score = 2000
            self.attack_cd = 1.2

        self.base_color = self.color
        self.attack_timer = self.attack_cd
        self.wobble = random.uniform(0, math.pi * 2)

    def update(self, dt, player):
        if not self.alive:
            return

        self.wobble += dt * 3

        if self.flash > 0:
            self.flash -= dt
            if self.flash <= 0:
                self.color = self.base_color

        # Knockback
        if abs(self.knockback_x) > 0.5 or abs(self.knockback_y) > 0.5:
            self.x += self.knockback_x
            self.y += self.knockback_y
            self.knockback_x *= 0.82
            self.knockback_y *= 0.82
        else:
            self.knockback_x = 0
            self.knockback_y = 0
            # Chase player
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > self.radius + player.radius:
                dx /= dist
                dy /= dist
                # Slight wobble for natural movement
                wobble_x = math.sin(self.wobble) * 0.3
                wobble_y = math.cos(self.wobble) * 0.3
                self.x += (dx + wobble_x) * self.speed
                self.y += (dy + wobble_y) * self.speed
            elif self.attack_timer <= 0:
                player.take_damage(self.power)
                self.attack_timer = self.attack_cd

        self.attack_timer -= dt
        self.x = max(30, min(ARENA_W - 30, self.x))
        self.y = max(30, min(ARENA_H - 30, self.y))

    def take_damage(self, amount, kx=0, ky=0):
        self.hp -= amount
        self.flash = 0.1
        self.color = WHITE
        self.knockback_x = kx
        self.knockback_y = ky
        if self.hp <= 0:
            self.alive = False
            spawn_particles(self.x, self.y, self.base_color, 20, 6)
            play(snd_kill)

    def draw(self, surface, cam):
        if not self.alive:
            return
        sx, sy = cam.apply(self.x, self.y)
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            # Shadow
            pygame.draw.circle(surface, (15, 40, 15), (int(sx) + 2, int(sy) + 2), self.radius)

            # Body
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, BLACK, (int(sx), int(sy)), self.radius, 2)

            # Angry eyes
            angle_to_player = self.wobble  # Just for eye animation
            for offset in [-0.3, 0.3]:
                ex = sx + math.cos(angle_to_player + offset) * (self.radius * 0.35)
                ey = sy + math.sin(angle_to_player + offset) * (self.radius * 0.35)
                pygame.draw.circle(surface, WHITE, (int(ex), int(ey)), max(2, self.radius // 4))
                pygame.draw.circle(surface, RED if self.etype == 'boss' else BLACK,
                                   (int(ex), int(ey)), max(1, self.radius // 6))

            # HP bar
            bar_w = self.radius * 2.5
            bar_h = 4
            bx = sx - bar_w / 2
            by = sy - self.radius - 12
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, BLACK, (int(bx) - 1, int(by) - 1, int(bar_w) + 2, bar_h + 2))
            bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
            pygame.draw.rect(surface, bar_color, (int(bx), int(by), int(bar_w * ratio), bar_h))

            # Boss crown
            if self.etype == 'boss':
                pts = [
                    (int(sx) - 12, int(sy) - self.radius - 6),
                    (int(sx) - 6, int(sy) - self.radius - 16),
                    (int(sx), int(sy) - self.radius - 10),
                    (int(sx) + 6, int(sy) - self.radius - 16),
                    (int(sx) + 12, int(sy) - self.radius - 6),
                ]
                pygame.draw.polygon(surface, GOLD, pts)
                pygame.draw.polygon(surface, ORANGE, pts, 2)

# ============================================
# Game Setup
# ============================================
ARENA_W = 2000
ARENA_H = 2000

ground_decorations = []
for _ in range(120):
    ground_decorations.append((
        random.randint(50, ARENA_W - 50),
        random.randint(50, ARENA_H - 50),
        random.randint(2, 7),
        (random.randint(35, 60), random.randint(80, 120), random.randint(25, 50))
    ))

# Some trees/rocks
obstacles_deco = []
for _ in range(20):
    obstacles_deco.append((
        random.randint(100, ARENA_W - 100),
        random.randint(100, ARENA_H - 100),
        random.randint(15, 30),
        random.choice([(80, 60, 40), (60, 90, 40), (90, 80, 50)])
    ))

def draw_ground(surface, cam):
    surface.fill(DARK_GREEN)
    grid = 100
    start_x = int(cam.x // grid) * grid
    start_y = int(cam.y // grid) * grid
    for gx in range(start_x - grid, start_x + WIDTH + grid * 2, grid):
        sx, _ = cam.apply(gx, 0)
        pygame.draw.line(surface, (28, 70, 28), (int(sx), 0), (int(sx), HEIGHT), 1)
    for gy in range(start_y - grid, start_y + HEIGHT + grid * 2, grid):
        _, sy = cam.apply(0, gy)
        pygame.draw.line(surface, (28, 70, 28), (0, int(sy)), (WIDTH, int(sy)), 1)

    for dx, dy, dr, dc in ground_decorations:
        sx, sy = cam.apply(dx, dy)
        if -20 < sx < WIDTH + 20 and -20 < sy < HEIGHT + 20:
            pygame.draw.circle(surface, dc, (int(sx), int(sy)), dr)

    for ox, oy, orad, oc in obstacles_deco:
        sx, sy = cam.apply(ox, oy)
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            pygame.draw.circle(surface, (20, 40, 15), (int(sx) + 3, int(sy) + 3), orad)
            pygame.draw.circle(surface, oc, (int(sx), int(sy)), orad)
            pygame.draw.circle(surface, (40, 30, 20), (int(sx), int(sy)), orad, 2)

    bx1, by1 = cam.apply(20, 20)
    bx2, by2 = cam.apply(ARENA_W - 20, ARENA_H - 20)
    pygame.draw.rect(surface, (120, 100, 80), (int(bx1), int(by1), int(bx2 - bx1), int(by2 - by1)), 4)

def draw_ui(surface, player, game_state):
    # HP bar
    bar_x, bar_y = 20, 20
    bar_w, bar_h = 260, 28
    pygame.draw.rect(surface, BLACK, (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4))
    ratio = max(0, player.hp / player.max_hp)
    bar_color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
    pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
    pygame.draw.rect(surface, WHITE, (bar_x - 2, bar_y - 2, bar_w + 4, bar_h + 4), 2)

    font = pygame.font.SysFont('Arial', 18)
    font_bold = pygame.font.SysFont('Arial', 18, bold=True)
    hp_surf = font_bold.render(f'HP: {int(player.hp)}/{player.max_hp}', True, WHITE)
    surface.blit(hp_surf, (bar_x + 8, bar_y + 4))

    score_surf = font_bold.render(f'Score: {game_state["score"]}', True, GOLD)
    surface.blit(score_surf, (20, 58))

    kill_surf = font.render(f'Kills: {game_state["kills"]}  |  Wave: {game_state["wave"]}/5', True, WHITE)
    surface.blit(kill_surf, (20, 82))

    alive_count = sum(1 for e in game_state.get('enemies', []) if e.alive)
    remain_surf = font.render(f'Enemies: {alive_count}', True, WHITE)
    surface.blit(remain_surf, (20, 106))

    # Combo
    if game_state['combo'] > 1:
        combo_font = pygame.font.SysFont('Arial', 42, bold=True)
        combo_surf = combo_font.render(f'{game_state["combo"]} COMBO!', True, ORANGE)
        rect = combo_surf.get_rect(center=(WIDTH // 2, 60))
        # Shadow
        shadow = combo_font.render(f'{game_state["combo"]} COMBO!', True, BLACK)
        surface.blit(shadow, (rect.x + 2, rect.y + 2))
        surface.blit(combo_surf, rect)

    # Skills bar (bottom right)
    skill_y = HEIGHT - 60
    skill_x = WIDTH - 200

    # Ultimate
    if player.ult_ready:
        pygame.draw.rect(surface, CYAN, (skill_x, skill_y, 50, 50), 0, border_radius=8)
        pygame.draw.rect(surface, WHITE, (skill_x, skill_y, 50, 50), 2, border_radius=8)
        q_surf = font_bold.render('Q', True, BLACK)
    else:
        pygame.draw.rect(surface, GRAY, (skill_x, skill_y, 50, 50), 0, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), (skill_x, skill_y, 50, 50), 2, border_radius=8)
        cd_ratio = player.ult_cooldown / player.ult_max_cd
        pygame.draw.rect(surface, (40, 40, 40), (skill_x, skill_y + int(50 * (1 - cd_ratio)), 50, int(50 * cd_ratio)), border_radius=4)
        q_surf = font_bold.render('Q', True, WHITE)
        cd_text = font.render(f'{player.ult_cooldown:.1f}', True, WHITE)
        surface.blit(cd_text, (skill_x + 12, skill_y + 30))
    surface.blit(q_surf, (skill_x + 18, skill_y + 5))

    # Dash
    skill_x2 = skill_x + 60
    if player.dash_cooldown <= 0:
        pygame.draw.rect(surface, (100, 200, 100), (skill_x2, skill_y, 50, 50), 0, border_radius=8)
        pygame.draw.rect(surface, WHITE, (skill_x2, skill_y, 50, 50), 2, border_radius=8)
        sp_surf = font_bold.render('SPC', True, BLACK)
    else:
        pygame.draw.rect(surface, GRAY, (skill_x2, skill_y, 50, 50), 0, border_radius=8)
        pygame.draw.rect(surface, (80, 80, 80), (skill_x2, skill_y, 50, 50), 2, border_radius=8)
        sp_surf = font_bold.render('SPC', True, WHITE)
        cd_text = font.render(f'{player.dash_cooldown:.1f}', True, WHITE)
        surface.blit(cd_text, (skill_x2 + 12, skill_y + 30))
    surface.blit(sp_surf, (skill_x2 + 8, skill_y + 5))

    # Controls hint
    hint_font = pygame.font.SysFont('Arial', 13)
    hint_surf = hint_font.render('WASD:Move  Mouse:Aim  LMB:Attack  Space:Dash  Q:Ultimate  R:Reset', True, (140, 140, 140))
    surface.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 22))

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
            ex = max(60, min(ARENA_W - 60, ex))
            ey = max(60, min(ARENA_H - 60, ey))
            enemies.append(Enemy(ex, ey, etype))
    return enemies

# ============================================
# Main
# ============================================
def main():
    player = Player(ARENA_W // 2, ARENA_H // 2)
    game_state = {
        'score': 0, 'combo': 0, 'combo_timer': 0,
        'max_combo': 0, 'kills': 0, 'wave': 1,
        'game_over': False, 'victory': False, 'enemies': [],
    }

    enemies = spawn_wave(1, player.x, player.y)
    game_state['enemies'] = enemies

    wave_msg = "Wave 1!"
    wave_msg_timer = 2.0
    play(snd_wave)

    death_sound_played = False
    victory_sound_played = False

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
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
                    ult_effects.clear()
                    wave_msg = "Wave 1!"
                    wave_msg_timer = 2.0
                    cam.shake = 0
                    death_sound_played = False
                    victory_sound_played = False
                    play(snd_wave)
                    continue

                if not game_state['game_over'] and not game_state['victory']:
                    if event.key == pygame.K_SPACE:
                        player.dash()
                    if event.key == pygame.K_q:
                        player.ultimate(enemies)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_state['game_over'] and not game_state['victory']:
                    if event.button == 1:
                        player.attack(enemies)
                    if event.button == 3:
                        player.ultimate(enemies)

        # Game over / victory screen
        if game_state['game_over'] or game_state['victory']:
            if game_state['game_over'] and not death_sound_played:
                play(snd_death)
                death_sound_played = True
            if game_state['victory'] and not victory_sound_played:
                play(snd_victory)
                victory_sound_played = True

            # Update particles
            particles[:] = [p for p in particles if p.update(dt)]

            draw_ground(screen, cam)
            for e in enemies:
                e.draw(screen, cam)
            player.draw(screen, cam)
            for p in particles:
                p.draw(screen, cam)
            draw_ui(screen, player, game_state)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))

            big_font = pygame.font.SysFont('Arial', 52, bold=True)
            med_font = pygame.font.SysFont('Arial', 26)

            if game_state['game_over']:
                t1 = big_font.render('YOU DIED!', True, RED)
            else:
                t1 = big_font.render('VICTORY!', True, GOLD)

            t2 = med_font.render(f'Score: {game_state["score"]}  |  Kills: {game_state["kills"]}  |  Max Combo: {game_state["max_combo"]}', True, WHITE)
            t3 = med_font.render('Press R to Restart', True, (200, 200, 200))

            # Shadow text
            t1s = big_font.render(t1.get_at((0, 0)) and 'YOU DIED!' if game_state['game_over'] else 'VICTORY!', True, BLACK)
            screen.blit(t1s, (WIDTH // 2 - t1.get_width() // 2 + 3, HEIGHT // 2 - 63))
            screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 66))
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2))
            screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 45))

            pygame.display.flip()
            continue

        # Update
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        player.update(dt, keys, mx, my)
        cam.update(player.x, player.y)

        for e in enemies:
            e.update(dt, player)

        # Score kills
        for e in enemies:
            if not e.alive and not e.scored:
                e.scored = True
                game_state['score'] += e.score * max(1, game_state['combo'])
                game_state['kills'] += 1
                game_state['combo'] += 1
                game_state['combo_timer'] = 2.0
                if game_state['combo'] > game_state['max_combo']:
                    game_state['max_combo'] = game_state['combo']

        # Combo decay
        if game_state['combo'] > 0:
            game_state['combo_timer'] -= dt
            if game_state['combo_timer'] <= 0:
                game_state['combo'] = 0

        # Wave clear
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
                play(snd_wave)

        if player.hp <= 0:
            game_state['game_over'] = True

        # Update effects
        particles[:] = [p for p in particles if p.update(dt)]
        slash_effects[:] = [s for s in slash_effects if s.update(dt)]
        ult_effects[:] = [u for u in ult_effects if u.update(dt)]

        if wave_msg_timer > 0:
            wave_msg_timer -= dt

        # ====== DRAW ======
        draw_ground(screen, cam)

        for e in enemies:
            e.draw(screen, cam)

        player.draw(screen, cam)

        for s in slash_effects:
            s.draw(screen, cam)
        for u in ult_effects:
            u.draw(screen, cam)
        for p in particles:
            p.draw(screen, cam)

        draw_ui(screen, player, game_state)

        if wave_msg_timer > 0:
            wave_font = pygame.font.SysFont('Arial', 56, bold=True)
            wave_surf = wave_font.render(wave_msg, True, WHITE)
            shadow = wave_font.render(wave_msg, True, BLACK)
            rect = wave_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            screen.blit(shadow, (rect.x + 3, rect.y + 3))
            screen.blit(wave_surf, rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
