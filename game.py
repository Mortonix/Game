import sqlite3
import sys
import pygame
import random

try:
    con = sqlite3.connect('Data\gamebase.sqlite')
except:
    raise sqlite3.Error("Could not open the database")
cur = con.cursor()
res = list(cur.execute("SELECT resolution from settings"))[0][0].split('x')
res = tuple(map(lambda x: int(x), res))


class Star:
    def __init__(self, screen, y, speed):
        self.screen = screen
        self.size = random.randint(0, 2)
        brightness = random.randint(0, 100 * self.size)
        self.color = (random.randint(0, 50) + brightness,
                      random.randint(0, 10) + brightness,
                      random.randint(0, 50) + brightness)
        pos_x = random.randint(-25, width + 25)
        pos_y = y
        self.pos = [pos_x, pos_y]
        self.speed = speed

    def draw_star(self):
        self.pos[1] += self.speed
        pygame.draw.circle(self.screen, self.color, self.pos, self.size)

    def get_speed(self):
        return self.speed

    def change_speed(self, i):
        self.speed = i

    def check_visible(self):
        if self.pos[1] < height + 5:
            return True
        return False


pygame.init()
size = width, height = res
pygame.display.set_caption('Space Defender v0.0.1 (Alpha)')
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
FPS = 60
stars = []
running = True
start_wind = True
bright = 50
bup = True
n_speed = 10
cur_speed = 1
for i in range(85, 1, -1):
    stars.append(Star(screen, i * (height // 85), cur_speed))


def check_speed(cur_speed, n_speed):
    if cur_speed == n_speed:
        return cur_speed
    elif cur_speed < n_speed:
        return cur_speed + 0.1
    elif cur_speed > n_speed:
        return cur_speed - 0.1


while running:
    pygame.display.update()
    clock.tick(FPS)
    screen.fill((0, 0, 0))
    if random.randint(0, 60) < cur_speed * 5:
        stars.append(Star(screen, 0, cur_speed))
    cur_speed = check_speed(cur_speed, n_speed)
    print(len(stars))
    for s in stars:
        s.draw_star()
        if s.get_speed() != cur_speed:
            s.change_speed(cur_speed)
        if not s.check_visible():
            stars.remove(stars[0])
    if start_wind:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                start_wind = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                n_speed = 1
                start_wind = False
            if pygame.mouse.get_focused():
                pygame.mouse.set_visible(True)
        font = pygame.font.Font(None, width // 9 * 2)
        text = font.render('Tap to PLAY', True, (bright, bright, bright))
        text_x = width // 2 - text.get_width() // 2
        text_y = height // 1.1 - text.get_height() // 2
        text_w = text.get_width()
        text_h = text.get_height()
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

pygame.quit()
sys.exit()
