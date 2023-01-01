from pygame import draw, surface, rect, font, SRCALPHA
from settings import CLICK


class RadioButton:
    """ Класс графического элемента 'Радиокнопка' """
    def __init__(self, x: int, y: int, font_size: int, radius: int, text: str, screen: surface.Surface):
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

    def check_move(self, mouse_pose: [int, int]):
        if mouse_pose is not None and self.rect.collidepoint(mouse_pose):
            return True
        else:
            return False


class Label:
    """ Класс графического элемента 'Надпись' """
    def __init__(self, x: int, y: int, font_size: int, text: str, screen: surface.Surface):
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', font_size)
        self.screen = screen
        self.text_color = (255, 255, 255)
        self.text = self.font.render(text, True, self.text_color)
        self.rect = self.text.get_rect(x=x, y=y)

    def draw(self):
        self.screen.blit(self.text, self.rect)

    def change_text(self, text: str):
        self.text = self.font.render(text, True, self.text_color)


class Button:
    """ Класс графического элемента 'Кнопка' """
    def __init__(self, x: int, y: int, w: int, h: int, font_size: int, text: str, screen: surface.Surface):
        self.rect = rect.Rect(x, y, w, h)
        self.screen = screen
        self.font = font.Font('src/fonts/centurygothic_bold.ttf', font_size)
        self.text_color = (255, 255, 255)
        self.bg_color = (0, 0, 0, 210)
        self.bg_color_hover = (100, 100, 100, 200)
        self.bg = surface.Surface([self.rect.w, self.rect.h], SRCALPHA)
        self.text_orig = text
        self.text = self.font.render(text, True, self.text_color)
        self.text_rect = self.text.get_rect(center=self.rect.center)
        self.hover = False

    def draw(self):
        self.bg.fill(self.bg_color)
        if self.hover:
            self.bg.fill(self.bg_color_hover)
        self.screen.blit(self.bg, self.rect)
        self.screen.blit(self.text, self.text_rect)

    def set_center(self, x: int, y: int):
        self.rect.center = [x, y]
        self.text_rect.center = [x, y]

    def check_move(self, mouse_pose: [int, int]):
        if mouse_pose is not None and self.rect.collidepoint(mouse_pose):
            self.hover = True
            return True
        else:
            self.hover = False
            return False

    def check_press(self, mouse_pose: [int, int]):
        if self.rect.collidepoint(mouse_pose):
            CLICK.play(0)
            return True
        else:
            return False