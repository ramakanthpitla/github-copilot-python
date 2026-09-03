import pytest

import app
import sudoku_logic


@pytest.fixture(autouse=True)
def reset_current_game():
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.CURRENT['board'] = None
    app.CURRENT['hinted_cells'] = set()
    app.CURRENT['hints_used'] = 0
    yield
    app.CURRENT['puzzle'] = None
    app.CURRENT['solution'] = None
    app.CURRENT['board'] = None
    app.CURRENT['hinted_cells'] = set()
    app.CURRENT['hints_used'] = 0


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    with app.app.test_client() as test_client:
        yield test_client


def test_get_index_returns_game_page(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b"sudokuTheme" in response.data


def test_get_new_returns_puzzle_and_starts_game(client):
    response = client.get('/new')

    assert response.status_code == 200
    payload = response.get_json()
    puzzle = payload['puzzle']
    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert app.CURRENT['solution'] is not None


def test_post_new_preserves_existing_method_behavior(client):
    response = client.post('/new')

    assert response.status_code == 405


def test_post_check_with_valid_game_returns_no_incorrect_cells(client):
    client.get('/new')
    solution = app.CURRENT['solution']

    response = client.post('/check', json={'board': solution})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


def test_post_check_before_game_exists_returns_error(client):
    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_post_check_marks_incorrect_editable_entry(client):
    client.get('/new')
    board = sudoku_logic.deep_copy(app.CURRENT['puzzle'])
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if board[row][col] == sudoku_logic.EMPTY
    )
    board[row][col] = (app.CURRENT['solution'][row][col] % 9) + 1

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert [row, col] in response.get_json()['incorrect']


def test_post_check_ignores_empty_editable_cells(client):
    client.get('/new')

    response = client.post('/check', json={'board': app.CURRENT['puzzle']})

    assert response.status_code == 200
    assert response.get_json() == {'incorrect': []}


@pytest.mark.parametrize('board', [None, [], [[0] * 9] * 8])
def test_post_check_rejects_malformed_board(client, board):
    client.get('/new')

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_post_check_rejects_invalid_values(client):
    client.get('/new')
    board = sudoku_logic.deep_copy(app.CURRENT['puzzle'])
    row, col = next(
        (row, col)
        for row in range(sudoku_logic.SIZE)
        for col in range(sudoku_logic.SIZE)
        if board[row][col] == sudoku_logic.EMPTY
    )
    board[row][col] = 10

    response = client.post('/check', json={'board': board})

    assert response.status_code == 400


def test_post_hint_returns_correct_value_and_locks_one_cell(client):
    client.get('/new')
    puzzle = app.CURRENT['puzzle']
    solution = app.CURRENT['solution']

    response = client.post('/hint', json={'board': puzzle})

    assert response.status_code == 200
    hint = response.get_json()
    row, col = hint['row'], hint['col']
    assert hint['value'] == solution[row][col]
    assert (row, col) in app.CURRENT['hinted_cells']
    assert app.CURRENT['board'][row][col] == solution[row][col]
    assert hint['hints_used'] == 1
    assert sum(
        value != 0
        for row_values in app.CURRENT['board']
        for value in row_values
    ) == sum(value != 0 for row_values in puzzle for value in row_values) + 1


def test_hints_do_not_overwrite_clues_or_player_values(client):
    client.get('/new')
    board = sudoku_logic.deep_copy(app.CURRENT['puzzle'])
    player_cell = next(
        (row, col)
        for row in range(9)
        for col in range(9)
        if board[row][col] == 0
    )
    board[player_cell[0]][player_cell[1]] = 1
    clue_cell = next(
        (row, col)
        for row in range(9)
        for col in range(9)
        if app.CURRENT['puzzle'][row][col] != 0
    )

    first = client.post('/hint', json={'board': board}).get_json()
    assert tuple(player_cell) != (first['row'], first['col'])
    assert tuple(clue_cell) != (first['row'], first['col'])


def test_multiple_hints_use_different_cells_and_count_resets(client):
    client.get('/new')
    first = client.post('/hint').get_json()
    second = client.post('/hint').get_json()

    assert (first['row'], first['col']) != (second['row'], second['col'])
    assert second['hints_used'] == 2

    client.get('/new')
    assert app.CURRENT['hints_used'] == 0
    assert app.CURRENT['hinted_cells'] == set()


def test_hint_with_no_empty_cells_is_safe(client):
    client.get('/new')
    app.CURRENT['board'] = sudoku_logic.deep_copy(app.CURRENT['solution'])

    response = client.post('/hint')

    assert response.status_code == 200
    assert response.get_json() == {
        'hint': None,
        'hints_used': 0,
        'message': 'No empty editable cells remain.',
    }


def test_hint_before_game_exists_is_safe(client):
    response = client.post('/hint')

    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_hint_rejects_malformed_board(client):
    client.get('/new')

    response = client.post('/hint', json={'board': []})

    assert response.status_code == 400
    assert 'error' in response.get_json()


def test_check_preserves_server_tracked_hint(client):
    client.get('/new')
    hint = client.post('/hint').get_json()
    board = sudoku_logic.deep_copy(app.CURRENT['board'])
    board[hint['row']][hint['col']] = 0

    response = client.post('/check', json={'board': board})

    assert response.status_code == 200
    assert app.CURRENT['board'][hint['row']][hint['col']] == hint['value']
