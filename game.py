import pygame
import sys
import os
import math
import random

# ── Init ──────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

SCREEN_W, SCREEN_H = 1280, 720
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Slime Runner - Clean Version")
clock = pygame.time.Clock()
FPS = 60

# --- MAP DATA (2560 x 720) ---
TILE_SIZE = 40
MAP_WIDTH = 2560

# Matrix 64 kolom x 18 baris
level_data = [
    "1111111111111111111111111111111111111111111111111111111111111111",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1000000000000000000000000000000000000000000000000000000000000001",
    "1011000000000000000000000000000000000000000000000000000000000001",
    "1011000000000000000000000000000000000000000000000000000000000001",
    "1011000000011111111111000000000000000000011111111111100000000001",
    "1111111100110000000000000000000000000000000000000000110011110001",
    "1111100001110000000000000000000000000000000000000000111000000001",
    "1111111111111000000000100000000000000000000000000000111100000011",
    "11111111111110000000001111111111111111111000000000000111111111111",
    "1111111111111000000000111111111111111111100000000000111111111111",
]

# Font
font_indicator = pygame.font.SysFont(None, 32, bold=True)

# ── Colours ───────────────────────────────────────────────────────────────────
C_PLAYER       = (80, 140, 220)
C_GREEN_SLIME  = (60, 200, 80)
C_ORANGE_SLIME = (230, 110, 20)
C_HP_FULL      = (60, 220, 80)
C_HP_EMPTY     = (60, 60, 60)
C_TEXT         = (255, 255, 255)
C_WIN          = (80, 220, 160)
C_LOSE         = (220, 80, 80)

# ── Asset paths ───────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
MAP1_PATH = os.path.join(BASE, "assets", "1.jpeg")
MAP2_PATH = os.path.join(BASE, "assets", "2.jpeg")

PLAYER_IDLE_DIR  = os.path.join(BASE, "assets", "BlueWizard Animations", "BlueWizard", "2BlueWizardIdle")
PLAYER_JUMP_DIR  = os.path.join(BASE, "assets", "BlueWizard Animations", "BlueWizard", "2BlueWizardJump")
PLAYER_WALK_DIR  = os.path.join(BASE, "assets", "BlueWizard Animations", "BlueWizard", "2BlueWizardWalk")
SLIME_GREEN_DIR  = os.path.join(BASE, "assets", "Slimes", "SlimeGreen")
SLIME_ORANGE_DIR = os.path.join(BASE, "assets", "Slimes", "SlimeOrange")

# ── Audio paths & Loader ──────────────────────────────────────────────────────
SND_JUMP       = os.path.join(BASE, "assets", "sounds", "woosh 2.mp3")
SND_DASH       = os.path.join(BASE, "assets", "sounds", "woosh 1.mp3")
SND_SLIME_DIE  = os.path.join(BASE, "assets", "sounds", "kill.mp3")
SND_PLAYER_DIE = os.path.join(BASE, "assets", "sounds", "defeat.mp3")
SND_WIN        = os.path.join(BASE, "assets", "sounds", "win.mp3")

# --- TAMBAHAN SOUND BARU ---
SND_PLAYER_HIT = os.path.join(BASE, "assets", "sounds", "hit 1.mp3") 
SND_SLIME_HIT  = os.path.join(BASE, "assets", "sounds", "hit 2.mp3")
BGM_PATH       = os.path.join(BASE, "assets", "sounds", "bgm.mp3")

def load_sound(path):
    if os.path.exists(path):
        return pygame.mixer.Sound(path)
    return None

snd_jump       = load_sound(SND_JUMP)
snd_dash       = load_sound(SND_DASH)
snd_slime_die  = load_sound(SND_SLIME_DIE)
snd_player_die = load_sound(SND_PLAYER_DIE)
snd_win        = load_sound(SND_WIN)
snd_player_hit = load_sound(SND_PLAYER_HIT)
snd_slime_hit  = load_sound(SND_SLIME_HIT)

# ── Helper: load sprite frames ────────────────────────────────────────────────
def load_frames(folder, pattern, count, size=None):
    frames = []
    for i in range(count):
        path = os.path.join(folder, pattern.format(i))
        if os.path.exists(path):
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            frames.append(img)
    return frames

