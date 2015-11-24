import sys
import math
from random import randint, choice
import pygame
from pygame.locals import *


class Spaceship(pygame.sprite.Sprite):
    
    speed = 10

    def __init__(self, pos, screen_rect):
        pygame.sprite.Sprite.__init__(self)
        self.pos = pos
        self.screen_rect = screen_rect
        self.imageMaster = pygame.image.load('./pix/spaceship.gif')
        self.imageMasterProtected = pygame.image.load('./pix/spaceship_protected.gif')
        self.image = self.imageMaster
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
            self.image = pygame.transform.rotate(self.imageMasterProtected, self.angle)
        else:
            self.image = pygame.transform.rotate(self.imageMaster, self.angle)
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

    def take_hit(self):
        if not self.protected:
            self.lives -= 1
            if self.lives == 0:
                self.destroyed = True
                self.imageMaster = self.explode_image

    def powerup_projectile(self):
        self.powup_projectile_timer += 400

    def powerup_protect(self):
        self.powup_protected_timer += 400

    def powerup_life(self):
        self.lives += 1


class Alienship(pygame.sprite.Sprite):
    
    moves = [[-1, 1], [0, 1], [1, 1]]
    speeds = [3, 4]

    def __init__(self, width):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./pix/alienship.gif')
        self.rect = self.image.get_rect()
        self.x = randint(0, width)
        self.rect.center = (self.x, 0)
        self.direction = choice(Alienship.moves)
        self.speed = choice(Alienship.speeds) 
        if sum(map(abs, self.direction)) == 2:
            self.direction = [p / 1.412 for p in self.direction]
        self.direction = [self.speed * p for p in self.direction]

    def update(self):
        self.rect.move_ip(self.direction)

    def shooting(self):
        return True if randint(1, 100) > 95 else False
        

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


class AlienProjectile(Projectile):
    
    speed = 8


