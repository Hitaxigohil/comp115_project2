class Settings:
    """A class to store all settings for Alien Invasion."""

    def __init__(self):
        """Initialize the game's settings."""
        # Screen settings 
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (10, 10, 30)  
        self.star_color = (255, 255, 255) 
        self.star_speed = 1  
        self.ship_speed=3
        self.fullscreen_mode=True
        self.ship_limit=3
        #bullet settings
        self.bullet_speed = 5
        self.bullet_width = 4
        self.bullet_height = 15
        self.bullet_color = (255,215, 0)
        self.bullets_allowed = 100
      
        #alien setting
        self.alien_speed = 1.0
        self.fleet_drop_speed = 10

        #how quickly the game speeds up
        self.speedup_scale=1.1
        self.score_scale=1.5
        self.initialize_dynamic_settings()
        #fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        self.normal_bullets_allowed=3
        self.bullets_allowed=100
    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 3
        self.bullet_speed = 5
        self.alien_speed = 1.0
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction=1
        self.alien_points=50

    def increase_speed(self):
        """Increase speed settings."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_points=int(self.alien_points * self.score_scale)
        print(self.alien_points)
