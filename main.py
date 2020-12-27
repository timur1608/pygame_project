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
    image_damaged_ship = pygame.transform.scale(load_image('other/playerDamaged.png'), (50, 38))

    def __init__(self, *group, base):
        super().__init__(*group)
        self.base = base
        self.death = False
        self.image = Ship.image
        self.stop = False
        self.rect = self.image.get_rect()
        self.rect.x = 430
        self.rect.y = 440

        self.health = 2

    def move(self, args):
        if self.health == 1:
            self.image = Ship.image_damaged_ship
        elif self.health == 0:
            self.death = True
        elif args[0] > self.rect.x:
            self.image = Ship.image_right
        elif args[0] == self.rect.x:
            self.image = Ship.image
        elif args[0] < self.rect.x:
            self.image = Ship.image_left
        if not pygame.sprite.collide_mask(self, self.base):
            self.rect.x = args[0]
            self.rect.y = args[1]
            self.stop = False
        else:
            self.stop = True
            old_x = self.rect.x
            old_y = self.rect.y
            self.rect.x = args[0]
            self.rect.y = args[1]
            if pygame.sprite.collide_mask(self, self.base):
                self.rect.x = old_x
                self.rect.y = old_y


class Bullet(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('other/laserRed.png'), (7, 50))
    sound_of_gun = pygame.mixer.Sound('sound/gun/laser-gun-single-shot_zyz4u34u.mp3')
    sound_of_gun.set_volume(0.25)

    def __init__(self, *group, args):
        super().__init__(*group)
        self.image = Bullet.image
        self.speed = 8
        self.rect = self.image.get_rect()
        self.rect.x = args[0] + Ship.image.get_size()[0] // 2 - 3
        self.rect.y = args[1] - Ship.image.get_size()[1]
        Bullet.sound_of_gun.play()

    def update(self):
        self.rect = self.rect.move(0, -self.speed)


class Base(pygame.sprite.Sprite):
    image = pygame.transform.flip(load_image('other/base/wship1.png'), True, False)

    def __init__(self, *group):
        super().__init__(*group)
        self.death = False
        self.image = Base.image
        self.rect = self.image.get_rect()
        self.health = 5
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

    def __init__(self, *group, bullets, base, ship):
        super().__init__(*group)
        self.sound_of_crack = pygame.mixer.Sound(
            'sound/boom/142015__herbertboland__1distantcrack2.mp3')
        self.sound_of_crack.set_volume(0.5)
        self.image = Meteor.images[0]
        self.rect = self.image.get_rect()
        self.bullets = bullets
        self.base = base
        self.count = 0
        self.ship = ship
        self.rect.x = randint(800, 900)
        self.rect.y = randint(-100, 50)
        self.vx = randint(-5, -3)
        self.vy = randint(3, 5)

    def update(self):
        self.count += 1
        if self.count >= len(Meteor.images):
            self.count = 0
        self.image = Meteor.images[self.count]
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.collide_mask(self, self.base):
            self.sound_of_crack.play()
            self.base.health -= 1
            self.kill()
            if self.base.health == 0:
                self.base.death = True
        if pygame.sprite.spritecollideany(self, self.bullets):
            self.sound_of_crack.play()
            self.kill()
            pygame.sprite.spritecollide(self, self.bullets, True)
        if pygame.sprite.collide_mask(self, self.ship):
            self.sound_of_crack.play()
            self.ship.health -= 1
            self.kill()


class GameOverScreen(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('gameover.png'), (WIDTH, HEIGHT))

    def __init__(self, *group, borders):
        super().__init__(*group)
        self.borders = borders
        self.image = GameOverScreen.image
        self.rect = self.image.get_rect()
        self.rect.x = 0 - WIDTH

    def update(self):
        if not pygame.sprite.collide_mask(self, self.borders):
            self.rect = self.rect.move(10, 0)


class HorizonalBorders(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        self.image = pygame.Surface((1, HEIGHT))
        self.rect = pygame.Rect(WIDTH - 1, 0, 5, HEIGHT)


def start_game():
    # Переменные
    x1 = 0
    x2 = 200
    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    # Флаги
    running = True
    level = 1
    f = False
    game_on = False
    speed = 0
    end_on = False
    # Отслеживание времени
    clock = pygame.time.Clock()
    # Перманентные объекты
    horizontal_borders = HorizonalBorders(all_sprites)
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
    pygame.mixer.music.set_volume(0.4)
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
                bullet = Bullet(all_sprites, args=event.pos)
                bullets.add(bullet)
        if ship.death or base.death:
            end_on = True
            running = False

        if pygame.time.get_ticks() > 28000 and not f:
            pygame.mixer.music.load('music/bensound-scifi.mp3')
            pygame.mixer.music.play()
            f = True
        if pygame.time.get_ticks() % 1000 in range(-100, 100):
            SpeedLine(all_sprites)
        if pygame.time.get_ticks() % 1000 in range(-75, 75) and game_on:
            Meteor(all_sprites, base=base, ship=ship, bullets=bullets)
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

    end_screen = GameOverScreen(all_sprites, borders=horizontal_borders)
    pygame.mixer.music.load('music/539674__jhyland__game-over.mp3')
    pygame.mixer.music.play(1)
    while end_on:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                end_on = False
        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    start_screen()
    start_game()
    terminate()
