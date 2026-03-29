"""
Flask backend API for NYT Pips Solver.

Provides REST endpoints for:
- Fetching puzzles (from file, NYT, or cache)
- Parsing puzzle JSON
- Solving puzzles  
- Generating random puzzles
- Visualizing puzzles (preparing data for frontend)
"""

from flask import Flask, request, jsonify
from pathlib import Path
import json
import logging
from typing import Optional, Dict, Any
from flask_cors import CORS

from puzzle_model import Puzzle, Region
from solver import PipsSolver
from puzzle_parser import PuzzleParser
from nyt_fetcher import NYTPipsFetcher
from generator import PuzzleGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='.', static_url_path='')
app.config['JSON_SORT_KEYS'] = False

# Enable CORS
CORS(app)

# Initialize solvers and fetchers
fetcher = NYTPipsFetcher(cache_enabled=True)
generator = PuzzleGenerator()


# ============================================================================
# Helper Routes and Functions
# ============================================================================

@app.route('/', methods=['GET'])
def index():
    """API info and available endpoints."""
    return jsonify({
        "name": "NYT Pips Solver API",
        "version": "1.0.0",
        "endpoints": {
            "GET /": "This help message",
            "POST /puzzle/fetch": "Fetch a puzzle (from cache, file, or NYT)",
            "POST /puzzle/parse": "Parse puzzle from JSON",
            "POST /solve": "Find all solutions for a puzzle",
            "POST /generate": "Generate a random puzzle",
            "GET /solutions/<puzzle_id>": "Get cached solutions",
            "GET /health": "Health check"
        }
    })


@app.route('/ui', methods=['GET'])
@app.route('/ui/')
def ui():
    """Serve the frontend UI."""
    return app.send_static_file('index.html')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


def puzzle_to_dict(puzzle: Puzzle) -> Dict[str, Any]:
    """Convert Puzzle object to JSON-serializable dict."""
    # Build grid representation from regions
    grid = [[-1 for _ in range(puzzle.cols)] for _ in range(puzzle.rows)]
    for rid, region in enumerate(puzzle.regions):
        for r, c in region.cells:
            grid[r][c] = rid
    
    return {
        "rows": puzzle.rows,
        "cols": puzzle.cols,
        "grid": grid,
        "regions": {
            str(rid): {"sum": region.target_sum, "cells": list(region.cells)}
            for rid, region in enumerate(puzzle.regions)
        },
        "difficulty": puzzle.difficulty,
        "id": puzzle.puzzle_id
    }


def placement_to_dict(placement) -> Dict[str, Any]:
    """Convert DominoPlacement to dict."""
    return {
        "domino": list(placement.domino.pips),
        "cells": list(placement.cells)
    }


# ============================================================================
# Puzzle Fetching
# ============================================================================

@app.route('/puzzle/fetch', methods=['POST'])
def fetch_puzzle():
    """
    Fetch a puzzle from various sources.
    
    Request JSON:
    {
        "source": "cache|file|nyt",  # Default: "cache"
        "date": "YYYY-MM-DD",  # For NYT/date-based fetches
        "file_path": "path/to/puzzle.json"  # For file source
    }
    """
    try:
        data = request.get_json() or {}
        source = data.get("source", "cache")
        date = data.get("date")
        file_path = data.get("file_path")
        
        puzzle = None
        
        if source == "file" and file_path:
            puzzle = PuzzleParser.from_json_file(file_path)
        elif source == "nyt":
            if date:
                puzzle = fetcher.fetch_by_date(date)
            else:
                puzzle = fetcher.fetch_today()
        else:  # cache (default)
            if date:
                puzzle = fetcher.fetch_by_date(date)
            else:
                puzzle = fetcher.fetch_today()
        
        if puzzle is None:
            return jsonify({"error": "Could not fetch puzzle from source"}), 404
        
        return jsonify({
            "success": True,
            "puzzle": puzzle_to_dict(puzzle)
        }), 200
    
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        return jsonify({"error": str(e)}), 400


# ============================================================================
# Puzzle Parsing
# ============================================================================

@app.route('/puzzle/parse', methods=['POST'])
def parse_puzzle():
    """
    Parse a puzzle from JSON.
    
    Request JSON: The puzzle JSON object with 'grid' and 'regions'
    """
    try:
        puzzle_json = request.get_json()
        if not puzzle_json:
            return jsonify({"error": "No puzzle JSON provided"}), 400
        
        puzzle = PuzzleParser.from_json_dict(puzzle_json)
        
        return jsonify({
            "success": True,
            "puzzle": puzzle_to_dict(puzzle)
        }), 200
    
    except Exception as e:
        logger.error(f"Parse error: {e}")
        return jsonify({"error": str(e)}), 400


