import sys
import math
from random import randint, choice
import pygame
from pygame.locals import *
from collections import defaultdict

WIDTH = 1200
HEIGHT = 900

ALIENSHIPS = 'alienships'
SPACESHIP = 'spaceship'
PROJECTILE = 'projectile'
ALIEN_PROJECTILE = 'alien_projectile'
ASTEROIDS = 'asteroid'
POWERUPS = 'powerups'

class Projectile(pygame.sprite.Sprite):

    speed = 15

    def __init__(self, pos, angle):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.angle = angle + 90
        self.image = pygame.image.load('./pix/torpedo.gif')
        self.image = pygame.transform.rotate(self.image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = pos

    def update(self):
        dx = Projectile.speed * math.sin(math.radians(self.angle))
        dy = Projectile.speed * math.cos(math.radians(self.angle))
        self.rect.move_ip((dx, dy))


class Spaceship(pygame.sprite.Sprite):
    
    speed = 10

    def __init__(self, pos, screen_rect):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.screen_rect = screen_rect
        self.image_master = pygame.image.load('./pix/spaceship.gif')
        self.image_master_protected = pygame.image.load('./pix/spaceship_protected.gif')
        self.image = self.image_master
        self.explode_image = pygame.image.load('./pix/explosion.gif')
        self.rect = self.image.get_rect()
        self.rect.center = pos
        self.destroyed = False
        self.angle = 0
        self.shoot_delay = 0
        self.fire_rate = 10
        self.protected = False
        self.pressed = []
        self.moves = {K_a: (-1, 0), K_d: (1, 0), K_w: (0, -1), K_s: (0, 1)}
        self.lives = 3
        self.powup_projectile_timer = 0
        self.powup_protected_timer = 0
    
    def update(self):
        self.pressed = pygame.key.get_pressed()
        self.rotate()
        self.move()
        self.shooting()
        center = self.rect.center
        if self.protected:
            self.image = pygame.transform.rotate(self.image_master_protected, self.angle)
        else:
            self.image = pygame.transform.rotate(self.image_master, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = center
        # fire rate power up
        if self.powup_projectile_timer != 0:
            self.powup_projectile_timer -= 1
            self.fire_rate = 2
        else:
            self.fire_rate = 10
        # protected power up
        if self.powup_protected_timer != 0:
            self.powup_protected_timer -= 1
            self.protected = True
        else:
            self.protected = False
        if self.shoot_delay == 0:
            self.shoot_delay = self.fire_rate
        self.shoot_delay -= 1
    
    def move(self):
        move_vector = (0, 0)
        for m in (self.moves[key] for key in self.moves if self.pressed[key]):
            move_vector = map(sum, zip(move_vector, m))
        if sum(map(abs, move_vector)) == 2:
            move_vector = [p / 1.4142 for p in move_vector]
        move_vector = [Spaceship.speed * p for p in move_vector]
        self.rect.move_ip(move_vector)
        self.pos = (self.rect.centerx, self.rect.centery)
        self.rect.clamp_ip(self.screen_rect)

    def rotate(self):
        if self.pressed[K_RIGHT]:
            self.angle -= 5
        if self.pressed[K_LEFT]:
            self.angle += 5

    def shooting(self):
        return self.pressed[K_SPACE] and self.shoot_delay == 0

    def create_projectile(self):
        return Projectile(self.pos, self.angle)

    def take_hit(self):
        if not self.protected:
            self.lives -= 1
            if self.lives == 0:
                self.destroyed = True
                self.image_master = self.explode_image

    def use_powerup(self, powerup):
        powerup.use(self)

    def powerup_projectile(self):
        self.powup_projectile_timer += 400

    def powerup_protect(self):
        self.powup_protected_timer += 400

    def powerup_life(self):
        self.lives += 1


class AlienProjectile(Projectile):
    
    speed = 8



class Alienship(pygame.sprite.Sprite):
    
    moves = [[-1, 1], [0, 1], [1, 1]]
    speeds = [3, 4]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./pix/alienship.gif')
        self.rect = self.image.get_rect()
        self.x = randint(0, WIDTH)
        self.rect.center = (self.x, 0)
        self.direction = choice(Alienship.moves)
        self.speed = choice(Alienship.speeds) 
        if sum(map(abs, self.direction)) == 2:
            self.direction = [p / 1.412 for p in self.direction]
        self.direction = [self.speed * p for p in self.direction]
        self.pos = (self.rect.centerx, self.rect.centery)

    def update(self):
        self.rect.move_ip(self.direction)
        self.pos = (self.rect.centerx, self.rect.centery)

    def shooting(self):
        return True if randint(1, 100) > 95 else False

    def create_projectile(self):
        return AlienProjectile(self.pos, randint(1, 360))


class Powerup(pygame.sprite.Sprite):
    
    speeds = [3, 4, 5]

    def __init__(self, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.center = (randint(0, WIDTH), 0)
        self.direction = [0, choice(Powerup.speeds)]
        self.timer = 400

    def update(self):
        self.rect.move_ip(self.direction)

    def use(self, spaceship):
        pass


class PowerupProjectile(Powerup):
    
    def __init__(self):
        Powerup.__init__(self, './pix/powerup_projectile.gif')
    
    def use(self, spaceship):
        spaceship.powerup_projectile()


class PowerupProtect(Powerup):
    
    def __init__(self):
        Powerup.__init__(self, './pix/powerup_protect.gif')

    def use(self, spaceship):
        spaceship.powerup_protect()


class PowerupLife(Powerup):

    def __init__(self):
        Powerup.__init__(self, './pix/powerup_life.gif')

    def use(self, spaceship):
        spaceship.powerup_life()


class Asteroid(pygame.sprite.Sprite):
    
    IMAGES = ['./pix/asteroid1.gif', 
              './pix/asteroid2.gif', 
              './pix/asteroid3.gif', 
              './pix/asteroid4.gif']

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(choice(Asteroid.IMAGES))
        self.rect = self.image.get_rect()
        self.x = randint(0, WIDTH)
        self.rect.center = (self.x, 0)
        self.speed = randint(1, 3)
    
    def update(self):
        self.rect.move_ip((0, self.speed))



class Spyace():

    def __init__(self, screen_rect):
        self.score = 0
        self.spaceship = Spaceship((randint(0, HEIGHT), 900), screen_rect)
        self.sprites = defaultdict(pygame.sprite.RenderPlain)
        self.sprites[SPACESHIP].add(self.spaceship)
        self.asteroid_counter = 1
        self.multiplier = 1
    
    def update_sprites(self):
        for sprite in self.sprites:
            self.sprites[sprite].update()

    def draw_sprites_to_screen(self, screen):
        for sprite in self.sprites:
            self.sprites[sprite].draw(screen)

    def game_over(self):
        return self.spaceship.destroyed

    def tick(self):
        # check if spaceship is shooting
        if self.spaceship.shooting() and self.spaceship.shoot_delay == 0:
            self.sprites[PROJECTILE].add(self.spaceship.create_projectile())

        # check if alienship is shooting or out of bounds
        for alienship in self.sprites[ALIENSHIPS]:
            if not valid_coords(alienship):
                self.sprites[ALIENSHIPS].remove(alienship)
            if alienship.shooting():
                self.sprites[ALIEN_PROJECTILE].add(alienship.create_projectile())

        # check if projectile is out of bounds, or hits asteroid, or hits alien
        for projectile in self.sprites[PROJECTILE]:
            if not valid_coords(projectile):
                self.sprites[PROJECTILE].remove(projectile)
            for asteroid in self.sprites[ASTEROIDS]:
                if collision(asteroid, projectile):
                    self.score += 1
                    self.sprites[ASTEROIDS].remove(asteroid)
                    break
            for alienship in self.sprites[ALIENSHIPS]:
                if collision(projectile, alienship):
                    self.score += 3
                    self.sprites[ALIENSHIPS].remove(alienship)
                    break

        # check if alien projectile is out of bounds, or hits asteroid, or hits spaceship
        for alien_projectile in self.sprites[ALIEN_PROJECTILE]:
            if not valid_coords(alien_projectile):
                self.sprites[ALIEN_PROJECTILE].remove(alien_projectile)
            if collision(alien_projectile, self.spaceship):
                self.spaceship.take_hit()
                self.sprites[ALIEN_PROJECTILE].remove(alien_projectile)
                break

        # check if asteroid is out of bounds, or hits spaceship
        for asteroid in self.sprites[ASTEROIDS]:
            if not valid_coords(asteroid):
                self.sprites[ASTEROIDS].add(Asteroid())
                self.sprites[ASTEROIDS].remove(asteroid)
            if collision(asteroid, self.spaceship):
                self.spaceship.take_hit()
                self.sprites[ASTEROIDS].remove(asteroid)
                break

        # add new asteroids
        if self.asteroid_counter >= 60:
            self.sprites[ASTEROIDS].add(Asteroid())
            self.asteroid_counter = 0
        self.asteroid_counter += self.multiplier
        self.multiplier *= 1.0001

        # add new alien ships
        if randint(1, 300) == 60:
            self.sprites[ALIENSHIPS].add(Alienship())

        # add random powerups
        if randint(1, 1000) == 60:
            self.sprites[POWERUPS].add(choice([PowerupProjectile(), PowerupProtect()]))
        if randint(1, 2000) == 60:
            self.sprites[POWERUPS].add(PowerupLife())

        # check for collisions with powerups and check if powerups are used up
        for powerup in self.sprites[POWERUPS]:
            if not valid_coords(powerup):
                self.sprites[POWERUPS].remove(powerup)
                break
            if collision(powerup, self.spaceship):
                self.spaceship.use_powerup(powerup)
                self.sprites[POWERUPS].remove(powerup)
                break

def main():
    pygame.init()
    size = (WIDTH, HEIGHT)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)
    screen_rect = pygame.Rect((0, 0), size)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    game_font = pygame.font.Font(None, 30)
    large_font = pygame.font.Font(None, 60)
    font_color = (255, 255, 255)
    
    spaceship_destroyed_delay = 50
    paused = False
    spyace = Spyace(screen_rect)
    while True:   
        if paused:
            continue  
        
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                if event.key == K_ESCAPE:
                    sys.exit(0)
        clock.tick(60)
        screen.blit(background, (0, 0))
       
        # display score
        game_text = game_font.render('Score: {0}    Lives: {1}'.format(spyace.score, spyace.spaceship.lives), True, font_color)
        powerup_shield_text = game_font.render('Shield: {0}%'.format(percentage(spyace.spaceship.powup_protected_timer, 400)), True, font_color)
        powerup_firerate_text = game_font.render('Firerate: {0}%'.format(percentage(spyace.spaceship.powup_projectile_timer, 400)), True, font_color)
        screen.blit(game_text, (0, 0))
        screen.blit(powerup_shield_text, (WIDTH / 2 - 180, 0))
        screen.blit(powerup_firerate_text, (WIDTH / 2 + 50, 0))

        # check if spaceship is destroyed      
        if spyace.game_over():
            if spaceship_destroyed_delay == 0:
                break
            else:
                spaceship_destroyed_delay -= 1

        # Update all sprites
        spyace.update_sprites()

        # Do a game tick
        spyace.tick()

        # Draw sprites to screen
        spyace.draw_sprites_to_screen(screen)
        
        # Flip display buffers
        pygame.display.flip()
    
    # display score when game over
    score_text = large_font.render('Score: {0}'.format(spyace.score), True, (255, 255, 255))
    continue_text = game_font.render('Press any key to continue or esc to quit.', True, (255, 255, 255))
    screen.blit(score_text, (WIDTH / 2 - 150, HEIGHT/ 2))
    screen.blit(continue_text, (WIDTH / 2 - 150, HEIGHT / 2 + 100))
    pygame.display.update()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    sys.exit(0)
                main()

def collision(sprite_a, sprite_b):
    return sprite_a.rect.colliderect(sprite_b)

def valid_coords(sprite, width=WIDTH, height=HEIGHT):
    rect = sprite.rect
    return 0 <= rect.centerx <= width and 0 <= rect.centery <= height

def percentage(current, total):
    return int(round(100 * current / total))

if __name__ == '__main__':
    main()

