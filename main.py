import pygame
import pygame_gui
import sys
import os
from random import choice, randint
import time as tm
import math

pygame.init()
size = WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((size))
pygame.display.set_caption('pre_alpha_project')
manager = pygame_gui.UIManager((WIDTH, HEIGHT))
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


def calculate_angle(x0, y0, x1, y1) -> float:
    a = abs(x0 - x1) / math.sqrt(abs(x0 - x1) ** 2 + abs(y0 - y1) ** 2)
    if x0 >= x1:
        return math.degrees(math.asin(-a))
    else:
        return math.degrees(math.asin(a))


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
    death_sound = pygame.mixer.Sound('sound/ship/bomb-sound-effect.mp3')
    image = pygame.transform.scale(load_image('other/player.png'), (50, 38))
    image_right = pygame.transform.scale(load_image('other/playerRight.png'), (50, 38))
    image_left = pygame.transform.scale(load_image('other/playerLeft.png'), (50, 38))
    image_damaged_ship = pygame.transform.scale(load_image('other/playerDamaged.png'), (50, 38))

    def __init__(self, *group, base=None, horizontal_borders=None, vertical_borders=None):
        super().__init__(*group)
        self.base = base
        self.death = False
        self.stop = False
        self.vertical_borders = vertical_borders
        self.horizontal_borders = horizontal_borders
        self.image = Ship.image
        self.rect = self.image.get_rect()
        self.count = 0
        self.angle = 1
        self.rect.x = 430
        self.rect.y = 440

        self.health = 2
        self.damage = 1
        self.shield = 0

    def move(self, args):
        if args[0] > self.rect.x:
            self.image = Ship.image_right
        elif args[0] == self.rect.x:
            self.image = Ship.image
        elif args[0] < self.rect.x:
            self.image = Ship.image_left
        if self.base:
            if not pygame.sprite.collide_mask(self,
                                              self.base) and not pygame.sprite.spritecollideany(
                self, self.horizontal_borders) and not pygame.sprite.spritecollideany(self,
                                                                                      self.vertical_borders):
                self.rect.x = args[0]
                self.rect.y = args[1]
                self.stop = False
            else:
                self.stop = True
                old_x = self.rect.x
                old_y = self.rect.y
                self.rect.x = args[0]
                self.rect.y = args[1]
                if pygame.sprite.collide_mask(self, self.base) or pygame.sprite.spritecollideany(
                        self,
                        self.horizontal_borders) or pygame.sprite.spritecollideany(
                    self, self.vertical_borders):
                    self.rect.x = old_x
                    self.rect.y = old_y
        else:

            self.rect.x = args[0]
            self.rect.y = args[1]

    def drawhp(self):
        for _ in range(self.health):
            pygame.draw.rect(screen, 'green', (800 + self.count, 450, 20, 20))
            self.count += 20
        self.count = 0


class Shield(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('other/shield.png'), (75, 60))

    def __init__(self, *group):
        super().__init__(*group)
        self.image = Shield.image
        self.rect = self.image.get_rect()

    def move(self, args):
        self.rect.x = args[0] - 13
        self.rect.y = args[1] - 13


class Bullet(pygame.sprite.Sprite):
    speed = 8
    image = pygame.transform.scale(load_image('other/laserRed.png'), (7, 50))
    sound_of_gun = pygame.mixer.Sound('sound/gun/laser-gun-single-shot_zyz4u34u.mp3')
    sound_of_gun.set_volume(0.25)

    def __init__(self, *group, args, direction):
        super().__init__(*group)
        self.image = Bullet.image
        self.speed = Bullet.speed
        self.rect = self.image.get_rect()
        if direction == 'left':
            self.rect.x = args[0]
            self.rect.y = args[1] - Ship.image.get_size()[1]
        elif direction == 'right':
            self.rect.x = args[0] + Ship.image.get_size()[0] - 5
            self.rect.y = args[1] - 40
        Bullet.sound_of_gun.play()

    def update(self):
        self.rect = self.rect.move(0, -self.speed)


class Base(pygame.sprite.Sprite):
    sound_of_crack = pygame.mixer.Sound('sound/ship/zvuk-srednego-vzryiva-6952.mp3')
    image = pygame.transform.flip(load_image('other/base/wship1.png'), True, False)

    def __init__(self, *group):
        super().__init__(*group)
        self.death = False
        self.image = Base.image
        self.rect = self.image.get_rect()
        self.count = 0
        self.health = 5
        self.rect.y = 150

    def drawhp(self):
        for _ in range(self.health):
            pygame.draw.rect(screen, 'green', (5 + self.count, 130, 20, 20))
            self.count += 20
        self.count = 0


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


