from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
<<<<<<< HEAD
    'solution': None,
    'difficulty': None,
    'board': None,
    'hinted_cells': set(),
    'hints_used': 0,
=======
    'solution': None
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
<<<<<<< HEAD
    difficulty = request.args.get('difficulty')
    if difficulty is not None and difficulty not in sudoku_logic.DIFFICULTY_CLUES:
        valid_difficulties = ', '.join(sudoku_logic.DIFFICULTY_CLUES)
        return jsonify({
            'error': (
                f"Invalid difficulty '{difficulty}'. "
                f'Expected one of: {valid_difficulties}.'
            )
        }), 400

    if difficulty is None:
        clues = int(request.args.get('clues', 35))
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        current_difficulty = 'medium' if clues == sudoku_logic.DIFFICULTY_CLUES['medium'] else None
    else:
        puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)
        current_difficulty = difficulty

    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = current_difficulty
    CURRENT['board'] = sudoku_logic.deep_copy(puzzle)
    CURRENT['hinted_cells'] = set()
    CURRENT['hints_used'] = 0
    return jsonify({'puzzle': puzzle, 'difficulty': current_difficulty})


@app.route('/hint', methods=['POST'])
def use_hint():
    if CURRENT.get('solution') is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = CURRENT['board']
    if isinstance(data, dict) and 'board' in data:
        board = data['board']
    try:
        sudoku_logic.validate_board(board)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    for row, col in CURRENT['hinted_cells']:
        board[row][col] = CURRENT['solution'][row][col]

    hint = sudoku_logic.apply_hint(
        board,
        CURRENT['puzzle'],
        CURRENT['solution'],
        CURRENT['hinted_cells'],
    )
    CURRENT['board'] = board
    if hint is None:
        return jsonify({
            'hint': None,
            'hints_used': CURRENT['hints_used'],
            'message': 'No empty editable cells remain.',
        })

    CURRENT['hinted_cells'].add((hint['row'], hint['col']))
    CURRENT['hints_used'] += 1
    return jsonify({**hint, 'hints_used': CURRENT['hints_used']})

@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or 'board' not in data:
        return jsonify({'error': 'Request must include a board.'}), 400
    board = data['board']
    try:
        sudoku_logic.validate_board(board)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    for row, col in CURRENT['hinted_cells']:
        board[row][col] = CURRENT['solution'][row][col]
    CURRENT['board'] = board

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if CURRENT['puzzle'][i][j] == sudoku_logic.EMPTY and (
                board[i][j] != sudoku_logic.EMPTY
                and board[i][j] != solution[i][j]
            ):
=======
    clues = int(request.args.get('clues', 35))
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
>>>>>>> 8dc0113ed48f050354faa18de11c2047da621ea0
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)