"""
Musou Mini - 3D Third-Person Action Game
by B5 (Boom Fifth)

Controls:
  WASD    - Move
  Mouse   - Look around
  LMB     - Attack
  Space   - Jump
  Q       - Ultimate (AoE)
  R       - Reset
  ESC     - Unlock mouse
"""

from ursina import *
import random
import math

app = Ursina(title='Musou Mini', borderless=False, fullscreen=False)

# ============================================
# Game State
# ============================================
class GameState:
    def __init__(self):
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.max_combo = 0
        self.kill_count = 0
        self.total_enemies = 0
        self.game_over = False
        self.victory = False
        self.ultimate_ready = True
        self.ultimate_cooldown = 0
        self.wave = 1
        self.shake_amount = 0

game = GameState()

# ============================================
# Ground & Environment
# ============================================
ground = Entity(
    model='plane',
    scale=(60, 1, 60),
    color=color.rgb(80, 140, 80),
    texture='white_cube',
    texture_scale=(30, 30),
    collider='box'
)

# Boundary walls
walls = []
for pos, sc in [
    ((30, 2, 0), (1, 4, 60)),
    ((-30, 2, 0), (1, 4, 60)),
    ((0, 2, 30), (60, 4, 1)),
    ((0, 2, -30), (60, 4, 1)),
]:
    w = Entity(model='cube', position=pos, scale=sc, color=color.rgb(100, 100, 100), collider='box')
    walls.append(w)

# Obstacles (rocks/crates)
obstacles = []
for i in range(15):
    pos = (random.uniform(-25, 25), 0.5, random.uniform(-25, 25))
    if abs(pos[0]) < 3 and abs(pos[2]) < 3:
        continue
    ob = Entity(
        model='cube',
        position=pos,
        scale=(random.uniform(1, 2.5), random.uniform(1, 3), random.uniform(1, 2.5)),
        color=color.rgb(random.randint(120, 160), random.randint(100, 130), random.randint(80, 110)),
        collider='box'
    )
    obstacles.append(ob)

# Lighting
ambient = AmbientLight(color=color.rgba(100, 100, 100, 255))
directional = DirectionalLight(y=10, rotation=(45, 45, 0))

# ============================================
# Player
# ============================================
class Player(Entity):
    def __init__(self):
        super().__init__(
            model='cube',
            color=color.rgb(200, 50, 50),
            scale=(0.8, 1.8, 0.8),
            position=(0, 0.9, 0),
            collider='box'
        )
        self.speed = 8
        self.hp = 100
        self.max_hp = 100
        self.attack_power = 25
        self.attack_range = 3.0
        self.attacking = False
        self.attack_timer = 0
        self.y_velocity = 0
        self.grounded = True
        self.invincible = 0

        # Weapon (sword)
        self.weapon = Entity(
            model='cube',
            color=color.rgb(200, 200, 220),
            scale=(0.15, 0.15, 1.5),
            position=(0.6, 0.3, 0.8),
            parent=self
        )
        # Handle
        self.handle = Entity(
            model='cube',
            color=color.rgb(139, 69, 19),
            scale=(0.2, 0.2, 0.4),
            position=(0.6, 0.3, 0.1),
            parent=self
        )

    def take_damage(self, amount):
        if self.invincible > 0:
            return
        self.hp -= amount
        self.invincible = 0.3
        self.color = color.white
        game.combo = 0
        if self.hp <= 0:
            self.hp = 0
            game.game_over = True
        invoke(setattr, self, 'color', color.rgb(200, 50, 50), delay=0.15)

player = Player()

# ============================================
# Third Person Camera
# ============================================
camera.position = (0, 10, -12)
camera_pivot = Entity(position=player.position)
camera.parent = camera_pivot
camera.position = (0, 6, -10)
camera.rotation_x = 20
mouse.locked = True

cam_rot_x = 0
cam_rot_y = 0

# ============================================
# Enemy
# ============================================
enemies = []

