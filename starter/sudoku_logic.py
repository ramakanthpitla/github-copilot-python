import copy
import random

SIZE = 9
EMPTY = 0
<<<<<<< HEAD
MAX_GENERATION_ATTEMPTS = 20
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

=======
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0

def deep_copy(board):
    return copy.deepcopy(board)

<<<<<<< HEAD

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def validate_board(board, allow_empty=True):
    """Raise ``ValueError`` when ``board`` is not a valid Sudoku grid."""
    if not isinstance(board, list) or len(board) != SIZE:
        raise ValueError('Board must contain exactly 9 rows.')
    for row in board:
        if not isinstance(row, list) or len(row) != SIZE:
            raise ValueError('Each board row must contain exactly 9 values.')
        for value in row:
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError('Board values must be integers from 1 to 9.')
            minimum = EMPTY if allow_empty else 1
            if value < minimum or value > SIZE:
                expected = '0 to 9' if allow_empty else '1 to 9'
                raise ValueError(f'Board values must be integers from {expected}.')


def find_conflicts(board):
    """Return coordinates involved in row, column, or box duplicates."""
    validate_board(board)
    conflicts = set()

    def mark_duplicate_groups(groups):
        for group in groups:
            positions = {}
            for row, col in group:
                value = board[row][col]
                if value != EMPTY:
                    positions.setdefault(value, []).append((row, col))
            for duplicate_positions in positions.values():
                if len(duplicate_positions) > 1:
                    conflicts.update(duplicate_positions)

    mark_duplicate_groups(
        [[(row, col) for col in range(SIZE)] for row in range(SIZE)]
    )
    mark_duplicate_groups(
        [[(row, col) for row in range(SIZE)] for col in range(SIZE)]
    )
    mark_duplicate_groups(
        [
            [
                (row, col)
                for row in range(box_row, box_row + 3)
                for col in range(box_col, box_col + 3)
            ]
            for box_row in range(0, SIZE, 3)
            for box_col in range(0, SIZE, 3)
        ]
    )
    return sorted([list(position) for position in conflicts])


=======
def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]

>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

<<<<<<< HEAD

def _find_empty_cell(board):
    """Return the empty cell with the fewest possible candidates."""
    best_cell = None
    best_candidates = None
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = [
                num for num in range(1, SIZE + 1)
                if is_safe(board, row, col, num)
            ]
            if not candidates:
                return (row, col), []
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates
    return best_cell, best_candidates or []


def _has_valid_givens(board):
    """Return whether all non-empty values obey Sudoku constraints."""
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value not in range(1, SIZE + 1):
                return False
            board[row][col] = EMPTY
            valid = is_safe(board, row, col, value)
            board[row][col] = value
            if not valid:
                return False
    return True


def count_solutions(board, limit=2):
    """Count solutions, stopping once ``limit`` solutions are found.

    The default result is therefore 0, 1, or 2, where 2 means at least two
    solutions. The input board is restored before this function returns.
    """
    if limit < 1:
        return 0
    if not _has_valid_givens(board):
        return 0

    def search():
        cell, candidates = _find_empty_cell(board)
        if cell is None:
            return 1
        if not candidates:
            return 0

        row, col = cell
        solutions = 0
        for candidate in candidates:
            board[row][col] = candidate
            solutions += search()
            board[row][col] = EMPTY
            if solutions >= limit:
                return limit
        return solutions

    return search()


def solve_board(board):
    """Return one valid solution for ``board`` or ``None`` if unsolvable."""
    if not _has_valid_givens(board):
        return None
    solved_board = deep_copy(board)

    def search():
        cell, candidates = _find_empty_cell(solved_board)
        if cell is None:
            return True
        if not candidates:
            return False

        row, col = cell
        for candidate in candidates:
            solved_board[row][col] = candidate
            if search():
                return True
            solved_board[row][col] = EMPTY
        return False

    return solved_board if search() else None


def apply_hint(current_board, puzzle, solution, hinted_cells=None):
    """Fill and return one empty editable cell, or ``None`` if unavailable."""
    validate_board(current_board)
    validate_board(puzzle)
    validate_board(solution, allow_empty=False)
    hinted_cells = hinted_cells or set()

    for row in range(SIZE):
        for col in range(SIZE):
            position = (row, col)
            if (
                puzzle[row][col] == EMPTY
                and current_board[row][col] == EMPTY
                and position not in hinted_cells
            ):
                current_board[row][col] = solution[row][col]
                return {
                    'row': row,
                    'col': col,
                    'value': solution[row][col],
                }
    return None


=======
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True

<<<<<<< HEAD

=======
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    while attempts > 0:
        row = random.randrange(SIZE)
        col = random.randrange(SIZE)
        if board[row][col] != EMPTY:
            board[row][col] = EMPTY
            attempts -= 1

<<<<<<< HEAD

def _generate_unique_puzzle(solution, clues):
    """Remove as many cells as possible while preserving one solution."""
    puzzle = deep_copy(solution)
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)
    target_empty = SIZE * SIZE - clues

    for row, col in positions:
        if target_empty <= 0:
            break
        original = puzzle[row][col]
        puzzle[row][col] = EMPTY
        if count_solutions(puzzle) != 1:
            puzzle[row][col] = original
        else:
            target_empty -= 1
    return puzzle


def generate_puzzle(clues=35, difficulty=None):
    """Generate a uniquely solvable puzzle for a clue count or difficulty."""
    if isinstance(clues, str) and difficulty is None:
        difficulty = clues
        clues = 35
    if difficulty is not None:
        if difficulty not in DIFFICULTY_CLUES:
            valid_difficulties = ', '.join(DIFFICULTY_CLUES)
            raise ValueError(
                f"Invalid difficulty '{difficulty}'. "
                f"Expected one of: {valid_difficulties}."
            )
        clues = DIFFICULTY_CLUES[difficulty]

    clues = max(0, min(SIZE * SIZE, clues))
    best_puzzle = None
    best_solution = None

    for _ in range(MAX_GENERATION_ATTEMPTS):
        solution = create_empty_board()
        fill_board(solution)
        puzzle = _generate_unique_puzzle(solution, clues)
        clue_count = sum(cell != EMPTY for row in puzzle for cell in row)
        best_clue_count = (
            sum(cell != EMPTY for row in best_puzzle for cell in row)
            if best_puzzle is not None else SIZE * SIZE + 1
        )
        if clue_count < best_clue_count:
            best_puzzle = puzzle
            best_solution = solution
        if clue_count == clues:
            break

    unique_solution = solve_board(best_puzzle)
    return best_puzzle, unique_solution
=======
def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