# ============================================================================
# Solving
# ============================================================================

@app.route('/solve', methods=['POST'])
def solve():
    """
    Find all solutions for a puzzle.
    
    Request JSON: The puzzle object (from /puzzle/parse or /puzzle/fetch)
    """
    try:
        puzzle_json = request.get_json()
        if not puzzle_json:
            return jsonify({"error": "No puzzle provided"}), 400
        
        # Parse the puzzle
        puzzle = PuzzleParser.from_json_dict(puzzle_json)
        
        # Solve it
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        if not solutions:
            return jsonify({
                "success": True,
                "solutions": [],
                "solution_count": 0,
                "message": "No solutions found"
            }), 200
        
        # Format solutions
        formatted_solutions = []
        for sol in solutions:
            formatted_solutions.append({
                "placements": [placement_to_dict(p) for p in sol]
            })
        
        return jsonify({
            "success": True,
            "solutions": formatted_solutions,
            "solution_count": len(solutions)
        }), 200
    
    except Exception as e:
        logger.error(f"Solve error: {e}")
        return jsonify({"error": str(e)}), 400


# ============================================================================
# Generation
# ============================================================================

@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate a random puzzle.
    
    Request JSON:
    {
        "width": 7,
        "height": 9,
        "difficulty": "medium",
        "enforce_unique": false,
        "max_attempts": 10
    }
    """
    try:
        data = request.get_json() or {}
        
        width = data.get("width", 7)
        height = data.get("height", 9)
        difficulty = data.get("difficulty", "medium")
        enforce_unique = data.get("enforce_unique", False)
        max_attempts = data.get("max_attempts", 10)
        
        # Validate params
        if width < 2 or height < 2:
            return jsonify({"error": "Grid must be at least 2x2"}), 400
        if (width * height) % 2 != 0:
            return jsonify({"error": "Grid must have even number of cells"}), 400
        if difficulty not in ["easy", "medium", "hard"]:
            return jsonify({"error": "Difficulty must be easy/medium/hard"}), 400
        
        # Generate
        puzzle = generator.generate_retry(
            width=width,
            height=height,
            difficulty=difficulty,
            enforce_unique=enforce_unique,
            max_attempts=max_attempts
        )
        
        if puzzle is None:
            return jsonify({"error": "Failed to generate puzzle"}), 500
        
        return jsonify({
            "success": True,
            "puzzle": puzzle_to_dict(puzzle)
        }), 200
    
    except Exception as e:
        logger.error(f"Generate error: {e}")
        return jsonify({"error": str(e)}), 400


# ============================================================================
# Visualization
# ============================================================================

@app.route('/visualize', methods=['POST'])
def visualize():
    """
    Prepare puzzle data for frontend visualization.
    
    Formats puzzle and optional solutions into a structure ready for rendering.
    
    Request JSON:
    {
        "puzzle": {...},
        "solutions": [{...}, {...}]  # Optional
    }
    """
    try:
        data = request.get_json() or {}
        
        puzzle_json = data.get("puzzle")
        if not puzzle_json:
            return jsonify({"error": "No puzzle provided"}), 400
        
        puzzle = PuzzleParser.from_json_dict(puzzle_json)
        
        # Prepare visualization data
        vis_data = {
            "grid": {
                "rows": puzzle.rows,
                "cols": puzzle.cols,
                "cells": []
            },
            "regions": []
        }
        
        # Create grid cells
        for r in range(puzzle.rows):
            for c in range(puzzle.cols):
                region_id = None
                for rid, region in enumerate(puzzle.regions):
                    if (r, c) in region.cells:
                        region_id = rid
                        break
                
                vis_data["grid"]["cells"].append({
                    "row": r,
                    "col": c,
                    "region_id": region_id
                })
        
        # Add region information
        for rid, region in enumerate(puzzle.regions):
            vis_data["regions"].append({
                "id": rid,
                "target_sum": region.target_sum,
                "cell_count": len(region.cells)
            })
        
        # Add solutions if provided
        if "solutions" in data:
            solutions = data["solutions"]
            vis_data["solutions"] = solutions
            vis_data["solution_count"] = len(solutions)
        
        return jsonify({
            "success": True,
            "visualization": vis_data
        }), 200
    
    except Exception as e:
        logger.error(f"Visualization error: {e}")
        return jsonify({"error": str(e)}), 400


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    # Run development server
    app.run(debug=True, host="0.0.0.0", port=5000)
