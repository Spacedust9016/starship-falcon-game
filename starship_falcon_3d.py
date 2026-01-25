#!/usr/bin/env python3
"""
🚀 Starship Falcon 3D - Space Valley Shooter
A modern 3D space shooter game with realistic physics and stunning visuals.
"""

import pygame
import pygame.locals as pg
import math
import random
import sys
from typing import List, Tuple, Dict

# Game Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GRAVITY = 0
MAX_SPEED = 5
ACCELERATION = 0.2
FRICTION = 0.95

# Colors (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2


class Vector2:
    """2D vector class for game physics"""
    def __init__(self, x: float = 0, y: float = 0):
        self.x = x
        self.y = y
    
    def __add__(self, other):
        return Vector2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self):
        mag = self.magnitude()
        if mag != 0:
            self.x /= mag
            self.y /= mag
        return self
    
    def limit(self, max_speed: float):
        mag = self.magnitude()
        if mag > max_speed:
            self.normalize()
            self.x *= max_speed
            self.y *= max_speed


class GameObject:
    """Base class for all game objects"""
    def __init__(self, x: float, y: float, width: float, height: float):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, 0)
        self.acceleration = Vector2(0, 0)
        self.width = width
        self.height = height
        self.alive = True
        self.angle = 0
        self.color = WHITE
    
    def update(self, dt: float):
        """Update object physics"""
        self.velocity += self.acceleration
        self.velocity *= FRICTION
        self.velocity.limit(MAX_SPEED)
        self.position += self.velocity
        self.acceleration = Vector2(0, 0)
    
    def apply_force(self, force: Vector2):
        """Apply force to object"""
        self.acceleration += force
    
    def draw(self, screen: pygame.Surface):
        """Draw object (to be overridden by subclasses)"""
        pass
    
    def check_collision(self, other) -> bool:
        """Check if this object collides with another"""
        return (self.position.x < other.position.x + other.width and
                self.position.x + self.width > other.position.x and
                self.position.y < other.position.y + other.height and
                self.position.y + self.height > other.position.y)


class Starship(GameObject):
    """Player-controlled starship"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 40, 60)
        self.color = YELLOW
        self.speed = 0
        self.max_health = 100
        self.health = self.max_health
        self.shoot_cooldown = 0
        self.shoot_rate = 0.2
        self.particles = []
        self.score = 0
    
    def update(self, dt: float):
        super().update(dt)
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
        
        # Update engine particles
        self.particles = [p for p in self.particles if p.alive]
        for particle in self.particles:
            particle.update(dt)
        
        # Generate engine particles
        if self.velocity.magnitude() > 0.5:
            for _ in range(2):
                particle = Particle(
                    self.position.x + random.randint(-15, 15),
                    self.position.y + self.height // 2,
                    ORANGE,
                    lifetime=0.5
                )
                particle.velocity = Vector2(
                    random.uniform(-1, 1),
                    random.uniform(2, 4)
                )
                self.particles.append(particle)
    
    def draw(self, screen: pygame.Surface):
        # Draw engine particles
        for particle in self.particles:
            particle.draw(screen)
        
        # Draw starship body
        ship_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Main body
        pygame.draw.polygon(ship_surface, self.color, [
            (self.width // 2, 0),
            (self.width, self.height),
            (self.width // 2, self.height - 10),
            (0, self.height)
        ])
        
        # Cockpit
        pygame.draw.circle(ship_surface, BLUE, (self.width // 2, self.height // 3), 8)
        
        # Wings
        pygame.draw.polygon(ship_surface, ORANGE, [
            (self.width // 2, self.height // 2),
            (self.width // 2 - 15, self.height // 2 + 10),
            (self.width // 2, self.height // 2 + 20),
            (self.width // 2 + 15, self.height // 2 + 10)
        ])
        
        screen.blit(ship_surface, (self.position.x - self.width // 2, self.position.y - self.height // 2))
    
    def shoot(self) -> 'Projectile':
        """Fire a projectile"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            return Projectile(
                self.position.x,
                self.position.y - self.height // 2,
                Vector2(0, -10)
            )
        return None
    
    def take_damage(self, damage: int):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
    
    def add_score(self, points: int):
        """Add points to score"""
        self.score += points


