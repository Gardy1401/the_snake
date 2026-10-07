"""Классическая змейка с переходом через границы игрового поля."""

import sys
from random import choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
START_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (93, 216, 228)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

SPEED = 20

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Базовый игровой объект с позицией и цветом."""

    def __init__(self, position=START_POSITION, body_color=None):
        """Задать позицию и цвет игрового объекта."""
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Определить интерфейс отрисовки для дочерних классов."""
        raise NotImplementedError(
            f'Метод draw не переопределён в классе {type(self).__name__}'
        )

    def draw_cell(self, position, body_color=None, border_color=BORDER_COLOR):
        """Нарисовать клетку заданного цвета с необязательной рамкой."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        color = self.body_color if body_color is None else body_color
        pg.draw.rect(screen, color, rect)
        if border_color is not None:
            pg.draw.rect(screen, border_color, rect, 1)


class Apple(GameObject):
    """Яблоко, появляющееся в случайной свободной клетке."""

    def __init__(self, occupied_positions=(), position=None,
                 body_color=APPLE_COLOR):
        """Задать цвет и позицию; по умолчанию выбрать свободную клетку."""
        super().__init__(position, body_color)
        if position is None:
            self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=()):
        """Выбрать свободную клетку или None, если поле заполнено."""
        occupied = set(occupied_positions)
        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied
        ]
        self.position = choice(free_positions) if free_positions else None

    def draw(self):
        """Нарисовать яблоко с рамкой, если для него есть место."""
        if self.position is not None:
            self.draw_cell(self.position)


class Snake(GameObject):
    """Змейка с управляемым направлением и списком сегментов."""

    def __init__(self, position=START_POSITION, body_color=SNAKE_COLOR):
        """Создать змейку с заданными начальной позицией и цветом."""
        super().__init__(position, body_color)
        self.start_position = position
        self.reset()

    def update_direction(self):
        """Применить ожидающий поворот, запретив движение назад."""
        opposite = (-self.direction[0], -self.direction[1])
        if self.next_direction in (UP, DOWN, LEFT, RIGHT):
            if self.next_direction != opposite:
                self.direction = self.next_direction
        self.next_direction = None

    def move(self):
        """Сдвинуть сегменты на клетку с переходом через границы."""
        x, y = self.get_head_position()
        dx, dy = self.direction
        self.position = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, self.position)
        self.last = None
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def draw(self):
        """Стереть ушедший хвост и нарисовать новую голову."""
        if self.last is not None:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, None)
        self.draw_cell(self.get_head_position())

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Очистить поле и вернуть змейку в её начальное состояние."""
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.position = self.start_position
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать стрелки, закрытие окна и выход по Escape."""
    directions = {
        pg.K_UP: UP,
        pg.K_DOWN: DOWN,
        pg.K_LEFT: LEFT,
        pg.K_RIGHT: RIGHT,
    }
    opposite = (-game_object.direction[0], -game_object.direction[1])
    for event in pg.event.get():
        if (event.type == pg.QUIT
                or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            direction = directions.get(event.key)
            if direction is not None and direction != opposite:
                game_object.next_direction = direction


def main():
    """Запустить игровой цикл до закрытия окна пользователем."""
    pg.init()
    snake = Snake()
    apple = Apple(snake.positions)
    snake.draw()
    apple.draw()

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            # Сохранить хвост, удалённый при движении, для роста сразу.
            if snake.last is not None:
                snake.positions.append(snake.last)
                snake.last = None
            apple.randomize_position(snake.positions)
            if apple.position is None:
                snake.reset()
                apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
