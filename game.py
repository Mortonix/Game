import os
import sqlite3
import sys
from objs import *

game_version = '0.0.2 (Alpha)'

try:
    con = sqlite3.connect('Data\gamebase.sqlite')
except:
    raise sqlite3.Error("Could not open the database")
cur = con.cursor()
res = list(cur.execute("SELECT resolution from settings"))[0][0].split('x')
res = tuple(map(lambda x: int(x), res))

pygame.init()
size = width, height = res
pygame.display.set_caption(f'Space Defender v{game_version}')
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60
stars = []
running = True
start_wind = True
bright = 50
bup = True
n_speed = 100
cur_speed = 50
for i in range(85, 1, -1):
    stars.append(Star(screen, i * (height // 85), cur_speed))


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


sprites = {
    'p_mothership': load_image('Data/Ships/MotherShip/ship_starCruiser_pirate.png'),
    'p_assault': load_image('Data/Ships/Assault/ship_bounty_tiny_01_pirate.png')
}

mothership = Ship(screen, screen.get_width() // 2, screen.get_height() * 1.2, sprites['p_mothership'])

while running:
    pygame.display.flip()
    clock.tick(FPS)
    screen.fill((0, 0, 0))
    if random.randint(0, 600) < cur_speed * 5:
        stars.append(Star(screen, 0, cur_speed))
    cur_speed = check_speed(cur_speed, n_speed)
    for s in stars:
        s.draw_star()
        if s.get_speed() != cur_speed:
            s.change_speed(cur_speed)
        if not s.check_visible():
            stars.remove(s)
    mothership.draw_ship()
    if start_wind:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                start_wind = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                n_speed = 1
                tick_timer = 0
                start_wind = False
            if pygame.mouse.get_focused():
                pygame.mouse.set_visible(True)
        font = pygame.font.Font(None, width // 18 * 3)
        text = font.render('Click to PLAY', True, (bright, bright, bright))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 1.1 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
        mothership.change_pos(screen.get_width() // 2 + random.randint(-1, 1),
                              screen.get_height() // 2 + random.randint(-1, 1))
        screen.blit(text, (text_x, text_y))

        if bup:
            if bright != 250:
                bright += 2
            else:
                bup = False
        else:
            if bright != 50:
                bright -= 2
            else:
                bup = True
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        if pygame.mouse.get_focused():
            pygame.mouse.set_visible(False)

        if tick_timer < 100:
            tick_timer += 1
            mothership.change_pos(screen.get_width() // 2, screen.get_height() * 0.8)

pygame.quit()
sys.exit()
