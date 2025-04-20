import pygame
import time
import random

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Snake Game")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)

# Snake initial position and size
snake_block = 10
snake_speed = 15
snake_list = []
snake_length = 1

# Snake direction
direction = "RIGHT"

# Score
score = 0

# Food position
food_x = round(random.randrange(0, screen_width - snake_block) / 10.0) * 10.0
food_y = round(random.randrange(0, screen_height - snake_block) / 10.0) * 10.0

# Function to draw snake on the screen
def draw_snake(snake_block, snake_list):
    for x in snake_list:
        pygame.draw.rect(screen, green, [x[0], x[1], snake_block, snake_block])

# Main game loop
game_over = False
clock = pygame.time.Clock()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                direction = "LEFT"
            elif event.key == pygame.K_RIGHT:
                direction = "RIGHT"
            elif event.key == pygame.K_UP:
                direction = "UP"
            elif event.key == pygame.K_DOWN:
                direction = "DOWN"

    if direction == "LEFT":
        snake_head = [snake_list[0][0] - snake_block, snake_list[0][1]]
    elif direction == "RIGHT":
        snake_head = [snake_list[0][0] + snake_block, snake_list[0][1]]
    elif direction == "UP":
        snake_head = [snake_list[0][0], snake_list[0][1] - snake_block]
    elif direction == "DOWN":
        snake_head = [snake_list[0][0], snake_list[0][1] + snake_block]

    snake_list.insert(0, snake_head)
    if snake_list[0][0] == food_x and snake_list[0][1] == food_y:
        score += 1
        food_x = round(random.randrange(0, screen_width - snake_block) / 10.0) * 10.0
        food_y = round(random.randrange(0, screen_height - snake_block) / 10.0) * 10.0
    else:
        snake_list.pop()

    screen.fill(black)
    pygame.draw.rect(screen, red, [food_x, food_y, snake_block, snake_block])
    draw_snake(snake_block, snake_list)

    # Game over conditions
    if snake_list[0][0] < 0 or snake_list[0][0] >= screen_width or snake_list[0][1] < 0 or snake_list[0][1] >= screen_height:
        game_over = True
    for block in snake_list[1:]:
        if block == snake_list[0]:
            game_over = True

    pygame.display.update()
    clock.tick(snake_speed)

pygame.quit()