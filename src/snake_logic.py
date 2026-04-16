from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable


Coordinate = tuple[int, int]

UP: Coordinate = (0, -1)
DOWN: Coordinate = (0, 1)
LEFT: Coordinate = (-1, 0)
RIGHT: Coordinate = (1, 0)

OPPOSITE_DIRECTIONS = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}


@dataclass(frozen=True)
class SnakeState:
    width: int
    height: int
    snake: tuple[Coordinate, ...]
    direction: Coordinate
    food: Coordinate
    score: int = 0
    game_over: bool = False


def create_initial_state(width: int = 12, height: int = 12, seed: int = 0) -> SnakeState:
    if width < 4 or height < 4:
        raise ValueError("Grid must be at least 4x4.")

    start_x = width // 2
    start_y = height // 2
    snake = ((start_x, start_y), (start_x - 1, start_y), (start_x - 2, start_y))
    randomizer = Random(seed)
    food = place_food(width, height, snake, randomizer)
    return SnakeState(
        width=width,
        height=height,
        snake=snake,
        direction=RIGHT,
        food=food,
    )


def change_direction(current: Coordinate, requested: Coordinate) -> Coordinate:
    if requested not in OPPOSITE_DIRECTIONS:
        return current
    if requested == OPPOSITE_DIRECTIONS[current]:
        return current
    return requested


def step_state(
    state: SnakeState,
    requested_direction: Coordinate | None = None,
    rng: Random | None = None,
) -> SnakeState:
    if state.game_over:
        return state

    direction = state.direction
    if requested_direction is not None:
        direction = change_direction(direction, requested_direction)

    head_x, head_y = state.snake[0]
    dx, dy = direction
    next_head = (head_x + dx, head_y + dy)

    if not is_inside_grid(next_head, state.width, state.height):
        return SnakeState(**{**state.__dict__, "direction": direction, "game_over": True})

    grows = next_head == state.food
    body_to_check = state.snake if grows else state.snake[:-1]
    if next_head in body_to_check:
        return SnakeState(**{**state.__dict__, "direction": direction, "game_over": True})

    next_snake = (next_head,) + state.snake
    if not grows:
        next_snake = next_snake[:-1]

    next_food = state.food
    next_score = state.score
    if grows:
        next_score += 1
        next_food = place_food(state.width, state.height, next_snake, rng or Random())

    return SnakeState(
        width=state.width,
        height=state.height,
        snake=next_snake,
        direction=direction,
        food=next_food,
        score=next_score,
        game_over=False,
    )


def is_inside_grid(position: Coordinate, width: int, height: int) -> bool:
    x, y = position
    return 0 <= x < width and 0 <= y < height


def place_food(
    width: int,
    height: int,
    snake: Iterable[Coordinate],
    rng: Random | None = None,
) -> Coordinate:
    snake_cells = set(snake)
    available = [
        (x, y)
        for y in range(height)
        for x in range(width)
        if (x, y) not in snake_cells
    ]
    if not available:
        raise ValueError("Cannot place food on a full board.")
    chooser = rng or Random()
    return chooser.choice(available)
