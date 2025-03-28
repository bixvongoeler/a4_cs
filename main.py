import numpy as np
import pygame
import sys
import csv
from SudokuDataset import SudokuDataset

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 540, 540
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
FONT_SIZE = 36

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")

# Create a font for rendering numbers
font = pygame.font.SysFont(None, FONT_SIZE)

SudokuDataset = SudokuDataset('puzzles/sudoku.csv')

# Sample Sudoku grid as a numpy array (0 represents empty cells)
sudoku_grid, solution = SudokuDataset.get_puzzle(0)

def draw_grid():
    """Draw the Sudoku grid and its numbers on the screen"""
    # Fill the background with white
    screen.fill(WHITE)

    # Draw cells and numbers
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            # Draw cell borders
            pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

            # Draw the numbers (if cell is not empty)
            if sudoku_grid[i][j] != 0:
                number = font.render(str(sudoku_grid[i][j]), True, BLACK)
                # Center the number in the cell
                number_rect = number.get_rect(center=(j * CELL_SIZE + CELL_SIZE // 2,
                                                      i * CELL_SIZE + CELL_SIZE // 2))
                screen.blit(number, number_rect)

    # Draw thick lines to separate 3x3 boxes
    for i in range(0, GRID_SIZE + 1, 3):
        # Horizontal lines
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE), 3)
        # Vertical lines
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT), 3)

def main():
    """Main game loop"""
    # Run until the user asks to quit
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Draw the grid
        draw_grid()

        # Update the display
        pygame.display.update()

    # Clean up
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()