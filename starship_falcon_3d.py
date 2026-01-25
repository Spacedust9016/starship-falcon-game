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
