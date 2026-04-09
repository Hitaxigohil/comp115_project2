import sys
import random
from time import sleep
import pygame
import pygame.font

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from particle import Particle
from button import Button
from ship import Ship
from bullet import Bullet
from alien import Alien



class AlienInvasion:
    """Overall class to manage game assets and behavior."""
    

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        self.stars=[]
        
        for i in range(50):
            x = random.randint(0, self.settings.screen_width)
            y = random.randint(0, self.settings.screen_height)
            self.stars.append([x, y])

        #Create the screen as a window and set the SIZE to the window you want
        if self.settings.fullscreen_mode:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.settings.screen_width = self.screen.get_rect().width
            self.settings.screen_height = self.screen.get_rect().height
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height))
        pygame.display.set_caption("Hitaxi's Alien Invasion")

        #create an instance to store game stats
        self.stats = GameStats(self)
        self.aliens_killed=0
        self.combo_active= False
        self.combo_start_time=0
        self.combo_frames=0
        self.sb= Scoreboard(self)
        self.game_active = False
        self.particles = pygame.sprite.Group()

        
        
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

        self.play_button = Button(self, "Play")
        self.bg_color = (10, 10, 30)  
        self.star_color = (255, 255, 255) 
        
        self.normal_bullets_allowed = 3

    def _create_fleet(self):
        """Create the fleet of aliens."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        
        # Start the first alien at one width/height in from the top-left
        current_x, current_y = alien_width, alien_height
        
        # OUTER LOOP: Controls the rows (Vertical / Y)
        while current_y < (self.settings.screen_height - 3 * alien_height):
            
            # INNER LOOP: Controls the aliens in each row (Horizontal / X)
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x, current_y)
                current_x += 2 * alien_width
            
            # Row finished! 
            # 1. Reset x to the left side for the NEXT row
            current_x = alien_width
            # 2. Move y down to the next row level
            current_y += 2 * alien_height


    def _create_alien(self, x_position, y_position):
        """Create an alien and place it in the fleet."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position # This places it in the correct row
        self.aliens.add(new_alien)
           
    def _check_fleet_edges(self):
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1


    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self.particles.update()

                if self.combo_active:
                    current_time=pygame.time.get_ticks()

                    if current_time-self.combo_start_time<2000:
                        self.combo_frames+=1
                        if self.combo_frames%10==0:
                            self._fire_bullet()
                    else:
                        self.combo_active=False
                        self.combo_frames=0
                        self.aliens_killed=0
                        self.sb.prep_kills()
                     
                
            self._update_screen()
            self.clock.tick(60)

            

            

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type== pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mouse_pos=pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        if self.play_button.rect.collidepoint(mouse_pos):
            button_clicked= self.play_button.rect.collidepoint(mouse_pos)
            if button_clicked and not self.game_active:
                #reset the game settings
                self.settings.initialize_dynamic_settings()
                self.stats.reset_stats()
                self.aliens_killed=0
                self.combo_active=False
                self.combo_frames=0
                self.sb.prep_score()
                self.sb.prep_level()
                self.sb.prep_ships()
                self.game_active=True
                # get rid of remaining bullets and aliens
                self.bullets.empty()
                self.aliens.empty()
                #create a new fleet and center the ship
                self.ship.center_ship()

                #hide cursor
                pygame.mouse.set_visible(False)
                pygame.mouse.set_visible(True)


    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right= True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key== pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        if event.key== pygame.K_RIGHT:
            self.ship.moving_right= False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """create a new bullet and add it to the bullets group."""
        if self.combo_active:
            limit = self.settings.bullets_allowed
        else:
            limit = self.settings.normal_bullets_allowed

        if len(self.bullets) < limit:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)
        
                   
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

       
        #get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom<=0:
                self.bullets.remove(bullet)
            

        self._check_bullet_alien_collisions()
        
    def _check_bullet_alien_collisions(self):
        # remove any bullets and alients that ahev collided
        colllisions =  pygame.sprite.groupcollide(
                self.bullets, self.aliens, True, True)
        
        if colllisions:
            for aliens in colllisions.values():
                for alien in aliens:
                    for _ in range(15):
                        new_particle = Particle(self, alien.rect.centerx, alien.rect.centery)
                        self.particles.add(new_particle)
                num_aliens = len(aliens)
                self.stats.score += self.settings.alien_points * num_aliens
                
                # Update combo counter
                self.aliens_killed += num_aliens
                self.sb.prep_kills()

                # Trigger combo every 10 kills
                if self.aliens_killed >= 10 and not self.combo_active:
                    self.combo_active = True
                    self.combo_start_time = pygame.time.get_ticks()
            
            self.sb.prep_score()
            self.sb.check_high_score()
          
        if not self.aliens: 
            #destory existing aliens and create new fleet
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()

            #increase level
            self.stats.level += 1
            self.sb.prep_level()


    def _update_screen(self):
        """update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        for star in self.stars:
            star[1] += self.settings.star_speed
            if star[1] > self.settings.screen_height:
                star[1] = 0
            pygame.draw.rect(self.screen, self.settings.star_color, (star[0], star[1], 2, 2))

        
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()  

        self.particles.draw(self.screen)
        

        if self.combo_active:
            combo_font=pygame.font.SysFont(None, 70)
            combo_image=combo_font.render("COMBO ACTIVE!", True, (255, 0, 0))
            combo_rect=combo_image.get_rect()
            combo_rect.center=self.screen.get_rect().center
            self.screen.blit(combo_image, combo_rect)

        #draw score info
        self.ship.blitme()
        self.aliens.draw(self.screen) 
        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()

            # Make the most recently drawn screen visible.
        pygame.display.flip()

    def _update_aliens(self):
        self._check_fleet_edges()
        self.aliens.update()
        self.aliens.update()
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

         
        self._check_aliens_bottom()
        
    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left>0:
            # Decrement ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships() 
        
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
 
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()

            #pause
            sleep(0.5)

        else:
            self.game_active = False
    
    

      

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():

            if alien.rect.bottom >= self.settings.screen_height:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break
  

if __name__ == '__main__':
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()

