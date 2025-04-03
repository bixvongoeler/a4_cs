import numpy as np

class SudokuSolver:
    def __init__(self, grid):
        self.grid = grid
        self.domains = self.init_domains()

        # For step-by-step solving
        self.stack = []
        self.current_cell = None
        self.solving_finished = False
        self.solution_found = False

    def init_domains(self):
        domains = {}

        # For each cell in the grid
        for i in range(9):
            for j in range(9):
                if self.grid[i, j] == 0:
                    domains[(i, j)] = self.get_valid_values(i, j)

        return domains

    def get_valid_values(self, row, col):
        # all possible
        valid_values = set(range(1, 10))

        # Remove values row
        for j in range(9):
            if self.grid[row, j] != 0:
                valid_values.discard(self.grid[row, j])

        # Remove values column
        for i in range(9):
            if self.grid[i, col] != 0:
                valid_values.discard(self.grid[i, col])

        # Remove values box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i, j] != 0:
                    valid_values.discard(self.grid[i, j])

        return valid_values

    def is_valid_assignment(self, row, col, value):
        # Check row constraint
        for j in range(9):
            if self.grid[row, j] == value:
                return False

        # Check column constraint
        for i in range(9):
            if self.grid[i, col] == value:
                return False

        # Check 3x3 box constraint
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i, j] == value:
                    return False

        return True

    def select_unassigned_variable(self):
        # Find all unassigned cells
        unassigned = [(i, j) for i in range(9) for j in range(9) if self.grid[i, j] == 0]

        if not unassigned:
            return None  # All cells are assigned

        # Use MRV
        min_remaining_values = float('inf')
        mrv_cells = []

        for cell in unassigned:
            num_values = len(self.domains.get(cell, set()))
            if num_values < min_remaining_values:
                min_remaining_values = num_values
                mrv_cells = [cell]
            elif num_values == min_remaining_values:
                mrv_cells.append(cell)

        if len(mrv_cells) == 1:
            return mrv_cells[0]

        # cell with most constraints on other cells
        max_degree = -1
        selected_cell = None

        for cell in mrv_cells:
            degree = self.count_constraints(cell)
            if degree > max_degree:
                max_degree = degree
                selected_cell = cell

        return selected_cell

    def count_constraints(self, cell):
        row, col = cell
        constrained_cells = set()

        # Cells in row
        for j in range(9):
            if j != col and self.grid[row, j] == 0:
                constrained_cells.add((row, j))

        # Cells in column
        for i in range(9):
            if i != row and self.grid[i, col] == 0:
                constrained_cells.add((i, col))

        # Cells in box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.grid[i, j] == 0:
                    constrained_cells.add((i, j))

        return len(constrained_cells)

    def forward_checking(self, var, value):
        row, col = var
        affected_domains = {}

        # Save current domain
        for j in range(9):
            if j != col and self.grid[row, j] == 0:
                affected_domains[(row, j)] = self.domains.get((row, j), set()).copy()

        # Cells in column
        for i in range(9):
            if i != row and self.grid[i, col] == 0:
                affected_domains[(i, col)] = self.domains.get((i, col), set()).copy()

        # Cells in box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.grid[i, j] == 0:
                    affected_domains[(i, j)] = self.domains.get((i, j), set()).copy()

        # remove the value from dom of affected cells
        for cell in affected_domains:
            if cell in self.domains:
                self.domains[cell].discard(value)

        for cell, domain in self.domains.items():
            if not domain:
                for cell, old_domain in affected_domains.items():
                    self.domains[cell] = old_domain
                return False, affected_domains

        return True, affected_domains

    def start_solving(self):
        # Reset state
        self.stack = []
        self.solving_finished = False
        self.solution_found = False

        # Select the first cell to try
        self.current_cell = self.select_unassigned_variable()

        if self.current_cell is None:
            # Puzzle is already solved
            if self.check_is_solved():
                self.solving_finished = True
                self.solution_found = True
            else:
                print("No solution found on init.")
                return
        else:
            row, col = self.current_cell
            self.stack.append({
                'cell': self.current_cell,
                'domain': sorted(list(self.domains.get(self.current_cell, set()))),
                'index': 0,
                'old_domains': {}
            })

    def step(self):
        """Perform one step in the solving process."""
        if self.solving_finished:
            return

        if not self.stack:
            # No more cells to try, backtracking has failed
            self.solving_finished = True
            self.solution_found = False
            return

        # Get the current cell from the top of the stack
        current = self.stack[-1]
        row, col = current['cell']
        domain = current['domain']
        index = current['index']

        if index >= len(domain):
            # We've tried all values for this cell, backtrack
            self.grid[row, col] = 0  # Clear the cell
            self.stack.pop()  # Remove this cell from the stack

            # Restore domains from the previous step
            if self.stack:
                prev_cell = self.stack[-1]
                if 'old_domains' in prev_cell:
                    for cell, domain in prev_cell['old_domains'].items():
                        self.domains[cell] = domain

            # Update current cell
            self.current_cell = self.stack[-1]['cell'] if self.stack else None
            return

        # Try the next value
        value = domain[index]
        current['index'] += 1  # Move to the next value for next time

        if not self.is_valid_assignment(row, col, value):
            # This value is not valid, try the next one
            return

        # Assign the value
        self.grid[row, col] = value

        # Apply forward checking
        valid, affected_domains = self.forward_checking(current['cell'], value)

        if not valid:
            self.grid[row, col] = 0
            return

        # Save the affected domains for backtracking
        current['old_domains'] = affected_domains

        # Select the next cell to try
        next_cell = self.select_unassigned_variable()

        if next_cell is None:
            # All cells are assigned, puzzle is solved
            self.solving_finished = True
            self.solution_found = True
            return

        # Push the next cell onto the stack
        self.stack.append({
            'cell': next_cell,
            'domain': sorted(list(self.domains.get(next_cell, set()))),
            'index': 0,
            'old_domains': {}
        })

        # Update the current cell
        self.current_cell = next_cell

    def get_current_cell(self):
        """Get the current cell being considered."""
        return self.current_cell

    def is_finished(self):
        """Check if the solving process is finished."""
        return self.solving_finished

    def is_solved(self):
        """Check if a solution was found."""
        return self.solution_found

    def get_solution(self):
        """Return the current grid (solution if found)."""
        return self.grid

    def check_is_solved(self):
        for row in self.grid:
            values = set(range(1, 10))
            for cell in row:
                if cell in values:
                    values.discard(cell)
            if len(values) != 0:
                return False

        for col in self.grid:
            values = set(range(1, 10))
            for cell in col:
                if cell in values:
                    values.discard(cell)
            if len(values) != 0:
                return False

        # Check boxes
        for box_row in range(0,9,3):
            for box_col in range(0,9,3):
                values = set(range(1, 10))
                for row_idx in range(0,3):
                    for col_idx in range(0,3):
                        if self.grid[box_row + row_idx][box_col + col_idx] in values:
                            values.discard(self.grid[box_row + row_idx][box_col + col_idx])
                if len(values) != 0:
                    return False

        # Return True if Solved
        return True