class Enemy(Entity):
    def __init__(self, pos, enemy_type='normal'):
        self.enemy_type = enemy_type
        if enemy_type == 'normal':
            c = color.rgb(50, 50, 200)
            sc = (0.7, 1.6, 0.7)
            self.hp = 40
            self.speed = 3
            self.attack_power = 8
            self.score_value = 100
        elif enemy_type == 'fast':
            c = color.rgb(200, 200, 50)
            sc = (0.5, 1.3, 0.5)
            self.hp = 25
            self.speed = 6
            self.attack_power = 5
            self.score_value = 150
        elif enemy_type == 'tank':
            c = color.rgb(100, 50, 150)
            sc = (1.2, 2.2, 1.2)
            self.hp = 100
            self.speed = 1.5
            self.attack_power = 20
            self.score_value = 300
        else:  # boss
            c = color.rgb(200, 30, 30)
            sc = (1.5, 2.8, 1.5)
            self.hp = 300
            self.speed = 2.5
            self.attack_power = 25
            self.score_value = 1000

        super().__init__(
            model='cube',
            color=c,
            scale=sc,
            position=(pos[0], sc[1]/2, pos[2]),
            collider='box'
        )
        self.max_hp = self.hp
        self.base_color = c
        self.attack_timer = 0
        self.hit_flash = 0
        self.knockback = Vec3(0, 0, 0)

        # HP bar
        self.hp_bar_bg = Entity(
            model='cube',
            color=color.black,
            scale=(1.2, 0.1, 0.05),
            position=(0, self.scale_y / 2 + 0.3, 0),
            parent=self,
            billboard=True
        )
        self.hp_bar = Entity(
            model='cube',
            color=color.rgb(0, 220, 0),
            scale=(1.1, 0.08, 0.05),
            position=(0, self.scale_y / 2 + 0.3, 0),
            parent=self,
            billboard=True
        )

    def take_damage(self, amount, knockback_dir=None):
        self.hp -= amount
        self.hit_flash = 0.1
        self.color = color.white

        if knockback_dir:
            self.knockback = knockback_dir * 5

        ratio = max(0, self.hp / self.max_hp)
        self.hp_bar.scale_x = 1.1 * ratio
        if ratio < 0.3:
            self.hp_bar.color = color.rgb(220, 0, 0)
        elif ratio < 0.6:
            self.hp_bar.color = color.rgb(220, 220, 0)

        if self.hp <= 0:
            self.die()

    def die(self):
        game.score += self.score_value * max(1, game.combo)
        game.kill_count += 1
        game.combo += 1
        game.combo_timer = 2
        if game.combo > game.max_combo:
            game.max_combo = game.combo

        # Death particles
        for _ in range(8):
            p = Entity(
                model='cube',
                color=self.base_color,
                scale=0.2,
                position=self.position,
            )
            p.animate_position(
                p.position + Vec3(random.uniform(-3, 3), random.uniform(1, 5), random.uniform(-3, 3)),
                duration=0.5
            )
            p.animate_scale(0, duration=0.5)
            destroy(p, delay=0.5)

        if self in enemies:
            enemies.remove(self)
        destroy(self)

        if len(enemies) == 0:
            check_wave()

    def update_enemy(self):
        if game.game_over or game.victory:
            return

        if self.hit_flash > 0:
            self.hit_flash -= time.dt
            if self.hit_flash <= 0:
                self.color = self.base_color

        if self.knockback.length() > 0.1:
            self.position += self.knockback * time.dt
            self.knockback *= 0.9
        else:
            self.knockback = Vec3(0, 0, 0)

        to_player = player.position - self.position
        to_player.y = 0
        dist = to_player.length()

        if dist > 2:
            direction = to_player.normalized()
            self.position += direction * self.speed * time.dt
            self.look_at(player.position)
        elif self.attack_timer <= 0:
            player.take_damage(self.attack_power)
            self.attack_timer = 1.5 if self.enemy_type != 'fast' else 0.8
            game.shake_amount = 0.3

        self.attack_timer -= time.dt

# ============================================
# Wave Spawner
# ============================================
def spawn_wave(wave_num):
    spawn_list = []
    if wave_num == 1:
        spawn_list = [('normal', 5)]
    elif wave_num == 2:
        spawn_list = [('normal', 4), ('fast', 3)]
    elif wave_num == 3:
        spawn_list = [('normal', 3), ('fast', 3), ('tank', 2)]
    elif wave_num == 4:
        spawn_list = [('normal', 5), ('fast', 4), ('tank', 3)]
    elif wave_num >= 5:
        spawn_list = [('normal', 3), ('fast', 2), ('tank', 2), ('boss', 1)]

    total = 0
    for etype, count in spawn_list:
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(12, 25)
            pos = (math.cos(angle) * dist, 0, math.sin(angle) * dist)
            e = Enemy(pos, etype)
            enemies.append(e)
            total += 1

    game.total_enemies = total
    wave_text.text = f'Wave {wave_num}!'
    wave_text.visible = True
    invoke(setattr, wave_text, 'visible', False, delay=2)

def check_wave():
    if game.wave >= 5:
        game.victory = True
        return
    game.wave += 1
    invoke(spawn_wave, game.wave, delay=2)