class EnemyShip(pygame.sprite.Sprite):
    image = pygame.transform.scale(load_image('other/enemyShip.png'), (49, 25))

    def __init__(self, *group, x, y):
        super().__init__(*group)
        self.image = EnemyShip.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.orig_image = self.image.copy()

    def rotate(self, args):
        self.angle = calculate_angle(self.rect.x, self.rect.y, args[0], args[1])
        orig_center = self.rect.center
        self.image = pygame.transform.rotate(self.orig_image, self.angle)
        self.rect = self.image.get_rect(center=orig_center)


class BulletOfEnemy(pygame.sprite.Sprite):
    image = load_image('other/laserGreen.png')

    def __init__(self, *group, enemy):
        super().__init__(*group)
        self.image = BulletOfEnemy.image
        self.rect = self.image.get_rect()
        self.enemy = enemy
        self.orig_image = self.image.copy()

    def rotate(self, args):
        orig_center = self.rect.center
        self.image = pygame.transform.rotate(self.orig_image, enemy.angle)
        self.rect = self.image.get_rect(center=orig_center)


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
        self.rect.x = randint(650, 900)
        self.rect.y = randint(-100, 50)
        self.vx = randint(-13, -10)
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
                Base.sound_of_crack.play()
        if pygame.sprite.spritecollideany(self, self.bullets):
            self.sound_of_crack.play()
            self.kill()
            pygame.sprite.spritecollide(self, self.bullets, True)
        if pygame.sprite.collide_mask(self, self.ship):
            self.sound_of_crack.play()
            self.ship.health -= 1
            self.kill()


class HorizonalBorders(pygame.sprite.Sprite):
    def __init__(self, *group, direction):
        super().__init__(*group)
        self.image = pygame.Surface((1, HEIGHT))
        if direction == 'right':
            self.rect = pygame.Rect(WIDTH - 1, 0, 1, HEIGHT)
        elif direction == 'left':
            self.rect = pygame.Rect(0, 0, 1, HEIGHT)


class VerticalBorders(pygame.sprite.Sprite):
    def __init__(self, *group, direction):
        super().__init__(*group)
        self.image = pygame.Surface((WIDTH, 1))
        if direction == 'up':
            self.rect = pygame.Rect(0, 0, WIDTH, 1)
        elif direction == 'down':
            self.rect = pygame.Rect(0, HEIGHT - 1, WIDTH, 1)


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


class CongratulationScreen(pygame.sprite.Sprite):
    image = load_image('Background\maxresdefault.jpg')
    count = 2

    def __init__(self, *group, vertical_borders, ship):
        super().__init__(*group)
        self.vertical_borders = vertical_borders
        self.image = pygame.transform.scale(CongratulationScreen.image,
                                            (WIDTH, HEIGHT))
        self.rect = self.image.get_rect()
        self.stop = False
        self.rect.y = 0 - HEIGHT
        self.ship = ship
        self.count = 2
        strings = ["Поздравляю, вы прошли 1 уровень.",
                   f'У вас есть {CongratulationScreen.count} очков умений для улучшения корабля']
        skills = [f'Здоровье: {self.ship.health}', f'Наличие щита: {self.ship.shield}',
                  f'Скорость снаряда: {Bullet.speed}', f'Урон: {self.ship.damage}']
        font = pygame.font.SysFont('comicsansms', 30)
        for i, j in enumerate(strings):
            string = font.render(j, True, pygame.Color('#C0C0C0'))
            self.image.blit(string, (100, 125 + i * 30))
        for i, j in enumerate(skills):
            string = font.render(j, True, pygame.Color('#C0C0C0'))
            self.image.blit(string, (100, 190 + i * 30))

    def update(self):
        if not pygame.sprite.spritecollideany(self, self.vertical_borders):
            self.rect = self.rect.move(0, 10)
        else:
            self.stop = True


class Cursor(pygame.sprite.Sprite):
    def __init__(self, *group):
        super().__init__(*group)
        cursor_img = load_image('cursor/arrow.png')
        self.image = cursor_img
        self.rect = cursor_img.get_rect()
        self.rect.x = -100

    def update(self, args):
        self.rect.x = args[0]
        self.rect.y = args[1]


