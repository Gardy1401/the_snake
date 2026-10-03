"""Классическая змейка с переходом через границы игрового поля."""

from random import choice

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый игровой объект с позицией и цветом."""

    def __init__(self, body_color=None):
        """Разместить объект в центре поля и задать его цвет."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = body_color

    def draw(self):
        """Определить интерфейс отрисовки для дочерних классов."""
        pass


class Apple(GameObject):
    """Яблоко, появляющееся в случайной свободной клетке."""

    def __init__(self, occupied_positions=()):
        """Задать цвет и выбрать начальную позицию яблока."""
        super().__init__(APPLE_COLOR)
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
            rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Змейка с управляемым направлением и списком сегментов."""

    def __init__(self):
        """Создать зелёную змейку длиной в одну клетку."""
        super().__init__(SNAKE_COLOR)
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
        """Стереть след и нарисовать все сегменты змейки с рамкой."""
        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
        for position in self.positions:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Вернуть змейку в центр поля с движением вправо."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать стрелки и завершить игру при закрытии окна."""
    directions = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }
    opposite = (-game_object.direction[0], -game_object.direction[1])
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            direction = directions.get(event.key)
            if direction is not None and direction != opposite:
                game_object.next_direction = direction


def main():
    """Запустить игровой цикл до закрытия окна пользователем."""
    pygame.init()
    snake = Snake()
    apple = Apple(snake.positions)
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)
        elif snake.get_head_position() == apple.position:
            snake.length += 1
            # Сохранить хвост, удалённый при движении, для роста сразу.
            if snake.last is not None:
                snake.positions.append(snake.last)
                snake.last = None
            apple.randomize_position(snake.positions)
            if apple.position is None:
                # Поле заполнено: начать новую партию.
                snake.reset()
                apple.randomize_position(snake.positions)
                screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
