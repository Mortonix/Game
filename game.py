import os
import sqlite3
import sys

import pygame.key

from objs import *

game_version = '0.0.5 (Alpha)'

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
pygame.mixer.music.load('Data/Sounds/background_music.mp3')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.1)

total_money = 0
money = 0
enemies_destroyed = 0
shots_fired = 0


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


def check_hit(bullet, obj):
    if pygame.sprite.collide_mask(bullet, obj):
        return True
    return False


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
        self.in_shop = False

        self.friendly_objects.append(
            MotherShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3), all_sprites['p_mothership'], True))
        self.friendly_objects.append(
            AssaultShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3), all_sprites['p_assault'], True))

    def run_game(self):
        global shots_fired, total_money, money, enemies_destroyed
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
                if bul.sprite.rect.y <= -10:
                    self.f_bullets.remove(bul)

            for obj in self.friendly_objects:
                obj.draw()

            if self.cur_scene == 'start':
                self.start_win()
            elif self.cur_scene == 'fight_field':
                self.fight_field()
            elif self.cur_scene == 'shop':
                self.shop()

    def start_win(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                close_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.cur_scene = 'shop'
                self.n_speed = 1
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif event.type == pygame.KEYDOWN:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

                self.enemy_objects.append(
                    Asteroid(screen, (screen.get_width() // 2, 100), 0, 1, all_sprites['l_aster'], 'l'))
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
        for obj in self.friendly_objects:
            obj.draw()
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
        global shots_fired, total_money, money, enemies_destroyed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_pause()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.cur_scene = 'shop'
                self.n_speed = 1
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
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
                        shots_fired += 1

        self.friendly_objects[0].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 0.95)
        self.friendly_objects[0].change_rotation(90)
        if pygame.mouse.get_pos()[1] < screen.get_height() * 0.85:
            self.friendly_objects[1].change_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        else:
            self.friendly_objects[1].change_pos(pygame.mouse.get_pos()[0], screen.get_height() * 0.85)
        for obj in self.friendly_objects:
            if obj.can_shoot:
                obj.delay -= 1
        for obj in self.enemy_objects:
            obj.draw()
            for bullet in self.f_bullets:
                if check_hit(bullet.sprite, obj.sprite):
                    if obj.take_damage(bullet.damage):
                        obj.destroy(screen, all_sprites, self.enemy_objects)
                        self.enemy_objects.remove(obj)
                    self.f_bullets.remove(bullet)

    def shop(self):
        global money
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                close_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

        self.friendly_objects[0].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 0.8)
        self.friendly_objects[0].change_rotation(0)
        self.friendly_objects[1].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 0.53)


if __name__ == '__main__':
    game = Game()
    game.run_game()