def make_placeholder(w, h, colour, label=""):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, colour, (0, 0, w, h), border_radius=8)
    if label:
        f = pygame.font.SysFont(None, 18)
        t = f.render(label, True, (255,255,255))
        surf.blit(t, (w//2 - t.get_width()//2, h//2 - t.get_height()//2))
    return surf

def placeholder_frames(w, h, colour, label, n):
    return [make_placeholder(w, h, colour, label) for _ in range(n)]

# ── Load Assets ───────────────────────────────────────────────────────────────
PLAYER_W, PLAYER_H   = 164, 180
SLIME_W,  SLIME_H    = 118, 108

player_idle_frames = (
    load_frames(PLAYER_IDLE_DIR, "Chara - BlueIdle{:05d}.png", 20, (PLAYER_W, PLAYER_H)) or
    load_frames(PLAYER_IDLE_DIR, "Chara - BlueIdle{:05d}.PNG", 20, (PLAYER_W, PLAYER_H)) or
    placeholder_frames(PLAYER_W, PLAYER_H, C_PLAYER, "idle", 4)
)
player_jump_frames = (
    load_frames(PLAYER_JUMP_DIR, "CharaWizardJump_{:05d}.png", 8, (PLAYER_W, PLAYER_H)) or
    load_frames(PLAYER_JUMP_DIR, "CharaWizardJump_{:05d}.PNG", 8, (PLAYER_W, PLAYER_H)) or
    placeholder_frames(PLAYER_W, PLAYER_H, C_PLAYER, "jump", 4)
)
player_walk_frames = (
    load_frames(PLAYER_WALK_DIR, "Chara_BlueWalk{:05d}.png", 20, (PLAYER_W, PLAYER_H)) or
    load_frames(PLAYER_WALK_DIR, "Chara_BlueWalk{:05d}.PNG", 20, (PLAYER_W, PLAYER_H)) or
    placeholder_frames(PLAYER_W, PLAYER_H, C_PLAYER, "walk", 4)
)
green_frames = (
    load_frames(SLIME_GREEN_DIR, "SlimeBasic_{:05d}.png", 30, (SLIME_W, SLIME_H)) or
    load_frames(SLIME_GREEN_DIR, "SlimeBasic_{:05d}.PNG", 30, (SLIME_W, SLIME_H)) or
    placeholder_frames(SLIME_W, SLIME_H, C_GREEN_SLIME, "slime", 6)
)
orange_frames = (
    load_frames(SLIME_ORANGE_DIR, "SlimeOrange_{:05d}.png", 30, (SLIME_W, SLIME_H)) or
    load_frames(SLIME_ORANGE_DIR, "SlimeOrange_{:05d}.PNG", 30, (SLIME_W, SLIME_H)) or
    placeholder_frames(SLIME_W, SLIME_H, C_ORANGE_SLIME, "slime+", 6)
)

def load_bg(path):
    if os.path.exists(path):
        return pygame.transform.scale(pygame.image.load(path).convert(), (SCREEN_W, SCREEN_H))
    surf = pygame.Surface((SCREEN_W, SCREEN_H))
    surf.fill((15, 25, 45))
    return surf

bg1 = load_bg(MAP1_PATH)
bg2 = load_bg(MAP2_PATH)

# ── Particle system ───────────────────────────────────────────────────────────
particles = []

def spawn_particles(x, y, colour, n=12):
    for _ in range(n):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(2, 6)
        particles.append({
            "x": x, "y": y,
            "vx": math.cos(angle)*speed,
            "vy": math.sin(angle)*speed - 2,
            "life": random.randint(20, 35),
            "colour": colour,
            "size": random.randint(3, 7),
        })

def update_draw_particles(camera_x):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.3
        p["life"] -= 1
        alpha = max(0, int(255 * p["life"] / 35))
        s = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["colour"], alpha), (p["size"], p["size"]), p["size"])
        
        screen_x = int(p["x"] - camera_x - p["size"])
        screen_y = int(p["y"] - p["size"])
        screen.blit(s, (screen_x, screen_y))
        
        if p["life"] <= 0:
            particles.remove(p)

# ── Flash overlay ─────────────────────────────────────────────────────────────
class FlashOverlay:
    def __init__(self):
        self.timer = 0
        self.colour = (220, 60, 60)
    def trigger(self, colour=(220,60,60)):
        self.timer = 12
        self.colour = colour
    def draw(self):
        if self.timer > 0:
            alpha = int(120 * self.timer / 12)
            s = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            s.fill((*self.colour, alpha))
            screen.blit(s, (0,0))
            self.timer -= 1