class Projectile(GameObject):
    """Projectile fired by the starship or enemies"""
    def __init__(self, x: float, y: float, velocity: Vector2):
        super().__init__(x, y, 4, 8)
        self.velocity = velocity
        self.color = GREEN
        self.lifetime = 2.0
        self.time_alive = 0
    
    def update(self, dt: float):
        self.position += self.velocity
        self.time_alive += dt
        if self.time_alive > self.lifetime:
            self.alive = False
    
    def draw(self, screen: pygame.Surface):
        pygame.draw.rect(
            screen,
            self.color,
            (self.position.x - self.width // 2, self.position.y - self.height // 2,
             self.width, self.height)
        )


class Enemy(GameObject):
    """Enemy spaceship"""
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 35, 50)
        self.color = RED
        self.health = 3
        self.pattern = random.choice(['straight', 'zigzag', 'circle'])
        self.pattern_timer = 0
        self.shoot_cooldown = random.uniform(1.0, 2.0)
        self.shoot_rate = random.uniform(1.0, 3.0)
    
    def update(self, dt: float):
        super().update(dt)
        
        # Move in patterns
        self.pattern_timer += dt
        
        if self.pattern == 'straight':
            self.velocity.y = 3
        elif self.pattern == 'zigzag':
            self.velocity.y = 2
            self.velocity.x = math.sin(self.pattern_timer * 2) * 3
        elif self.pattern == 'circle':
            self.velocity.x = math.sin(self.pattern_timer * 3) * 2
            self.velocity.y = math.cos(self.pattern_timer * 3) * 2
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= dt
    
    def draw(self, screen: pygame.Surface):
        enemy_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Enemy body
        pygame.draw.polygon(enemy_surface, self.color, [
            (self.width // 2, self.height),
            (self.width, 0),
            (self.width // 2, 10),
            (0, 0)
        ])
        
        # Enemy cockpit
        pygame.draw.circle(enemy_surface, YELLOW, (self.width // 2, self.height // 3), 6)
        
        screen.blit(enemy_surface, (self.position.x - self.width // 2, self.position.y - self.height // 2))
    
    def shoot(self) -> 'Projectile':
        """Fire a projectile"""
        if self.shoot_cooldown <= 0:
            self.shoot_cooldown = self.shoot_rate
            return Projectile(
                self.position.x,
                self.position.y + self.height // 2,
                Vector2(0, 5)
            )
        return None
    
    def take_damage(self, damage: int):
        """Take damage"""
        self.health -= damage
        if self.health <= 0:
            self.alive = False


class SpaceDebris(GameObject):
    """Space debris object"""
    def __init__(self, x: float, y: float):
        size = random.randint(10, 30)
        super().__init__(x, y, size, size)
        self.color = (100, 100, 100)
        self.velocity = Vector2(random.uniform(-2, 2), random.uniform(2, 5))
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.shape = random.choice(['rock1', 'rock2', 'rock3'])
    
    def update(self, dt: float):
        super().update(dt)
        self.rotation += self.rotation_speed
        if self.rotation > 360:
            self.rotation -= 360
        if self.rotation < 0:
            self.rotation += 360
    
    def draw(self, screen: pygame.Surface):
        debris_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw debris shape
        if self.shape == 'rock1':
            pygame.draw.polygon(debris_surface, self.color, [
                (self.width // 2, 0),
                (self.width, self.height // 3),
                (self.width // 2, self.height),
                (0, self.height // 2)
            ])
        elif self.shape == 'rock2':
            pygame.draw.polygon(debris_surface, self.color, [
                (self.width // 2, 0),
                (self.width, self.height // 2),
                (self.width // 2, self.height),
                (0, self.height // 2)
            ])
        else:
            pygame.draw.circle(debris_surface, self.color, (self.width // 2, self.height // 2), self.width // 2)
        
        # Rotate the debris
        rotated_surface = pygame.transform.rotate(debris_surface, self.rotation)
        rect = rotated_surface.get_rect()
        
        screen.blit(
            rotated_surface,
            (self.position.x - rect.width // 2, self.position.y - rect.height // 2)
        )


class Particle(GameObject):
    """Particle effect"""
    def __init__(self, x: float, y: float, color: Tuple[int, int, int], lifetime: float = 1.0):
        size = random.randint(2, 5)
        super().__init__(x, y, size, size)
        self.color = color
        self.lifetime = lifetime
        self.time_alive = 0
        self.velocity = Vector2(
            random.uniform(-2, 2),
            random.uniform(-2, 2)
        )
    
    def update(self, dt: float):
        self.position += self.velocity
        self.time_alive += dt
        if self.time_alive > self.lifetime:
            self.alive = False
    
    def draw(self, screen: pygame.Surface):
        # Fade out effect using a surface with alpha
        alpha = max(0, min(255, int(255 * (1 - self.time_alive / self.lifetime))))
        w, h = int(self.width), int(self.height)
        if w <= 0 or h <= 0:
            return
        particle_surface = pygame.Surface((w, h), pygame.SRCALPHA)
        color = (int(self.color[0]), int(self.color[1]), int(self.color[2]), alpha)
        pygame.draw.rect(particle_surface, color, (0, 0, w, h))
        screen.blit(particle_surface, (int(self.position.x - w // 2), int(self.position.y - h // 2)))


class Background:
    """Game background with starfield and parallax effect"""
    def __init__(self):
        self.stars = []
        self.planets = []
        self.create_stars()
        self.create_planets()
        self.speed = 0
    
    def create_stars(self):
        """Create starfield"""
        for _ in range(200):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(-SCREEN_HEIGHT, SCREEN_HEIGHT)
            size = random.randint(1, 3)
            brightness = random.randint(50, 255)
            color = (brightness, brightness, brightness)
            speed = random.uniform(1, 5)
            self.stars.append({
                'x': x, 'y': y, 'size': size, 'color': color, 'speed': speed
            })
    
    def create_planets(self):
        """Create distant planets (parallax effect)"""
        for _ in range(3):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(-SCREEN_HEIGHT, 0)
            size = random.randint(30, 60)
            color = random.choice([(138, 43, 226), (0, 191, 255), (255, 165, 0)])
            speed = random.uniform(0.5, 1.5)
            self.planets.append({
                'x': x, 'y': y, 'size': size, 'color': color, 'speed': speed
            })
    
    def update(self, dt: float):
        """Update background"""
        # Update stars
        for star in self.stars:
            star['y'] += star['speed'] * (self.speed / 2)
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = -10
                star['x'] = random.randint(0, SCREEN_WIDTH)
        
        # Update planets
        for planet in self.planets:
            planet['y'] += planet['speed'] * (self.speed / 4)
            if planet['y'] > SCREEN_HEIGHT:
                planet['y'] = -100
                planet['x'] = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen: pygame.Surface):
        """Draw background"""
        # Draw planets
        for planet in self.planets:
            pygame.draw.circle(screen, planet['color'], (int(planet['x']), int(planet['y'])), planet['size'])
        
        # Draw stars
        for star in self.stars:
            pygame.draw.rect(
                screen,
                star['color'],
                (int(star['x']), int(star['y']), star['size'], star['size'])
            )


class Game:
    """Main game class"""
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Starship Falcon 3D")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.state = STATE_MENU
        self.background = Background()
        self.starship = None
        self.projectiles = []
        self.enemies = []
        self.debris = []
        self.particles = []
        self.score = 0
        self.enemy_spawn_timer = 0
        self.debris_spawn_timer = 0
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
    
    def run(self):
        """Main game loop"""
        while True:
            dt = self.clock.tick(FPS) / 1000
            
            for event in pygame.event.get():
                if event.type == pg.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pg.KEYDOWN:
                    if self.state == STATE_MENU:
                        if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                            self.start_game()
                    elif self.state == STATE_GAME_OVER:
                        if event.key == pg.K_SPACE or event.key == pg.K_RETURN:
                            self.start_game()
            
            self.handle_input()
            self.update(dt)
            self.draw()
    
    def handle_input(self):
        """Handle keyboard input"""
        keys = pygame.key.get_pressed()
        
        if self.state == STATE_PLAYING and self.starship:
            # Movement
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.starship.apply_force(Vector2(-ACCELERATION, 0))
            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.starship.apply_force(Vector2(ACCELERATION, 0))
            if keys[pg.K_UP] or keys[pg.K_w]:
                self.starship.apply_force(Vector2(0, -ACCELERATION))
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.starship.apply_force(Vector2(0, ACCELERATION))
            
            # Shooting
            if keys[pg.K_SPACE]:
                projectile = self.starship.shoot()
                if projectile:
                    self.projectiles.append(projectile)
    
    def update(self, dt: float):
        """Update game state"""
        if self.state == STATE_PLAYING:
            # Update background
            self.background.speed = 1
            self.background.update(dt)
            
            # Update starship
            self.starship.update(dt)
            
            # Boundary checks
            if self.starship.position.x < 0:
                self.starship.position.x = 0
            if self.starship.position.x > SCREEN_WIDTH:
                self.starship.position.x = SCREEN_WIDTH
            if self.starship.position.y < 0:
                self.starship.position.y = 0
            if self.starship.position.y > SCREEN_HEIGHT:
                self.starship.position.y = SCREEN_HEIGHT
            
            # Spawn enemies
            self.enemy_spawn_timer += dt
            if self.enemy_spawn_timer > 2.0:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0
            
            # Spawn debris
            self.debris_spawn_timer += dt
            if self.debris_spawn_timer > 1.5:
                self.spawn_debris()
                self.debris_spawn_timer = 0
            
            # Update projectiles
            self.projectiles = [p for p in self.projectiles if p.alive]
            for projectile in self.projectiles:
                projectile.update(dt)
                
                # Remove projectiles outside screen
                if (projectile.position.x < 0 or projectile.position.x > SCREEN_WIDTH or
                    projectile.position.y < 0 or projectile.position.y > SCREEN_HEIGHT):
                    projectile.alive = False
            
            # Update enemies
            self.enemies = [e for e in self.enemies if e.alive]
            for enemy in self.enemies:
                enemy.update(dt)
                
                # Enemy shooting
                projectile = enemy.shoot()
                if projectile:
                    self.projectiles.append(projectile)
                
                # Remove enemies outside screen
                if enemy.position.y > SCREEN_HEIGHT + 50:
                    enemy.alive = False
            
            # Update debris
            self.debris = [d for d in self.debris if d.alive]
            for debris in self.debris:
                debris.update(dt)
                
                # Remove debris outside screen
                if debris.position.y > SCREEN_HEIGHT + 50:
                    debris.alive = False
            
            # Update particles
            self.particles = [p for p in self.particles if p.alive]
            for particle in self.particles:
                particle.update(dt)
            
            # Check collisions
            self.check_collisions()
    
    def check_collisions(self):
        """Check for collisions between game objects"""
        # Projectiles vs Enemies
        for projectile in self.projectiles:
            if projectile.velocity.y < 0:  # Player's projectile
                for enemy in self.enemies:
                    if projectile.check_collision(enemy):
                        enemy.take_damage(1)
                        projectile.alive = False
                        self.starship.add_score(100)
                        
                        # Create explosion particles
                        self.create_explosion(enemy.position.x, enemy.position.y)
                        
                        break
            
            elif projectile.velocity.y > 0:  # Enemy's projectile
                if projectile.check_collision(self.starship):
                    self.starship.take_damage(20)
                    projectile.alive = False
                    self.create_explosion(self.starship.position.x, self.starship.position.y)
        
        # Starship vs Enemies
        for enemy in self.enemies:
            if self.starship.check_collision(enemy):
                self.starship.take_damage(50)
                enemy.alive = False
                self.create_explosion(enemy.position.x, enemy.position.y)
        
        # Starship vs Debris
        for debris in self.debris:
            if self.starship.check_collision(debris):
                self.starship.take_damage(30)
                debris.alive = False
                self.create_explosion(debris.position.x, debris.position.y)
        
        # Check game over
        if not self.starship.alive:
            self.state = STATE_GAME_OVER
    
    def create_explosion(self, x: float, y: float):
        """Create explosion particle effect"""
        for _ in range(20):
            particle = Particle(x, y, ORANGE, lifetime=0.5)
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            particle.velocity = Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            self.particles.append(particle)
    
    def spawn_enemy(self):
        """Spawn an enemy"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        enemy = Enemy(x, -50)
        self.enemies.append(enemy)
    
    def spawn_debris(self):
        """Spawn space debris"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        debris = SpaceDebris(x, -50)
        self.debris.append(debris)
    
    def start_game(self):
        """Start a new game"""
        self.state = STATE_PLAYING
        self.starship = Starship(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.projectiles = []
        self.enemies = []
        self.debris = []
        self.particles = []
        self.enemy_spawn_timer = 0
        self.debris_spawn_timer = 0
        self.score = 0
        self.background.speed = 0
    
    def draw(self):
        """Draw game elements"""
        self.screen.fill(BLACK)
        
        self.background.draw(self.screen)
        
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_PLAYING:
            self.draw_playing()
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_menu(self):
        """Draw main menu"""
        title = self.large_font.render("STARSHIP FALCON 3D", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(title, title_rect)
        
        instruction = self.font.render("Press SPACE or RETURN to Start", True, WHITE)
        instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(instruction, instruction_rect)
        
        controls = [
            "W/UP   - Move Up",
            "S/DOWN - Move Down",
            "A/LEFT - Move Left",
            "D/RIGHT - Move Right",
            "SPACE - Shoot",
            "ESC - Quit"
        ]
        
        y_offset = SCREEN_HEIGHT // 2 + 80
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, (150, 150, 150))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset + i * 30))
            self.screen.blit(text, text_rect)
    
    def draw_playing(self):
        """Draw playing state"""
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(self.screen)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        # Draw debris
        for debris in self.debris:
            debris.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw starship
        if self.starship:
            self.starship.draw(self.screen)
        
        # Draw UI
        score_text = self.font.render(f"Score: {self.starship.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        
        health_text = self.font.render(f"Health: {self.starship.health}/{self.starship.max_health}", True, WHITE)
        self.screen.blit(health_text, (20, 60))
        
        enemy_text = self.font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
        self.screen.blit(enemy_text, (20, 100))
        
        debris_text = self.font.render(f"Debris: {len(self.debris)}", True, WHITE)
        self.screen.blit(debris_text, (20, 140))
    
    def draw_game_over(self):
        """Draw game over state"""
        # Draw starfield (slower)
        self.background.speed = 0.5
        self.background.update(1/60)
        self.background.draw(self.screen)
        
        # Draw game over text
        game_over_text = self.large_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.screen.blit(game_over_text, game_over_rect)
        
        score_text = self.font.render(f"Final Score: {self.starship.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(score_text, score_rect)
        
        restart_text = self.font.render("Press SPACE to Restart", True, YELLOW)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
        
        quit_text = self.small_font.render("Press ESC to Quit", True, (150, 150, 150))
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(quit_text, quit_rect)


if __name__ == "__main__":
    import traceback
    print("Starship Falcon 3D - Space Valley Shooter")
    print("Controls: W/A/S/D or Arrow Keys to move, SPACE to shoot, ESC to quit")
    
    try:
        game = Game()
        game.run()
    except Exception as e:
        traceback.print_exc()
        pygame.quit()
        sys.exit(1)

