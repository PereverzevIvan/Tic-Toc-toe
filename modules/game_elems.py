from pygame import draw, surface, rect, font, image, transform, SRCALPHA
from settings import CELL_SIZE
from modules.bot_for_game import EMPTY_CHAR


def get_computer_char(user_char):
    return 'O' if user_char == 'X' else 'X'


class Field:
    """ Класс игрового поля """
    def __init__(self, rows: int, cols: int, x: int, y: int, screen: surface.Surface):
        self.screen = screen
        self.rect = rect.Rect(x, y, CELL_SIZE * rows, CELL_SIZE * cols)
        self.field = [[0] * cols for _ in range(rows)]
        self.cells_coords = [[[x + CELL_SIZE * col, y + CELL_SIZE * row]
                              for col in range(cols)] for row in range(rows)]
        self.border_color = (100, 100, 100)

        self.cells = [[Cell(col[0], col[1], self.screen) for col in row] for row in self.cells_coords]
        self.board = [[EMPTY_CHAR] * 3 for _ in range(3)]
        self.contrast_screen = surface.Surface([self.rect.w, self.rect.h], SRCALPHA)
        self.contrast_screen.fill((0, 0, 0, 150))

        self.query = 0

    def refresh_field(self):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                self.cells[row][col].refresh()
        self.query = 0
        self.board = [[EMPTY_CHAR] * 3 for _ in range(3)]

    def change_query(self):
        self.query = (self.query + 1) % 2

    def update_board(self):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                self.board[row][col] = self.cells[row][col].char

    def check_move(self, mouse_pos: [int, int]):
        hovers = []
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                hovers += [self.cells[row][col].check_move(mouse_pos)]
        return any(hovers)

    def draw(self):
        self.screen.blit(self.contrast_screen, self.rect)
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                self.cells[row][col].draw()
        for _ in self.cells_coords:
            for row in range(1, 3):
                x1, y1 = self.cells_coords[row][0]
                draw.line(self.screen, self.border_color, [x1, y1], [self.rect.right - 1, y1], width=4)
            for col in range(1, 3):
                x1, y1 = self.cells_coords[0][col]
                draw.line(self.screen, self.border_color, [x1, y1], [x1, self.rect.bottom - 1], width=4)
        draw.rect(self.screen, self.border_color, self.rect, width=3)

    def check_press_on_cells(self, mouse_pos, hu_char):
        for row in range(len(self.cells)):
            for col in range(len(self.cells[row])):
                if self.cells[row][col].check_press(mouse_pos, self.query, hu_char):
                    self.update_board()
                    self.change_query()
                    return True
        return False