def start_level_1():
    # Переменные
    x1 = 0
    x2 = 200
    x3 = 900
    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    horizontal_borders = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    # Флаги
    running = True
    level = 1
    f = False
    game_on = False
    win = False
    first_time = 0
    speed = 0
    end_on = False
    # Отслеживание времени
    clock = pygame.time.Clock()
    # Границы
    horizontal_border_1 = HorizonalBorders(all_sprites, direction='right')
    vertical_border_1 = VerticalBorders(all_sprites, direction='up')
    horizontal_border_2 = HorizonalBorders(all_sprites, direction='left')
    vertical_border_2 = VerticalBorders(all_sprites, direction='down')
    horizontal_borders.add(horizontal_border_1)
    horizontal_borders.add(horizontal_border_2)
    vertical_borders.add(vertical_border_1)
    vertical_borders.add(vertical_border_2)
    # Перманентные объекты
    base = Base(all_sprites)
    ship = Ship(all_sprites, base=base, horizontal_borders=horizontal_borders,
                vertical_borders=vertical_borders)
    # Надписи на экране
    level_text = ['Защитите торговый корабль от метеоритов',
                  'Здоровье:', 'Прочность корабля:']
    font = pygame.font.SysFont('comicsansms', 30)
    font_2 = pygame.font.SysFont('comicsansms', 25)
    string = f'Уровень {level}'
    health_ship = font.render(level_text[1], True, pygame.Color('#C0C0C0'))
    health_base = font_2.render(level_text[2], True, pygame.Color('#C0C0C0'))
    warning = 'Нажмите Space, чтобы начать'
    warning = font.render(warning, True, pygame.Color('#C0C0C0'))
    string = font.render(string, True, pygame.Color('#C0C0C0'))
    text = font.render(level_text[0], True, pygame.Color('#C0C0C0'))
    fon = pygame.transform.scale(load_image('Background/kosmos.jpg'), (WIDTH, HEIGHT))
    # Музыка
    pygame.mixer.music.load('music/audioblocks-80-s-dreamwave-logo_rS6JYzJfU_WM.mp3')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.4)
    # Звуки
    win_sound = pygame.mixer.Sound(
        'sound/ship/456968__funwithsound__success-resolution-video-game-fanfare-sound-effect.mp3')
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
                bullet_1 = Bullet(all_sprites, args=event.pos, direction='left')
                bullet_2 = Bullet(all_sprites, args=event.pos, direction='right')
                bullets.add(bullet_1)
                bullets.add(bullet_2)

        if ship.health == 1:
            ship.image = Ship.image_damaged_ship
        elif ship.health == 0:
            Ship.death_sound.play()
            ship.death = True
        if ship.death or base.death:
            end_on = True
            running = False
        if win:
            pygame.mixer.music.load(
                'sound/ship/456968__funwithsound__success-resolution-video-game-fanfare-sound-effect.mp3')
            pygame.mixer.music.play()
            win_screen(ship)
            return
        if pygame.time.get_ticks() > 28000 and not f:
            pygame.mixer.music.load('music/bensound-scifi.mp3')
            pygame.mixer.music.play()
            f = True
        if pygame.time.get_ticks() % 1000 in range(-100, 100):
            SpeedLine(all_sprites)
        if pygame.time.get_ticks() % 500 in range(-40, 40) and game_on:
            Meteor(all_sprites, base=base, ship=ship, bullets=bullets)

        screen.blit(fon, (0, 0))
        if x1 + WIDTH > 0:
            x1 -= speed
            x2 -= speed
        if x3 > 0:
            x3 -= speed
        screen.blit(string, (x1, 0))
        if game_on:
            time = pygame.time.get_ticks()
            if not first_time:
                first_time = time
            timer = f'Осталось еще продержаться: {60 - (time - first_time) // 1000}'
            timer = font.render(timer, True, pygame.Color('#C0C0C0'))
            screen.blit(timer, (x3, 0))
            if 1 - (time - first_time) // 1000 == 0:
                win = True
        screen.blit(text, (x2, 0))
        screen.blit(health_ship, (650, 435))
        screen.blit(health_base, (5, 90))
        ship.drawhp()
        base.drawhp()
        if not game_on:
            screen.blit(warning, (250, 250))
        pygame.mouse.set_visible(False)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)

    end_screen = GameOverScreen(all_sprites, borders=horizontal_border_1)
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


