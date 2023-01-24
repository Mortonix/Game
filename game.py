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
dif = list(cur.execute("SELECT last_dif from settings"))[0][0]
print(dif)
cur.close()

size = width, height = res

pygame.init()
pygame.display.set_caption(f'Space Defender v{game_version}')
screen = pygame.display.set_mode(size)
bg_music = pygame.mixer.Sound('Data/Sounds/background_music.mp3')
bg_music.play(-1)
bg_music.set_volume(0.1)

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
    's_mothership': load_image('Data/Ships/MotherShip/ship_starCruiser_shield.png'),
    'p_assault': load_image('Data/Ships/Assault/ship_bounty_tiny_01_pirate.png'),
    's_assault': load_image('Data/Ships/Assault/ship_bounty_tiny_01_shield.png'),
    'p_sniper': load_image('Data/Ships/Sniper/ship_civ_mole_pirate.png'),
    's_sniper': load_image('Data/Ships/Sniper/ship_civ_mole_shield.png'),
    'f_bullet': load_image('Data/f_bullet.png'),
    'e_bullet': load_image('Data/e_bullet.png'),
    'l_aster': load_image('Data/Asteroids/large_rock.png'),
    'm_aster': load_image('Data/Asteroids/medium_rock.png'),
    's_aster': load_image('Data/Asteroids/small_rock.png'),
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
        self.booms = []
        for i in range(85, 1, -1):
            self.stars.append(Star(screen, i * (height // 85), self.cur_speed))

        self.text_bright = 50
        self.font = pygame.font.Font(None, width // 18 * 3)
        self.fire = False
        self.bup = True
        self.in_shop = False
        self.choose = ''
        self.mothership = MotherShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3),
                                     all_sprites['p_mothership'], all_sprites['s_mothership'], True)
        self.sniper = SniperShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3), all_sprites['p_sniper'],
                                 all_sprites['s_sniper'], True)
        self.assault = AssaultShip(screen, (screen.get_width() // 2, screen.get_height() * 1.3),
                                   all_sprites['p_assault'], all_sprites['s_assault'], True)

        self.friendly_objects.append(self.mothership)
        self.friendly_objects.append(self.sniper)
        self.friendly_objects.append(self.assault)

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

            if self.cur_scene == 'start':
                self.start_win()
            elif self.cur_scene == 'fight_field':
                self.fight_field()
            elif self.cur_scene == 'shop':
                self.shop()
            elif self.cur_scene == 'end':
                self.end()

            for bul in self.f_bullets:
                bul.draw()
                if bul.sprite.rect.y <= -10:
                    self.f_bullets.remove(bul)

            for obj in self.friendly_objects:
                obj.draw()

            # for boom in self.booms:
            #     if boom.cur_frame < len(boom.frames):
            #         boom.update()
            #     else:
            #         self.booms.remove(boom)

    def start_win(self):
        self.friendly_objects[0].change_pos(screen.get_width() // 2 + random.randint(-1, 1),
                                            screen.get_height() // 2 + random.randint(-1, 1))
        self.friendly_objects[1].change_pos((screen.get_width() // 2) * 0.5 + random.randint(-1, 1),
                                            screen.get_height() // 2 + random.randint(-1, 1))
        self.friendly_objects[2].change_pos((screen.get_width() // 2) * 1.5 + random.randint(-1, 1),
                                            screen.get_height() // 2 + random.randint(-1, 1))
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                close_game()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.cur_scene = 'shop'
                self.n_speed = 1
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                self.friendly_objects.remove(self.assault)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                self.friendly_objects.remove(self.sniper)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        for s in self.stars:
            s.draw_star()
            if s.get_speed() != self.cur_speed:
                s.change_speed(self.cur_speed)
            if not s.check_visible():
                self.stars.remove(s)
        for obj in self.friendly_objects:
            obj.draw()
        text = self.font.render('Choose a Ship', True, (self.text_bright, self.text_bright, self.text_bright))
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

        if len(self.enemy_objects) == 0:
            self.enemy_objects.append(
                Asteroid(screen, (random.randint(0, screen.get_width()), -99), 0, 1,
                         all_sprites['l_aster'],
                         'l'))

        for i in self.enemy_objects:
            if dif == 0:
                i.hp = i.hp * 0.1
            else:
                i.hp = i.hp * (dif * 0.5)
        if self.fire:
            for obj in self.friendly_objects:
                if obj.can_shoot:
                    if obj.try_shoot():
                        self.f_bullets.append(
                            Bullet(screen, obj.cur_pos(), all_sprites['f_bullet'], obj.damage))
                        shots_fired += 1
        self.friendly_objects[0].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 0.95)
        self.friendly_objects[0].change_rotation(90)
        if pygame.mouse.get_pos()[1] < screen.get_height() * 0.85 and len(self.friendly_objects) != 0:
            self.friendly_objects[1].change_pos(pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1])
        elif len(self.friendly_objects) != 0:
            self.friendly_objects[1].change_pos(pygame.mouse.get_pos()[0], screen.get_height() * 0.85)
        for obj in self.friendly_objects:
            # for aster in self.enemy_objects:
            #     if check_hit(obj.sprite, aster.sprite):
            #         obj.take_damage(aster.damage)
            #         if obj.hp <= 0:
            #             self.friendly_objects.remove(obj)
            if obj.can_shoot:
                obj.delay -= 1
        for obj in self.enemy_objects:
            obj.draw()
            for bullet in self.f_bullets:
                if check_hit(bullet.sprite, obj.sprite):
                    if obj.take_damage(bullet.damage):
                        obj.destroy(screen, all_sprites, self.enemy_objects)
                        enemies_destroyed += 1
                        self.enemy_objects.remove(obj)
                        for i in self.enemy_objects:
                            if dif == 0:
                                i.hp = i.hp * 0.1
                            else:
                                i.hp = i.hp * (dif * 0.5)
                    self.f_bullets.remove(bullet)
            if obj.x < -screen.get_width() * 0.2 or obj.y < -screen.get_height() * 0.2:
                self.enemy_objects.remove(obj)
            if obj.x > screen.get_width() + screen.get_width() * 0.2 or \
                    obj.y > screen.get_height() + screen.get_height() * 0.2:
                self.enemy_objects.remove(obj)
            if screen.get_width() * 0.25 < obj.x < screen.get_width() * 0.75 and \
                    screen.get_height() * 0.85 < obj.y < screen.get_height():
                self.cur_scene = 'end'
                self.n_speed = 1
                self.text_bright = 50
                self.bup = True

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

    def end(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                close_game()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.cur_scene = 'fight_field'
                self.n_speed = 10
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        self.friendly_objects[0].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 2)
        self.friendly_objects[0].change_rotation(360)
        self.friendly_objects[1].change_pos(screen.get_width() // 2,
                                            screen.get_height() * 2)
        self.friendly_objects[1].change_rotation(360)

        font1 = pygame.font.Font(None, width // 18 * 3)
        font2 = pygame.font.Font(None, width // 18 * 1)
        text1 = font1.render('GAME OVER', True, (self.text_bright, 0, 0))
        t_enemies_destroyed = font2.render(f'Астероидов уничтожено: {enemies_destroyed}', True, (250, 250, 250))
        t_shots_fired = font2.render(f'Выстрелов сделано: {shots_fired}', True, (250, 250, 250))
        text1_x, text1_y = width // 2 - text1.get_width() // 2, width * 0.2
        t_enemies_destroyed_x, t_enemies_destroyed_y = width // 2 - t_enemies_destroyed.get_width() // 2, width * 0.4
        t_shots_fired_x, t_shots_fired_y = width // 2 - t_shots_fired.get_width() // 2, width * 0.45
        screen.blit(text1, (text1_x, text1_y))
        screen.blit(t_enemies_destroyed, (t_enemies_destroyed_x, t_enemies_destroyed_y))
        screen.blit(t_shots_fired, (t_shots_fired_x, t_shots_fired_y))

        if self.bup:
            if self.text_bright != 200:
                self.text_bright += 1
            else:
                self.bup = False
        else:
            if self.text_bright != 50:
                self.text_bright -= 1
            else:
                self.bup = True


if __name__ == '__main__':
    game = Game()
    game.run_game()
