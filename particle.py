import pygame
import random
from pygame.sprite import Sprite

class Particle(Sprite):
    """A class to represent a single particle from an explosion."""
    def __init__(self, ai_game, x, y):
        super().__init__()
        self.screen = ai_game.screen
        
        # Create a small square for the particle
        size = random.randint(2, 5)
        self.image = pygame.Surface((size, size))
        
        # Make it a random "fire" color (Orange, Yellow, Red)
        self.image.fill((random.randint(200, 255), random.randint(50, 150), 0))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        # Give it a random direction and speed
        self.v_x = random.uniform(-3, 3)
        self.v_y = random.uniform(-3, 3)
        self.lifetime = 20  # How many frames it lasts

    def update(self):
        """Move the particle and fade it out."""
        self.rect.x += self.v_x
        self.rect.y += self.v_y
        self.lifetime -= 1
        
        # Delete the particle when it 'dies'
        if self.lifetime <= 0:
            self.kill()