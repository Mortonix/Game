import random
import math
import pygame

pygame.mixer.init()

sounds = {
    'shield': pygame.mixer.Sound('Data/Sounds/shilds_down.wav'),
    'assault_shoot': pygame.mixer.Sound('Data/Sounds/assault_gun.mp3'),
    'sniper_shoot': pygame.mixer.Sound('Data/Sounds/sniper_gun.mp3'),
    'a_boom1': pygame.mixer.Sound('Data/Sounds/aster_boom1.mp3'),
    'a_boom2': pygame.mixer.Sound('Data/Sounds/aster_boom2.mp3')
}


class Star:
    def __init__(self, screen, y, speed):
        self.screen = screen
        self.size = random.randint(0, 2)
        brightness = random.randint(0, 100 * self.size)
        self.color = (random.randint(0, 50) + brightness,
                      random.randint(0, 10) + brightness,
                      random.randint(0, 50) + brightness)
        pos_x = random.randint(-25, screen.get_width() + 25)
        pos_y = y
        self.pos = [pos_x, pos_y]
        self.speed = speed * 0.1
        self.add_speed = brightness * 0.005

    def draw_star(self):
        self.pos[1] += self.speed
        pygame.draw.circle(self.screen, self.color, self.pos, self.size)

    def get_speed(self):
        return self.speed

    def change_speed(self, i):
        self.speed = (i + self.add_speed) * 0.1

    def check_visible(self):
        if self.pos[1] < self.screen.get_height() + 5:
            return True
        return False


class Bullet:
    def __init__(self, screen, pos, surface, damage, team=True):
        self.sprite = pygame.sprite.Sprite()
        self.team = team
        self.sprite.rect = surface.get_rect()
        self.sprite.rect.x, self.sprite.rect.y = (i for i in pos)
        self.speed = 10
        self.damage = damage
        self.screen = screen
        self.sprite.image = pygame.transform.scale(surface, (50 * (screen.get_width() / 540) * 0.9,
                                                             50 * (screen.get_height() / 960) * 0.9))
        self.mask = pygame.mask.from_surface(surface)

    def draw(self):
        # sprite = pygame.transform.rotate(self.sprite)
        self.sprite.rect.y -= self.speed
        self.screen.blit(self.sprite.image, self.sprite.rect)


class Asteroid:
    def __init__(self, screen, pos, direction, speed, surface, tip):
        self.x = pos[0]
        self.y = pos[1]
        self.sprite = pygame.sprite.Sprite()
        self.screen = screen
        self.direction = direction
        self.speed = speed
        self.surface = surface
        self.tip = tip

        self.angle = 0
        self.size = 0

        if self.tip == 'l':
            self.surface = pygame.transform.scale(self.surface, (100 * (self.screen.get_width() / 540),
                                                                 100 * (self.screen.get_height() / 960)))
            self.rotation_speed = random.randint(-10, 10)
            self.hp = 100
            self.size = 100
            self.damage = 50
        elif self.tip == 'm':
            self.surface = pygame.transform.scale(self.surface, (70 * (self.screen.get_width() / 540),
                                                                 70 * (self.screen.get_height() / 960)))
            self.rotation_speed = random.randint(-30, 30)
            self.hp = 50
            self.size = 70
            self.damage = 25
        elif self.tip == 's':
            self.surface = pygame.transform.scale(self.surface, (60 * (self.screen.get_width() / 540),
                                                                 60 * (self.screen.get_height() / 960)))
            self.rotation_speed = random.randint(-50, 50)
            self.hp = 25
            self.size = 60
            self.damage = 10

        self.sprite.mask = pygame.mask.from_surface(self.surface)
        self.sprite.rect = self.surface.get_rect()
        self.sprite.rect.x += pos[0]
        self.sprite.rect.y += pos[1]

    def cur_pos(self):
        return self.x - self.sprite.rect.centerx, self.y - self.sprite.rect.centery

    def draw(self):
        self.angle += self.rotation_speed * 0.1
        self.sprite.image = pygame.transform.rotate(self.surface, self.angle)
        self.sprite.rect = self.sprite.image.get_rect()
        self.x -= self.speed * math.sin(self.direction)
        self.y += self.speed * math.cos(self.direction)
        self.screen.blit(self.sprite.image, (self.cur_pos()))
        self.sprite.rect.x, self.sprite.rect.y = self.cur_pos()
        self.sprite.mask = pygame.mask.from_surface(self.sprite.image)

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            return True
        return False

    def destroy(self, screen, all_sprites, e_objs):
        pos = self.x, self.y
        cur = self.cur_pos()
        if random.randint(1, 2) == 1:
            sounds['a_boom1'].set_volume(0.2)
            sounds['a_boom1'].play()
        else:
            sounds['a_boom2'].set_volume(0.2)
            sounds['a_boom2'].play()
        if self.tip == 'l':
            e_objs.append(
                Asteroid(screen, (pos[0] - cur[0], pos[1] - cur[1]), random.randint(-90, 90) // 2, self.speed,
                         all_sprites['m_aster'], 'm'))
            e_objs.append(
                Asteroid(screen, (pos[0] - cur[0], pos[1] - cur[1]), random.randint(-90, 90) // 2, self.speed,
                         all_sprites['m_aster'], 'm'))
        if self.tip == 'm':
            e_objs.append(
                Asteroid(screen, (pos[0] - cur[0], pos[1] - cur[1]), random.randint(-90, 90) // 2, self.speed,
                         all_sprites['s_aster'], 's'))
            e_objs.append(
                Asteroid(screen, (pos[0] - cur[0], pos[1] - cur[1]), random.randint(-90, 90) // 2, self.speed,
                         all_sprites['s_aster'], 's'))


