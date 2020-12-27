import pygame
import sys
import os
from random import choice, randint

pygame.init()
size = WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((size))
pygame.display.set_caption('pre_alpha_project')
FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
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


def start_screen():
    font_size = 20
    speed = 1
    x = 250
    y = 450
    pygame.mixer.music.load('music/Retro Vibes.mp3')
    pygame.mixer.music.play()
    fon = pygame.transform.scale(load_image('Flat Night 4 BG.png'), (WIDTH, HEIGHT))
    intro_text = ['Чтобы начать игру, нажмите SPACE',
                  'made by Timur Izmaylov',
                  ]
    font_2 = pygame.font.Font(None, 20)
    string_2 = font_2.render(intro_text[1], True, pygame.Color('#C0C0C0'))
    place_2 = (10, 10)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]:
                terminate()
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                pygame.mixer.music.stop()
                return
        font_size += speed
        x += -speed * 5
        if font_size == 38:
            speed = -1
        elif font_size == 24:
            speed = 1
        screen.blit(fon, (0, 0))
        place_1 = (x, y)
        screen.blit(string_2, place_2)
        font = pygame.font.SysFont('comicsansms', font_size)
        string = font.render(intro_text[0], True, pygame.Color('#C0C0C0'))
        screen.blit(string, place_1)

        pygame.display.flip()
        clock.tick(FPS)


class Ship(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('other/player.png'), (50, 38))
    image_right = pygame.transform.scale(load_image('other/playerRight.png'), (50, 38))
    image_left = pygame.transform.scale(load_image('other/playerLeft.png'), (50, 38))
    # image_damaged_ship = pygame.transform.scale('other/player')

    def __init__(self, *group, base):
        super().__init__(*group)
        self.base = base
        self.image = Ship.image
        self.stop = False
        self.rect = self.image.get_rect()
        self.rect.x = 430
        self.rect.y = 440

        self.health = 2

    def move(self, args):
        if args[0] > self.rect.x:
            self.image = Ship.image_right
        elif args[0] == self.rect.x:
            self.image = Ship.image
        elif args[0] < self.rect.x:
            self.image = Ship.image_left
        if not pygame.sprite.collide_mask(self, self.base):
            self.stop = False
            self.rect.x = args[0]
            self.rect.y = args[1]
        else:
            old_x = self.rect.x
            old_y = self.rect.y
            self.rect.x = args[0]
            self.rect.y = args[1]
            if pygame.sprite.collide_mask(self, self.base):
                self.rect.x = old_x
                self.rect.y = old_y
            self.stop = True


class Bullet(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('other/laserRed.png'), (7, 50))

    def __init__(self, *group, args):
        super().__init__(*group)
        self.image = Bullet.image
        self.speed = 8
        self.rect = self.image.get_rect()
        self.rect.x = args[0] + Ship.image.get_size()[0] // 2 - 3
        self.rect.y = args[1] - Ship.image.get_size()[1]

    def update(self):
        self.rect = self.rect.move(0, -self.speed)


class Base(pygame.sprite.Sprite):
    image = pygame.transform.flip(load_image('other/base/wship1.png'), True, False)

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Base.image
        self.rect = self.image.get_rect()
        self.rect.y = 150


class SpeedLine(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('Background/speedLine.png'), (5, 550))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = SpeedLine.image
        self.rect = self.image.get_rect()
        rang = list(range(10, 100)) + list(range(800, 890))
        self.rect.x = choice(rang)

    def update(self):
        self.rect = self.rect.move(0, 5)


class Meteor(pygame.sprite.Sprite):
    images = list()
    for i in range(60):
        if not i >= 10:
            images.append(load_image(f'other/meteors/Asteroid-A-10-0{i}.png'))
        else:
            images.append(load_image(f'other/meteors/Asteroid-A-10-{i}.png'))

    def __init__(self, *group, base, ship):
        super().__init__(*group)
        self.image = Meteor.images[0]
        self.rect = self.image.get_rect()
        self.base = base
        self.ship = ship
        self.rect.x = randint(800, 900)
        self.rect.y = randint(-100, 50)
        self.vx = randint(-4, -1)
        self.vy = randint(1, 4)

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.collide_mask(self, self.base) or pygame.sprite.collide_mask(self, self.ship):
            self.ship.health -= 1
            self.kill()


def start_game():
    # Переменные
    x1 = 0
    x2 = 200
    # Группа всех спрайтов
    all_sprites = pygame.sprite.Group()
    # Флаги
    running = True
    level = 1
    f = False
    game_on = False
    speed = 0
    # Отслеживание времени
    clock = pygame.time.Clock()
    # Перманентные объекты
    base = Base(all_sprites)
    ship = Ship(all_sprites, base=base)
    # Надписи на экране
    level_text = ['Защитите торговый корабль от метеоритов',
                  ]
    font = pygame.font.SysFont('comicsansms', 30)
    string = f'Уровень {level}'
    warning = 'Нажмите Space, чтобы начать'
    warning = font.render(warning, True, pygame.Color('#C0C0C0'))
    string = font.render(string, True, pygame.Color('#C0C0C0'))
    text = font.render(level_text[0], True, pygame.Color('#C0C0C0'))
    fon = pygame.transform.scale(load_image('Background/kosmos.jpg'), (WIDTH, HEIGHT))
    # Музыка
    pygame.mixer.music.load('music/audioblocks-80-s-dreamwave-logo_rS6JYzJfU_WM.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.5)
    # Основной цикл
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION and game_on:
                ship.move(event.pos)
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                game_on = True
                speed = 3
            if game_on and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not ship.stop:
                Bullet(all_sprites, args=event.pos)
        if pygame.time.get_ticks() > 28000 and not f:
            pygame.mixer.music.load('music/bensound-scifi.mp3')
            pygame.mixer.music.play()
            f = True
        if pygame.time.get_ticks() % 1000 in range(-100, 100):
            SpeedLine(all_sprites)
        if pygame.time.get_ticks() % 1000 in range(-50, 50) and game_on:
            Meteor(all_sprites, base=base, ship=ship)
        screen.blit(fon, (0, 0))
        x1 -= speed
        x2 -= speed
        screen.blit(string, (x1, 0))
        screen.blit(text, (x2, 0))
        if not game_on:
            screen.blit(warning, (250, 250))
        pygame.mouse.set_visible(False)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    start_screen()
    start_game()
    terminate()
