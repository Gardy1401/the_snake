"""Проверки движения, управления, роста и перезапуска игры."""

from unittest.mock import Mock

import pygame
import pytest

from conftest import StopInfiniteLoop


@pytest.mark.parametrize(
    'position, direction, expected',
    [
        ((620, 240), (1, 0), (0, 240)),
        ((0, 240), (-1, 0), (620, 240)),
        ((320, 0), (0, -1), (320, 460)),
        ((320, 460), (0, 1), (320, 0)),
    ],
)
def test_move_wraps_at_every_edge(snake, position, direction, expected):
    """Змейка проходит через каждую из четырёх границ."""
    snake.positions = [position]
    snake.direction = direction
    snake.move()
    assert snake.positions == [expected]
    assert snake.last == position


def test_move_keeps_body_length(snake):
    """Движение сохраняет длину тела и запоминает ушедший хвост."""
    snake.positions = [(100, 100), (80, 100), (60, 100)]
    snake.length = 3
    snake.move()
    assert snake.positions == [(120, 100), (100, 100), (80, 100)]
    assert snake.last == (60, 100)


def test_apple_uses_only_free_cell(_the_snake):
    """Даже на почти заполненном поле яблоко находит свободную клетку."""
    free = (0, 0)
    occupied = [
        (x, y)
        for x in range(0, _the_snake.SCREEN_WIDTH, _the_snake.GRID_SIZE)
        for y in range(0, _the_snake.SCREEN_HEIGHT, _the_snake.GRID_SIZE)
        if (x, y) != free
    ]
    apple = _the_snake.Apple(occupied)
    assert apple.position == free
    apple.randomize_position(occupied + [free])
    assert apple.position is None


def test_keys_cannot_reverse_in_one_frame(_the_snake, snake, monkeypatch):
    """Несколько событий за кадр не позволяют развернуть змейку назад."""
    events = [
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP),
        pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT),
    ]
    monkeypatch.setattr(pygame.event, 'get', lambda: events)
    _the_snake.handle_keys(snake)
    snake.update_direction()
    assert snake.direction == _the_snake.UP
    assert snake.next_direction is None


def test_update_direction_rejects_reverse(_the_snake, snake):
    """Защита от разворота действует и при прямой установке направления."""
    snake.next_direction = _the_snake.LEFT
    snake.update_direction()
    assert snake.direction == _the_snake.RIGHT
    assert snake.next_direction is None


def test_draw_keeps_head_on_vacated_tail(_the_snake, snake):
    """Вход в клетку уходящего хвоста не стирает новую голову."""
    snake.positions = [(100, 100), (100, 120), (80, 120), (80, 100)]
    snake.length = 4
    snake.direction = _the_snake.LEFT
    snake.move()
    assert snake.get_head_position() not in snake.positions[1:]
    snake.draw()
    assert _the_snake.screen.get_at((90, 110))[:3] == snake.body_color


def run_one_frame(module, snake, apple, monkeypatch):
    """Выполнить одну итерацию настоящего игрового цикла."""
    clock = Mock()
    clock.tick.side_effect = [None, StopInfiniteLoop]
    monkeypatch.setattr(module, 'clock', clock)
    monkeypatch.setattr(module, 'Snake', lambda: snake)
    monkeypatch.setattr(module, 'Apple', lambda occupied: apple)
    monkeypatch.setattr(module, 'handle_keys', lambda game_object: None)
    with pytest.raises(StopInfiniteLoop):
        module.main()


def test_main_grows_immediately(_the_snake, snake, apple, monkeypatch):
    """Поедание яблока сохраняет хвост и добавляет сегмент в тот же кадр."""
    old_head = snake.get_head_position()
    apple.position = (old_head[0] + _the_snake.GRID_SIZE, old_head[1])
    run_one_frame(_the_snake, snake, apple, monkeypatch)
    assert snake.length == len(snake.positions) == 2
    assert snake.positions[1] == old_head
    assert apple.position not in snake.positions
    assert snake.last is None


def test_main_resets_after_self_collision(
    _the_snake, snake, apple, monkeypatch,
):
    """Столкновение сбрасывает тело, направление и старые следы."""
    snake.positions = [
        (100, 100), (120, 100), (120, 120), (100, 120), (80, 120),
    ]
    snake.length = 5
    run_one_frame(_the_snake, snake, apple, monkeypatch)
    assert snake.positions == [(320, 240)]
    assert snake.length == 1
    assert snake.direction == _the_snake.RIGHT
    assert snake.next_direction is None
    assert apple.position not in snake.positions
    assert _the_snake.screen.get_at((110, 110))[:3] == (0, 0, 0)


def test_close_window_exits(_the_snake, snake, monkeypatch):
    """Закрытие окна освобождает Pygame и завершает программу."""
    monkeypatch.setattr(
        pygame.event, 'get', lambda: [pygame.event.Event(pygame.QUIT)],
    )
    quit_mock = Mock()
    monkeypatch.setattr(pygame, 'quit', quit_mock)
    with pytest.raises(SystemExit):
        _the_snake.handle_keys(snake)
    quit_mock.assert_called_once_with()
