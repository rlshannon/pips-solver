"""
Backtracking solver for Pips puzzles.

Finds all solutions to a Pips puzzle using depth-first search with early pruning.
"""

from typing import List
from puzzle_model import Puzzle, PuzzleState, DominoPlacement


class PipsSolver:
    """Solver for Pips puzzles using backtracking."""
    
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.solutions: List[List[DominoPlacement]] = []
        self.call_count = 0
    
    def solve(self) -> List[List[DominoPlacement]]:
        """
        Find all solutions to the puzzle.
        
        Returns a list of solutions, where each solution is a list of DominoPlacement objects.
        """
        self.solutions = []
        self.call_count = 0
        state = PuzzleState(self.puzzle)
        self._backtrack(state)
        return self.solutions
    
    def _backtrack(self, state: PuzzleState) -> None:
        """Recursively search for solutions."""
        self.call_count += 1
        
        # Base case: all cells filled
        if state.is_complete():
            if self._validate_solution(state):
                self.solutions.append(state.placements.copy())
            return
        
        # Find next empty cell
        empty_cell = state.get_empty_cell()
        if not empty_cell:
            return
        
        row, col = empty_cell
        
        # Try each available domino in each valid orientation
        for domino in list(state.available_dominoes):
            # Try horizontal placement (same row, next column)
            if col + 1 < self.puzzle.cols and not state.is_cell_occupied(row, col + 1):
                cell2 = (row, col + 1)
                placement = DominoPlacement(domino, (row, col), cell2)
                
                try:
                    state.place_domino(placement)
                    if self._is_state_valid(state):
                        self._backtrack(state)
                    state.remove_domino(placement)
                except ValueError:
                    # Cell already occupied, skip
                    pass
            
            # Try vertical placement (next row, same column)
            if row + 1 < self.puzzle.rows and not state.is_cell_occupied(row + 1, col):
                cell2 = (row + 1, col)
                placement = DominoPlacement(domino, (row, col), cell2)
                
                try:
                    state.place_domino(placement)
                    if self._is_state_valid(state):
                        self._backtrack(state)
                    state.remove_domino(placement)
                except ValueError:
                    # Cell already occupied, skip
                    pass
    
    def _is_state_valid(self, state: PuzzleState) -> bool:
        """Check if current state is still potentially valid."""
        for region in self.puzzle.regions:
            current_sum = state.get_region_sum(region)
            
            # Sum already exceeded - prune this branch
            if current_sum > region.target_sum:
                return False
            
            # Region complete but sum doesn't match
            if state.is_region_complete(region):
                if current_sum != region.target_sum:
                    return False
        
        return True
    
    def _validate_solution(self, state: PuzzleState) -> bool:
        """Validate that a completed solution satisfies all constraints."""
        # Check all regions have correct sum
        for region in self.puzzle.regions:
            if state.get_region_sum(region) != region.target_sum:
                return False
        
        # Check that number of dominoes used equals number of cells / 2
        # (Each domino covers exactly 2 cells)
        expected_dominoes = (self.puzzle.rows * self.puzzle.cols) // 2
        if len(state.used_dominoes) != expected_dominoes:
            return False
        
        return True
