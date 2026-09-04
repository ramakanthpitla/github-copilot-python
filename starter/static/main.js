// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuGameLeaderboardV1';
const THEME_STORAGE_KEY = 'sudokuTheme';
const VALID_DIFFICULTIES = new Set(['easy', 'medium', 'hard']);
const VALID_THEMES = new Set(['light', 'dark']);
let puzzle = [];
const hintedCells = new Set();
let timerIntervalId = null;
let elapsedSeconds = 0;
let currentDifficulty = 'medium';
let completionRecorded = false;
let completionPending = false;

function getStoredTheme() {
  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    return VALID_THEMES.has(storedTheme) ? storedTheme : null;
  } catch (error) {
    return null;
  }
}

function setTheme(theme, persist = true) {
  const nextTheme = VALID_THEMES.has(theme) ? theme : 'light';
  document.documentElement.dataset.theme = nextTheme;
  const toggle = document.getElementById('theme-toggle');
  const isDark = nextTheme === 'dark';
  toggle.setAttribute('aria-pressed', String(isDark));
  toggle.setAttribute(
    'aria-label',
    `Dark mode is ${isDark ? 'on' : 'off'}. Switch to ${isDark ? 'light' : 'dark'} mode`
  );
  toggle.innerText = isDark ? 'Light Mode' : 'Dark Mode';
  if (persist) {
    try {
      window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
    } catch (error) {
      // Storage failures do not prevent changing the current page theme.
    }
  }
}

function sanitizeLeaderboardEntries(value) {
  if (!Array.isArray(value)) return [];
  return value.reduce((entries, entry) => {
    if (!entry || typeof entry !== 'object') return entries;
    const name = typeof entry.name === 'string' ? entry.name.trim() : '';
    const time = entry.time;
    const hints = entry.hints;
    if (
      !name || name.length > 40 ||
      !Number.isSafeInteger(time) || time < 0 ||
      !VALID_DIFFICULTIES.has(entry.difficulty) ||
      !Number.isSafeInteger(hints) || hints < 0
    ) return entries;
    entries.push({name, time, difficulty: entry.difficulty, hints});
    return entries;
  }, []).sort(compareLeaderboardEntries).slice(0, 10);
}

function compareLeaderboardEntries(first, second) {
  return first.time - second.time ||
    first.name.localeCompare(second.name) ||
    first.difficulty.localeCompare(second.difficulty) ||
    first.hints - second.hints;
}

function loadLeaderboard() {
  try {
    const stored = window.localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    return sanitizeLeaderboardEntries(stored ? JSON.parse(stored) : []);
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(entries) {
  try {
    window.localStorage.setItem(
      LEADERBOARD_STORAGE_KEY,
      JSON.stringify(sanitizeLeaderboardEntries(entries))
    );
  } catch (error) {
    // Private browsing and storage quotas must not stop the game.
  }
}

function renderLeaderboard() {
  const body = document.getElementById('leaderboard-body');
  const emptyMessage = document.getElementById('leaderboard-empty');
  const entries = loadLeaderboard();
  body.innerHTML = '';
  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    [index + 1, entry.name, formatElapsedTime(entry.time),
      entry.difficulty, entry.hints].forEach((value) => {
      const cell = document.createElement('td');
      cell.innerText = value;
      row.appendChild(cell);
    });
    body.appendChild(row);
  });
  emptyMessage.hidden = entries.length > 0;
}

function recordCompletedGame() {
  if (completionRecorded) return;
  const nameInput = document.getElementById('player-name');
  const name = nameInput.value.trim();
  if (!name) {
    completionPending = true;
    document.getElementById('submit-score').hidden = false;
    nameInput.required = true;
    nameInput.focus();
    document.getElementById('message').innerText =
      'Enter your name to add your score to the leaderboard.';
    return;
  }
  const entries = loadLeaderboard();
  entries.push({
    name,
    time: elapsedSeconds,
    difficulty: currentDifficulty,
    hints: Number(document.getElementById('hint-count').dataset.count || 0),
  });
  saveLeaderboard(entries);
  completionRecorded = true;
  completionPending = false;
  document.getElementById('submit-score').hidden = true;
  renderLeaderboard();
}

function formatElapsedTime(seconds) {
  const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
  const remainingSeconds = (seconds % 60).toString().padStart(2, '0');
  return `${minutes}:${remainingSeconds}`;
}

