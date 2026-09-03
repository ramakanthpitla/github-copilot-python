# Sudoku Project Instructions

## Project Goal

Refactor the existing Flask Sudoku application into a clean,
maintainable, responsive, accessible and user-friendly Sudoku game.

The existing application is legacy code. Preserve working functionality
while incrementally improving the architecture and adding the required
features.

## Technology

Use:

- Python 3
- Flask
- HTML5
- CSS3
- JavaScript
- Browser localStorage
- pytest for testing

Avoid unnecessary dependencies.

## Python Coding Standards

- Follow PEP 8.
- Use clear and descriptive names.
- Prefer small, focused and reusable functions.
- Use type hints where they improve readability.
- Add docstrings to important functions.
- Avoid unnecessary global state.
- Avoid duplicated logic.
- Handle errors gracefully.
- Keep Sudoku logic separate from Flask route handling.
- Keep frontend presentation separate from backend Sudoku logic.
- Prefer readable code over clever code.

## Sudoku Logic

The application must:

- Generate valid 9x9 Sudoku puzzles.
- Generate a complete valid Sudoku solution.
- Guarantee that every generated puzzle has exactly one solution.
- Support Easy, Medium and Hard difficulty levels.
- Adjust the number of prefilled cells according to difficulty.
- Keep prefilled cells locked.
- Validate user entries.
- Detect invalid/conflicting entries.
- Provide a correct hint.
- Lock cells filled by hints.
- Detect when the puzzle has been solved correctly.

## Difficulty

Difficulty levels should have clearly different numbers of
prefilled cells:

- Easy: most prefilled cells
- Medium: fewer prefilled cells
- Hard: fewest prefilled cells

Every difficulty must still produce a puzzle with exactly one solution.

## Backend Architecture

Keep Flask routes thin.

Sudoku generation, solving, validation and puzzle-management logic
should be implemented in reusable functions or modules rather than
being embedded directly inside Flask routes.

Use appropriate HTTP status codes and meaningful error responses.

## Frontend Architecture

Use semantic HTML and maintainable JavaScript.

Prefer event delegation where appropriate instead of attaching
unnecessary individual event handlers.

Keep UI logic separate from data-management logic.

## Required Game Features

The final application must include:

1. Difficulty selector:
   - Easy
   - Medium
   - Hard

2. New Game button.

3. Timer that tracks solving time.

4. Check button that highlights incorrect entries.

5. Immediate feedback when a user enters an invalid value.

6. Hint button:
   - fills one correct empty cell
   - visually identifies the hinted cell
   - locks the hinted cell
   - tracks the number of hints used

7. Completion message when the puzzle is solved.

8. Top 10 leaderboard containing:
   - player name
   - completion time
   - difficulty
   - number of hints

9. Save leaderboard data using browser localStorage so scores
   persist across page refreshes and browser sessions.

10. Dark/light mode toggle.

## User Interface

The interface must:

- Look good in both light and dark modes.
- Work on desktop and mobile devices.
- Scale smoothly between viewport sizes.
- Keep controls readable and usable.
- Use alternating visual styles for the 3x3 Sudoku boxes.
- Clearly distinguish:
  - prefilled cells
  - user-entered cells
  - incorrect cells
  - hinted cells
  - selected/focused cells

Avoid layout shifts when cell states change.

## Accessibility

Follow WCAG 2.1 AA principles where practical.

Use:

- semantic HTML
- accessible button labels
- visible keyboard focus
- sufficient color contrast
- appropriate ARIA attributes when needed
- labels or accessible names for controls
- keyboard-friendly interactions

Do not rely on color alone to communicate important information.

## Responsive Design

Use responsive CSS.

The Sudoku board and controls must remain usable on:

- desktop
- tablet
- mobile

Do not allow the board to overflow the viewport unnecessarily.

## Testing

Use pytest for backend tests.

Tests should cover:

- board creation
- valid Sudoku generation
- Sudoku solving
- unique solution validation
- difficulty behavior
- puzzle generation
- input validation
- hint behavior
- completion behavior
- Flask routes and error handling

Run the tests before and after significant changes.

Do not remove existing tests merely to make them pass.

## Error Handling

Handle invalid requests gracefully.

Examples include:

- no active game
- malformed board data
- invalid cell values
- invalid difficulty
- invalid board dimensions

Return useful error messages without exposing unnecessary
implementation details.

## Copilot Guidelines

When suggesting code changes:

1. Inspect the existing implementation first.
2. Explain the proposed approach before making major changes.
3. Prefer incremental refactoring.
4. Avoid unrelated changes.
5. Preserve working behavior unless a requirement requires changing it.
6. Do not introduce unnecessary dependencies.
7. Consider edge cases.
8. Prefer reusable functions.
9. Explain potentially risky changes.
10. Do not assume generated code is correct without testing it.

When multiple approaches are possible, explain the trade-offs.

## Development Process

Follow this order when practical:

1. Establish baseline tests.
2. Confirm baseline tests pass.
3. Refactor Sudoku logic.
4. Guarantee unique puzzle solutions.
5. Add difficulty levels.
6. Add validation and immediate feedback.
7. Add hints.
8. Add timer.
9. Add leaderboard/localStorage.
10. Improve UI and responsive design.
11. Add dark/light mode.
12. Improve accessibility.
13. Add and run regression tests.
14. Update documentation.

After each significant change, run the relevant tests.

## Code Review

Before considering a feature complete, verify:

- The implementation satisfies the requirement.
- Existing functionality still works.
- Tests pass.
- Error cases are handled.
- The implementation is understandable and maintainable.

Do not blindly accept AI-generated code. Evaluate the suggested
implementation and modify or reject it when necessary.