import pytest

import sudoku_logic


UNIQUE_PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def assert_valid_board(board):
    expected = set(range(1, sudoku_logic.SIZE + 1))

    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(set(row) == expected for row in board)
    assert all(
        set(board[row][col] for row in range(sudoku_logic.SIZE)) == expected
        for col in range(sudoku_logic.SIZE)
    )
    assert all(
        {
            board[row][col]
            for row in range(box_row, box_row + 3)
            for col in range(box_col, box_col + 3)
        }
        == expected
        for box_row in range(0, sudoku_logic.SIZE, 3)
        for box_col in range(0, sudoku_logic.SIZE, 3)
    )


def test_create_empty_board_returns_9_by_9_zero_board():
    board = sudoku_logic.create_empty_board()

    assert board == [[0] * sudoku_logic.SIZE for _ in range(sudoku_logic.SIZE)]


def test_is_safe_rejects_row_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 0, 1, 5) is False


def test_is_safe_rejects_column_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 1, 0, 5) is False


def test_is_safe_rejects_box_conflict():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5

    assert sudoku_logic.is_safe(board, 1, 1, 5) is False


def test_is_safe_accepts_candidate_without_conflict():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.is_safe(board, 0, 0, 5) is True


def test_validate_board_accepts_empty_cells_and_valid_values():
    sudoku_logic.validate_board(sudoku_logic.create_empty_board())


@pytest.mark.parametrize('value', [-1, 10, '5', True])
def test_validate_board_rejects_invalid_values(value):
    board = sudoku_logic.create_empty_board()
    board[0][0] = value

    with pytest.raises(ValueError):
        sudoku_logic.validate_board(board)


def test_find_conflicts_marks_row_column_and_box_duplicates():
    board = sudoku_logic.create_empty_board()
    board[0][0] = 5
    board[0][1] = 5
    board[1][0] = 5
    board[1][1] = 5

    assert sudoku_logic.find_conflicts(board) == [
        [0, 0], [0, 1], [1, 0], [1, 1]
    ]


def test_fill_board_creates_complete_valid_board():
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.fill_board(board) is True
    assert_valid_board(board)


def test_generate_puzzle_returns_expected_dimensions_and_clue_count():
    clues = 35

    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert_valid_board(solution)
    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == clues
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_count_solutions_identifies_unique_puzzle():
    assert sudoku_logic.count_solutions(UNIQUE_PUZZLE) == 1


def test_count_solutions_stops_at_multiple_solutions():
    assert sudoku_logic.count_solutions(sudoku_logic.create_empty_board()) == 2


def test_count_solutions_rejects_puzzle_with_conflicting_givens():
    puzzle = sudoku_logic.create_empty_board()
    puzzle[0][0] = 5
    puzzle[0][1] = 5

    assert sudoku_logic.count_solutions(puzzle) == 0


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sudoku_logic.solve_board(puzzle) == solution


def test_generated_solution_solves_generated_puzzle():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_difficulty_levels_have_different_clue_counts():
    puzzles = {
        difficulty: sudoku_logic.generate_puzzle(difficulty=difficulty)
        for difficulty in sudoku_logic.DIFFICULTY_CLUES
    }
    clue_counts = {
        difficulty: sum(
            cell != sudoku_logic.EMPTY
            for row in puzzle
            for cell in row
        )
        for difficulty, (puzzle, _) in puzzles.items()
    }

    assert clue_counts == sudoku_logic.DIFFICULTY_CLUES
    assert clue_counts['easy'] > clue_counts['medium']
    assert clue_counts['medium'] > clue_counts['hard']


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_each_difficulty_generates_a_unique_puzzle(difficulty):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    assert sudoku_logic.count_solutions(puzzle) == 1
    assert sudoku_logic.solve_board(puzzle) == solution
    assert all(
        puzzle[row][col] in (sudoku_logic.EMPTY, solution[row][col])
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
    )


def test_generate_puzzle_accepts_difficulty_as_first_argument():
    puzzle, _ = sudoku_logic.generate_puzzle('easy')

    assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == (
        sudoku_logic.DIFFICULTY_CLUES['easy']
    )


def test_generate_puzzle_rejects_invalid_difficulty():
    with pytest.raises(ValueError, match='Invalid difficulty'):
        sudoku_logic.generate_puzzle(difficulty='expert')
