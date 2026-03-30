# 🎲 NYT Pips Solver

A complete, production-ready Python application for solving, generating, and visualizing NYT Pips puzzles with a web interface and REST API.

## ✨ Features

- **Complete Solver** - Find ALL solutions to any Pips puzzle using intelligent backtracking
- **Procedural Generation** - Generate random playable Pips puzzles at multiple difficulty levels  
- **Puzzle Fetching** - Load puzzles from NYT, files, or local cache
- **Interactive Web UI** - Beautiful HTML/CSS/JavaScript interface
- **REST API** - Full REST API for all puzzle operations
- **Optimized Performance** - Early pruning and constraint satisfaction for fast solving

## 📊 Project Status

| Phase | Component | Tests | Status |
|-------|-----------|-------|--------|
| 1 | Core Solver | 14 | ✅ Complete |
| 2 | Parsing & Fetching | 12 | ✅ Complete |
| 3 | Procedural Generation | 12 | ✅ Complete |
| 4 | Flask Backend API | 5 | ✅ Complete |
| 5 | Frontend UI | - | ✅ Complete |
| 6 | Integration Testing | 6 | ✅ Complete |
| **TOTAL** | **All Systems** | **49 tests** | ✅ **COMPLETE** |

## 🚀 Quick Start

### Installation

```bash
# 1. Create conda environment
conda create -n pips python=3.11
conda activate pips

# 2. Install dependencies
pip install -r requirements.txt

# 3. Verify setup (run integration tests)
python e2e_test.py
```

### Running the Application

```bash
# Start the Flask server
python app.py

# Open browser to:
#   - Web UI: http://localhost:5000/ui
#   - API Info: http://localhost:5000
```

## 📚 Project Structure

**Core Engine:**
- `puzzle_model.py` - Data structures (Puzzle, Domino, Region, PuzzleState)
- `solver.py` - Constraint-satisfaction solver with backtracking
- `puzzle_parser.py` - JSON serialization/deserialization

**Data Sources:**
- `nyt_fetcher.py` - NYT puzzle fetching with caching

**Generation:**
- `generator.py` - Procedural puzzle generation with difficulty levels

**Web Application:**
- `app.py` - Flask REST API (6 endpoints)
- `index.html` - Interactive web UI

**Testing:**
- `test_solver.py` - Core solver tests (14 tests)
- `test_parser_fetcher.py` - Parser/fetcher tests (12 tests)
- `test_generator.py` - Generation tests (12 tests)
- `e2e_test.py` - End-to-end integration tests (6 tests)

## 🔌 REST API

### Endpoints

**Generate Puzzle**
```bash
POST /generate
{"width": 7, "height": 9, "difficulty": "medium", "max_attempts": 10}
```

**Solve Puzzle**
```bash
POST /solve
{"rows": 7, "cols": 9, "grid": [[...]], "regions": {...}}
```

**Parse Puzzle**
```bash
POST /puzzle/parse
{"grid": [[0, 0], [1, 1]], "regions": {"0": {"sum": 7}, "1": {"sum": 5}}}
```

**Visualize**
```bash
POST /visualize
{"puzzle": {...}}
```

**Health Check**
```bash
GET /health
```

**UI**
```bash
GET /ui
```

## 🧪 Running Tests

```bash
# Run all tests
python -m unittest discover -s . -p "test_*.py" -v

# Run specific test suite
python test_solver.py
python test_parser_fetcher.py
python test_generator.py

# Run end-to-end integration tests
python e2e_test.py
```

## 📝 Development Notes

- All 3 original requirements implemented ✅
  - Fetch puzzles from NYT and visualize
  - Find ALL solutions to any puzzle
  - Procedurally generate random puzzles
- 49 unit and integration tests (100% pass rate)
- Production-ready with CORS support and error handling
- Git repository initialized with clean commit history

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