# ============================================
# UI
# ============================================
hp_bg = Entity(parent=camera.ui, model='quad', color=color.black, scale=(0.4, 0.035), position=(-0.45, 0.45))
hp_bar = Entity(parent=camera.ui, model='quad', color=color.rgb(220, 30, 30), scale=(0.38, 0.028), position=(-0.45, 0.45))
hp_text = Text(text='HP: 100/100', position=(-0.63, 0.43), scale=1.2, color=color.white)

score_text = Text(text='Score: 0', position=(-0.63, 0.38), scale=1.2, color=color.yellow)
combo_text = Text(text='', position=(0, 0.3), scale=2.5, color=color.orange, origin=(0, 0))
kill_text = Text(text='Kills: 0', position=(-0.63, 0.33), scale=1.2, color=color.white)

ult_text = Text(text='[Q] Ultimate: Ready', position=(-0.63, 0.28), scale=1.2, color=color.cyan)

wave_text = Text(text='', position=(0, 0.1), scale=4, color=color.white, origin=(0, 0), visible=False)

gameover_text = Text(text='', position=(0, 0.05), scale=3, color=color.red, origin=(0, 0), visible=False)
restart_text = Text(text='', position=(0, -0.05), scale=1.5, color=color.white, origin=(0, 0), visible=False)

help_text = Text(
    text='WASD Move | Mouse Look | LMB Attack | Space Jump | Q Ultimate | R Reset',
    position=(0, -0.45),
    scale=1,
    color=color.rgb(200, 200, 200),
    origin=(0, 0)
)

# ============================================
# Attack
# ============================================
def do_attack():
    if player.attacking:
        return
    player.attacking = True
    player.attack_timer = 0.3

    player.weapon.animate_rotation((0, 0, -90), duration=0.15)
    invoke(lambda: player.weapon.animate_rotation((0, 0, 0), duration=0.15), delay=0.15)

    hit_any = False
    for e in enemies[:]:
        dist = (e.position - player.position).length()
        if dist < player.attack_range:
            forward = Vec3(
                math.sin(math.radians(camera_pivot.rotation_y)),
                0,
                math.cos(math.radians(camera_pivot.rotation_y))
            )
            to_enemy = (e.position - player.position).normalized()
            to_enemy.y = 0
            dot = forward.x * to_enemy.x + forward.z * to_enemy.z
            if dot > -0.3:
                knockback_dir = to_enemy
                e.take_damage(player.attack_power, knockback_dir)
                hit_any = True

    if hit_any:
        game.shake_amount = 0.15
        slash = Entity(
            model='cube',
            color=color.rgb(255, 200, 50),
            scale=(2, 0.1, 0.1),
            position=player.position + Vec3(0, 1, 0),
            rotation=(0, camera_pivot.rotation_y + random.uniform(-20, 20), random.uniform(-30, 30))
        )
        slash.animate_scale(0, duration=0.2)
        destroy(slash, delay=0.2)

def do_ultimate():
    if not game.ultimate_ready:
        return
    game.ultimate_ready = False
    game.ultimate_cooldown = 8
    game.shake_amount = 0.5

    wave_effect = Entity(
        model='sphere',
        color=color.rgba(255, 100, 50, 150),
        scale=1,
        position=player.position
    )
    wave_effect.animate_scale(15, duration=0.5)
    wave_effect.animate_color(color.rgba(255, 100, 50, 0), duration=0.5)
    destroy(wave_effect, delay=0.5)

    for e in enemies[:]:
        dist = (e.position - player.position).length()
        if dist < 10:
            knockback_dir = (e.position - player.position).normalized()
            e.take_damage(80, knockback_dir)

# ============================================
# Reset
# ============================================
def reset_game():
    for e in enemies[:]:
        destroy(e)
    enemies.clear()

    player.hp = player.max_hp
    player.position = (0, 0.9, 0)
    player.color = color.rgb(200, 50, 50)

    game.score = 0
    game.combo = 0
    game.combo_timer = 0
    game.max_combo = 0
    game.kill_count = 0
    game.game_over = False
    game.victory = False
    game.ultimate_ready = True
    game.ultimate_cooldown = 0
    game.wave = 1
    game.shake_amount = 0

    gameover_text.visible = False
    restart_text.visible = False

    spawn_wave(1)