def win_screen(ship):
    ship.health = 2
    # Флаги
    buttons_on = False
    running = True
    old_tick = 0
    # Группы спрайтов
    all_sprites = pygame.sprite.Group()
    vertical_borders = pygame.sprite.Group()
    cursor_group = pygame.sprite.Group()
    vertical_border = VerticalBorders(all_sprites, direction='down')
    vertical_borders.add(vertical_border)
    # Время
    clock = pygame.time.Clock()
    # Появление победного экрана
    winsc = CongratulationScreen(all_sprites, vertical_borders=vertical_borders, ship=ship)
    # Новый курсор
    cursor = Cursor(cursor_group)
    # Основной цикл
    while running:
        if not old_tick:
            old_tick = pygame.time.get_ticks()
        time_delta = clock.tick(60) / 1000.0
        if not buttons_on and pygame.time.get_ticks() - old_tick > 7000:
            buttons_on = True
            next_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((400, 400), (100, 50)),
                text='Next Level',
                manager=manager
            )
            health_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((400, 195), (30, 30)),
                text='+',
                manager=manager
            )
            shield_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((400, 225), (30, 30)),
                text='+',
                manager=manager
            )
            speed_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((400, 255), (30, 30)),
                text='+',
                manager=manager
            )
            damage_button = pygame_gui.elements.UIButton(
                relative_rect=pygame.Rect((400, 285), (30, 30)),
                text='+',
                manager=manager
            )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            manager.process_events(event)
            if event.type == pygame.MOUSEMOTION and pygame.time.get_ticks() - old_tick > 7000:
                cursor.update(event.pos)
            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == health_button:
                        if winsc.count > 0:
                            ship.health += 1
                            winsc.count -= 1
                            print(ship.health)
                    if event.ui_element == speed_button:
                        if winsc.count > 0:
                            Bullet.speed += 3
                            winsc.count -= 1
                            print(Bullet.speed)
                    if event.ui_element == shield_button:
                        if winsc.count > 0 and ship.shield == 0:
                            ship.shield = 1
                            winsc.count -= 1
                            print(ship.shield)
                    if event.ui_element == damage_button:
                        if winsc.count > 0:
                            winsc.count -= 1
                            ship.damage += 1
                            print(ship.damage)
                    if event.ui_element == next_button:
                        running = False
                        start_level_2(ship)
                        return

        manager.update(time_delta)
        all_sprites.draw(screen)
        if not winsc.stop:
            all_sprites.update()
        manager.draw_ui(screen)
        cursor_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def start_level_2(ship):
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(load_image('Background/level_2/background_screen.jpg'),
                                 (WIDTH, HEIGHT))
    # Спрайты
    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    # Новые объекты
    new_ship = Ship(all_sprites)
    # Улучшения корабля
    new_ship.health = ship.health
    new_ship.shield = ship.shield
    new_ship.damage = ship.damage
    # Щит
    if new_ship.shield:
        shield = Shield(all_sprites)
    # Флаги
    running = True
    stage1 = True
    stage2 = False
    stage3 = False
    stage4 = False
    # Текст
    text = 'Здоровье: '
    font = pygame.font.SysFont('comicsansms', 30)
    text = font.render(text, True, pygame.Color('#C0C0C0'))

    while running:
        if stage1:
            start_time = pygame.time.get_ticks()
            enemy1 = EnemyShip(all_sprites, x=40, y=40)
            enemy2 = EnemyShip(all_sprites, x=400, y=40)
            enemy3 = EnemyShip(all_sprites, x=820, y=40)
            stage1 = False
            stage2 = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                if new_ship.shield:
                    shield.move(event.pos)
                new_ship.move(event.pos)
                if stage2:
                    enemy1.rotate(event.pos)
                    enemy2.rotate(event.pos)
                    enemy3.rotate(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bullet_1 = Bullet(all_sprites, args=event.pos, direction='left')
                bullet_2 = Bullet(all_sprites, args=event.pos, direction='right')
                bullets.add(bullet_1)
                bullets.add(bullet_2)
            if stage2:
                if (pygame.time.get_ticks() - start_time) // 1000 % 2 == 0:
                    bullet_enemy_1 = BulletOfEnemy(all_sprites, enemy=enemy1)
        # if pygame.time.get_ticks() > 8000
        screen.blit(fon, (0, 0))
        screen.blit(text, (650, 435))
        new_ship.drawhp()
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == '__main__':
    pygame.mixer.pre_init(44100, -16, 1, 512)
    start_screen()
    tm.sleep(0.1)
    start_level_1()
    terminate()
