import unittest
from random import Random

from src.snake_logic import DOWN, LEFT, RIGHT, SnakeState, create_initial_state, place_food, step_state


class SnakeLogicTests(unittest.TestCase):
    def test_initial_state_has_three_segments_and_food_not_on_snake(self):
        state = create_initial_state(width=12, height=12, seed=5)

        self.assertEqual(len(state.snake), 3)
        self.assertEqual(state.direction, RIGHT)
        self.assertNotIn(state.food, state.snake)

    def test_snake_moves_one_cell_forward(self):
        state = SnakeState(
            width=6,
            height=6,
            snake=((3, 3), (2, 3), (1, 3)),
            direction=RIGHT,
            food=(0, 0),
        )

        next_state = step_state(state)

        self.assertEqual(next_state.snake, ((4, 3), (3, 3), (2, 3)))
        self.assertEqual(next_state.score, 0)

    def test_snake_grows_and_scores_when_eating(self):
        state = SnakeState(
            width=6,
            height=6,
            snake=((3, 3), (2, 3), (1, 3)),
            direction=RIGHT,
            food=(4, 3),
        )

        next_state = step_state(state, rng=Random(7))

        self.assertEqual(next_state.snake, ((4, 3), (3, 3), (2, 3), (1, 3)))
        self.assertEqual(next_state.score, 1)
        self.assertNotIn(next_state.food, next_state.snake)

    def test_reverse_direction_is_ignored(self):
        state = SnakeState(
            width=6,
            height=6,
            snake=((3, 3), (2, 3), (1, 3)),
            direction=RIGHT,
            food=(0, 0),
        )

        next_state = step_state(state, requested_direction=LEFT)

        self.assertEqual(next_state.direction, RIGHT)
        self.assertEqual(next_state.snake[0], (4, 3))

    def test_wall_collision_sets_game_over(self):
        state = SnakeState(
            width=5,
            height=5,
            snake=((4, 2), (3, 2), (2, 2)),
            direction=RIGHT,
            food=(0, 0),
        )

        next_state = step_state(state)

        self.assertTrue(next_state.game_over)

    def test_body_collision_sets_game_over(self):
        state = SnakeState(
            width=6,
            height=6,
            snake=((3, 2), (3, 3), (2, 3), (2, 2), (2, 1), (3, 1)),
            direction=DOWN,
            food=(0, 0),
        )

        next_state = step_state(state)

        self.assertTrue(next_state.game_over)

    def test_place_food_uses_open_cells_only(self):
        snake = ((0, 0), (1, 0), (0, 1))

        food = place_food(2, 2, snake, Random(1))

        self.assertEqual(food, (1, 1))


if __name__ == "__main__":
    unittest.main()
