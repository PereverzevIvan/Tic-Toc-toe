from pygame import display, time, event, mouse, init, image, transform, quit
from settings import *
from modules.bot_for_game import *
from random import choice
from sys import exit
from modules.gui_elems import *
from modules.game_elems import *
init()


def play_symbol_sound(symbol):
    if symbol == 'O':
        SHIELD.play(0)
    else:
        SWORD_1.play(0)
        SWORD_2.play(0)


class Game:
    """ Класс игры в целом """
    def __init__(self):
        self.window = display.set_mode([WIDTH, HEIGHT])
        display.set_caption("Крестики и нолики")
        display.set_icon(image.load('src/img/swords.png'))
        self.screen = surface.Surface([WIDTH, HEIGHT])
        self.clock = time.Clock()

    def run(self):
        start_screen = StartScreen()
        while True:
            start_screen.run()
            game_screen = GameScreen(*start_screen.get_chars())
            game_screen.run()


class GameScreen(Game):
    """ Класс игрового экрана """
    def __init__(self, hu_char: str, ai_char: str):
        super(GameScreen, self).__init__()
        self.field = Field(3, 3, 300, 55, self.screen)
        self.rule_place = RulePlace(780, 55, CELL_SIZE*1.9, CELL_SIZE*3, self.screen)
        self.btn_reset = Button(20, 350, CELL_SIZE*1.66, CELL_SIZE*0.4, 20, 'Начать новую игру', self.screen)
        self.btn_quit = Button(20, 445, CELL_SIZE * 1.66, CELL_SIZE * 0.4, 20, 'Выйти из игры', self.screen)
        self.btn_return = Button(20, 10, CELL_SIZE * 1.66, CELL_SIZE*0.2, 16,
                                 'Вернуться на главный экран', self.screen)
        self.counter = Counter(20, 55, CELL_SIZE*1.66, CELL_SIZE*0.85, self.screen)
        self.label_cur_player = Label(20, HEIGHT // 3, 20, 'Сейчас ходит: игрок', self.screen)
        self.contrast_screen = surface.Surface([WIDTH, HEIGHT], SRCALPHA)
        self.bg = image.load('src/img/game_screen_bg_pixel.png')
        self.bg = transform.scale(self.bg, (WIDTH, HEIGHT))
        self.font_header = font.Font("src/fonts/Sonic 1 Title Screen Filled.ttf", 75)
        self.buttons = [
            self.btn_quit,
            self.btn_return,
            self.btn_reset
        ]

        self.comp_turn = False
        self.was_win = False
        self.bot_first = False
        self.winner = ""
        self.winner_text = None
        self.winner_text_rect = None
        self.want_back = False
        self.was_bot_turn = False
        self.begin = True
        self.can_click = True
        self.click_time = 0

        self.bot = Bot(hu_char, ai_char)

        self.winner_text_color = (0, 0, 0)

    def update_click(self):
        if not self.can_click:
            mouse.set_cursor(NORM_CURSOR)
            cur_time = time.get_ticks()
            if cur_time - self.click_time >= 1000:
                self.can_click = True

    def rising(self):
        for i in range(26):
            self.contrast_screen.fill((0, 0, 0, 250 - 10*i))
            mixer.music.set_volume(0 + 0.1 * i)
            self.window.blit(self.screen, (0, 0))
            self.window.blit(self.contrast_screen, (0, 0))
            self.clock.tick(FPS)
            display.update()

    def refresh(self):
        self.was_win = False
        self.comp_turn = False
        self.field.refresh_field()
        if self.bot.ai_char == 'X':
            self.field.query = 1
            self.bot_first = True
        self.change_cur_player()

    def attenuation(self):
        for i in range(1, 26):
            self.contrast_screen.fill((0, 0, 0, 10*i))
            mixer.music.set_volume(1 - 0.1 * i)
            self.window.blit(self.screen, (0, 0))
            self.window.blit(self.contrast_screen, (0, 0))
            self.clock.tick(FPS)
            display.update()

    def change_cur_player(self):
        if self.field.query % 2 == 0:
            self.label_cur_player.change_text('Сейчас ходит: игрок')
        else:
            self.label_cur_player.change_text('Сейчас ходит: бот')

    def gameplay(self):
        self.refresh()
        mouse_pos = mouse.get_pos()
        run = True
        while run:
            if self.comp_turn:
                self.update_game()
                time.delay(1000)
            for evt in event.get():
                if evt.type == QUIT:
                    self.attenuation()
                    exit_()
                if evt.type == MOUSEMOTION and not self.begin:
                    mouse_pos = mouse.get_pos()
                    hovers = any([self.buttons[i].check_move(mouse_pos) for i in range(len(self.buttons))])
                    if self.field.check_move(mouse_pos) or hovers:
                        mouse.set_cursor(FINGER_CURSOR)
                    else:
                        mouse.set_cursor(NORM_CURSOR)
                if evt.type == MOUSEBUTTONDOWN and self.can_click:
                    if self.btn_reset.check_press(mouse_pos):
                        run = False
                        self.can_click = False
                        self.click_time = time.get_ticks() + 1000
                        if not self.was_win:
                            self.counter.update_counters('computer')
                            self.change_cur_player()
                    if self.btn_quit.check_press(mouse_pos):
                        self.attenuation()
                        exit_()
                    if self.btn_return.check_press(mouse_pos):
                        if not self.was_win:
                            self.counter.update_counters('computer')
                        run = False
                        self.want_back = True
                    if not self.was_win:
                        if self.field.check_press_on_cells(mouse_pos, self.bot.hu_char):
                            play_symbol_sound(self.bot.hu_char)
                            self.change_cur_player()
                            self.comp_turn = True
                            self.can_click = False
                            self.click_time = time.get_ticks() - 500
            self.update_click()
            self.screen.blit(self.bg, (0, 0))
            self.field.draw()
            self.rule_place.draw()
            self.counter.draw()
            self.label_cur_player.draw()
            if self.was_win:
                self.screen.blit(self.contrast_screen, (0, 0))
                self.screen.blit(self.winner_text, self.winner_text_rect)
            if self.was_bot_turn:
                play_symbol_sound(self.bot.ai_char)
                self.was_bot_turn = False
            self.btn_reset.draw()
            self.btn_quit.draw()
            self.btn_return.draw()

            if self.begin:
                self.rising()
                self.begin = False

            self.window.blit(self.screen, (0, 0))
            self.clock.tick(FPS)
            display.update()

            if self.bot_first:
                x = self.field.rect.x + CELL_SIZE * choice([0, 2])
                y = self.field.rect.y + CELL_SIZE * choice([0, 2])
                self.field.check_press_on_cells([x, y], self.bot.hu_char)
                self.was_bot_turn = True
                self.change_cur_player()
                self.bot_first = False
                time.delay(1000)

    def run(self):
        mixer.music.load('src/audio/game_screen_theme.mp3')
        mixer.music.play(-1)
        while True:
            self.gameplay()
            if self.want_back:
                self.attenuation()
                break

    def update_game(self):
        move = self.bot.computer_position(self.field.board)
        if move is not None:
            row, col = move
            x = self.field.rect.x + CELL_SIZE * col
            y = self.field.rect.y + CELL_SIZE * row
            self.field.check_press_on_cells([x, y], self.bot.hu_char)
            self.was_bot_turn = True

        if piece(self.field.board, self.bot.hu_char, self.bot.ai_char):
            self.winner = 'piece'
            self.was_win = True
        if check_win(self.field.board, self.bot.hu_char):
            self.was_win = True
            self.winner = 'human'
        if check_win(self.field.board, self.bot.ai_char):
            self.was_win = True
            self.winner = 'computer'

        if self.was_win:
            self.counter.update_counters(self.winner)
            self.render_win_text()

        self.change_cur_player()
        self.comp_turn = False

    def render_win_text(self):
        if self.winner == 'human':
            message = 'ПОБЕДА'
        elif self.winner == 'computer':
            message = 'ПОРАЖЕНИЕ'
        else:
            message = 'НИЧЬЯ'
        self.contrast_screen.fill((255, 255, 255, 100))
        self.winner_text = self.font_header.render(message, True, self.winner_text_color)
        self.winner_text_rect = self.winner_text.get_rect(center=[WIDTH//2, HEIGHT // 3])


class StartScreen(Game):
    """ Главного экрана """
    def __init__(self):
        super(StartScreen, self).__init__()
        self.header = Label(0, 0, 65, "Крестики и нолики", self.screen)
        self.btn_next = Button(0, 0, 300, 70, 25, "Начать игру", self.screen)
        self.btn_quit = Button(0, 0, 300, 70, 25, "Выйти из игры", self.screen)
        self.question = Label(10, 10, 21, 'Каким знаком вы хотите играть?', self.screen)
        self.bg = image.load('src/img/start_screen_bg_pixel.png')
        self.bg = transform.scale(self.bg, (WIDTH, HEIGHT))

        self.attenuation_screen = surface.Surface([WIDTH, HEIGHT], SRCALPHA)

        self.btn_quit.set_center(WIDTH // 1.86, HEIGHT // 1.3)
        self.btn_next.set_center(WIDTH // 1.86, HEIGHT // 1.7)
        self.header.rect.center = [WIDTH // 1.86, HEIGHT // 9]
        self.question.rect.center = [WIDTH // 1.86, HEIGHT // 2.8]

        self.char_choice = [RadioButton(WIDTH // 2.3, HEIGHT // 2.35, 18, 10, 'Крестики', self.screen),
                            RadioButton(WIDTH//1.8, HEIGHT//2.35, 18, 10, 'Нолики', self.screen)]
        self.char_choice[0].active = True

        self.buttons = [self.btn_next, self.btn_quit, *self.char_choice]

        self.begin = False

    def rising(self):
        for i in range(25):
            self.attenuation_screen.fill((0, 0, 0, 250 - 10 * i))
            mixer.music.set_volume(0 + 0.1 * i)
            self.window.blit(self.screen, (0, 0))
            self.window.blit(self.attenuation_screen, (0, 0))
            self.clock.tick(FPS // 1.5)
            display.update()

    def attenuation(self):
        for i in range(1, 26):
            self.attenuation_screen.fill((0, 0, 0, 10*i))
            mixer.music.set_volume(1 - 0.1 * i)
            self.window.blit(self.screen, (0, 0))
            self.window.blit(self.attenuation_screen, (0, 0))
            self.clock.tick(FPS // 1.5)
            display.update()

    def run(self):
        self.begin = True
        self.attenuation_screen.fill((0, 0, 0))
        mixer.music.load('src/audio/start_screen_theme.mp3')
        mixer.music.play(-1)
        mouse_pos = [0, 0]

        run = True
        while run:
            for evt in event.get():
                if evt.type == QUIT:
                    self.attenuation()
                    exit_()
                if evt.type == MOUSEMOTION and not self.begin:
                    mouse_pos = mouse.get_pos()
                    hovers = any([self.buttons[i].check_move(mouse_pos) for i in range(len(self.buttons))])
                    if hovers:
                        mouse.set_cursor(FINGER_CURSOR)
                    else:
                        mouse.set_cursor(NORM_CURSOR)
                if evt.type == MOUSEBUTTONDOWN:
                    if self.char_choice[0].check_press(mouse_pos):
                        self.update_char(0)
                    if self.char_choice[1].check_press(mouse_pos):
                        self.update_char(1)
                    if self.btn_next.check_press(mouse_pos):
                        run = False
                        mouse.set_cursor(NORM_CURSOR)
                        GATE_UNLOCK.play(0)
                    if self.btn_quit.check_press(mouse_pos):
                        self.attenuation()
                        exit_()
            self.screen.blit(self.bg, (0, 0))
            self.header.draw()
            self.question.draw()
            [radio.update() for radio in self.char_choice]
            self.btn_next.draw()
            self.btn_quit.draw()
            if self.begin:
                self.rising()
                self.begin = False

            self.window.blit(self.screen, (0, 0))
            self.clock.tick(FPS)
            display.update()
        time.delay(3000)
        self.attenuation()

    def update_char(self, index):
        self.char_choice[index].active = True
        self.char_choice[(index + 1) % 2].active = False

    def get_chars(self):
        if self.char_choice[0].active:
            return 'X', 'O'
        else:
            return 'O', 'X'


def exit_():
    file = open('src/count.txt', mode='w', encoding='utf-8')
    file.write('win=0\nlose=0\npiece=0')
    file.close()
    quit()
    exit()


if __name__ == '__main__':
    game = Game()
    game.run()
