"""
Unit tests for the Pips solver engine.

Tests constraint propagation, backtracking, and solution validation.
"""

import unittest
from puzzle_model import (
    Puzzle, Region, Domino, PuzzleState, DominoPlacement
)
from solver import PipsSolver


class TestDomino(unittest.TestCase):
    """Test domino class."""
    
    def test_domino_creation(self):
        d1 = Domino(2, 5)
        self.assertEqual(d1.pips, (2, 5))
    
    def test_domino_sort(self):
        d1 = Domino(5, 2)
        self.assertEqual(d1.pips, (2, 5))
    
    def test_domino_sum(self):
        d = Domino(3, 4)
        self.assertEqual(d.sum_pips(), 7)
    
    def test_domino_contains(self):
        d = Domino(2, 5)
        self.assertTrue(d.contains(2))
        self.assertTrue(d.contains(5))
        self.assertFalse(d.contains(3))


class TestRegion(unittest.TestCase):
    """Test region class."""
    
    def test_region_creation(self):
        cells = {(0, 0), (0, 1)}
        region = Region(region_id=1, cells=cells, target_sum=5)
        self.assertEqual(region.size(), 2)
        self.assertEqual(region.target_sum, 5)
    
    def test_region_empty_cells_invalid(self):
        with self.assertRaises(ValueError):
            Region(region_id=1, cells=set(), target_sum=5)


class TestPuzzle(unittest.TestCase):
    """Test puzzle class."""
    
    def test_simple_2x2_puzzle(self):
        """Create a minimal 2x2 puzzle with 2 regions."""
        # Two 2-cell regions
        region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=7)
        region2 = Region(region_id=2, cells={(1, 0), (1, 1)}, target_sum=5)
        
        puzzle = Puzzle(rows=2, cols=2, regions=[region1, region2])
        self.assertEqual(puzzle.size(), (2, 2))
        self.assertEqual(len(puzzle.regions), 2)
    
    def test_puzzle_cell_coverage(self):
        """Puzzle must cover all cells exactly once."""
        region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=5)
        # Missing cells (1, 0) and (1, 1)
        
        with self.assertRaises(ValueError):
            Puzzle(rows=2, cols=2, regions=[region1])


class TestPuzzleState(unittest.TestCase):
    """Test puzzle state tracking."""
    
    def setUp(self):
        """Create a minimal puzzle for testing."""
        region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=7)
        region2 = Region(region_id=2, cells={(1, 0), (1, 1)}, target_sum=5)
        self.puzzle = Puzzle(rows=2, cols=2, regions=[region1, region2])
        self.state = PuzzleState(self.puzzle)
    
    def test_initial_state(self):
        """Initial state has no placements."""
        self.assertEqual(len(self.state.placements), 0)
        self.assertEqual(len(self.state.used_dominoes), 0)
        self.assertEqual(len(self.state.available_dominoes), 28)
    
    def test_place_domino(self):
        """Test placing a domino."""
        domino = Domino(3, 4)
        placement = DominoPlacement(domino, (0, 0), (0, 1))
        
        self.state.place_domino(placement)
        
        self.assertEqual(len(self.state.placements), 1)
        self.assertIn(domino, self.state.used_dominoes)
        self.assertNotIn(domino, self.state.available_dominoes)
        self.assertTrue(self.state.is_cell_occupied(0, 0))
        self.assertTrue(self.state.is_cell_occupied(0, 1))
    
    def test_remove_domino(self):
        """Test removing a domino."""
        domino = Domino(3, 4)
        placement = DominoPlacement(domino, (0, 0), (0, 1))
        
        self.state.place_domino(placement)
        self.state.remove_domino(placement)
        
        self.assertEqual(len(self.state.placements), 0)
        self.assertNotIn(domino, self.state.used_dominoes)
        self.assertIn(domino, self.state.available_dominoes)
    
    def test_get_region_sum(self):
        """Test calculating region sum."""
        domino = Domino(3, 4)
        placement = DominoPlacement(domino, (0, 0), (0, 1))
        
        region1 = self.puzzle.regions[0]
        
        # Before placement
        self.assertEqual(self.state.get_region_sum(region1), 0)
        
        # After placement
        self.state.place_domino(placement)
        self.assertEqual(self.state.get_region_sum(region1), 7)


class TestSimpleSolve(unittest.TestCase):
    """Test solver on simple puzzles."""
    
    def test_trivial_puzzle(self):
        """
        Test a very simple 2x1 puzzle (just 1 domino).
        
        Grid: (0,0)-(0,1)
        Region 1: (0,0)-(0,1), sum=7 (only 3-4)
        """
        region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=7)
        puzzle = Puzzle(rows=1, cols=2, regions=[region1])
        
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        # Should find at least one solution
        self.assertGreater(len(solutions), 0)
        
        # Verify solution
        if solutions:
            first_solution = solutions[0]
            self.assertEqual(len(first_solution), 1)  # 1 domino for 2 cells
    
    def test_4cell_puzzle(self):
        """
        Test a 2x2 grid with a configuration that allows placement.
        """
        # Simple 2x2 grid: (0,0)-(0,1) in region 1, (1,0)-(1,1) in region 2
        region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=5)
        region2 = Region(region_id=2, cells={(1, 0), (1, 1)}, target_sum=7)
        puzzle = Puzzle(rows=2, cols=2, regions=[region1, region2])
        
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        # This puzzle should have multiple solutions since there are many ways
        # to achieve sums of 5 and 7 with different dominoes
        self.assertGreater(len(solutions), 0, "Should find at least one solution")


if __name__ == '__main__':
    unittest.main()