flash = FlashOverlay()

# ── Player ────────────────────────────────────────────────────────────────────
class Player:
    SPEED      = 5
    JUMP_VEL   = -16
    GRAVITY    = 0.7
    DASH_SPEED = 14
    DASH_DUR   = 12
    DASH_CD    = 45
    MAX_HP     = 5
    INVULN_DUR = 60

    def __init__(self):
        self.x = 50.0
        self.y = 100.0 
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.facing = 1
        self.hp = self.MAX_HP
        self.alive = True
        self.state = "idle"
        self.frame_idx = 0.0
        self.anim_speed = 0.25
        self.dash_timer = 0
        self.dash_cd    = 0
        self.is_dashing = False
        self.is_defending = False
        self.invuln = 0
        self.shake = 0
        
        # --- Motion Blur ---
        self.trail = []
        self.TRAIL_LENGTH = 5

    @property
    def rect(self):
        width = 50 
        height = 110
        y_offset = 20 
        return pygame.Rect(
            int(self.x) + (PLAYER_W // 2 - width // 2), 
            int(self.y) + (PLAYER_H - height - y_offset),
            width, height
        )

    @property
    def stomp_rect(self):
        r = self.rect
        return pygame.Rect(r.x + 5, r.bottom, r.width - 10, 8)

    def handle_input(self, keys, mouse_btns):
        if not self.alive: return
        self.is_defending = mouse_btns[2] and self.on_ground
        current_speed = self.SPEED * 0.5 if self.is_defending else self.SPEED
        moving = False
        if not self.is_dashing:
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.vx = current_speed
                self.facing = 1
                moving = True
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.vx = -current_speed
                self.facing = -1
                moving = True
            else:
                self.vx = 0

        # PLAY SOUND: JUMP
        if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            if not self.is_defending:
                self.vy = self.JUMP_VEL
                self.on_ground = False
                if snd_jump:
                    snd_jump.play()

        # PLAY SOUND: DASH
        if keys[pygame.K_LSHIFT] and self.dash_cd <= 0 and not self.is_dashing:
            if not self.is_defending:
                self.is_dashing = True
                self.dash_timer = self.DASH_DUR
                self.dash_cd    = self.DASH_CD
                self.vx = self.DASH_SPEED * self.facing
                if snd_dash:
                    snd_dash.play()

        if self.is_dashing:
            self.state = "walk"; self.anim_speed = 0.5
        elif not self.on_ground:
            self.state = "jump"; self.anim_speed = 0.3
        elif moving:
            self.state = "walk"; self.anim_speed = 0.3 if not self.is_defending else 0.15
        else:
            self.state = "idle"; self.anim_speed = 0.2

    def update(self, tiles):
        if not self.alive: return
        if self.is_dashing:
            self.dash_timer -= 1
            if self.dash_timer <= 0: self.is_dashing = False
        if self.dash_cd > 0: self.dash_cd -= 1

        self.x += self.vx
        self.x = max(0.0, min(self.x, MAP_WIDTH - PLAYER_W)) 
        player_rect = self.rect
        for t in tiles:
            if player_rect.colliderect(t):
                if self.vx > 0: self.x -= (player_rect.right - t.left)
                elif self.vx < 0: self.x += (t.right - player_rect.left)
                player_rect = self.rect

        self.vy += self.GRAVITY
        self.y  += self.vy
        self.on_ground = False
        player_rect = self.rect
        for t in tiles:
            if player_rect.colliderect(t):
                if self.vy > 0:
                    self.y -= (player_rect.bottom - t.top)
                    self.vy = 0; self.on_ground = True
                elif self.vy < 0:
                    self.y += (t.bottom - player_rect.top)
                    self.vy = 0
                player_rect = self.rect

        if self.invuln > 0: self.invuln -= 1
        if self.shake > 0:  self.shake -= 1
        frames = self._current_frames()
        self.frame_idx = (self.frame_idx + self.anim_speed) % len(frames)
        
        # --- Motion Blur Update ---
        if abs(self.vx) > 1 or abs(self.vy) > 1:
            self.trail.append((self.x, self.y, self.frame_idx, self.state, self.facing))
            if len(self.trail) > self.TRAIL_LENGTH:
                self.trail.pop(0)
        else:
            if len(self.trail) > 0:
                self.trail.pop(0)

        # PLAY SOUND: PLAYER DIE (FALLING)
        if self.y > SCREEN_H + 50:
            self.hp = 0
            if self.alive:
                self.alive = False
                if snd_player_die:
                    snd_player_die.play()
                pygame.mixer.music.fadeout(1000)

    def take_damage(self, dmg):
        if self.invuln > 0: return
        self.hp -= dmg
        self.invuln = self.INVULN_DUR
        self.shake  = 12
        flash.trigger()
        
        # PLAY SOUND: PLAYER HIT
        if self.hp > 0 and snd_player_hit:
            snd_player_hit.play()
        
        # PLAY SOUND: PLAYER DIE (0 HP)
        if self.hp <= 0: 
            self.hp = 0
            if self.alive:
                self.alive = False
                if snd_player_die:
                    snd_player_die.play()
                pygame.mixer.music.fadeout(1000)

    def _current_frames(self):
        if self.state == "jump": return player_jump_frames
        if self.state == "walk": return player_walk_frames
        return player_idle_frames

    def draw(self, surface, camera_x):
        if self.invuln > 0 and (self.invuln // 6) % 2 == 0: return
        frames = self._current_frames()
        img = frames[int(self.frame_idx) % len(frames)]
        if self.facing == -1: img = pygame.transform.flip(img, True, False)
        ox, oy = int(self.x - camera_x), int(self.y)
        if self.shake > 0:
            ox += random.randint(-3, 3); oy += random.randint(-2, 2)
            
        if self.is_defending:
            shield_surf = pygame.Surface((PLAYER_W + 40, PLAYER_H + 20), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (100, 200, 255, 80), shield_surf.get_rect())
            pygame.draw.ellipse(shield_surf, (100, 200, 255, 200), shield_surf.get_rect(), 4)
            surface.blit(shield_surf, (ox - 20, oy - 10))

        # --- Draw Motion Blur ---
        for i, (tx, ty, tf_idx, t_state, t_facing) in enumerate(self.trail):
            if t_state == "jump": t_frames = player_jump_frames
            elif t_state == "walk": t_frames = player_walk_frames
            else: t_frames = player_idle_frames
            
            t_img = t_frames[int(tf_idx) % len(t_frames)]
            if t_facing == -1: t_img = pygame.transform.flip(t_img, True, False)
            
            ghost_blur = t_img.copy()
            alpha = int(100 * ((i + 1) / len(self.trail)))
            ghost_blur.set_alpha(alpha)
            
            surface.blit(ghost_blur, (int(tx - camera_x), int(ty)))

        surface.blit(img, (ox, oy))
        
        if self.is_dashing:
            ghost = img.copy(); ghost.set_alpha(80)
            surface.blit(ghost, (ox - self.facing*20, oy))

# ── Slime ─────────────────────────────────────────────────────────────────────
class Slime:
    GRAVITY = 0.6
    def __init__(self, x, frames, hp, speed, jump_interval, dmg, colour):
        self.x, self.y = float(x), 100.0 
        self.vx, self.vy = 0.0, 0.0
        self.on_ground = False
        self.hp, self.max_hp = hp, hp
        self.speed, self.jump_interval = speed, jump_interval
        self.jump_timer = random.randint(10, jump_interval)
        self.dmg, self.colour = dmg, colour
        self.alive, self.frames = True, frames
        self.frame_idx, self.anim_speed = 0.0, 0.25
        self.hit_flash, self.facing = 0, -1
        self.state, self.alert_timer = "idle", 0

    @property
    def rect(self):
        ox, oy = 30, 75
        return pygame.Rect(int(self.x)+ox, int(self.y)+oy, SLIME_W-(ox*2), SLIME_H-oy)

    @property
    def head_rect(self):
        ox, oy = 25, 55
        return pygame.Rect(int(self.x)+ox, int(self.y)+oy, SLIME_W-(ox*2), 20)

    def update(self, player_x, tiles):
        if not self.alive: return
        dist = abs(player_x - self.x)
        if self.state == "idle" and dist < 380:
            self.state = "alert"; self.alert_timer = 45
        elif self.state == "alert":
            self.alert_timer -= 1
            if self.alert_timer <= 0: self.state = "active"
        elif self.state == "active":
            dx = player_x - self.x
            if abs(dx) > 0: self.facing = 1 if dx > 0 else -1
            self.jump_timer -= 1
            if self.jump_timer <= 0 and self.on_ground:
                self.jump_timer = self.jump_interval + random.randint(-10, 20)
                self.vy, self.vx = -12, self.facing * self.speed

        self.vy += self.GRAVITY
        self.y  += self.vy
        self.on_ground = False
        for t in tiles:
            if self.rect.colliderect(t):
                if self.vy > 0:
                    self.y = t.top - SLIME_H
                    self.vy = 0; self.vx *= 0.7; self.on_ground = True

        self.x += self.vx
        self.x = max(0.0, min(self.x, MAP_WIDTH - SLIME_W))
        for t in tiles:
            if self.rect.colliderect(t):
                if self.vx > 0: self.x = t.left - SLIME_W + 30
                elif self.vx < 0: self.x = t.right - 30
                self.vx *= -1 

        self.frame_idx = (self.frame_idx + self.anim_speed) % len(self.frames)
        if self.hit_flash > 0: self.hit_flash -= 1
        if self.y > SCREEN_H + 50: self.hp = 0; self.alive = False

    def take_hit(self):
        self.hp -= 1; self.hit_flash = 8; self.vy, self.vx = -8, 0
        if self.state != "active": self.state = "active"
        
        # PLAY SOUND: SLIME HIT
        if self.hp > 0 and snd_slime_hit:
            snd_slime_hit.play()

        if self.hp <= 0:
            if self.alive:
                self.alive = False
                # PLAY SOUND: SLIME DIE
                if snd_slime_die:
                    snd_slime_die.play()
                spawn_particles(self.x + SLIME_W//2, self.y + SLIME_H//2, self.colour, 18)
                return True
        return False

    def draw(self, surface, camera_x):
        sx, sy = int(self.x - camera_x), int(self.y)
        if sx < -100 or sx > SCREEN_W + 100: return
        img = self.frames[int(self.frame_idx) % len(self.frames)]
        if self.facing == 1: img = pygame.transform.flip(img, True, False)
        if self.hit_flash > 0 and self.hit_flash % 2 == 0:
            white = img.copy(); white.fill((255,255,255,180), special_flags=pygame.BLEND_RGBA_MAX)
            surface.blit(white, (sx, sy))
        else: surface.blit(img, (sx, sy))
        if self.state == "idle":
            fy = math.sin(pygame.time.get_ticks() * 0.005) * 4
            txt = font_indicator.render("z Z", True, (200, 220, 255))
            surface.blit(txt, (sx + 10, sy - 25 + fy))
        elif self.state == "alert" and (self.alert_timer // 6) % 2 == 0:
            txt = font_indicator.render("!", True, (255, 60, 60))
            surface.blit(txt, (sx + SLIME_W//2 - txt.get_width()//2, sy - 28))
        if self.max_hp > 1: self._draw_hp(surface, camera_x)

    def _draw_hp(self, surface, camera_x):
        bw, bh = SLIME_W, 6
        bx, by = int(self.x - camera_x), int(self.y) - 10
        pygame.draw.rect(surface, (60,60,60), (bx, by, bw, bh), border_radius=3)
        filled = int(bw * self.hp / self.max_hp)
        pygame.draw.rect(surface, self.colour, (bx, by, filled, bh), border_radius=3)
        pygame.draw.rect(surface, (200,200,200), (bx, by, bw, bh), 1, border_radius=3)

class GreenSlime(Slime):
    def __init__(self, x): super().__init__(x, green_frames, 1, 1.8, 90, 1, C_GREEN_SLIME)
class OrangeSlime(Slime):
    def __init__(self, x): super().__init__(x, orange_frames, 3, 3.5, 60, 2, C_ORANGE_SLIME); self.anim_speed = 0.4

# ── UI & Game Engine ──────────────────────────────────────────────────────────
class ScrollBG:
    def draw(self, surface, camera_x):
        surface.blit(bg1, (-camera_x, 0))
        surface.blit(bg2, (-camera_x + SCREEN_W, 0))

def draw_hud(player, slimes):
    font_big = pygame.font.SysFont(None, 28)
    bar_w, bar_h, padding = 36, 36, 6
    hx, hy = 20, 20
    for i in range(player.MAX_HP):
        bx = hx + i * (bar_w + padding)
        col = C_HP_FULL if i < player.hp else C_HP_EMPTY
        pygame.draw.rect(screen, col, (bx, hy, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, (200,220,200), (bx, hy, bar_w, bar_h), 2, border_radius=6)
        if i < player.hp: pygame.draw.circle(screen, (255,255,255), (bx+bar_w//2, hy+bar_h//2), 8)
    alive = sum(1 for s in slimes if s.alive)
    txt = font_big.render(f"Slimes: {alive} / 7", True, C_TEXT)
    screen.blit(txt, (SCREEN_W - txt.get_width() - 20, 20))

def draw_end_screen(win):
    overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160)); screen.blit(overlay, (0, 0))
    big, small = pygame.font.SysFont(None, 90), pygame.font.SysFont(None, 36)
    if win:
        msg = big.render("YOU WIN!", True, C_WIN)
        sub = small.render("All slimes defeated! Press R to restart.", True, C_TEXT)
    else:
        msg = big.render("GAME OVER", True, C_LOSE)
        sub = small.render("Press R to restart.", True, C_TEXT)
    screen.blit(msg, (SCREEN_W//2 - msg.get_width()//2, SCREEN_H//2 - 80))
    screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, SCREEN_H//2 + 20))

def make_game():
    player, tiles, valid_x = Player(), [], []
    for r_idx, row in enumerate(level_data):
        for c_idx, cell in enumerate(row):
            if cell == "1":
                rect = pygame.Rect(c_idx*TILE_SIZE, r_idx*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tiles.append(rect); valid_x.append(rect.x)
    valid_x = [x for x in list(set(valid_x)) if x > 400]
    slimes = []
    types = [GreenSlime, OrangeSlime, GreenSlime, GreenSlime, OrangeSlime, GreenSlime, OrangeSlime]
    chosen_pos = random.sample(valid_x, len(types)) if len(valid_x) >= len(types) else [random.choice(valid_x) for _ in types]
    for cls, sx in zip(types, chosen_pos): slimes.append(cls(sx))
    return player, slimes, ScrollBG(), tiles

def main():
    player, slimes, bg, tiles = make_game()
    game_over = game_win = False
    camera_x = 0
    
    # PLAY BGM
    if os.path.exists(BGM_PATH):
        pygame.mixer.music.load(BGM_PATH)
        pygame.mixer.music.set_volume(0.4) 
        pygame.mixer.music.play(-1) 

    while True:
        clock.tick(FPS)
        keys, m_btns = pygame.key.get_pressed(), pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    player, slimes, bg, tiles = make_game()
                    game_over = game_win = False; particles.clear()
                    # Restart BGM saat menekan R
                    if os.path.exists(BGM_PATH):
                        pygame.mixer.music.play(-1)
                if event.key == pygame.K_ESCAPE: pygame.quit(); sys.exit()

        if not game_over and not game_win:
            player.handle_input(keys, m_btns); player.update(tiles)
            camera_x = max(0, min(player.x - SCREEN_W//2, MAP_WIDTH - SCREEN_W))
            for slime in slimes:
                if not slime.alive: continue
                slime.update(player.x, tiles)
                if player.vy >= 0 and player.stomp_rect.colliderect(slime.head_rect):
                    slime.take_hit(); player.vy = -10
                    spawn_particles(slime.x + SLIME_W//2, slime.y, slime.colour, 10)
                elif player.rect.colliderect(slime.rect):
                    if player.is_defending:
                        if slime.state == "active" and slime.jump_timer < 30:
                            slime.vx, slime.vy, slime.jump_timer = -slime.facing*6, -4, 60
                            spawn_particles(slime.x+SLIME_W//2, slime.y+SLIME_H//2, (100,200,255), 8)
                    elif player.invuln == 0:
                        player.take_damage(slime.dmg)
                        slime.vx, slime.jump_timer = -slime.facing*3, 60
            if not player.alive: game_over = True
            
            # PLAY SOUND: WIN (Jika semua slime mati)
            if not game_win and all(not s.alive for s in slimes):
                game_win = True
                if snd_win:
                    snd_win.play()
                # Hentikan BGM saat menang
                pygame.mixer.music.fadeout(1000)

        bg.draw(screen, camera_x)
        for slime in slimes:
            if slime.alive: slime.draw(screen, camera_x)
        player.draw(screen, camera_x)
        update_draw_particles(camera_x)
        flash.draw(); draw_hud(player, slimes)
        if game_over: draw_end_screen(False)
        if game_win:  draw_end_screen(True)
        pygame.display.flip()

if __name__ == "__main__": main()