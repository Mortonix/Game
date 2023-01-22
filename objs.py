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
    def __init__(self, screen, pos, sprite, team=True):
        self.team = team
        self.pos = [i for i in pos]
        self.speed = 10
        self.screen = screen
        self.sprite = pygame.transform.scale(sprite, (50 * (screen.get_width() / 540) * 0.9,
                                                      50 * (screen.get_height() / 960) * 0.9))
        self.mask = pygame.mask.from_surface(self.sprite)
        self.rect = self.mask.get_rect()

    def draw(self):
        # sprite = pygame.transform.rotate(self.sprite)
        self.pos[1] -= self.speed
        self.screen.blit(self.sprite, self.pos)


class Asteroid:
    def __init__(self, screen, pos, direction, speed, sprite, type):
        self.screen = screen
        self.pos = [i for i in pos]
        self.speed = speed
        self.direction = direction
        self.sprite = sprite
        if type == 'l':
            self.sprite = pygame.transform.scale(sprite, (100 * (screen.get_width() / 540),
                                                          100 * (screen.get_height() / 960)))
        elif type == 'm':
            self.sprite = pygame.transform.scale(sprite, (85 * (screen.get_width() / 540),
                                                          85 * (screen.get_height() / 960)))
        elif type == 's':
            self.sprite = pygame.transform.scale(sprite, (70 * (screen.get_width() / 540),
                                                          70 * (screen.get_height() / 960)))

    def draw(self):
        self.pos[1] += self.speed * math.cos(self.direction)
        self.pos[0] += self.speed * math.sin(self.direction)
        self.screen.blit(self.sprite, self.pos)


class Ship:
    def __init__(self, screen, pos, sprite, team, shoot):
        self.team = team
        self.x, self.y = pos
        self.angle = 0
        self.hp = 1000
        self.shield = 100
        self.sprite = sprite
        self.screen = screen
        self.can_shoot = shoot
        self.rect = sprite.get_rect()
        self.movement_speed = 1
        self.rotation_speed = 1

    def get_current_position(self):
        return self.x - self.rect.center[0], self.y - self.rect.center[1]

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
        sprite = pygame.transform.rotate(self.sprite, self.angle)
        self.rect = sprite.get_rect()
        self.screen.blit(sprite, self.get_current_position())


class MotherShip(Ship):
    def __init__(self, screen, pos, sprite, team, shoot=False):
        super().__init__(screen, pos, sprite, team, shoot)
        self.name = 'MotherShip'
        self.sprite = pygame.transform.scale(sprite,
                                             (400 * (screen.get_width() / 540), 400 * (screen.get_height() / 960)))

    def return_name(self):
        return self.name


class AssaultShip(Ship):
    def __init__(self, screen, pos, sprite, team, shoot=True):
        super().__init__(screen, pos, sprite, team, shoot)
        self.name = 'Assault'
        self.sprite = pygame.transform.scale(sprite,
                                             (48 * (screen.get_width() / 540), 48 * (screen.get_height() / 960)))
        self.shoot_delay = 10
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
