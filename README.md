# NYT Pips Solver

A Python-based solver for the New York Times Pips game with a web-based interface. Features include:

- **Fetch & Solve**: Automatically fetch the current NYT Pips puzzle and find ALL solutions
- **Visualize Solutions**: Interactive HTML/SVG visualization of puzzles and solutions
- **Generate Puzzles**: Procedurally generate random Pips puzzles with configurable difficulty
- **Web Interface**: Flask backend with interactive web frontend

## Project Structure

```
├── puzzle_model.py       # Core data structures (Puzzle, Domino, Region, PuzzleState)
├── solver.py             # Constraint-satisfaction solver with backtracking
├── nyt_fetcher.py        # Fetch puzzles from NYT (Phase 2)
├── generator.py          # Procedural puzzle generation (Phase 3)
├── app.py                # Flask backend (Phase 4)
├── templates/            # HTML templates (Phase 5)
├── static/               # CSS and JavaScript (Phase 5)
└── requirements.txt      # Python dependencies
```

## Installation

1. Create a conda environment or virtual environment:
   ```bash
   conda create -n pips-solver python=3.11
   conda activate pips-solver
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Tests
```bash
python -m unittest test_solver -v
```

### Starting the Web Server (Phase 4+)
```bash
python app.py
```

Then open your browser to `http://localhost:5000`

## Development Status

- [x] **Phase 1**: Core Solver Engine - ✅ Complete
  - ✅ Puzzle data model (Puzzle, Region, Domino classes)
  - ✅ Constraint-satisfaction solver with backtracking
  - ✅ Unit tests for all components
  - ✅ All-solutions finding capability
  
- [x] **Phase 2**: Puzzle Parsing & Fetching - ✅ Complete
  - ✅ JSON puzzle parser (read/write)
  - ✅ NYT fetcher with optional browser automation support
  - ✅ Local puzzle caching system
  - ✅ Comprehensive tests (12 tests passing)
  - ✅ Example usage script
  
- [ ] **Phase 3**: Procedural Generation
  - [ ] Random region generator
  - [ ] Puzzle generation pipeline
  - [ ] Difficulty scaling
  
- [ ] **Phase 4**: Flask Backend API
  - [ ] Create Flask app structure
  - [ ] Implement API endpoints
  - [ ] Add data persistence
  
- [ ] **Phase 5**: Frontend UI
  - [ ] HTML structure and SVG rendering
  - [ ] Interactive controls
  - [ ] Solution gallery
  
- [ ] **Phase 6**: Integration & Testing

## Architecture

### Solver Algorithm
- **Backtracking**: Depth-first search with constraint validation
- **Early Pruning**: Region sum constraints are checked after each placement
- **All-Solutions**: Finds and returns all valid solutions for a puzzle

### Data Model
- `Domino`: Represents a single domino (two pip values 0-6)
- `Region`: A cage/region with a target sum constraint
- `Puzzle`: Complete puzzle state with grid and regions
- `PuzzleState`: Current placement state during solving

## Notes for Contributors

- The solver uses a standard double-6 domino set (28 total dominoes)
- Dominoes can span region boundaries
- Each domino occupies exactly 2 adjacent cells (horizontally or vertically)
- All solutions satisfy all region sum constraints and use all required dominoes