class Powerup(pygame.sprite.Sprite):
    
    speeds = [3, 4, 5]

    def __init__(self, width, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.rect.center = (randint(0, width), 0)
        self.direction = [0, choice(Powerup.speeds)]
        self.activated = False
        self.timer = 400

    def activate(self):
        self.activated = True
    
    def spent(self):
        return self.timer == 0

    def update(self):
        if self.activated:
            self.timer -= 1
        self.rect.move_ip(self.direction)


class PowerupProjectile(Powerup):
    
    def __init__(self, spaceship, width):
        Powerup.__init__(self, width, './pix/powerup_projectile.gif')
        self.spaceship = spaceship
        self.original_fire_rate = self.spaceship.fire_rate
    
    def use(self):
        self.spaceship.powerup_projectile()


class PowerupProtect(Powerup):
    
    def __init__(self, spaceship, width):
        Powerup.__init__(self, width, './pix/powerup_protect.gif')
        self.spaceship = spaceship

    def use(self):
        self.spaceship.powerup_protect()


class PowerupLife(Powerup):

    def __init__(self, spaceship, width):
        Powerup.__init__(self, width, './pix/powerup_life.gif')
        self.spaceship = spaceship

    def use(self):
        self.spaceship.powerup_life()


class Asteroid(pygame.sprite.Sprite):

    def __init__(self, width, image_path):
        pygame.sprite.Sprite.__init__(self)
        self.image_path = image_path
        self.image = pygame.image.load(image_path)
        self.rect = self.image.get_rect()
        self.x = randint(0, width)
        self.rect.center = (self.x, 0)
        self.speed = randint(1, 3)
    
    def update(self):
        self.rect.move_ip((0, self.speed))


def main():
    pygame.init()
    width = 1200
    height = 900
    size = (width, height)
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(size)
    screen_rect = pygame.Rect((0, 0), size)
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    game_font = pygame.font.Font(None, 30)
    font_color = (255, 255, 255)

    asteroid_images = ['./pix/asteroid1.gif', './pix/asteroid2.gif', './pix/asteroid3.gif', './pix/asteroid4.gif']
    spaceship = Spaceship((randint(0, width), 900), screen_rect)
    spaceship_sprite = pygame.sprite.RenderPlain((spaceship, ))
    alienship_sprites = pygame.sprite.RenderPlain(())
    projectile_sprites = pygame.sprite.RenderPlain(())
    alien_projectile_sprites = pygame.sprite.RenderPlain(())
    powerup_sprites = pygame.sprite.RenderPlain(())
    asteroid_sprites = pygame.sprite.RenderPlain(())
    score = 0
    for i in range(10):
        asteroid_sprites.add(Asteroid(width, choice(asteroid_images)))
    new_roid = 1
    multiplier = 1
    spaceship_destroyed_delay = 50
    paused = False
    while True:   
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            if event.type == KEYDOWN:
                if event.key == K_p:
                    paused = not paused
                if event.key == K_ESCAPE:
                    sys.exit(0)
        if paused:
            continue  
        clock.tick(60)
        screen.blit(background, (0, 0))
        
        spaceship_sprite.update()
        alienship_sprites.update()
        projectile_sprites.update()
        alien_projectile_sprites.update()
        powerup_sprites.update()
        asteroid_sprites.update()
        # display score
        game_text = game_font.render('Score: {0}    Lives: {1}'.format(score, spaceship.lives), True, font_color)
        powerup_shield_text = game_font.render('Shield: {0}%'.format(percentage(spaceship.powup_protected_timer, 400)), True, font_color)
        powerup_firerate_text = game_font.render('Firerate: {0}%'.format(percentage(spaceship.powup_projectile_timer, 400)), True, font_color)
        screen.blit(game_text, (0, 0))
        screen.blit(powerup_shield_text, (width / 2 - 180, 0))
        screen.blit(powerup_firerate_text, (width / 2 + 50, 0))

        # check if spaceship is destroyed      
        if spaceship.destroyed:
            if spaceship_destroyed_delay == 0:
                break
            else:
                spaceship_destroyed_delay -= 1
        # check if spaceship is shooting
        if spaceship.shooting() and spaceship.shoot_delay == 0:
            projectile_sprites.add(Projectile(spaceship.pos, spaceship.angle))
        # check if alienship is shooting or out of bounds
        for alienship in alienship_sprites:
            if not valid_coords(alienship, width, height):
                alienship_sprites.remove(alienship)
            if alienship.shooting():
                alien_projectile_sprites.add(AlienProjectile((alienship.rect.centerx, alienship.rect.centery), randint(1, 360)))
        # check if projectile is out of bounds, or hits asteroid, or hits alien
        for p in projectile_sprites:
            if not valid_coords(p, width, height):
                projectile_sprites.remove(p)
            for a in asteroid_sprites:
                if a.rect.colliderect(p.rect):
                    score += 1
                    asteroid_sprites.remove(a)
                    break
            for alienship in alienship_sprites:
                if p.rect.colliderect(alienship.rect):
                    score += 3
                    alienship_sprites.remove(alienship)
                    break
        # check if alien projectile is out of bounds, or hits asteroid, or hits spaceship
        for ap in alien_projectile_sprites:
            if not valid_coords(ap, width, height):
                alien_projectile_sprites.remove(ap)
            if ap.rect.colliderect(spaceship.rect):
                spaceship.take_hit()
                alien_projectile_sprites.remove(ap)
                break
        # check if asteroid is out of bounds, or hits spaceship
        for a in asteroid_sprites:
            if not valid_coords(a, width, height):
                asteroid_sprites.add(Asteroid(width, a.image_path))
                asteroid_sprites.remove(a)
            if a.rect.colliderect(spaceship.rect):
                spaceship.take_hit()
                asteroid_sprites.remove(a)
                break
        # add new asteroids
        if new_roid >= 60:
            asteroid_sprites.add(Asteroid(width, choice(asteroid_images)))
            new_roid = 0
        new_roid += multiplier
        multiplier *= 1.0001
        # add new alien ships
        if randint(1, 300) == 60:
            alienship_sprites.add(Alienship(width))
        # add random powerups
        if randint(1, 1000) == 60:
            powerup_sprites.add(choice([PowerupProjectile(spaceship, width), PowerupProtect(spaceship, width)]))
        if randint(1, 2000) == 60:
            powerup_sprites.add(PowerupLife(spaceship, width))
        # check for collisions with powerups and check if powerups are used up
        for p in powerup_sprites:
            if not valid_coords(p, width, height):
                powerup_sprites.remove(p)
                break
            if p.rect.colliderect(spaceship.rect):
                p.use()
                powerup_sprites.remove(p)
                break
        spaceship_sprite.draw(screen)
        alienship_sprites.draw(screen)
        projectile_sprites.draw(screen)
        alien_projectile_sprites.draw(screen)
        powerup_sprites.draw(screen)
        asteroid_sprites.draw(screen)
        pygame.display.flip()
    
    # display score when game over
    large_font = pygame.font.Font(None, 60)
    small_font = pygame.font.Font(None, 30)
    score_text = large_font.render('Score: {0}'.format(score), True, (255, 255, 255))
    continue_text = small_font.render('Press any key to continue or esc to quit.', True, (255, 255, 255))
    screen.blit(score_text, (width / 2 - 150, height / 2))
    screen.blit(continue_text, (width / 2 - 150, height / 2 + 100))
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

def valid_coords(sprite, width, height):
    rect = sprite.rect
    return 0 <= rect.centerx <= width and 0 <= rect.centery <= height

def percentage(current, total):
    return int(round(100 * current / total))

main()