function updateTimer() {
  document.getElementById('game-timer').innerText =
    `Time: ${formatElapsedTime(elapsedSeconds)}`;
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimer();
  timerIntervalId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimer();
  }, 1000);
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.inputMode = 'numeric';
      input.autocomplete = 'off';
      input.className = 'sudoku-cell';
      input.classList.add(
        (Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 0 ? 'box-even' : 'box-odd'
      );
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      input.dataset.row = i;
      input.dataset.col = j;
      input.setAttribute('aria-describedby', 'message');
      input.addEventListener('input', (e) => {
        handleCellInput(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function readBoard() {
  const inputs = document.querySelectorAll('.sudoku-cell');
  return Array.from({length: SIZE}, (_, row) =>
    Array.from({length: SIZE}, (_, col) => {
      const value = inputs[row * SIZE + col].value;
      return value ? Number(value) : 0;
    })
  );
}

function isBoardComplete(board) {
  return board.every((row) => row.every((value) => value !== 0));
}

function getConflictKeys(board) {
  const conflicts = new Set();
  const markDuplicates = (positions) => {
    const values = new Map();
    positions.forEach(([row, col]) => {
      const value = board[row][col];
      if (value) {
        if (!values.has(value)) values.set(value, []);
        values.get(value).push(`${row}-${col}`);
      }
    });
    values.forEach((keys) => {
      if (keys.length > 1) keys.forEach((key) => conflicts.add(key));
    });
  };
  for (let index = 0; index < SIZE; index++) {
    markDuplicates(Array.from({length: SIZE}, (_, offset) => [index, offset]));
    markDuplicates(Array.from({length: SIZE}, (_, offset) => [offset, index]));
  }
  for (let boxRow = 0; boxRow < SIZE; boxRow += 3) {
    for (let boxCol = 0; boxCol < SIZE; boxCol += 3) {
      markDuplicates(Array.from({length: 9}, (_, index) => [
        boxRow + Math.floor(index / 3), boxCol + index % 3
      ]));
    }
  }
  return conflicts;
}

function updateValidationMessage(conflictCount) {
  const message = document.getElementById('message');
  if (conflictCount) {
    message.className = 'error-message';
    message.innerText = `${conflictCount} conflicting cell${conflictCount === 1 ? '' : 's'}.`;
  } else if (message.className === 'error-message') {
    message.className = '';
    message.innerText = '';
  }
}

function refreshConflicts() {
  const board = readBoard();
  const conflicts = getConflictKeys(board);
  document.querySelectorAll('.sudoku-cell:not(:disabled)').forEach((input) => {
    const key = `${input.dataset.row}-${input.dataset.col}`;
    const isConflict = conflicts.has(key);
    const isInvalid = input.classList.contains('invalid-input');
    input.classList.toggle('conflict', isConflict);
    input.setAttribute('aria-invalid', isConflict || isInvalid ? 'true' : 'false');
    input.title = isConflict
      ? 'Conflicting value'
      : isInvalid ? 'Enter a number from 1 to 9, or leave this cell empty.' : '';
  });
  updateValidationMessage(conflicts.size);
}

function handleCellInput(input) {
  const value = input.value;
  if (value && !/^[1-9]$/.test(value)) {
    input.value = '';
    input.classList.add('invalid-input');
    input.setAttribute('aria-invalid', 'true');
    input.title = 'Enter a number from 1 to 9, or leave this cell empty.';
  } else {
    input.classList.remove('invalid-input');
  }
  refreshConflicts();
}

function renderPuzzle(puz) {
  puzzle = puz;
  hintedCells.clear();
  completionRecorded = false;
  completionPending = false;
  document.getElementById('submit-score').hidden = true;
  document.getElementById('player-name').required = false;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
        inp.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}, given clue ${val}`);
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  stopTimer();
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (!res.ok) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  currentDifficulty = data.difficulty;
  document.getElementById('current-difficulty').innerText =
    `Difficulty: ${data.difficulty}`;
  document.getElementById('message').innerText = '';
  const hintCount = document.getElementById('hint-count');
  hintCount.dataset.count = '0';
  hintCount.innerText = 'Hints used: 0';
  startTimer();
}

async function useHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (!res.ok) {
    msg.innerText = data.error;
    return;
  }
  const hintCount = document.getElementById('hint-count');
  hintCount.dataset.count = data.hints_used;
  hintCount.innerText = `Hints used: ${data.hints_used}`;
  if (data.hint === null) {
    msg.innerText = data.message;
    return;
  }
  const key = `${data.row}-${data.col}`;
  const input = document.querySelector(
    `.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`
  );
  input.value = data.value;
  input.disabled = true;
  input.classList.add('hinted');
  input.setAttribute('aria-label', `${input.getAttribute('aria-label')}, hinted`);
  hintedCells.add(key);
  msg.innerText = `Hint filled row ${data.row + 1}, column ${data.col + 1}.`;
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  refreshConflicts();
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
      inp.setAttribute('aria-invalid', 'true');
      inp.title = 'Incorrect value';
    } else {
      inp.classList.remove('incorrect');
      if (!inp.classList.contains('conflict') && !inp.classList.contains('invalid-input')) {
        inp.setAttribute('aria-invalid', 'false');
      }
    }
  }
  if (incorrect.size === 0 && isBoardComplete(board)) {
    stopTimer();
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
    recordCompletedGame();
  } else if (incorrect.size === 0) {
    msg.className = '';
    msg.innerText = 'No incorrect entries. Complete the remaining cells.';
  } else {
    msg.className = 'error-message';
    msg.style.color = '#d32f2f';
    msg.innerText = `${incorrect.size} incorrect cell${incorrect.size === 1 ? '' : 's'}.`;
  }
}

// Wire buttons
window.addEventListener('load', () => {
  setTheme(getStoredTheme() || document.documentElement.dataset.theme || 'light', false);
  document.getElementById('theme-toggle').addEventListener('click', () => {
    const currentTheme = document.documentElement.dataset.theme || 'light';
    setTheme(currentTheme === 'dark' ? 'light' : 'dark');
  });
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', useHint);
  document.getElementById('submit-score').addEventListener('click', () => {
    if (completionPending) {
      recordCompletedGame();
      if (completionRecorded) {
        document.getElementById('message').innerText =
          'Congratulations! Your score was added to the leaderboard.';
      }
    }
  });
  renderLeaderboard();
  // initialize
  newGame();
});