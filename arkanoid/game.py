import pygame
import random
from enum import Enum
from collections import namedtuple

pygame.init()
font = pygame.font.SysFont('arial', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    LUNCH = 5


Point = namedtuple('Point', 'x0 x1 y0 y1')

WHITE = (255, 255, 255)
RED = (200, 0, 0)
DARK_RED = (150, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
BLUE = (0, 140, 255)
DARK_BLUE = (0, 100, 155)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPACE_BETWEEN_BLOCKS = 2
GOAL_BLOCK_SIZE = BLOCK_SIZE * 2
SPEED = 20


class ArkanoidGame:

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

        self.racket_size = 100
        self.reset()

    def reset(self):
        self.direction = None
        self.racket = Point((self.w / 2) - self.racket_size / 2, (self.w / 2) + self.racket_size / 2,
              self.h - 30, self.h - 30 - BLOCK_SIZE)
        self.ball = Point((self.w / 2) - BLOCK_SIZE / 2, (self.w / 2) + BLOCK_SIZE / 2,
              self.h - 30 - BLOCK_SIZE, self.h - 30 - BLOCK_SIZE * 2)
        self.blocks.clear()
        self.score = 0
        self._place_blocks()
        self.frame_iteration = 0

    def get_edge_space_size(self):
        self.row_block_count = self.w // (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS)
        self.edge_space_size = (self.w - (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) * self.row_block_count + SPACE_BETWEEN_BLOCKS) / 2

    def _place_blocks(self):
        for j in range(6, 8, 1):
            current_y_position = j * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS)
            current_x_position = self.edge_space_size
            while current_x_position < self.w - GOAL_BLOCK_SIZE - SPACE_BETWEEN_BLOCKS:
                self.blocks.append(Point(current_x_position, current_x_position + GOAL_BLOCK_SIZE,
                                         current_y_position, current_y_position + BLOCK_SIZE))
                current_x_position += GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS

        for i in range(25):
            x = random.randint(0, self.row_block_count - 1)
            y = random.randint(0, 5)
            item = Point(self.edge_space_size + x * (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS),
                         self.edge_space_size + x * (GOAL_BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) + GOAL_BLOCK_SIZE,
                         y * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS), y * (BLOCK_SIZE + SPACE_BETWEEN_BLOCKS) + BLOCK_SIZE)
            if item not in self.blocks:
                self.blocks.append(item)

    def play_step(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT

        self._move(self.direction)
        self._update_ui()

        self.direction = None
        self.clock.tick(SPEED)
        return False, self.score

    def _move(self, direction):
        difference = 0
        if direction == Direction.RIGHT:
            difference += BLOCK_SIZE
        elif direction == Direction.LEFT:
            difference -= BLOCK_SIZE

        if self.is_edge(difference) is True:
            self.racket = Point(self.racket.x0 + difference, self.racket.x1 + difference,
                                self.racket.y0,  self.racket.y1)

    def is_edge(self, difference):
        x0, x1, y0, y1 = self.racket
        return True if self.w >= x1 + difference and x0 + difference >= 0 else False

    def _update_ui(self):
        self.display.fill(WHITE)

        border_size = 2
        pygame.draw.rect(self.display, DARK_BLUE, pygame.Rect(self.racket.x0, self.racket.y0,
                                                         self.racket.x1 - self.racket.x0,
                                                         self.racket.y0 - self.racket.y1))
        pygame.draw.rect(self.display, BLUE, pygame.Rect(self.racket.x0 + border_size, self.racket.y0 + border_size,
                                                         self.racket.x1 - self.racket.x0 - border_size * 2,
                                                         self.racket.y0 - self.racket.y1 - border_size * 2))

        pygame.draw.rect(self.display, DARK_RED, pygame.Rect(self.ball.x0, self.ball.y0, BLOCK_SIZE, BLOCK_SIZE), border_radius=8)
        pygame.draw.rect(self.display, RED, pygame.Rect(self.ball.x0 + 1, self.ball.y0 + 1,
                                                        BLOCK_SIZE - 1 * 2, BLOCK_SIZE - 1 * 2), border_radius=8)

        for item in self.blocks:
            pygame.draw.rect(self.display, DARK_GREEN, pygame.Rect(item.x0, item.y0, GOAL_BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, GREEN, pygame.Rect(item.x0 + border_size, item.y0 + border_size,
                                                              GOAL_BLOCK_SIZE - border_size * 2,
                                                              BLOCK_SIZE - border_size * 2))

        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [5, self.h - 30])
        pygame.display.flip()


if __name__ == '__main__':
    game = ArkanoidGame()

    while True:
        game_over, score = game.play_step()
        if game_over is True:
            break

    print('Score: ', score)
    pygame.quit()