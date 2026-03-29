"""
Example script: Fetch and solve a Pips puzzle.

This demonstrates the complete workflow:
1. Fetch a puzzle (from file, JSON, or NYT)
2. Solve it to find all solutions
3. Display the results
"""

from nyt_fetcher import NYTPipsFetcher
from solver import PipsSolver
from puzzle_parser import PuzzleParser


def example_solve_from_file():
    """Example: Solve a puzzle from a file."""
    print("=" * 60)
    print("Example 1: Solve puzzle from file")
    print("=" * 60)
    
    fetcher = NYTPipsFetcher(cache_enabled=True)
    puzzle = fetcher.fetch_from_file("puzzle_cache/sample_2x2.json")
    
    if not puzzle:
        print("Failed to load puzzle")
        return
    
    print(f"\nLoaded puzzle: {puzzle.rows}x{puzzle.cols} with {len(puzzle.regions)} regions")
    print(f"Regions: {[f'Region {r.region_id} (sum={r.target_sum})' for r in puzzle.regions]}")
    
    # Solve
    print("\nSolving...")
    solver = PipsSolver(puzzle)
    solutions = solver.solve()
    
    print(f"Found {len(solutions)} solution(s)")
    
    for i, solution in enumerate(solutions, 1):
        print(f"\nSolution {i}:")
        for placement in solution:
            print(f"  {placement.domino} at {placement.cell1}-{placement.cell2}")


def example_solve_from_json():
    """Example: Solve a puzzle from JSON string."""
    print("\n" + "=" * 60)
    print("Example 2: Solve puzzle from JSON string")
    print("=" * 60)
    
    puzzle_json = """{
        "id": "demo",
        "difficulty": "easy",
        "grid": [
            [1, 1],
            [2, 2]
        ],
        "regions": {
            "1": {"sum": 5},
            "2": {"sum": 7}
        }
    }"""
    
    fetcher = NYTPipsFetcher(cache_enabled=False)
    puzzle = fetcher.fetch_from_json_string(puzzle_json)
    
    if not puzzle:
        print("Failed to parse puzzle")
        return
    
    print(f"\nLoaded puzzle: {puzzle.rows}x{puzzle.cols}")
    
    # Solve
    print("Solving...")
    solver = PipsSolver(puzzle)
    solutions = solver.solve()
    
    print(f"Found {len(solutions)} solution(s)")
    print(f"First solution:")
    if solutions:
        for placement in solutions[0]:
            print(f"  {placement.domino}")


def example_format_info():
    """Display information about the Pips puzzle JSON format."""
    print("\n" + "=" * 60)
    print("Pips Puzzle JSON Format")
    print("=" * 60)
    
    format_doc = """
The Pips puzzle JSON format consists of:

1. Grid: 2D array of region IDs
   - Each cell contains the ID of its region
   - Example: [[1, 1], [2, 2]] means a 2x2 grid with 2 regions

2. Regions: Dictionary of region definitions
   - Key: region_id (as string)
   - Value: object with { "sum": target_sum }
   - Example: {"1": {"sum": 5}, "2": {"sum": 7}}

3. Metadata (optional):
   - "id": puzzle identifier
   - "difficulty": puzzle difficulty (easy, medium, hard)

Full example:
{
    "id": "puzzle_20260329",
    "difficulty": "medium",
    "grid": [
        [1, 1, 2, 2],
        [1, 3, 3, 2],
        [4, 4, 5, 5],
        [4, 6, 6, 5]
    ],
    "regions": {
        "1": {"sum": 10},
        "2": {"sum": 12},
        "3": {"sum": 8},
        "4": {"sum": 14},
        "5": {"sum": 11},
        "6": {"sum": 9}
    }
}
"""
    
    print(format_doc)


if __name__ == "__main__":
    print("\nPips Solver - Usage Examples\n")
    
    try:
        example_solve_from_file()
    except FileNotFoundError:
        print("Note: sample_2x2.json not found, skipping file example")
    
    example_solve_from_json()
    example_format_info()
    
    print("\n" + "=" * 60)
    print("For more information, see README.md")
    print("=" * 60)