class Ship:
    def __init__(self, screen, pos, surface, s_surface, team, shoot):
        self.s_surface = s_surface
        self.s_alpha = 10
        self.sprite = pygame.sprite.Sprite()
        self.screen = screen
        self.x, self.y = pos
        self.surface = surface
        self.team = team
        self.can_shoot = shoot
        self.damage = 0
        self.angle = 0
        self.hp = 0
        self.shield = 0
        self.movement_speed = 1
        self.rotation_speed = 1
        self.sprite.image = surface
        self.sprite.mask = pygame.mask.from_surface(self.surface)
        self.sprite.rect = self.surface.get_rect()
        self.sprite.rect.x += pos[0]
        self.sprite.rect.y += pos[1]
        self.shield_enabled = False

    def cur_pos(self):
        return self.x - self.sprite.rect.centerx, self.y - self.sprite.rect.centery

    def change_pos(self, x, y):
        if self.x < x and x - self.x < self.movement_speed:
            self.x = x
        elif self.x > x and self.x - x < self.movement_speed:
            self.x = x
        elif self.x < x:
            self.x += self.movement_speed + self.movement_speed * (x - self.x) // 32
        elif self.x > x:
            self.x -= self.movement_speed + self.movement_speed * (self.x - x) // 32
        if self.y < y and y - self.y < self.movement_speed:
            self.y = y
        elif self.y > y and self.y - y < self.movement_speed:
            self.y = y
        elif self.y < y:
            self.y += self.movement_speed + self.movement_speed * (y - self.y) // 32
        elif self.y > y:
            self.y -= self.movement_speed + self.movement_speed * (self.y - y) // 32

    def change_rotation(self, angle):
        if self.angle < angle and angle - self.angle < self.rotation_speed:
            self.angle = angle
        elif self.angle > angle and self.angle - angle < self.rotation_speed:
            self.angle = angle
        elif self.angle < angle:
            self.angle += self.rotation_speed
        elif self.angle > angle:
            self.angle -= self.rotation_speed

    def draw(self):
        if self.shield_enabled:
            s_sprite = pygame.transform.rotate(self.s_surface, self.angle)
            self.screen.blit(s_sprite, self.cur_pos())
        self.sprite.image = pygame.transform.rotate(self.surface, self.angle)
        self.sprite.mask = pygame.mask.from_surface(self.sprite.image)
        self.sprite.rect = self.sprite.image.get_rect()
        self.screen.blit(self.sprite.image, self.cur_pos())

    def shield_activation(self):
        if self.shield <= 0:
            self.s_alpha = 0
        else:
            self.s_surface.set_alpha(10)

    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= damage
        else:
            self.hp -= damage
        if self.shield < 0:
            self.shield = 0


