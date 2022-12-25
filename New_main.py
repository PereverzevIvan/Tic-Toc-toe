from pygame import display, time, event, draw, surface, rect, mouse, font, init, image, transform
from pygame.locals import *
from settings import *
from modules.bot_for_game import *
init()


def get_computer_char(user_char):
    return 'O' if user_char == 'X' else 'X'


def play_symbol_sound(symbol):
    if symbol == 'O':
        SHIELD.play(0)
    else:
        SWORD_1.play(0)
        SWORD_2.play(0)


class RadioButton:
    def __init__(self, x: int, y: int, font_size: int, radius: int, text: str, screen:surface.Surface):
        self.rect = rect.Rect(x, y, radius*2, radius*2)
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', font_size)
        self.text = Label(self.rect.right + 10, y, font_size, text, screen)
        self.screen = screen
        self.radius = radius
        self.active = False

    def update(self):
        self.draw()
        self.text.draw()

    def draw(self):
        draw.ellipse(self.screen, (200, 200, 200), self.rect)
        if self.active:
            draw.circle(self.screen, (30, 30, 30), self.rect.center, self.radius // 2)

    def check_press(self, mouse_pos: [int, int]):
        if self.rect.collidepoint(mouse_pos) or self.text.rect.collidepoint(mouse_pos):
            CLICK.play(0)
            return True
        return False


class Label:
    def __init__(self, x: int, y: int, font_size: int, text: str, screen: surface.Surface):
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', font_size)
        self.screen = screen
        self.text_color = (150, 150, 150)
        self.text = self.font.render(text, True, self.text_color)
        self.rect = self.text.get_rect(x=x, y=y)

    def draw(self):
        self.screen.blit(self.text, self.rect)

    def change_text(self, text: str):
        self.text = self.font.render(text, True, self.text_color)


class Button:
    def __init__(self, x: int, y: int, w: int, h: int, font_size: int, text: str, screen: surface.Surface):
        self.rect = rect.Rect(x, y, w, h)
        self.screen = screen
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', font_size)
        self.text_color = (150, 150, 150)
        self.bg_color = (200, 200, 200)
        self.bg_color_hover = (230, 230, 230)
        self.text_orig = text
        self.text = self.font.render(text, True, self.text_color)
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.hover = False

    def draw(self):
        if self.hover:
            draw.rect(self.screen, self.bg_color_hover, self.rect)
        else:
            draw.rect(self.screen, self.bg_color, self.rect)
        self.screen.blit(self.text, self.text_rect)

    def update(self, mouse_pose: [int, int]):
        self.check_move(mouse_pose)
        self.draw()

    def set_center(self, x: int, y: int):
        self.rect.center = [x, y]
        self.text_rect.center = [x, y]

    def check_move(self, mouse_pose: [int, int]):
        if mouse_pose is not None and self.rect.collidepoint(mouse_pose):
            self.hover = True
        else:
            self.hover = False

    def check_press(self, mouse_pose: [int, int]):
        if self.rect.collidepoint(mouse_pose):
            CLICK.play(0)
            return True
        else:
            return False


class Field:
    def __init__(self, rows: int, cols: int, x: int, y: int, screen: surface.Surface):
        self.screen = screen
        self.rect = rect.Rect(x, y, CELL_SIZE * rows, CELL_SIZE * cols)
        self.field = [[0] * cols for row in range(rows)]
        self.cells_coords = [[[x + CELL_SIZE * col, y + CELL_SIZE * row]
                              for col in range(cols)] for row in range(rows)]

        self.cells = [[Cell(col[0], col[1]) for col in row] for row in self.cells_coords]
        self.board = [[EMPTY_CHAR] * 3 for i in range(3)]

        self.query = 0

    def refresh_field(self):
        self.cells = [[Cell(col[0], col[1]) for col in row] for row in self.cells_coords]
        self.query = 0
        self.board = [[EMPTY_CHAR] * 3 for i in range(3)]

    def change_query(self):
        self.query = (self.query + 1) % 2

    def update_board(self):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                self.board[row][col] = self.cells[row][col].char

    def update(self, mouse_pos: [int, int]):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                self.cells[row][col].update(self.screen, mouse_pos)
        self.draw()

    def draw(self):
        for row in self.cells_coords:
            for col in row:
                draw.rect(self.screen, (180, 180, 180), self.rect, width=3)
                for row_ in range(3):
                    x1, y1 = self.cells_coords[row_][0]
                    draw.line(self.screen, (180, 180, 180), [x1, y1], [self.rect.right - 2, y1], width=3)
                for col_ in range(3):
                    x1, y1 = self.cells_coords[0][col_]
                    draw.line(self.screen, (180, 180, 180), [x1, y1], [x1, self.rect.bottom - 2], width=3)

    def check_press_on_cells(self, mouse_pos, hu_char):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                if self.cells[row][col].check_press(mouse_pos, self.query, hu_char):
                    self.update_board()
                    self.change_query()
                    return True
        return False


class Cell:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.char = EMPTY_CHAR
        self.hover = False
        self.rect = rect.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.font = font.Font(None, 100)

    def update(self, screen: surface.Surface, mouse_pos: [int, int]):
        self.check_move(mouse_pos)
        self.draw(screen)

    def draw(self, screen):
        if self.hover:
            draw.rect(screen, (230, 230, 230), self.rect)
        if self.char != EMPTY_CHAR:
            char = self.font.render(self.char, True, (0, 0, 0))
            char_rect = char.get_rect(center=self.rect.center)
            screen.blit(char, char_rect)

    def check_move(self, mouse_pos: [int, int]):
        if mouse_pos is not None:
            if self.rect.collidepoint(mouse_pos):
                self.hover = True
            else:
                self.hover = False

    def check_press(self, mouse_pos: [int, int], query: int, hu_char: str):
        if self.rect.collidepoint(mouse_pos):
            if self.char == EMPTY_CHAR:
                if query % 2 == 0:
                    self.char = hu_char
                else:
                    self.char = get_computer_char(hu_char)
                return True
        return False


class Counter:
    def __init__(self, x: int, y: int, w: int, h: int, screen: surface.Surface):
        self.rect = rect.Rect(x, y, w, h)
        self.screen = screen
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', 20)
        self.win = 0
        self.lose = 0
        self.piece = 0
        self.text = []
        self.rects = []
        self.render_text()

    def render_text(self):
        self.text = [
            self.font.render("Победы:", True, (150, 150, 150)),
            self.font.render("Поражения:", True, (150, 150, 150)),
            self.font.render("Ничьи:", True, (150, 150, 150)),
            self.font.render(str(self.win), True, (150, 150, 150)),
            self.font.render(str(self.lose), True, (150, 150, 150)),
            self.font.render(str(self.piece), True, (150, 150, 150))
        ]
        self.rects = [line.get_rect() for line in self.text]
        for i in range(3):
            self.rects[i].left = self.rect.left + 10
            self.rects[i].top = self.rect.top + 20 + 30 * i
        for i in range(3, 6):
            self.rects[i].right = self.rect.right - 10
            self.rects[i].top = self.rect.top + 20 + 30 * (i - 3)

    def update_counters(self, result):
        if result == 'human':
            self.win += 1
        elif result == 'computer':
            self.lose += 1
        else:
            self.piece += 1
        self.render_text()

    def draw(self):
        draw.rect(self.screen, (180, 180, 180), self.rect, width=3)
        for i in range(6):
            self.screen.blit(self.text[i], self.rects[i])


class RulePlace:
    def __init__(self, x: int, y: int, w: int, h: int, screen: surface.Surface):
        self.rect = rect.Rect(x, y, w, h)
        self.screen = screen
        self.font_header = font.Font("src/fonts/centurygothic_bold.ttf", 20)
        self.font = font.Font("src/fonts/centurygothic_bold.ttf", 16)
        self.text_fish = ['• Игроки по очереди ставят',
                          '   на свободные клетки поля',
                          '   3×3 знаки (один всегда ',
                          '   крестики, другой всегда ',
                          '   нолики).',
                          '• Первый ход делает игрок,',
                          '   ставящий крестики. ',
                          '• Игра продолжается пока не ',
                          '   заполнятся все клетки, или ',
                          '   один из участников не сделает ',
                          '   цепочку из трёх одинаковых ',
                          '   символов. ',
                          '• Причём ряд идёт по ',
                          '   горизонтали, вертикали',
                          '   или диагонали.']
        self.text_header = self.font_header.render('Правила игры', True, (150, 150, 150))
        self.text = []

        self.render_text()

    def render_text(self):
        for line in self.text_fish:
            self.text += [self.font.render(line, True, (150, 150, 150))]

    def draw(self):
        draw.rect(self.screen, (180, 180, 180), self.rect, width=3)
        x, y = self.rect[:2]
        x += 10
        y += 10
        self.screen.blit(self.text_header, [x, y])
        y += 20
        for line in self.text:
            y += 20
            self.screen.blit(line, [x, y])


class Game:
    def __init__(self):
        self.window = display.set_mode([WIDTH, HEIGHT])
        display.set_caption("Крестики и нолики")
        self.screen = surface.Surface([WIDTH, HEIGHT])
        self.clock = time.Clock()
        self.font_header = font.Font("src/fonts/Sonic 1 Title Screen Filled.ttf", 65)

    def run(self):
        start_screen = StartScreen()
        while True:
            start_screen.run()
            game_screen = GameScreen(*start_screen.get_chars())
            game_screen.run()


class GameScreen(Game):
    def __init__(self, hu_char: str, ai_char: str):
        super(GameScreen, self).__init__()
        self.winner_text_color = (100, 100, 100)
        self.field = Field(3, 3, 300, 55, self.screen)
        self.rule_place = RulePlace(780, 55, CELL_SIZE*1.9, CELL_SIZE*3, self.screen)
        self.btn_reset = Button(20, 350, CELL_SIZE*1.66, CELL_SIZE*0.4, 20, 'Начать новую игру', self.screen)
        self.btn_quit = Button(20, 445, CELL_SIZE * 1.66, CELL_SIZE * 0.4, 20, 'Выйти из игры', self.screen)
        self.btn_return = Button(20, 10, CELL_SIZE * 1.66, CELL_SIZE*0.2, 16,
                                 'Вернуться на главный экран', self.screen)
        self.counter = Counter(20, 55, CELL_SIZE*1.66, CELL_SIZE*0.85, self.screen)
        self.label_cur_player = Label(20, 300, 20, 'Сейчас ходит: игрок', self.screen)
        self.contrast_screen = surface.Surface([WIDTH, HEIGHT], SRCALPHA)
        self.bg = image.load('src/img/game_screen_bg_pixel.png')
        self.bg = transform.scale(self.bg, (WIDTH, HEIGHT))

        self.was_press = False
        self.was_win = False
        self.bot_first = False
        self.winner = ""
        self.winner_text = None
        self.winner_text_rect = None
        self.want_back = False
        self.was_bot_turn = False

        self.contrast_screen.fill((255, 255, 255, 200))

        self.bot = Bot(hu_char, ai_char)

    def refresh(self):
        self.was_press = False
        self.was_win = False
        self.field.refresh_field()
        if self.bot.ai_char == 'X':
            self.field.query = 1
            self.bot_first = True
        self.change_cur_player()

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
            if self.was_press:
                self.update_game()
                time.delay(1000)
            for evt in event.get():
                if evt.type == QUIT:
                    time.delay(1000)
                    exit(0)
                if evt.type == MOUSEMOTION:
                    mouse_pos = mouse.get_pos()
                if evt.type == MOUSEBUTTONDOWN:
                    if self.btn_reset.check_press(mouse_pos):
                        run = False
                        if not self.was_win:
                            self.counter.update_counters('computer')
                            self.change_cur_player()
                    if self.btn_quit.check_press(mouse_pos):
                        time.delay(1000)
                        exit(0)
                    if self.btn_return.check_press(mouse_pos):
                        run = False
                        self.want_back = True
                    if not self.was_win:
                        if self.field.check_press_on_cells(mouse_pos, self.bot.hu_char):
                            play_symbol_sound(self.bot.hu_char)
                            self.change_cur_player()
                            self.was_press = True
            self.screen.fill((255, 255, 255))
            self.field.update(mouse_pos)
            self.rule_place.draw()
            self.counter.draw()
            self.label_cur_player.draw()
            if self.was_win:
                self.screen.blit(self.contrast_screen, (0, 0))
                self.screen.blit(self.winner_text, self.winner_text_rect)
            if self.was_bot_turn:
                play_symbol_sound(self.bot.ai_char)
                self.was_bot_turn = False
            self.btn_reset.update(mouse_pos)
            self.btn_quit.update(mouse_pos)
            self.btn_return.update(mouse_pos)

            self.window.blit(self.screen, (0, 0))
            self.clock.tick(FPS)
            display.update()

            if self.bot_first:
                x = self.field.rect.x + 1
                y = self.field.rect.y + 1
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
        self.was_press = False

    def render_win_text(self):
        if self.winner == 'human':
            message = 'ПОБЕДА'
        elif self.winner == 'computer':
            message = 'ПОРАЖЕНИЕ'
        else:
            message = 'НИЧЬЯ'
        self.winner_text = self.font_header.render(message, True, self.winner_text_color)
        self.winner_text_rect = self.winner_text.get_rect(center=[WIDTH//2, HEIGHT // 3])


class StartScreen(Game):
    def __init__(self):
        super(StartScreen, self).__init__()
        self.header = Label(0, 0, 65, "Крестики и нолики", self.screen)
        self.btn_next = Button(0, 0, 300, 70, 25, "Начать игру", self.screen)
        self.btn_quit = Button(0, 0, 300, 70, 25, "Выйти из игры", self.screen)
        self.question = Label(10, 10, 20, 'Каким знаком вы хотите играть?', self.screen)
        self.bg = image.load('src/img/start_screen_bg_pixel.png')
        self.bg = transform.scale(self.bg, (WIDTH, HEIGHT))

        self.btn_quit.set_center(WIDTH // 2, HEIGHT // 1.3)
        self.btn_next.set_center(WIDTH // 2, HEIGHT // 1.7)
        self.header.rect.center = [WIDTH // 2, HEIGHT // 10]
        self.question.rect.center = [WIDTH // 2, HEIGHT // 3]

        self.char_choice = [RadioButton(WIDTH // 2.7, HEIGHT // 2.5, 16, 10, 'Крестики', self.screen),
                            RadioButton(WIDTH//1.85, HEIGHT//2.5, 16, 10, 'Нолики', self.screen)]
        self.char_choice[0].active = True

    def run(self):
        mixer.music.load('src/audio/start_screen_theme.mp3')
        mixer.music.play(-1)
        mouse_pos = mouse.get_pos()
        run = True
        while run:
            for evt in event.get():
                if evt.type == QUIT:
                    time.delay(1000)
                    exit(0)
                if evt.type == MOUSEMOTION:
                    mouse_pos = mouse.get_pos()
                if evt.type == MOUSEBUTTONDOWN:
                    if self.char_choice[0].check_press(mouse_pos):
                        self.update_char(0)
                    if self.char_choice[1].check_press(mouse_pos):
                        self.update_char(1)
                    if self.btn_next.check_press(mouse_pos):
                        run = False
                        GATE_UNLOCK.play(0)
                        time.delay(3000)
                    if self.btn_quit.check_press(mouse_pos):
                        time.delay(1000)
                        exit(0)
            self.screen.blit(self.bg, (0, 0))
            self.header.draw()
            self.question.draw()
            [radio.update() for radio in self.char_choice]
            self.btn_next.update(mouse_pos)
            self.btn_quit.update(mouse_pos)
            self.window.blit(self.screen, (0, 0))
            self.clock.tick(FPS)
            display.update()
        mixer.music.stop()

    def update_char(self, index):
        self.char_choice[index].active = True
        self.char_choice[(index + 1) % 2].active = False

    def get_chars(self):
        if self.char_choice[0].active:
            return 'X', 'O'
        else:
            return 'O', 'X'


if __name__ == '__main__':
    game = Game()
    game.run()
