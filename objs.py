import random
import math
import pygame


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
    def __init__(self, screen, pos, surface, team=True):
        self.sprite = pygame.sprite.Sprite()
        self.team = team
        self.sprite.rect = surface.get_rect()
        self.sprite.rect.x, self.sprite.rect.y = (i for i in pos)
        self.speed = 10
        self.damage = 10
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
            self.sprite.image = pygame.transform.scale(self.surface, (100 * (screen.get_width() / 540),
                                                                      100 * (screen.get_height() / 960)))
            self.rotation_speed = random.randint(-10, 10)
            self.hp = 100
            self.size = 100
            self.damage = 50
        elif self.tip == 'm':
            self.sprite.image = pygame.transform.scale(self.surface, (70 * (screen.get_width() / 540),
                                                                      70 * (screen.get_height() / 960)))
            self.rotation_speed = random.randint(-30, 30)
            self.hp = 50
            self.size = 70
            self.damage = 25
        elif self.tip == 's':
            self.sprite.image = pygame.transform.scale(self.surface, (60 * (screen.get_width() / 540),
                                                                      60 * (screen.get_height() / 960)))
            self.rotation_speed = random.randint(-50, 50)
            self.hp = 25
            self.size = 60
            self.damage = 10

        self.sprite.image = self.surface
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
    def __init__(self, screen, pos, surface, team, shoot):
        self.sprite = pygame.sprite.Sprite()
        self.screen = screen
        self.x, self.y = pos
        self.surface = surface
        self.team = team
        self.can_shoot = shoot
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
        self.sprite.image = pygame.transform.rotate(self.surface, self.angle)
        self.sprite.rect = self.sprite.image.get_rect()
        self.screen.blit(self.sprite.image, self.cur_pos())

    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= damage
        else:
            self.hp -= damage
        if self.shield < 0:
            self.shield = 0


class MotherShip(Ship):
    def __init__(self, screen, pos, surface, team, shoot=False):
        super().__init__(screen, pos, surface, team, shoot)
        self.name = 'MotherShip'
        self.hp = 1000
        self.shield = 100
        self.surface = pygame.transform.scale(surface,
                                              (400 * (screen.get_width() / 540), 400 * (screen.get_height() / 960)))

    def return_name(self):
        return self.name


class AssaultShip(Ship):
    def __init__(self, screen, pos, surface, team, shoot=True):
        super().__init__(screen, pos, surface, team, shoot)
        self.name = 'Assault'
        self.surface = pygame.transform.scale(surface,
                                              (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.shoot_delay = 30
        self.delay = 0

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
            return True
        else:
            return False
