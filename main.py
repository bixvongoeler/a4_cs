import pygame
import sys
from Solver import SudokuSolver
from SudokuDataset import SudokuDataset
import argparse
import random

# create an ArgumentParser object
parser = argparse.ArgumentParser()

# add arguments
parser.add_argument("-s", "--speed", default=15, type=int, help="Millisecond Delay Between Solve Steps (default 15)")
parser.add_argument("-p", "--puzzle",  default="evil", help="Puzzle to solve: [easy | evil | rand] (default evil)")

# parse the arguments
args = parser.parse_args()

# initialize Pygame
pygame.init()

# constants
WIDTH, HEIGHT = 540, 540
GRID_SIZE = 9
CELL_SIZE = WIDTH // GRID_SIZE
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
BLUE = (0, 0, 150)
HIGHLIGHT = (255, 240, 200)  # Light yellow for highlighting current cell
FONT_SIZE = 36
SOLVING_DELAY = args.speed  # Milliseconds delay between solver steps

if args.puzzle == "easy":
    FILENAME = 'puzzles/sudoku_small.csv'
    PUZZLE = 0
elif args.puzzle == "evil":
    FILENAME = 'puzzles/sudoku_small.csv'
    PUZZLE = 1
elif args.puzzle == "rand":
    FILENAME = 'puzzles/sudoku_10k.csv'
    PUZZLE = random.randrange(0, 9999)
else:
    raise ValueError("Invalid Puzzle")

# Create the window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku Solver")

# Create a font for rendering numbers
font = pygame.font.SysFont(None, FONT_SIZE)

# Load puzzle dataset
SudokuDataset = SudokuDataset(FILENAME)

# Sudoku grid as a numpy array
og_grid, solution = SudokuDataset.get_puzzle(PUZZLE)
sudoku_grid = og_grid

# For solving animation
solver = None
solving = False
solve_step_timer = 0


def draw_grid():
    # Fill the background with white
    screen.fill(WHITE)

    # Draw cells and numbers
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            # Check if this is the current cell being considered by the solver
            is_current_cell = False
            if solving and solver:
                current_cell = solver.get_current_cell()
                if current_cell and current_cell[0] == i and current_cell[1] == j:
                    is_current_cell = True
                    # Highlight the current cell
                    pygame.draw.rect(screen, HIGHLIGHT, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

            # Draw cell borders
            pygame.draw.rect(screen, GRAY, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

            # Draw the numbers (if cell is not empty)
            if sudoku_grid[i][j] != 0:
                if og_grid[i][j] != 0:  # Check if the cell is from the original puzzle
                    color = BLACK
                else:
                    color = BLUE  # Dark blue for solved cells
                number = font.render(str(sudoku_grid[i][j]), True, color)
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


def start_solving():
    """Start the step-by-step solving process."""
    global solving, solver

    # Create a new solver with the current grid
    solver = SudokuSolver(sudoku_grid.copy())

    # Start the solving process
    solver.start_solving()

    # Set the solving flag
    solving = True


def update_solving_state():
    """Update the solving state and grid."""
    global solving, sudoku_grid, solve_step_timer

    if not solving or not solver:
        return

    # Check if it's time for the next step
    current_time = pygame.time.get_ticks()
    if current_time - solve_step_timer >= SOLVING_DELAY:
        # perform one step of the solving process
        solver.step()

        # update the grid from the solver
        sudoku_grid = solver.get_solution().copy()

        # check if solving is finished
        if solver.is_finished():
            solving = False
            if solver.is_solved():
                print("Puzzle solved!")
            else:
                print("No solution found.")

        solve_step_timer = current_time


def main():
    global solving, solve_step_timer

    # run until quit
    running = True
    while running:
        # handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not solving:
                    start_solving()
                    solve_step_timer = pygame.time.get_ticks()

        update_solving_state()
        draw_grid()

        # update display
        pygame.display.update()
        pygame.time.delay(10)

    # exit
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()