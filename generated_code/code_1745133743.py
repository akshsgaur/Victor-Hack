import sys

# First, let's check if the required library 'pygame' is installed
# This library is necessary for creating a graphical interface for the chess game
try:
    import pygame
    from pygame.locals import *
except ImportError:
    print("pygame is not installed. Please install it by running 'pip install pygame' in your terminal.")
    sys.exit()

try:
    import numpy as np
except ImportError:
    print("numpy is not installed. Please install it by running 'pip install numpy' in your terminal.")
    sys.exit()

# Initialize pygame
pygame.init()

# Constants for the game
BOARD_SIZE = 8
SQUARE_SIZE = 60
WINDOW_SIZE = BOARD_SIZE * SQUARE_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
FPS = 30

# Set up the display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('Chess')
clock = pygame.time.Clock()

# Load images
def load_images():
    pieces = ["R", "N", "B", "Q", "K", "P"]
    colors = ["w", "b"]
    images = {}
    for piece in pieces:
        for color in colors:
            try:
                images[color + piece] = pygame.transform.scale(pygame.image.load(f"assets/{color}{piece}.png"), (SQUARE_SIZE, SQUARE_SIZE))
            except pygame.error as e:
                print(f"Error loading image assets/{color}{piece}.png: {e}")
                sys.exit()
    return images

# Initialize the chess board
def init_board():
    # Using an 8x8 matrix to represent the board
    # Empty squares are represented by '.', white pieces by 'w', and black pieces by 'b'
    board = np.array([
        ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
        ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        [".", ".", ".", ".", ".", ".", ".", "."],
        ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
        ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    ])
    return board

# Draw the board and pieces
def draw_board(screen, board, images):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            piece = board[row][col]
            if piece != ".":
                screen.blit(images[piece], pygame.Rect(col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

# Main game loop
def main():
    images = load_images()
    board = init_board()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

        draw_board(screen, board, images)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
        pygame.quit()
        sys.exit()