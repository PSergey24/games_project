import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np


pygame.init()
font = pygame.font.SysFont('arial', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    SPACE = 3
    NOTHING = 4


Point = namedtuple('Point', 'x0 x1 y0 y1')
PointBlocks = namedtuple('PointBlocks', 'x0 x1 y0 y1 live')
PointBall = namedtuple('PointBall', 'x0 y0 r')

WHITE = (255, 255, 255)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)

PINK = (255, 183, 255)
DARK_PINK = (255, 153, 255)

BLUE = (0, 140, 255)
DARK_BLUE = (0, 100, 155)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPACE_BETWEEN_BLOCKS = 2
GOAL_BLOCK_SIZE = BLOCK_SIZE * 2
SPEED = 40


class ArkanoidGameAI:

    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Arkanoid game')
        self.clock = pygame.time.Clock()

        self.blocks = []
        self.block_size = BLOCK_SIZE * 2

        self.edge_space_size = None
        self.row_block_count = None
        self.get_edge_space_size()

        self.racket_size = 60
        self.reset()

    def reset(self):
        self.direction = Direction.SPACE
        self.racket = Point((self.w / 2) - self.racket_size / 2, (self.w / 2) + self.racket_size / 2,
              self.h - 30 - BLOCK_SIZE, self.h - 30)

        self.ball_motion = False
        self.ball_speed_x = 0
        self.ball_speed_y = 0
        self.ball = PointBall((self.w / 2), self.racket.y0 - BLOCK_SIZE / 2, BLOCK_SIZE / 2)

        self.blocks.clear()
        self._place_blocks()

        self.score = 0
        self.reward = 0
        self.frame_iteration = 0

    def get_edge_space_size(self):
        self.row_block_count = self.w // (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS)
        self.edge_space_size = (self.w - (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) * self.row_block_count + SPACE_BETWEEN_BLOCKS) / 2

    def _place_blocks(self):
        for j in range(6, 6, 1):
            current_y_position = j * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS)
            current_x_position = self.edge_space_size
            while current_x_position < self.w - GOAL_BLOCK_SIZE - SPACE_BETWEEN_BLOCKS:
                self.blocks.append(PointBlocks(current_x_position, current_x_position + GOAL_BLOCK_SIZE,
                                         current_y_position, current_y_position + BLOCK_SIZE, random.randint(1,1)))
                current_x_position += GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS

        for i in range(8):
            x = random.randint(0, self.row_block_count - 1)
            y = random.randint(0, 5)
            item = PointBlocks(self.edge_space_size + x * (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS),
                         self.edge_space_size + x * (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) + GOAL_BLOCK_SIZE,
                         y * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS), y * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) + BLOCK_SIZE, random.randint(1,1))
            if item not in self.blocks:
                self.blocks.append(item)

    def play_step(self, action):
        self.frame_iteration += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        self.reward = 0
        self._move(action)
        game_over = self._ball_move(self.direction)

        if game_over is True:
            self.reward = -10

        if len(self.blocks) == 0:
            game_over = True
            self.reward += 30

        self._update_ui()
        self.clock.tick(SPEED)
        return self.reward, game_over, self.score

    def _move(self, action):
        # [nothing, start, right, left]

        clock_wise = [Direction.NOTHING, Direction.SPACE, Direction.RIGHT, Direction.LEFT]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        elif np.array_equal(action, [0, 0, 0, 1]):
            next_idx = (idx + 2) % 4
            new_dir = clock_wise[next_idx]
        else:
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        difference = 0
        if self.direction == Direction.RIGHT:
            difference += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            difference -= BLOCK_SIZE

        if self.is_racket_edge(difference) is True:
            self.racket = Point(self.racket.x0 + difference, self.racket.x1 + difference,
                                self.racket.y0,  self.racket.y1)
            if self.ball_motion is False:
                self.ball = PointBall(self.ball.x0 + difference, self.ball.y0, self.ball.r)

    def is_racket_edge(self, difference):
        x0, x1, y0, y1 = self.racket
        return True if self.w >= x1 + difference and x0 + difference >= 0 else False

    def _ball_move(self, direction):
        if direction == Direction.SPACE and self.ball_motion is False:
            self.ball_motion = True
            self.ball_speed_x = random.randint(-4, 4)
            self.ball_speed_y = random.randint(-3, -3)

        game_over = False
        if self.ball_motion is True:
            next_position = self.get_next_position()
            next_position, game_over = self.is_ball_edge(next_position)
            next_position = self.is_other_subject(next_position)
            self.ball = next_position

        return game_over

    def get_next_position(self):
        return PointBall(self.ball.x0 + self.ball_speed_x, self.ball.y0 + self.ball_speed_y, self.ball.r)

    def is_ball_edge(self, next_pos):
        gg = False

        if next_pos.x0 - next_pos.r <= 0:
            next_pos = PointBall(next_pos.r + abs(next_pos.x0 - next_pos.r), abs(next_pos.y0), next_pos.r)
            self.ball_speed_x *= -1

        elif next_pos.x0 + next_pos.r >= self.w:
            next_pos = PointBall(self.w - abs(next_pos.x0 + next_pos.r - self.w) - next_pos.r,
                             next_pos.y0, next_pos.r)
            self.ball_speed_x *= -1

        if next_pos.y0 - next_pos.r <= 0:
            next_pos = PointBall(abs(next_pos.x0), next_pos.r + abs(next_pos.y0 - next_pos.r), next_pos.r)
            self.ball_speed_y *= -1
        elif next_pos.y0 + next_pos.r >= self.h:
            gg = True
            next_pos = PointBall(next_pos.x0,
                                 self.h - abs(next_pos.y0 + next_pos.r - self.h) - next_pos.r, next_pos.r)
            self.ball_speed_y *= -1

        return next_pos, gg

    def is_other_subject(self, next_step):
        xDist, yDist = self.get_distance(next_step, self.racket)
        if self.is_collision(xDist, yDist, next_step) is True and self.ball_motion is True:
            side = self.get_side(xDist, yDist)
            k = self.get_coefficient(next_step)
            self.change_speed(side, is_racket=True, coefficient=k)
            self.reward += 10

        for i, item in enumerate(self.blocks):
            xDist, yDist = self.get_distance(next_step, item)
            if self.is_collision(xDist, yDist, next_step) is True:
                side = self.get_side(xDist, yDist)
                if item.live == 1:
                    self.blocks.pop(i)
                else:
                    self.blocks[i] = PointBlocks(item.x0, item.x1, item.y0, item.y1, item.live - 1)

                self.score += 1
                self.reward += 1
                self.change_speed(side)
                break
        return next_step

    def get_distance(self, ball, brick):
        brick_width = brick.x1 - brick.x0
        brick_height = brick.y1 - brick.y0
        xDist = self.calculate_distance(ball.x0, brick.x1 - brick_width / 2) - brick_width / 2
        yDist = self.calculate_distance(ball.y0, brick.y1 - brick_height / 2) - brick_height / 2
        return xDist, yDist

    @staticmethod
    def is_collision(xDist, yDist, ball):
        return True if xDist < ball.r and yDist < ball.r else False

    @staticmethod
    def calculate_distance(a, b):
        return abs(a-b)

    def get_side(self, xDist, yDist):
        if self.ball_speed_x < 0 and self.ball_speed_y < 0:
            if xDist < yDist:
                return "BOTTOM"
            elif xDist == yDist:
                return "CORNER"
            else:
                return "RIGHT"
        elif self.ball_speed_x < 0 and self.ball_speed_y >= 0:
            if xDist < yDist:
                return "TOP"
            elif xDist == yDist:
                return "CORNER"
            else:
                return "RIGHT"
        elif self.ball_speed_x >= 0 and self.ball_speed_y < 0:
            if xDist < yDist:
                return "BOTTOM"
            elif xDist == yDist:
                return "CORNER"
            else:
                return "LEFT"
        elif self.ball_speed_x >= 0 and self.ball_speed_y >= 0:
            if xDist < yDist:
                return "TOP"
            elif xDist == yDist:
                return "CORNER"
            else:
                return "LEFT"

    def get_coefficient(self, ball):
        return (ball.x0 - self.racket.x0) / (self.racket.x1 - self.racket.x0)

    def change_speed(self, side, is_racket=False, coefficient=None):
        if is_racket is False:
            if side == "RIGHT" or side == "LEFT":
                self.ball_speed_x *= (-1)
            else:
                self.ball_speed_y *= (-1)
        if is_racket is True:
            self.ball_speed_y *= (-1)
            if self.ball_speed_x > 0 and coefficient < 0.5 or self.ball_speed_x < 0 and coefficient >= 0.5:
                r = random.randint(-40, 40)
                self.ball_speed_x *= (-1) * abs((100 + r) / 100)

    def _update_ui(self):
        border_size = 2
        self.display.fill(WHITE)

        pygame.draw.rect(self.display, DARK_BLUE, pygame.Rect(self.racket.x0, self.racket.y0, self.racket.x1 - self.racket.x0, self.racket.y1 - self.racket.y0))
        pygame.draw.rect(self.display, BLUE, pygame.Rect(self.racket.x0 + border_size, self.racket.y0 + border_size,
                                                         self.racket.x1 - self.racket.x0 - border_size * 2, self.racket.y1 - self.racket.y0 - border_size * 2))
        pygame.draw.circle(self.display, DARK_RED, (round(self.ball.x0), round(self.ball.y0)), self.ball.r)

        for item in self.blocks:
            color = PINK
            d_color = DARK_PINK
            if item.live == 1:
                color = GREEN
                d_color = DARK_GREEN

            pygame.draw.rect(self.display, d_color, pygame.Rect(item.x0, item.y0, GOAL_BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, color, pygame.Rect(item.x0 + border_size, item.y0 + border_size,
                                                              GOAL_BLOCK_SIZE - border_size * 2,
                                                              BLOCK_SIZE - border_size * 2))

        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [5, self.h - 30])
        pygame.display.flip()
