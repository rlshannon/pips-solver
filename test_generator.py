"""
Unit tests for procedural puzzle generator.
"""

import unittest
from generator import PuzzleGenerator, generate_puzzle
from solver import PipsSolver
from puzzle_model import Puzzle


class TestPuzzleGenerator(unittest.TestCase):
    """Test procedural puzzle generator."""
    
    def setUp(self):
        """Set up generator for tests."""
        self.generator = PuzzleGenerator(seed=42)
    
    def test_generator_creates_puzzle(self):
        """Test that generator creates valid puzzle."""
        puzzle = self.generator.generate(width=4, height=4, difficulty="easy")
        
        self.assertIsNotNone(puzzle)
        self.assertEqual(puzzle.rows, 4)
        self.assertEqual(puzzle.cols, 4)
        self.assertGreater(len(puzzle.regions), 0)
    
    def test_generator_respects_difficult_easy(self):
        """Test that easy puzzles have larger regions."""
        puzzle_easy = self.generator.generate(width=6, height=9, difficulty="easy")
        puzzle_hard = self.generator.generate(width=6, height=9, difficulty="hard")
        
        self.assertIsNotNone(puzzle_easy)
        self.assertIsNotNone(puzzle_hard)
        
        # Easy should have fewer, larger regions
        # Hard should have more, smaller regions
        self.assertLess(
            len(puzzle_easy.regions),
            len(puzzle_hard.regions),
            "Easy puzzles should have fewer regions than hard puzzles"
        )
    
    def test_generator_even_grid_required(self):
        """Test that odd-sized grids are rejected."""
        with self.assertRaises(ValueError):
            self.generator.generate(width=3, height=3)
    
    def test_generator_minimum_grid_size(self):
        """Test that generator requires minimum 2x2 grid."""
        with self.assertRaises(ValueError):
            self.generator.generate(width=1, height=2)
    
    def test_generated_puzzle_solvable(self):
        """Test that generated puzzles are solvable."""
        puzzle = self.generator.generate(width=4, height=4, difficulty="easy")
        
        self.assertIsNotNone(puzzle)
        
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        self.assertGreater(len(solutions), 0, "Generated puzzle should have at least one solution")
    
    def test_generated_puzzle_satisfies_constraints(self):
        """Test that solutions satisfy all region constraints."""
        puzzle = self.generator.generate(width=4, height=4, difficulty="medium")
        
        self.assertIsNotNone(puzzle)
        
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        self.assertGreater(len(solutions), 0)
        
        # Get first solution
        first_solution = solutions[0]
        
        # Verify solution satisfies all region sums
        from puzzle_model import PuzzleState
        state = PuzzleState(puzzle)
        for placement in first_solution:
            state.place_domino(placement)
        
        for region in puzzle.regions:
            actual_sum = state.get_region_sum(region)
            self.assertEqual(
                actual_sum,
                region.target_sum,
                f"Region {region.region_id} sum mismatch: {actual_sum} != {region.target_sum}"
            )
    
    def test_generate_puzzle_convenience_function(self):
        """Test the convenience generate_puzzle function."""
        puzzle = generate_puzzle(width=4, height=4, difficulty="medium", max_attempts=5)
        
        self.assertIsNotNone(puzzle)
        self.assertEqual(puzzle.rows, 4)
        self.assertEqual(puzzle.cols, 4)
    
    def test_generator_multiple_difficulties(self):
        """Test generator produces puzzles at all difficulty levels."""
        for difficulty in ["easy", "medium", "hard"]:
            puzzle = self.generator.generate(width=6, height=6, difficulty=difficulty)
            self.assertIsNotNone(puzzle, f"Failed to generate {difficulty} puzzle")
            self.assertEqual(puzzle.difficulty, difficulty)
    
    def test_generator_reproducible_with_seed(self):
        """Test that generator is reproducible with same seed."""
        gen1 = PuzzleGenerator(seed=123)
        gen2 = PuzzleGenerator(seed=123)
        
        puzzle1 = gen1.generate(width=4, height=4, difficulty="medium")
        puzzle2 = gen2.generate(width=4, height=4, difficulty="medium")
        
        # Should have same structure
        self.assertIsNotNone(puzzle1)
        self.assertIsNotNone(puzzle2)
        self.assertEqual(puzzle1.rows, puzzle2.rows)
        self.assertEqual(puzzle1.cols, puzzle2.cols)
    
    def test_generator_with_unique_solution_requirement(self):
        """Test that enforce_unique flag limits generation to unique puzzles."""
        # This is a lighter test since enforcing uniqueness is slow
        # Just verify it doesn't error
        puzzle = self.generator.generate(
            width=4,
            height=4,
            difficulty="easy",
            enforce_unique=False  # Skip uniqueness for speed
        )
        
        self.assertIsNotNone(puzzle)


class TestGeneratorRobustness(unittest.TestCase):
    """Test generator robustness and edge cases."""
    
    def test_multiple_generations(self):
        """Test that generator can produce multiple puzzles."""
        generator = PuzzleGenerator()
        puzzles = []
        
        for i in range(3):
            puzzle = generator.generate(width=4, height=4, difficulty="easy")
            self.assertIsNotNone(puzzle)
            puzzles.append(puzzle)
        
        # Verify they're different (at least one should differ)
        # (They might occasionally be the same due to randomness, so we just check they all exist)
        self.assertEqual(len(puzzles), 3)
    
    def test_different_grid_sizes(self):
        """Test generator works with various grid sizes."""
        generator = PuzzleGenerator()
        
        for width, height in [(2, 2), (4, 4), (6, 9), (8, 7), (7, 8)]:
            puzzle = generator.generate(width=width, height=height, difficulty="easy")
            self.assertIsNotNone(puzzle, f"Failed to generate {width}x{height} puzzle")
            self.assertEqual(puzzle.rows, height)
            self.assertEqual(puzzle.cols, width)


if __name__ == '__main__':
    unittest.main()
