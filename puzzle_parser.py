"""
Puzzle parser for Pips puzzles in JSON format.

Converts NYT Pips puzzle JSON format to our internal Puzzle model.
"""

import json
from typing import Dict, Any, Optional, Set, Tuple
from puzzle_model import Puzzle, Region


class PuzzleParser:
    """Parse Pips puzzles from various formats."""
    
    @staticmethod
    def from_json_string(json_str: str) -> Puzzle:
        """
        Parse puzzle from JSON string.
        
        Expected JSON format:
        {
            "id": "puzzle_id",
            "grid": [
                [region_id, region_id, ...],
                [region_id, region_id, ...],
                ...
            ],
            "regions": {
                "region_id": {"sum": target_sum},
                ...
            }
        }
        """
        data = json.loads(json_str)
        return PuzzleParser.from_json_dict(data)
    
    @staticmethod
    def from_json_file(filepath: str) -> Puzzle:
        """Parse puzzle from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return PuzzleParser.from_json_dict(data)
    
    @staticmethod
    def from_json_dict(data: Dict[str, Any]) -> Puzzle:
        """
        Parse puzzle from dictionary representation.
        
        Args:
            data: Dictionary with 'grid' and 'regions' keys
        
        Returns:
            Puzzle object
        """
        # Extract grid and validate
        grid = data.get('grid')
        if not grid or len(grid) == 0:
            raise ValueError("Invalid puzzle: missing or empty grid")
        
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        
        if cols == 0:
            raise ValueError("Invalid puzzle: grid has no columns")
        
        # Validate all rows same length
        for i, row in enumerate(grid):
            if len(row) != cols:
                raise ValueError(f"Invalid puzzle: row {i} has {len(row)} columns, expected {cols}")
        
        # Extract region definitions
        regions_data = data.get('regions', {})
        
        # Build regions from grid
        regions = {}
        region_cells: Dict[int, Set[Tuple[int, int]]] = {}
        
        # First pass: collect all cells for each region
        for r in range(rows):
            for c in range(cols):
                region_id = grid[r][c]
                if region_id is None:
                    raise ValueError(f"Invalid puzzle: cell ({r},{c}) has no region assignment")
                
                if region_id not in region_cells:
                    region_cells[region_id] = set()
                region_cells[region_id].add((r, c))
        
        # Second pass: create Region objects
        for region_id, cells in region_cells.items():
            target_sum = regions_data.get(str(region_id), {}).get('sum')
            
            if target_sum is None:
                raise ValueError(f"Region {region_id} missing target sum in regions data")
            
            regions[region_id] = Region(
                region_id=region_id,
                cells=cells,
                target_sum=target_sum
            )
        
        # Create and return Puzzle
        puzzle = Puzzle(
            rows=rows,
            cols=cols,
            regions=list(regions.values()),
            puzzle_id=data.get('id'),
            difficulty=data.get('difficulty')
        )
        
        return puzzle
    
    @staticmethod
    def to_json_dict(puzzle: Puzzle) -> Dict[str, Any]:
        """
        Convert puzzle to JSON dictionary representation.
        
        Returns:
            Dictionary with 'grid' and 'regions' keys
        """
        # Create grid representation
        grid = [[None for _ in range(puzzle.cols)] for _ in range(puzzle.rows)]
        
        # Fill grid with region IDs
        for region in puzzle.regions:
            for row, col in region.cells:
                grid[row][col] = region.region_id
        
        # Create regions dict
        regions = {}
        for region in puzzle.regions:
            regions[str(region.region_id)] = {
                'sum': region.target_sum
            }
        
        data = {
            'id': puzzle.puzzle_id or 'custom',
            'difficulty': puzzle.difficulty or 'unknown',
            'grid': grid,
            'regions': regions
        }
        
        return data
    
    @staticmethod
    def to_json_string(puzzle: Puzzle, indent: int = 2) -> str:
        """Convert puzzle to JSON string."""
        data = PuzzleParser.to_json_dict(puzzle)
        return json.dumps(data, indent=indent)
    
    @staticmethod
    def to_json_file(puzzle: Puzzle, filepath: str) -> None:
        """Save puzzle to JSON file."""
        data = PuzzleParser.to_json_dict(puzzle)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)


# Example puzzle strings for testing
SAMPLE_PUZZLE_1x2_JSON = """{
    "id": "sample_1x2",
    "difficulty": "easy",
    "grid": [
        [1, 1]
    ],
    "regions": {
        "1": { "sum": 7 }
    }
}"""

SAMPLE_PUZZLE_2x2_JSON = """{
    "id": "sample_2x2",
    "difficulty": "easy",
    "grid": [
        [1, 1],
        [2, 2]
    ],
    "regions": {
        "1": { "sum": 5 },
        "2": { "sum": 7 }
    }
}"""

# Larger example puzzle
SAMPLE_PUZZLE_6x9_JSON = """{
    "id": "sample_6x9",
    "difficulty": "medium",
    "grid": [
        [1, 1, 2, 2, 3, 3, 4, 4, 5],
        [1, 6, 6, 2, 7, 3, 8, 4, 5],
        [9, 9, 6, 7, 7, 8, 8, 9, 5],
        [10, 11, 11, 12, 8, 13, 13, 14, 5],
        [10, 10, 11, 12, 12, 13, 14, 14, 15],
        [16, 16, 17, 17, 18, 18, 19, 19, 15]
    ],
    "regions": {
        "1": { "sum": 11 },
        "2": { "sum": 12 },
        "3": { "sum": 10 },
        "4": { "sum": 10 },
        "5": { "sum": 15 },
        "6": { "sum": 13 },
        "7": { "sum": 12 },
        "8": { "sum": 15 },
        "9": { "sum": 14 },
        "10": { "sum": 12 },
        "11": { "sum": 13 },
        "12": { "sum": 15 },
        "13": { "sum": 13 },
        "14": { "sum": 14 },
        "15": { "sum": 13 },
        "16": { "sum": 10 },
        "17": { "sum": 11 },
        "18": { "sum": 12 },
        "19": { "sum": 11 }
    }
}"""
