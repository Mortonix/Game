import os
import sqlite3
import sys

import pygame.key

from objs import *

game_version = '0.0.3 (Alpha)'

try:
    con = sqlite3.connect('Data\gamebase.sqlite')
except:
    raise sqlite3.Error("Could not open the database")
cur = con.cursor()
res = list(cur.execute("SELECT resolution from settings"))[0][0].split('x')
res = tuple(map(lambda x: int(x), res))
cur.close()

size = width, height = res
pygame.init()
pygame.display.set_caption(f'Space Defender v{game_version}')
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join(name)
    if not os.path.isfile(fullname):
        print(f'Файл с изображением {fullname} не найден!')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def check_speed(current, new):
    if current == new:
        return current
    elif current < new:
        return current + 1
    elif current > new:
        return current - 1


all_sprites = {
    'p_mothership': load_image('Data/Ships/MotherShip/ship_starCruiser_pirate.png'),
    'p_assault': load_image('Data/Ships/Assault/ship_bounty_tiny_01_pirate.png'),
    'f_bullet': load_image('Data/f_bullet.png'),
    'e_bullet': load_image('Data/e_bullet.png'),
    'l_aster': load_image('Data/Asteroids/large_rock.png'),
    'm_aster': load_image('Data/Asteroids/medium_rock.png'),
    's_aster': load_image('Data/Asteroids/small_rock.png')
}


def game_pause():
    bup = True
    paused = True
    text_bright = 50
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            if event.type == pygame.KEYDOWN:
                paused = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass
        font1 = pygame.font.Font(None, width // 18 * 3)
        font2 = pygame.font.Font(None, width // 18 * 2)
        text1 = font1.render('PAUSE', True, (text_bright, text_bright, text_bright))
        text2 = font2.render('Press any key to continue', True, (text_bright, text_bright, text_bright))
        text1_x = width // 2 - text1.get_width() // 2
        text1_y = height // 1.2 - text1.get_height() // 2
        text2_x = width // 2.5 - text1.get_width()
        text2_y = height // 1.1 - text1.get_height() // 2
        pygame.display.flip()
        screen.blit(text1, (text1_x, text1_y))
        screen.blit(text2, (text2_x, text2_y))
        if bup:
            if text_bright != 200:
                text_bright += 0.5
            else:
                bup = False
        else:
            if text_bright != 50:
                text_bright -= 0.5
            else:
                bup = True


def close_game():
    pygame.quit()
    sys.exit()


class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.FPS = 60
        self.n_speed = 100
        self.cur_speed = 50

        self.cur_scene = 'start'

        self.stars = []
        self.friendly_objects = []
        self.f_bullets = []
        self.e_bullets = []
        self.enemy_objects = []
        for i in range(85, 1, -1):
            self.stars.append(Star(screen, i * (height // 85), self.cur_speed))

        self.text_bright = 50
        self.font = pygame.font.Font(None, width // 18 * 3)
        self.fire = False
        self.bup = True

        self.friendly_objects.append(
            MotherShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3), all_sprites['p_mothership'], True))
        self.friendly_objects.append(
            AssaultShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3), all_sprites['p_assault'], True))

    def run_game(self):
        while True:
            pygame.display.flip()
            self.clock.tick(self.FPS)
            screen.fill((0, 0, 0))

            if random.randint(0, 600) < self.cur_speed * 5:
                self.stars.append(Star(screen, 0, self.cur_speed))
            self.cur_speed = check_speed(self.cur_speed, self.n_speed)

            for s in self.stars:
                s.draw_star()
                if s.get_speed() != self.cur_speed:
                    s.change_speed(self.cur_speed)
                if not s.check_visible():
                    self.stars.remove(s)

            for bul in self.f_bullets:
                bul.draw()
                if bul.pos[1] <= -10:
                    self.f_bullets.remove(bul)

            for object in self.friendly_objects:
                object.draw()

            if self.cur_scene == 'start':
                self.start_win()
            elif self.cur_scene == 'fight_field':
                self.fight_field()

    def start_win(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                close_game()
            if event.type == pygame.KEYDOWN:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

                self.enemy_objects.append(
                    Asteroid(screen, (screen.get_width() // 2, -100), 25, 5, all_sprites['s_aster'], 's'))
        self.friendly_objects[0].change_pos(screen.get_width() // 2 + random.randint(-1, 1),
                                            screen.get_height() // 2 + random.randint(-1, 1))
        self.friendly_objects[1].change_pos((screen.get_width() // 2) * 0.5 + random.randint(-1, 1),
                                            screen.get_height() // 2 + random.randint(-1, 1))
        for s in self.stars:
            s.draw_star()
            if s.get_speed() != self.cur_speed:
                s.change_speed(self.cur_speed)
            if not s.check_visible():
                self.stars.remove(s)
        for object in self.friendly_objects:
            object.draw()
        text = self.font.render('Press to PLAY', True, (self.text_bright, self.text_bright, self.text_bright))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 1.1 - text.get_height() // 2
        screen.blit(text, (text_x, text_y))
        if self.bup:
            if self.text_bright != 250:
                self.text_bright += 2
            else:
                self.bup = False
        else:
            if self.text_bright != 50:
                self.text_bright -= 2
            else:
                self.bup = True

    def fight_field(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_pause()
            if pygame.mouse.get_pressed(3)[0]:
                self.fire = True
            if not pygame.mouse.get_pressed(3)[0]:
                self.fire = False

        if self.fire:
            for obj in self.friendly_objects:
                if obj.can_shoot:
                    if obj.try_shoot():
                        self.f_bullets.append(
                            Bullet(screen, obj.get_current_position(), all_sprites['f_bullet']))

        self.friendly_objects[0].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 0.95)
        self.friendly_objects[0].change_rotation(90)
        self.friendly_objects[1].change_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        for obj in self.friendly_objects:
            if obj.can_shoot:
                obj.delay -= 1
        for obj in self.enemy_objects:
            obj.draw()


if __name__ == '__main__':
    game = Game()
    game.run_game()
