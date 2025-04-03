import numpy as np
import csv, itertools

class SudokuDataset:
    def __init__(self, filepath):
        """Initialize the dataset from the file path."""
        self.filepath = filepath


    def get_puzzle(self, row_number):
        with open(self.filepath) as csvfile:
            data = csv.DictReader(csvfile)
            line = next(itertools.islice(data, row_number, row_number + 1))

        puzzle_str = line['puzzle']
        solution_str = line['solution']

        # Convert strings to grids and return them
        return self.string_to_grid(puzzle_str), self.string_to_grid(solution_str)

    @staticmethod
    def string_to_grid(string):
        # Convert string to list of integers
        grid = np.array([int(char) for char in string], dtype=np.int8)

        # Reshape to 9x9 grid
        return grid.reshape(9, 9)