#!/usr/bin/env python
"""Quick test of region generation fix."""

from generator import PuzzleGenerator

def test_generation():
    """Test region generation for various sizes."""
    gen = PuzzleGenerator(seed=42)
    
    test_cases = [
        (4, 4, "easy"),
        (4, 4, "medium"),
        (6, 6, "hard"),
        (2, 2, "easy"),
    ]
    
    for width, height, difficulty in test_cases:
        try:
            puzzle = gen.generate(width, height, difficulty)
            total_cells = sum(len(r.cells) for r in puzzle.regions)
            expected = width * height
            status = "✓" if total_cells == expected else "✗"
            print(f"{status} {width}x{height} {difficulty}: {total_cells}/{expected} cells")
        except Exception as e:
            print(f"✗ {width}x{height} {difficulty}: {e}")

if __name__ == "__main__":
    test_generation()
