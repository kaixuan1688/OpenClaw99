"""
Musou Mini 2D - Dark Fantasy Hack & Slash v4
by B5 (Boom Fifth)

WASD/Arrows - Move
Mouse - Aim
LMB - Attack
RMB / Q - Ultimate
Space - Dash
F - Heal (3 charges)
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
pygame.display.set_caption("Musou Mini - Dark Fantasy")
clock = pygame.time.Clock()

# Dark Fantasy Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLOOD_RED = (180, 20, 20)
DARK_RED = (120, 10, 10)
CRIMSON = (160, 30, 40)
BONE_WHITE = (220, 210, 190)
DARK_GOLD = (180, 150, 40)
GOLD = (220, 190, 60)
SHADOW_PURPLE = (60, 20, 80)
DEMON_BLUE = (30, 40, 160)
GHOST_GREEN = (40, 180, 80)
POISON_GREEN = (100, 200, 40)
HELL_ORANGE = (220, 100, 20)
FIRE_YELLOW = (255, 200, 40)
DARK_GRAY = (30, 28, 32)
MID_GRAY = (50, 48, 55)
ASH_GRAY = (80, 75, 85)
VOID_BLACK = (8, 5, 12)
SOUL_CYAN = (60, 200, 220)
CORRUPT_PURPLE = (140, 40, 180)

# ============================================
# Sound Generator
# ============================================
def make_wav(samples, sample_rate=44100):
    n = len(samples)
    data = struct.pack('<4sI4s4sIHHIIHH4sI',
        b'RIFF', 36 + n * 2, b'WAVE',
        b'fmt ', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16,
        b'data', n * 2)
    raw = b''.join(struct.pack('<h', max(-32768, min(32767, int(s)))) for s in samples)
    return io.BytesIO(data + raw)

def gen_dark_slash():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.18)):
        t = i / sr
        env = max(0, 1 - t / 0.18) ** 0.5
        noise = random.uniform(-1, 1)
        sweep = math.sin(2 * math.pi * (600 - t * 3000) * t)
        low = math.sin(2 * math.pi * 80 * t) * 0.3
        samples.append((noise * 0.3 + sweep * 0.5 + low) * env * 22000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_hit():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.12)):
        t = i / sr
        env = max(0, 1 - t / 0.12)
        val = math.sin(2 * math.pi * 120 * t) * env
        val += math.sin(2 * math.pi * 60 * t) * env * 0.5
        val += random.uniform(-0.4, 0.4) * env
        samples.append(val * 28000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_kill():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.3)):
        t = i / sr
        env = max(0, 1 - t / 0.3)
        freq = 200 + t * 600
        val = math.sin(2 * math.pi * freq * t) * env * 0.6
        val += math.sin(2 * math.pi * 100 * t) * env * 0.4
        val += random.uniform(-0.2, 0.2) * env
        samples.append(val * 24000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_ult():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.6)):
        t = i / sr
        env = max(0, 1 - t / 0.6) ** 0.7
        val = math.sin(2 * math.pi * 50 * t) * env
        val += math.sin(2 * math.pi * 100 * t) * env * 0.6
        val += math.sin(2 * math.pi * 200 * t) * env * 0.3
        val += random.uniform(-0.4, 0.4) * env * 0.4
        samples.append(val * 30000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_dash():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.1)):
        t = i / sr
        env = max(0, 1 - t / 0.1)
        val = random.uniform(-1, 1) * 0.6 + math.sin(2 * math.pi * (500 + t * 1500) * t) * 0.4
        samples.append(val * env * 16000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_hurt():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.25)):
        t = i / sr
        env = max(0, 1 - t / 0.25)
        val = math.sin(2 * math.pi * 100 * t) * env
        val += random.uniform(-0.6, 0.6) * env * 0.5
        val += math.sin(2 * math.pi * 50 * t) * env * 0.3
        samples.append(val * 22000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_wave():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.5)):
        t = i / sr
        env = min(1, t / 0.05) * max(0, 1 - (t - 0.05) / 0.45) ** 0.5
        val = math.sin(2 * math.pi * 300 * t) * env * 0.5
        val += math.sin(2 * math.pi * 150 * t) * env * 0.5
        samples.append(val * 22000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_victory():
    sr = 44100
    samples = []
    notes = [392, 494, 587, 784]
    dur = 1.0
    for i in range(int(sr * dur)):
        t = i / sr
        idx = min(int(t / dur * len(notes)), len(notes) - 1)
        freq = notes[idx]
        env = max(0, 1 - (t % (dur / len(notes))) / (dur / len(notes)) * 0.3)
        val = math.sin(2 * math.pi * freq * t) * env
        val += math.sin(2 * math.pi * freq * 2 * t) * env * 0.3
        samples.append(val * 20000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_dark_death():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.8)):
        t = i / sr
        env = max(0, 1 - t / 0.8) ** 0.5
        freq = 250 - t * 280
        val = math.sin(2 * math.pi * max(30, freq) * t) * env
        val += random.uniform(-0.4, 0.4) * env * 0.5
        val += math.sin(2 * math.pi * 40 * t) * env * 0.3
        samples.append(val * 24000)
    return pygame.mixer.Sound(make_wav(samples))

def gen_heal():
    sr = 44100
    samples = []
    for i in range(int(sr * 0.4)):
        t = i / sr
        env = min(1, t / 0.05) * max(0, 1 - t / 0.4)
        freq = 600 + t * 400
        val = math.sin(2 * math.pi * freq * t) * env
        val += math.sin(2 * math.pi * freq * 1.5 * t) * env * 0.3
        samples.append(val * 18000)
    return pygame.mixer.Sound(make_wav(samples))

try:
    snd_slash = gen_dark_slash()
    snd_hit = gen_dark_hit()
    snd_kill = gen_dark_kill()
    snd_ult = gen_dark_ult()
    snd_dash = gen_dark_dash()
    snd_hurt = gen_dark_hurt()
    snd_wave = gen_dark_wave()
    snd_victory = gen_dark_victory()
    snd_death = gen_dark_death()
    snd_heal = gen_heal()
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
        self.x += (target_x - WIDTH // 2 - self.x) * 0.08
        self.y += (target_y - HEIGHT // 2 - self.y) * 0.08
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
    def __init__(self, x, y, color, vx=None, vy=None, size=None, life=None, glow=False):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx or random.uniform(-4, 4)
        self.vy = vy or random.uniform(-4, 4)
        self.size = size or random.uniform(2, 6)
        self.life = life or random.uniform(0.3, 0.8)
        self.max_life = self.life
        self.glow = glow

    def update(self, dt):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= dt
        self.size *= 0.97
        return self.life > 0 and self.size > 0.3

    def draw(self, surface, cam):
        alpha = max(0, self.life / self.max_life)
        sx, sy = cam.apply(self.x, self.y)
        if 0 <= sx <= WIDTH and 0 <= sy <= HEIGHT:
            r = max(0, min(255, int(self.color[0] * alpha)))
            g = max(0, min(255, int(self.color[1] * alpha)))
            b = max(0, min(255, int(self.color[2] * alpha)))
            s = max(1, int(self.size))
            if self.glow and s > 2:
                pygame.draw.circle(surface, (r // 3, g // 3, b // 3), (int(sx), int(sy)), s + 3)
            pygame.draw.circle(surface, (r, g, b), (int(sx), int(sy)), s)

def spawn_particles(x, y, color, count=10, speed=4, glow=False):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(1, speed)
        particles.append(Particle(x, y, color, math.cos(angle)*spd, math.sin(angle)*spd, glow=glow))

def spawn_blood(x, y, count=12):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(2, 7)
        c = random.choice([BLOOD_RED, DARK_RED, CRIMSON, (200, 30, 30)])
        particles.append(Particle(x, y, c, math.cos(angle)*spd, math.sin(angle)*spd,
                                  random.uniform(2, 6), random.uniform(0.3, 0.6)))

def spawn_soul(x, y, count=8):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        spd = random.uniform(0.5, 2)
        particles.append(Particle(x, y, SOUL_CYAN, math.cos(angle)*spd, math.sin(angle)*spd - 1,
                                  random.uniform(2, 5), random.uniform(0.5, 1.2), glow=True))

# ============================================
# Slash Effect
# ============================================
slash_effects = []

class SlashEffect:
    def __init__(self, x, y, angle, radius=70):
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

        points = []
        for i in range(16):
            a = start_angle + (end_angle - start_angle) * i / 15
            px = sx + math.cos(a) * r
            py = sy + math.sin(a) * r
            points.append((int(px), int(py)))
        if len(points) > 1:
            c = int(220 * alpha)
            pygame.draw.lines(surface, (c, int(c * 0.3), int(c * 0.1)), False, points, max(1, int(5 * alpha)))
            r2 = r * 0.65
            points2 = []
            for i in range(16):
                a = start_angle + (end_angle - start_angle) * i / 15
                points2.append((int(sx + math.cos(a) * r2), int(sy + math.sin(a) * r2)))
            pygame.draw.lines(surface, (c, int(c * 0.6), int(c * 0.2)), False, points2, max(1, int(3 * alpha)))

# ============================================
# Effects
# ============================================
ult_effects = []

class UltEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 0.6
        self.max_life = 0.6
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
            c = max(0, min(255, int(200 * alpha)))
            pygame.draw.circle(surface, (c, int(c * 0.2), 0), (int(sx), int(sy)), r, max(1, int(6 * alpha)))
            pygame.draw.circle(surface, (c, int(c * 0.4), int(c * 0.1)), (int(sx), int(sy)), int(r * 0.6), max(1, int(3 * alpha)))
            pygame.draw.circle(surface, (int(c * 0.5), 0, int(c * 0.3)), (int(sx), int(sy)), int(r * 0.3), max(1, int(2 * alpha)))

# Floating damage numbers
dmg_texts = []

class DmgText:
    def __init__(self, x, y, text, color=FIRE_YELLOW):
        self.x = x + random.uniform(-10, 10)
        self.y = y
        self.text = text
        self.color = color
        self.life = 0.8
        self.max_life = 0.8

    def update(self, dt):
        self.y -= 40 * dt
        self.life -= dt
        return self.life > 0

    def draw(self, surface, cam):
        sx, sy = cam.apply(self.x, self.y)
        alpha = min(1, self.life / self.max_life * 2)
        font = pygame.font.SysFont('Arial', 20, bold=True)
        r = max(0, min(255, int(self.color[0] * alpha)))
        g = max(0, min(255, int(self.color[1] * alpha)))
        b = max(0, min(255, int(self.color[2] * alpha)))
        shadow = font.render(self.text, True, BLACK)
        surface.blit(shadow, (int(sx) + 1, int(sy) + 1))
        txt = font.render(self.text, True, (r, g, b))
        surface.blit(txt, (int(sx), int(sy)))

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
        self.attack_power = 35
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
        self.heals = 3
        self.souls = 0
        self.aura_timer = 0

    def update(self, dt, keys, mx, my):
        sx, sy = cam.apply(self.x, self.y)
        self.angle = math.atan2(my - sy, mx - sx)
        self.aura_timer += dt

        if self.dashing:
            self.dash_timer -= dt
            self.x += self.dash_dx * 14
            self.y += self.dash_dy * 14
            self.trail.append((self.x, self.y, 0.3))
            if random.random() < 0.5:
                particles.append(Particle(self.x, self.y, SHADOW_PURPLE,
                    random.uniform(-2, 2), random.uniform(-2, 2), 4, 0.3, glow=True))
            if self.dash_timer <= 0:
                self.dashing = False
        else:
            dx, dy = 0, 0
            if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
            if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
            if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
            if dx != 0 or dy != 0:
                length = math.sqrt(dx * dx + dy * dy)
                self.x += (dx / length) * self.speed
                self.y += (dy / length) * self.speed

        self.x = max(50, min(ARENA_W - 50, self.x))
        self.y = max(50, min(ARENA_H - 50, self.y))

        if self.attack_cooldown > 0: self.attack_cooldown -= dt
        if self.dash_cooldown > 0: self.dash_cooldown -= dt
        if self.invincible > 0: self.invincible -= dt
        if self.flash_timer > 0: self.flash_timer -= dt
        if not self.ult_ready:
            self.ult_cooldown -= dt
            if self.ult_cooldown <= 0:
                self.ult_ready = True

        self.trail = [(x, y, t - dt) for x, y, t in self.trail if t - dt > 0]

    def attack(self, enemies):
        if self.attack_cooldown > 0:
            return
        self.attack_cooldown = 0.2
        slash_effects.append(SlashEffect(self.x, self.y, self.angle, self.attack_range))
        play(snd_slash)
        cam.shake = 3
        hit = False
        for e in enemies:
            if not e.alive: continue
            dist = math.sqrt((e.x - self.x) ** 2 + (e.y - self.y) ** 2)
            if dist < self.attack_range + e.radius:
                angle_to = math.atan2(e.y - self.y, e.x - self.x)
                diff = abs(angle_to - self.angle)
                if diff > math.pi: diff = 2 * math.pi - diff
                if diff < 1.2:
                    kb = 10
                    e.take_damage(self.attack_power, math.cos(self.angle) * kb, math.sin(self.angle) * kb)
                    hit = True
                    spawn_blood(e.x, e.y, 8)
                    dmg_texts.append(DmgText(e.x, e.y - e.radius, str(self.attack_power)))
        if hit:
            cam.shake = 8
            play(snd_hit)

    def dash(self):
        if self.dash_cooldown > 0 or self.dashing: return
        self.dashing = True
        self.dash_timer = 0.12
        self.dash_cooldown = 0.6
        self.invincible = 0.2
        self.dash_dx = math.cos(self.angle)
        self.dash_dy = math.sin(self.angle)
        play(snd_dash)

    def heal(self):
        if self.heals <= 0 or self.hp >= self.max_hp: return
        self.heals -= 1
        heal_amount = 35
        self.hp = min(self.max_hp, self.hp + heal_amount)
        play(snd_heal)
        spawn_particles(self.x, self.y, GHOST_GREEN, 20, 4, glow=True)
        dmg_texts.append(DmgText(self.x, self.y - self.radius, f'+{heal_amount}', GHOST_GREEN))

    def ultimate(self, enemies):
        if not self.ult_ready: return
        self.ult_ready = False
        self.ult_cooldown = self.ult_max_cd
        cam.shake = 20
        play(snd_ult)
        ult_effects.append(UltEffect(self.x, self.y))
        for e in enemies:
            if not e.alive: continue
            dist = math.sqrt((e.x - self.x) ** 2 + (e.y - self.y) ** 2)
            if dist < 300:
                angle = math.atan2(e.y - self.y, e.x - self.x)
                e.take_damage(90, math.cos(angle) * 18, math.sin(angle) * 18)
                spawn_blood(e.x, e.y, 15)
                dmg_texts.append(DmgText(e.x, e.y - e.radius, '90', HELL_ORANGE))
        spawn_particles(self.x, self.y, HELL_ORANGE, 50, 10, glow=True)
        spawn_particles(self.x, self.y, BLOOD_RED, 30, 8)

    def take_damage(self, amount):
        if self.invincible > 0 or self.dashing: return
        self.hp -= amount
        self.invincible = 0.5
        self.flash_timer = 0.15
        cam.shake = 6
        spawn_blood(self.x, self.y, 10)
        play(snd_hurt)
        if self.hp <= 0: self.hp = 0

    def draw(self, surface, cam):
        # Dark aura
        sx, sy = cam.apply(self.x, self.y)
        aura_r = self.radius + 8 + math.sin(self.aura_timer * 3) * 3
        pygame.draw.circle(surface, (20, 5, 30), (int(sx), int(sy)), int(aura_r))

        # Trail
        for tx, ty, tl in self.trail:
            tsx, tsy = cam.apply(tx, ty)
            alpha = tl / 0.3
            r = int(self.radius * alpha)
            if r > 0:
                pygame.draw.circle(surface, (int(60 * alpha), int(10 * alpha), int(30 * alpha)),
                                   (int(tsx), int(tsy)), r)

        # Body
        body_color = WHITE if self.flash_timer > 0 else CRIMSON
        if self.invincible > 0 and int(self.invincible * 20) % 2 == 0:
            body_color = (80, 20, 30)

        # Shadow
        pygame.draw.circle(surface, (10, 5, 15), (int(sx) + 3, int(sy) + 3), self.radius)
        pygame.draw.circle(surface, body_color, (int(sx), int(sy)), self.radius)
        # Dark outline
        pygame.draw.circle(surface, (40, 10, 20), (int(sx), int(sy)), self.radius, 2)

        # Glowing eyes
        eye_dist = 7
        for offset in [0.35, -0.35]:
            ea = self.angle + offset
            ex = sx + math.cos(ea) * eye_dist
            ey = sy + math.sin(ea) * eye_dist
            # Glow
            pygame.draw.circle(surface, (80, 0, 0), (int(ex), int(ey)), 5)
            pygame.draw.circle(surface, BLOOD_RED, (int(ex), int(ey)), 4)
            pygame.draw.circle(surface, FIRE_YELLOW, (int(ex), int(ey)), 2)

        # Dark sword
        sword_start_x = sx + math.cos(self.angle) * (self.radius + 2)
        sword_start_y = sy + math.sin(self.angle) * (self.radius + 2)
        tip_x = sx + math.cos(self.angle) * (self.radius + 30)
        tip_y = sy + math.sin(self.angle) * (self.radius + 30)
        # Blade glow
        pygame.draw.line(surface, (60, 20, 20), (int(sword_start_x), int(sword_start_y)),
                         (int(tip_x), int(tip_y)), 6)
        pygame.draw.line(surface, (160, 140, 160), (int(sword_start_x), int(sword_start_y)),
                         (int(tip_x), int(tip_y)), 3)
        # Runes on blade
        mid_x = (sword_start_x + tip_x) / 2
        mid_y = (sword_start_y + tip_y) / 2
        glow_c = int(abs(math.sin(self.aura_timer * 5)) * 200)
        pygame.draw.circle(surface, (glow_c, int(glow_c * 0.2), 0), (int(mid_x), int(mid_y)), 3)
        # Tip
        pygame.draw.circle(surface, BLOOD_RED, (int(tip_x), int(tip_y)), 3)
        # Guard
        guard_x = sx + math.cos(self.angle) * (self.radius + 4)
        guard_y = sy + math.sin(self.angle) * (self.radius + 4)
        perp = self.angle + math.pi / 2
        pygame.draw.line(surface, DARK_GOLD,
                         (int(guard_x + math.cos(perp) * 7), int(guard_y + math.sin(perp) * 7)),
                         (int(guard_x - math.cos(perp) * 7), int(guard_y - math.sin(perp) * 7)), 3)

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
        self.wobble = random.uniform(0, math.pi * 2)

        if etype == 'normal':
            self.radius = 14
            self.speed = 2.2
            self.hp = 40
            self.max_hp = 40
            self.power = 8
            self.color = (40, 50, 140)
            self.score = 100
            self.attack_cd = 1.0
        elif etype == 'fast':
            self.radius = 11
            self.speed = 4.5
            self.hp = 25
            self.max_hp = 25
            self.power = 6
            self.color = (150, 180, 30)
            self.score = 150
            self.attack_cd = 0.6
        elif etype == 'tank':
            self.radius = 24
            self.speed = 1.2
            self.hp = 130
            self.max_hp = 130
            self.power = 22
            self.color = SHADOW_PURPLE
            self.score = 300
            self.attack_cd = 1.5
        elif etype == 'boss':
            self.radius = 38
            self.speed = 1.8
            self.hp = 600
            self.max_hp = 600
            self.power = 28
            self.color = (180, 20, 20)
            self.score = 2000
            self.attack_cd = 1.0

        self.base_color = self.color
        self.attack_timer = self.attack_cd

    def update(self, dt, player):
        if not self.alive: return
        self.wobble += dt * 3
        if self.flash > 0:
            self.flash -= dt
            if self.flash <= 0: self.color = self.base_color

        if abs(self.knockback_x) > 0.5 or abs(self.knockback_y) > 0.5:
            self.x += self.knockback_x
            self.y += self.knockback_y
            self.knockback_x *= 0.82
            self.knockback_y *= 0.82
        else:
            self.knockback_x = 0
            self.knockback_y = 0
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > self.radius + player.radius:
                dx /= dist
                dy /= dist
                wx = math.sin(self.wobble) * 0.3
                wy = math.cos(self.wobble) * 0.3
                self.x += (dx + wx) * self.speed
                self.y += (dy + wy) * self.speed
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
            spawn_blood(self.x, self.y, 20)
            spawn_soul(self.x, self.y, 6)
            play(snd_kill)

    def draw(self, surface, cam):
        if not self.alive: return
        sx, sy = cam.apply(self.x, self.y)
        if -50 < sx < WIDTH + 50 and -50 < sy < HEIGHT + 50:
            # Shadow
            pygame.draw.circle(surface, (8, 5, 12), (int(sx) + 3, int(sy) + 3), self.radius)
            # Body
            pygame.draw.circle(surface, self.color, (int(sx), int(sy)), self.radius)
            pygame.draw.circle(surface, BLACK, (int(sx), int(sy)), self.radius, 2)

            # Evil eyes
            angle = math.atan2(math.sin(self.wobble), math.cos(self.wobble))
            for offset in [-0.3, 0.3]:
                ea = angle + offset
                ex = sx + math.cos(ea) * (self.radius * 0.35)
                ey = sy + math.sin(ea) * (self.radius * 0.35)
                eye_r = max(2, self.radius // 4)
                pygame.draw.circle(surface, (200, 50, 30) if self.etype == 'boss' else (180, 180, 40),
                                   (int(ex), int(ey)), eye_r)
                pygame.draw.circle(surface, BLACK, (int(ex), int(ey)), max(1, eye_r // 2))

            # HP bar
            bar_w = self.radius * 2.5
            bar_h = 4
            bx = sx - bar_w / 2
            by = sy - self.radius - 12
            ratio = max(0, self.hp / self.max_hp)
            pygame.draw.rect(surface, BLACK, (int(bx) - 1, int(by) - 1, int(bar_w) + 2, bar_h + 2))
            bar_color = GHOST_GREEN if ratio > 0.5 else FIRE_YELLOW if ratio > 0.25 else BLOOD_RED
            pygame.draw.rect(surface, bar_color, (int(bx), int(by), int(bar_w * ratio), bar_h))

            # Boss skull crown
            if self.etype == 'boss':
                # Horns
                for side in [-1, 1]:
                    hx = sx + side * 15
                    hy = sy - self.radius - 5
                    pygame.draw.line(surface, BONE_WHITE, (int(hx), int(hy)),
                                     (int(hx + side * 8), int(hy - 18)), 3)
                    pygame.draw.circle(surface, BLOOD_RED, (int(hx + side * 8), int(hy - 18)), 3)
                # Crown
                pygame.draw.rect(surface, DARK_GOLD, (int(sx) - 10, int(sy) - self.radius - 8, 20, 6))

# ============================================
# Arena
# ============================================
ARENA_W = 2200
ARENA_H = 2200

ground_deco = []
for _ in range(80):
    ground_deco.append(('dot', random.randint(50, ARENA_W - 50), random.randint(50, ARENA_H - 50),
                         random.randint(2, 5), (random.randint(15, 30), random.randint(20, 40), random.randint(15, 25))))
# Bones
for _ in range(25):
    ground_deco.append(('bone', random.randint(100, ARENA_W - 100), random.randint(100, ARENA_H - 100),
                         random.uniform(0, math.pi), BONE_WHITE))
# Blood stains
for _ in range(15):
    ground_deco.append(('blood', random.randint(100, ARENA_W - 100), random.randint(100, ARENA_H - 100),
                         random.randint(8, 20), DARK_RED))
# Dead trees
trees = []
for _ in range(12):
    trees.append((random.randint(150, ARENA_W - 150), random.randint(150, ARENA_H - 150),
                  random.randint(15, 25)))
# Tombstones
tombs = []
for _ in range(8):
    tombs.append((random.randint(150, ARENA_W - 150), random.randint(150, ARENA_H - 150),
                  random.uniform(0, 0.3) - 0.15))

# Fog particles (ambient)
fog = []
for _ in range(40):
    fog.append([random.uniform(0, ARENA_W), random.uniform(0, ARENA_H),
                random.uniform(30, 80), random.uniform(0.3, 0.8), random.uniform(-0.3, 0.3), random.uniform(-0.2, 0.2)])

def draw_ground(surface, cam, dt):
    surface.fill(VOID_BLACK)

    # Subtle grid (dungeon tiles)
    grid = 80
    start_x = int(cam.x // grid) * grid
    start_y = int(cam.y // grid) * grid
    for gx in range(start_x - grid, start_x + WIDTH + grid * 2, grid):
        sx, _ = cam.apply(gx, 0)
        pygame.draw.line(surface, (15, 12, 20), (int(sx), 0), (int(sx), HEIGHT), 1)
    for gy in range(start_y - grid, start_y + HEIGHT + grid * 2, grid):
        _, sy = cam.apply(0, gy)
        pygame.draw.line(surface, (15, 12, 20), (0, int(sy)), (WIDTH, int(sy)), 1)

    # Ground decorations
    for deco in ground_deco:
        if deco[0] == 'dot':
            sx, sy = cam.apply(deco[1], deco[2])
            if -20 < sx < WIDTH + 20 and -20 < sy < HEIGHT + 20:
                pygame.draw.circle(surface, deco[4], (int(sx), int(sy)), deco[3])
        elif deco[0] == 'bone':
            sx, sy = cam.apply(deco[1], deco[2])
            if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
                angle = deco[3]
                l = 12
                x1 = sx + math.cos(angle) * l
                y1 = sy + math.sin(angle) * l
                x2 = sx - math.cos(angle) * l
                y2 = sy - math.sin(angle) * l
                pygame.draw.line(surface, (60, 55, 45), (int(x1), int(y1)), (int(x2), int(y2)), 2)
                pygame.draw.circle(surface, (60, 55, 45), (int(x1), int(y1)), 3)
                pygame.draw.circle(surface, (60, 55, 45), (int(x2), int(y2)), 3)
        elif deco[0] == 'blood':
            sx, sy = cam.apply(deco[1], deco[2])
            if -30 < sx < WIDTH + 30 and -30 < sy < HEIGHT + 30:
                pygame.draw.circle(surface, (40, 8, 8), (int(sx), int(sy)), deco[3])

    # Dead trees
    for tx, ty, tr in trees:
        sx, sy = cam.apply(tx, ty)
        if -60 < sx < WIDTH + 60 and -60 < sy < HEIGHT + 60:
            # Trunk
            pygame.draw.line(surface, (40, 30, 25), (int(sx), int(sy)), (int(sx), int(sy) - 40), 4)
            # Branches
            for bangle, blen in [(-0.8, 20), (0.6, 18), (-0.3, 15), (1.0, 12)]:
                bx = sx + math.cos(bangle - math.pi/2) * blen
                by = sy - 25 + math.sin(bangle - math.pi/2) * blen
                pygame.draw.line(surface, (35, 25, 20), (int(sx), int(sy) - 25), (int(bx), int(by)), 2)

    # Tombstones
    for tx, ty, tilt in tombs:
        sx, sy = cam.apply(tx, ty)
        if -40 < sx < WIDTH + 40 and -40 < sy < HEIGHT + 40:
            pts = [
                (int(sx - 8 + tilt * 5), int(sy)),
                (int(sx - 8 + tilt * 10), int(sy - 22)),
                (int(sx + tilt * 12), int(sy - 28)),
                (int(sx + 8 + tilt * 10), int(sy - 22)),
                (int(sx + 8 + tilt * 5), int(sy)),
            ]
            pygame.draw.polygon(surface, ASH_GRAY, pts)
            pygame.draw.polygon(surface, (40, 38, 45), pts, 2)

    # Fog
    for f in fog:
        f[0] += f[4]
        f[1] += f[5]
        if f[0] < -100: f[0] = ARENA_W + 100
        if f[0] > ARENA_W + 100: f[0] = -100
        if f[1] < -100: f[1] = ARENA_H + 100
        if f[1] > ARENA_H + 100: f[1] = -100
        sx, sy = cam.apply(f[0], f[1])
        if -100 < sx < WIDTH + 100 and -100 < sy < HEIGHT + 100:
            r = int(f[2])
            a = int(f[3] * 25)
            fog_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(fog_surf, (30, 25, 40, a), (r, r), r)
            surface.blit(fog_surf, (int(sx) - r, int(sy) - r))

    # Arena border (dark stone wall feel)
    bx1, by1 = cam.apply(20, 20)
    bx2, by2 = cam.apply(ARENA_W - 20, ARENA_H - 20)
    pygame.draw.rect(surface, (60, 40, 40), (int(bx1), int(by1), int(bx2 - bx1), int(by2 - by1)), 4)

def draw_vignette(surface):
    """Dark vignette overlay for atmosphere."""
    vig = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for i in range(5):
        r = int(math.sqrt(WIDTH**2 + HEIGHT**2) / 2 - i * 30)
        alpha = int(i * 12)
        pygame.draw.circle(vig, (0, 0, 0, alpha), (WIDTH // 2, HEIGHT // 2), max(1, r), 30)
    # Corner darkness
    corner_r = 350
    for cx, cy in [(0, 0), (WIDTH, 0), (0, HEIGHT), (WIDTH, HEIGHT)]:
        pygame.draw.circle(vig, (0, 0, 0, 40), (cx, cy), corner_r)
    surface.blit(vig, (0, 0))

def draw_ui(surface, player, game_state):
    # HP bar — dark frame
    bar_x, bar_y = 20, 20
    bar_w, bar_h = 260, 28
    pygame.draw.rect(surface, (20, 15, 25), (bar_x - 4, bar_y - 4, bar_w + 8, bar_h + 8), border_radius=4)
    pygame.draw.rect(surface, (10, 5, 10), (bar_x, bar_y, bar_w, bar_h))
    ratio = max(0, player.hp / player.max_hp)
    if ratio > 0:
        bar_color = BLOOD_RED
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, int(bar_w * ratio), bar_h))
        # Shine
        pygame.draw.rect(surface, (min(255, bar_color[0]+40), bar_color[1], bar_color[2]),
                         (bar_x, bar_y, int(bar_w * ratio), bar_h // 3))
    pygame.draw.rect(surface, (80, 60, 60), (bar_x - 4, bar_y - 4, bar_w + 8, bar_h + 8), 2, border_radius=4)

    font = pygame.font.SysFont('Arial', 17)
    font_bold = pygame.font.SysFont('Arial', 17, bold=True)
    small_font = pygame.font.SysFont('Arial', 14)

    hp_surf = font_bold.render(f'HP  {int(player.hp)} / {player.max_hp}', True, BONE_WHITE)
    surface.blit(hp_surf, (bar_x + 8, bar_y + 5))

    # Score
    score_surf = font_bold.render(f'Souls: {game_state["score"]}', True, SOUL_CYAN)
    surface.blit(score_surf, (20, 58))

    kill_surf = font.render(f'Kills: {game_state["kills"]}  |  Wave: {game_state["wave"]}/5', True, BONE_WHITE)
    surface.blit(kill_surf, (20, 80))

    alive_count = sum(1 for e in game_state.get('enemies', []) if e.alive)
    remain_surf = font.render(f'Enemies: {alive_count}', True, ASH_GRAY)
    surface.blit(remain_surf, (20, 100))

    # Heal charges
    heal_surf = font.render(f'Heals [F]: {player.heals}', True, GHOST_GREEN if player.heals > 0 else ASH_GRAY)
    surface.blit(heal_surf, (20, 120))

    # Combo
    if game_state['combo'] > 1:
        combo_font = pygame.font.SysFont('Arial', 44, bold=True)
        combo_text = f'{game_state["combo"]} COMBO!'
        shadow = combo_font.render(combo_text, True, (40, 10, 10))
        surface.blit(shadow, (WIDTH // 2 - shadow.get_width() // 2 + 2, 52))
        txt = combo_font.render(combo_text, True, HELL_ORANGE)
        surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, 50))

    # Skill icons (bottom right)
    skill_y = HEIGHT - 65
    skill_x = WIDTH - 210

    def draw_skill_icon(x, y, label, ready, cd=0, max_cd=1, col=SOUL_CYAN):
        if ready:
            pygame.draw.rect(surface, (30, 25, 40), (x, y, 50, 50), border_radius=6)
            pygame.draw.rect(surface, col, (x, y, 50, 50), 2, border_radius=6)
            lbl = font_bold.render(label, True, col)
        else:
            pygame.draw.rect(surface, (15, 12, 20), (x, y, 50, 50), border_radius=6)
            cd_ratio = cd / max_cd if max_cd > 0 else 0
            fill_h = int(50 * cd_ratio)
            pygame.draw.rect(surface, (25, 20, 30), (x, y + 50 - fill_h, 50, fill_h), border_radius=4)
            pygame.draw.rect(surface, (50, 40, 50), (x, y, 50, 50), 2, border_radius=6)
            lbl = font_bold.render(label, True, ASH_GRAY)
            if cd > 0:
                cd_txt = small_font.render(f'{cd:.1f}', True, BONE_WHITE)
                surface.blit(cd_txt, (x + 14, y + 32))
        surface.blit(lbl, (x + 25 - lbl.get_width() // 2, y + 6))

    draw_skill_icon(skill_x, skill_y, 'Q', player.ult_ready, player.ult_cooldown, player.ult_max_cd, HELL_ORANGE)
    draw_skill_icon(skill_x + 60, skill_y, 'SPC', player.dash_cooldown <= 0, player.dash_cooldown, 0.6, SHADOW_PURPLE)
    draw_skill_icon(skill_x + 120, skill_y, 'F', player.heals > 0, col=GHOST_GREEN)

    # Hint
    hint_surf = small_font.render('WASD:Move  Mouse:Aim  LMB:Slash  Space:Dash  Q:Ultimate  F:Heal  R:Reset', True, (60, 55, 65))
    surface.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 20))

# ============================================
# Wave Spawner
# ============================================
def spawn_wave(wave, px, py):
    enemies = []
    configs = {
        1: [('normal', 10)],
        2: [('normal', 8), ('fast', 5)],
        3: [('normal', 6), ('fast', 6), ('tank', 3)],
        4: [('normal', 8), ('fast', 6), ('tank', 5)],
        5: [('normal', 6), ('fast', 5), ('tank', 3), ('boss', 1)],
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
    wave_msg = "Wave 1"
    wave_msg_timer = 2.0
    play(snd_wave)
    death_played = False
    victory_played = False

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
                    dmg_texts.clear()
                    wave_msg = "Wave 1"
                    wave_msg_timer = 2.0
                    cam.shake = 0
                    death_played = False
                    victory_played = False
                    play(snd_wave)
                    continue
                if not game_state['game_over'] and not game_state['victory']:
                    if event.key == pygame.K_SPACE: player.dash()
                    if event.key == pygame.K_q: player.ultimate(enemies)
                    if event.key == pygame.K_f: player.heal()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not game_state['game_over'] and not game_state['victory']:
                    if event.button == 1: player.attack(enemies)
                    if event.button == 3: player.ultimate(enemies)

        # End screens
        if game_state['game_over'] or game_state['victory']:
            if game_state['game_over'] and not death_played:
                play(snd_death)
                death_played = True
            if game_state['victory'] and not victory_played:
                play(snd_victory)
                victory_played = True
            particles[:] = [p for p in particles if p.update(dt)]
            dmg_texts[:] = [d for d in dmg_texts if d.update(dt)]

            draw_ground(screen, cam, dt)
            for e in enemies: e.draw(screen, cam)
            player.draw(screen, cam)
            for p in particles: p.draw(screen, cam)
            for d in dmg_texts: d.draw(screen, cam)
            draw_vignette(screen)
            draw_ui(screen, player, game_state)

            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))

            big_font = pygame.font.SysFont('Arial', 56, bold=True)
            med_font = pygame.font.SysFont('Arial', 26)

            if game_state['game_over']:
                title = 'YOU DIED'
                title_color = BLOOD_RED
            else:
                title = 'VICTORY'
                title_color = GOLD

            t1_s = big_font.render(title, True, BLACK)
            t1 = big_font.render(title, True, title_color)
            screen.blit(t1_s, (WIDTH // 2 - t1.get_width() // 2 + 3, HEIGHT // 2 - 73))
            screen.blit(t1, (WIDTH // 2 - t1.get_width() // 2, HEIGHT // 2 - 76))

            stats = f'Souls: {game_state["score"]}    Kills: {game_state["kills"]}    Max Combo: {game_state["max_combo"]}'
            t2 = med_font.render(stats, True, BONE_WHITE)
            screen.blit(t2, (WIDTH // 2 - t2.get_width() // 2, HEIGHT // 2 - 5))

            t3 = med_font.render('Press R to Rise Again', True, ASH_GRAY)
            screen.blit(t3, (WIDTH // 2 - t3.get_width() // 2, HEIGHT // 2 + 40))

            pygame.display.flip()
            continue

        # === UPDATE ===
        keys = pygame.key.get_pressed()
        mx, my = pygame.mouse.get_pos()
        player.update(dt, keys, mx, my)
        cam.update(player.x, player.y)

        for e in enemies: e.update(dt, player)

        for e in enemies:
            if not e.alive and not e.scored:
                e.scored = True
                game_state['score'] += e.score * max(1, game_state['combo'])
                game_state['kills'] += 1
                game_state['combo'] += 1
                game_state['combo_timer'] = 2.0
                if game_state['combo'] > game_state['max_combo']:
                    game_state['max_combo'] = game_state['combo']

        if game_state['combo'] > 0:
            game_state['combo_timer'] -= dt
            if game_state['combo_timer'] <= 0:
                game_state['combo'] = 0

        alive_count = sum(1 for e in enemies if e.alive)
        if alive_count == 0:
            if game_state['wave'] >= 5:
                game_state['victory'] = True
            else:
                game_state['wave'] += 1
                enemies = spawn_wave(game_state['wave'], player.x, player.y)
                game_state['enemies'] = enemies
                wave_msg = f"Wave {game_state['wave']}"
                wave_msg_timer = 2.0
                play(snd_wave)
                # Heal bonus
                player.heals = min(3, player.heals + 1)

        if player.hp <= 0:
            game_state['game_over'] = True

        particles[:] = [p for p in particles if p.update(dt)]
        slash_effects[:] = [s for s in slash_effects if s.update(dt)]
        ult_effects[:] = [u for u in ult_effects if u.update(dt)]
        dmg_texts[:] = [d for d in dmg_texts if d.update(dt)]

        if wave_msg_timer > 0:
            wave_msg_timer -= dt

        # === DRAW ===
        draw_ground(screen, cam, dt)

        for e in enemies: e.draw(screen, cam)
        player.draw(screen, cam)
        for s in slash_effects: s.draw(screen, cam)
        for u in ult_effects: u.draw(screen, cam)
        for p in particles: p.draw(screen, cam)
        for d in dmg_texts: d.draw(screen, cam)

        draw_vignette(screen)
        draw_ui(screen, player, game_state)

        if wave_msg_timer > 0:
            wave_font = pygame.font.SysFont('Arial', 60, bold=True)
            sub_font = pygame.font.SysFont('Arial', 22)
            alpha = min(1, wave_msg_timer)
            c = int(180 * alpha)

            ws = wave_font.render(wave_msg, True, BLACK)
            wt = wave_font.render(wave_msg, True, (c, int(c * 0.3), int(c * 0.2)))
            rect = wt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(ws, (rect.x + 3, rect.y + 3))
            screen.blit(wt, rect)

            sub = sub_font.render('Prepare yourself...', True, (int(c * 0.5), int(c * 0.3), int(c * 0.3)))
            sub_rect = sub.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            screen.blit(sub, sub_rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