class Cell:
    """ Класс отдельной клетки игрового поля """
    def __init__(self, x: int, y: int, screen: surface.Surface):
        self.x = x
        self.y = y
        self.screen = screen
        self.char = EMPTY_CHAR
        self.hover = False
        self.rect = rect.Rect(x, y, CELL_SIZE, CELL_SIZE)
        self.font = font.Font(None, 100)
        self.cross = transform.scale(image.load('src/img/swords.png'), [self.rect.w-10, self.rect.h-10])
        self.circle = transform.scale(image.load('src/img/shield.png'), [self.rect.w-10, self.rect.h-10])
        self.image_rect = rect.Rect(x, y, CELL_SIZE - 10, CELL_SIZE - 10)
        self.image_rect.center = self.rect.center

        self.contrast_screen = surface.Surface([self.rect.w, self.rect.h], SRCALPHA)
        self.contrast_screen.fill((230, 230, 230, 30))

        self.slovar = {'X': self.cross, 'O': self.circle}

    def refresh(self):
        self.char = EMPTY_CHAR
        self.hover = False

    def draw(self):
        if self.hover:
            self.screen.blit(self.contrast_screen, self.rect)
        if self.char != EMPTY_CHAR:
            self.screen.blit(self.slovar[self.char], self.image_rect)

    def check_move(self, mouse_pos: [int, int]):
        if mouse_pos is not None:
            if self.rect.collidepoint(mouse_pos):
                self.hover = True
                return True
            else:
                self.hover = False
                return False

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
    """ Класс счетчика побед, поражений и ничей """
    def __init__(self, x: int, y: int, w: int, h: int, screen: surface.Surface):
        self.rect = rect.Rect(x, y, w, h)
        self.screen = screen
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', 20)

        self.rects = [rect.Rect(0, 0, 0, 0) for _ in range(6)]

        self.contrast_screen = surface.Surface([self.rect.w, self.rect.h], SRCALPHA)
        self.contrast_screen.fill((0, 0, 0, 150))

        self.white_contrast = [surface.Surface([CELL_SIZE * 0.5, CELL_SIZE * 0.175], SRCALPHA) for _ in range(3)]
        [self.white_contrast[i].fill((255, 255, 255, 40)) for i in range(3)]
        self.white_rects = [rect.Rect(0, 0, CELL_SIZE * 0.5, CELL_SIZE * 0.175) for _ in range(3)]

        self.text_color = (255, 255, 255)
        self.border_color = (100, 100, 100)

        self.win, self.lose, self.piece = self.read_file()
        self.text = []
        self.rects = []
        self.render_text()

    def read_file(self):
        file = open('src/count.txt', mode='r', encoding='utf-8')
        data = [int(line.split('=')[1]) for line in file.readlines()]
        file.close()
        return data

    def write_file(self):
        file = open('src/count.txt', mode='w', encoding='utf-8')
        file.write(f'win={self.win}\nlose={self.lose}\npiece={self.piece}')
        file.close()

    def render_text(self):
        self.text = [
            self.font.render("Победы:", True, self.text_color),
            self.font.render("Поражения:", True, self.text_color),
            self.font.render("Ничьи:", True, self.text_color),
            self.font.render(str(self.win), True, self.text_color),
            self.font.render(str(self.lose), True, self.text_color),
            self.font.render(str(self.piece), True, self.text_color)
        ]
        self.rects = [line.get_rect() for line in self.text]
        for i in range(3):
            self.rects[i].left = self.rect.left + 10
            self.rects[i].top = self.rect.top + 20 + 30 * i
        for i in range(3, 6):
            self.rects[i].right = self.rect.right - 15
            self.white_rects[i - 3].right = self.rect.right - 10
            self.white_rects[i-3].top = self.rects[i].top = self.rect.top + 20 + 30 * (i - 3)

    def update_counters(self, result):
        if result == 'human':
            self.win += 1
        elif result == 'computer':
            self.lose += 1
        else:
            self.piece += 1
        self.write_file()
        self.render_text()

    def draw(self):
        self.screen.blit(self.contrast_screen, self.rect)
        for j in range(3):
            self.screen.blit(self.white_contrast[j], self.white_rects[j])
        draw.rect(self.screen, self.border_color, self.rect, width=3)
        for i in range(6):
            self.screen.blit(self.text[i], self.rects[i])


class RulePlace:
    """ Класс области с правилами игры """
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
                          '',
                          '• Первый ход делает игрок,',
                          '   ставящий крестики. ',
                          '',
                          '• Игра продолжается пока не ',
                          '   заполнятся все клетки, или ',
                          '   один из участников не сделает ',
                          '   цепочку из трёх одинаковых ',
                          '   символов. ',
                          '',
                          '• Причём ряд идёт по ',
                          '   горизонтали, вертикали',
                          '   или диагонали.']
        self.text_header = self.font_header.render('Правила игры', True, (255, 255, 255))
        self.text = []

        self.contrast_screen = surface.Surface([self.rect.w, self.rect.h], SRCALPHA)
        self.contrast_screen.fill((0, 0, 0, 150))

        self.border_color = (100, 100, 100)

        self.render_text()

    def render_text(self):
        for line in self.text_fish:
            self.text += [self.font.render(line, True, (255, 255, 255))]

    def draw(self):
        self.screen.blit(self.contrast_screen, self.rect)
        draw.rect(self.screen, self.border_color, self.rect, width=3)
        x, y = self.rect[:2]
        x += 10
        y += 10
        self.screen.blit(self.text_header, [x, y])
        y += 20
        for line in self.text:
            y += 20
            self.screen.blit(line, [x, y])