class MotherShip(Ship):
    def __init__(self, screen, pos, surface, s_surface, team, shoot=False):
        super().__init__(screen, pos, surface, s_surface, team, shoot)
        self.name = 'MotherShip'
        self.hp = 1000
        self.shield = 100
        self.surface = pygame.transform.scale(surface,
                                              (400 * (screen.get_width() / 540), 400 * (screen.get_height() / 960)))
        self.s_surface = pygame.transform.scale(s_surface,
                                                (400 * (screen.get_width() / 540), 400 * (screen.get_height() / 960)))
        self.shield_enabled = True

    def return_name(self):
        return self.name

    def take_damage(self, damage):
        if self.shield > 0:
            if self.shield - damage <= 0:
                sounds['shield'].play()
            self.shield -= damage
        else:
            self.hp -= damage
        if self.shield < 0:
            self.shield = 0


class AssaultShip(Ship):
    def __init__(self, screen, pos, surface, s_surface, team, shoot=True):
        super().__init__(screen, pos, surface, s_surface, team, shoot)
        self.name = 'Assault'
        self.surface = pygame.transform.scale(surface,
                                              (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.s_surface = pygame.transform.scale(s_surface,
                                                (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.shoot_delay = 30
        self.hp = 100
        self.damage = 10
        self.shield = 0
        self.delay = 0
        self.shield_enabled = False

    def return_name(self):
        return self.name

    def change_pos(self, x, y):
        if self.x < x and x - self.x < self.movement_speed:
            self.x = x
        elif self.x > x and self.x - x < self.movement_speed:
            self.x = x
        elif self.x < x:
            self.x += self.movement_speed + self.movement_speed * (x - self.x) // 16
        elif self.x > x:
            self.x -= self.movement_speed + self.movement_speed * (self.x - x) // 16
        if self.y < y and y - self.y < self.movement_speed:
            self.y = y
        elif self.y > y and self.y - y < self.movement_speed:
            self.y = y
        elif self.y < y:
            self.y += self.movement_speed + self.movement_speed * (y - self.y) // 16
        elif self.y > y:
            self.y -= self.movement_speed + self.movement_speed * (self.y - y) // 16

    def try_shoot(self):
        if self.delay <= 0:
            self.delay = self.shoot_delay
            sounds['assault_shoot'].set_volume(0.1)
            sounds['assault_shoot'].play()
            return True
        else:
            return False


class SniperShip(Ship):
    def __init__(self, screen, pos, surface, s_surface, team, shoot=True):
        super().__init__(screen, pos, surface, s_surface, team, shoot)
        self.name = 'Sniper'
        self.surface = pygame.transform.scale(surface,
                                              (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.s_surface = pygame.transform.scale(s_surface,
                                                (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.shoot_delay = 60
        self.hp = 10
        self.damage = 25
        self.shield = 0
        self.delay = 0
        self.shield_enabled = False

    def return_name(self):
        return self.name

    def change_pos(self, x, y):
        if self.x < x and x - self.x < self.movement_speed:
            self.x = x
        elif self.x > x and self.x - x < self.movement_speed:
            self.x = x
        elif self.x < x:
            self.x += self.movement_speed + self.movement_speed * (x - self.x) // 16
        elif self.x > x:
            self.x -= self.movement_speed + self.movement_speed * (self.x - x) // 16
        if self.y < y and y - self.y < self.movement_speed:
            self.y = y
        elif self.y > y and self.y - y < self.movement_speed:
            self.y = y
        elif self.y < y:
            self.y += self.movement_speed + self.movement_speed * (y - self.y) // 16
        elif self.y > y:
            self.y -= self.movement_speed + self.movement_speed * (self.y - y) // 16

    def try_shoot(self):
        if self.delay <= 0:
            self.delay = self.shoot_delay
            sounds['sniper_shoot'].set_volume(0.1)
            sounds['sniper_shoot'].play()
            return True
        else:
            return False
