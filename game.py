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
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLACK = (0,0,0)

BLOCK_SIZE = 20
SPEED = 800
BOARD_SIZE = (640, 480)

class SnakeGameAI:

    def __init__(self, w=BOARD_SIZE[0], h=BOARD_SIZE[1]):
        self.w = w
        self.h = h
        self.speed = SPEED
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        # Name of the game window.
        pygame.display.set_caption('Snake')
        # Ticking.
        self.clock = pygame.time.Clock()
        # First start init.
        self.reset()
        # Failed attempt to preventing it from colliding with itself.
        #self.reward = 0


    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        # re-initialize starting speed.
        self.speed = SPEED

        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0


    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        #reward = self.reward
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 50*len(self.snake):
            game_over = True
            #reward = self.reward
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            if self.speed > 50:
                self.speed -= 10
            #reward = self.reward
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)
        # Failed attempt to prevent the snake from biting itself. reset reward.
        #self.reward = 0
        # 6. return game over and score
        return reward, game_over, self.score


    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # if it hits the screen boundary.
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Does the snake bites itself.
        if pt in self.snake[1:]:
            # A failed attemp to stop it from colliding with itself.
            #self.reward -= 1
            return True

        return False

    #Render. (Draw to the screen and update the frame.)
    def _update_ui(self):
        self.display.fill(WHITE)
        tone_b = 255
        tone_r = 0
        tone_g = 0

        for pt in self.snake:
            # Make the snake change its color when it gets longer.
            if tone_b > 10:
                tone_b -= 10
            if tone_r <= 245:
                tone_r += 10
            else:
                if tone_g <145:
                    tone_g += 10
            pygame.draw.rect(self.display, (0,0+tone_g,tone_b), 
                             pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, (tone_r, 100+tone_g, 255), 
                             pygame.Rect(pt.x+4, pt.y+4, BLOCK_SIZE*3/5, BLOCK_SIZE*3/5))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))
        # Score text.
        text = font.render("Score: " + str(self.score), True, BLACK)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)