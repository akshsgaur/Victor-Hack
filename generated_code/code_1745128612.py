import sys

# First, let's check if the required library 'pygame' is installed
try:
    import pygame
    import random
except ImportError:
    print("pygame is not installed. Please install it using 'pip install pygame'")
    sys.exit(1)

# Initialize pygame
pygame.init()

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Set the size of the window
size = (600, 400)
screen = pygame.display.set_mode(size)

pygame.display.set_caption("Snake Game")

# Loop until the user clicks the close button
done = False

# Used to manage how fast the screen updates
clock = pygame.time.Clock()

# Snake initial position
snake_pos = [100, 50]

# Snake body
snake_body = [[100, 50], [90, 50], [80, 50]]

# Food position
food_pos = [random.randrange(1, (size[0]//10)) * 10, random.randrange(1, (size[1]//10)) * 10]
food_spawn = True

# Direction control
direction = 'RIGHT'
change_to = direction

# Initial speed
speed = 15

# Score
score = 0

# Function to show the score
def show_score(choice, color, font, font_size):
    score_font = pygame.font.SysFont(font, font_size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (size[0]/10, 15)
    else:
        score_rect.midtop = (size[0]/2, size[1]/1.25)
    screen.blit(score_surface, score_rect)

# Main game loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != 'DOWN':
                change_to = 'UP'
            if event.key == pygame.K_DOWN and direction != 'UP':
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT and direction != 'RIGHT':
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT and direction != 'LEFT':
                change_to = 'RIGHT'
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Validate direction
    direction = change_to

    # Move the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    elif direction == 'DOWN':
        snake_pos[1] += 10
    elif direction == 'LEFT':
        snake_pos[0] -= 10
    elif direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos == food_pos:
        score += 1
        food_spawn = False
    else:
        snake_body.pop()

    if not food_spawn:
        food_pos = [random.randrange(1, (size[0]//10)) * 10, random.randrange(1, (size[1]//10)) * 10]
    food_spawn = True

    # Background
    screen.fill(BLACK)

    # Draw snake
    for pos in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    # Draw food
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Game Over conditions
    if snake_pos[0] < 0 or snake_pos[0] > size[0]-10 or snake_pos[1] < 0 or snake_pos[1] > size[1]-10:
        done = True
    for block in snake_body[1:]:
        if snake_pos == block:
            done = True

    show_score(1, WHITE, 'times new roman', 20)

    pygame.display.flip()

    clock.tick(speed)

# Game Over
pygame.quit()
sys.exit()