# ============================================
# Main Loop
# ============================================
def update():
    global cam_rot_x, cam_rot_y

    if game.game_over:
        gameover_text.text = f'YOU DIED!\nScore: {game.score}\nMax Combo: {game.max_combo}'
        gameover_text.visible = True
        restart_text.text = 'Press R to Restart'
        restart_text.visible = True
        mouse.locked = False
        return

    if game.victory:
        gameover_text.text = f'VICTORY!\nScore: {game.score}\nKills: {game.kill_count}\nMax Combo: {game.max_combo}'
        gameover_text.color = color.yellow
        gameover_text.visible = True
        restart_text.text = 'Press R to Play Again'
        restart_text.visible = True
        mouse.locked = False
        return

    cam_rot_y += mouse.velocity[0] * 100
    cam_rot_x -= mouse.velocity[1] * 100
    cam_rot_x = clamp(cam_rot_x, -30, 60)
    camera_pivot.rotation_y = cam_rot_y
    camera_pivot.rotation_x = cam_rot_x

    move_dir = Vec3(0, 0, 0)
    forward = Vec3(
        math.sin(math.radians(cam_rot_y)),
        0,
        math.cos(math.radians(cam_rot_y))
    )
    right = Vec3(
        math.sin(math.radians(cam_rot_y + 90)),
        0,
        math.cos(math.radians(cam_rot_y + 90))
    )

    if held_keys['w']: move_dir += forward
    if held_keys['s']: move_dir -= forward
    if held_keys['d']: move_dir += right
    if held_keys['a']: move_dir -= right

    if move_dir.length() > 0:
        move_dir = move_dir.normalized()
        new_pos = player.position + move_dir * player.speed * time.dt
        new_pos.x = clamp(new_pos.x, -28, 28)
        new_pos.z = clamp(new_pos.z, -28, 28)
        player.position = new_pos
        player.rotation_y = cam_rot_y

    if not player.grounded:
        player.y_velocity -= 20 * time.dt
        player.y += player.y_velocity * time.dt
        if player.y <= 0.9:
            player.y = 0.9
            player.grounded = True
            player.y_velocity = 0

    camera_pivot.position = lerp(camera_pivot.position, player.position, 8 * time.dt)

    if game.shake_amount > 0:
        camera.position = Vec3(
            random.uniform(-1, 1) * game.shake_amount,
            6 + random.uniform(-1, 1) * game.shake_amount,
            -10
        )
        game.shake_amount *= 0.9
        if game.shake_amount < 0.01:
            game.shake_amount = 0
            camera.position = Vec3(0, 6, -10)

    if player.attacking:
        player.attack_timer -= time.dt
        if player.attack_timer <= 0:
            player.attacking = False

    if player.invincible > 0:
        player.invincible -= time.dt

    if not game.ultimate_ready:
        game.ultimate_cooldown -= time.dt
        if game.ultimate_cooldown <= 0:
            game.ultimate_ready = True

    if game.combo > 0:
        game.combo_timer -= time.dt
        if game.combo_timer <= 0:
            game.combo = 0

    for e in enemies[:]:
        e.update_enemy()

    hp_ratio = player.hp / player.max_hp
    hp_bar.scale_x = 0.38 * hp_ratio
    hp_bar.x = -0.45 - 0.19 * (1 - hp_ratio)
    if hp_ratio < 0.3:
        hp_bar.color = color.rgb(220, 30, 30)
    elif hp_ratio < 0.6:
        hp_bar.color = color.rgb(220, 220, 30)
    else:
        hp_bar.color = color.rgb(30, 220, 30)

    hp_text.text = f'HP: {int(player.hp)}/{player.max_hp}'
    score_text.text = f'Score: {game.score}'
    kill_text.text = f'Kills: {game.kill_count} | Wave: {game.wave}/5'

    if game.combo > 1:
        combo_text.text = f'{game.combo} COMBO!'
        combo_text.visible = True
    else:
        combo_text.visible = False

    if game.ultimate_ready:
        ult_text.text = '[Q] Ultimate: READY'
        ult_text.color = color.cyan
    else:
        ult_text.text = f'[Q] Ultimate: {game.ultimate_cooldown:.1f}s'
        ult_text.color = color.gray

def input(key):
    if key == 'left mouse down' and not game.game_over and not game.victory:
        do_attack()
    if key == 'space' and player.grounded and not game.game_over:
        player.y_velocity = 8
        player.grounded = False
    if key == 'q' and not game.game_over and not game.victory:
        do_ultimate()
    if key == 'r':
        mouse.locked = True
        reset_game()
    if key == 'escape':
        mouse.locked = not mouse.locked

# ============================================
# Start!
# ============================================
spawn_wave(1)

Sky(color=color.rgb(135, 206, 235))

app.run()
