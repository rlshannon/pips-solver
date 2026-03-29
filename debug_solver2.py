"""Debug script to trace solver execution with more detail."""

from puzzle_model import Puzzle, Region, PuzzleState, Domino, DominoPlacement
from solver import PipsSolver

# Monkey-patch solver to add debugging
original_backtrack = PipsSolver._backtrack

debug_depth = 0

def debug_backtrack(self, state):
    global debug_depth
    debug_depth += 1
    indent = "  " * (debug_depth - 1)
    
    is_complete = state.is_complete()
    print(f"{indent}[{self.call_count}] Backtrack: depth={debug_depth}, complete={is_complete}, placements={len(state.placements)}")
    
    if is_complete:
        valid = self._validate_solution(state)
        print(f"{indent}  -> Complete! Valid={valid}")
        if valid:
            print(f"{indent}     ADDED SOLUTION")
        debug_depth -= 1
        return original_backtrack(self, state)
    
    empty_cell = state.get_empty_cell()
    if not empty_cell:
        debug_depth -= 1
        return original_backtrack(self, state)
    
    row, col = empty_cell
    print(f"{indent}  Empty cell: ({row},{col})")
    print(f"{indent}  Available dominoes: {len(state.available_dominoes)}")
    
    # Call original with tracking
    self.call_count += 1
    
    for domino in list(state.available_dominoes):
        # Try horizontal placement
        if col + 1 < self.puzzle.cols and not state.is_cell_occupied(row, col + 1):
            cell2 = (row, col + 1)
            placement = DominoPlacement(domino, (row, col), cell2)
            
            try:
                state.place_domino(placement)
                print(f"{indent}  Placed {domino}")
                if self._is_state_valid(state):
                    print(f"{indent}    -> Valid, recursing...")
                    debug_backtrack(self, state)
                else:
                    print(f"{indent}    -> Invalid, pruning")
                state.remove_domino(placement)
            except ValueError as e:
                print(f"{indent}  Failed to place {domino}: {e}")
        
        # Try vertical placement
        if row + 1 < self.puzzle.rows and not state.is_cell_occupied(row + 1, col):
            cell2 = (row + 1, col)
            placement = DominoPlacement(domino, (row, col), cell2)
            
            try:
                state.place_domino(placement)
                print(f"{indent}  Placed {domino} (vertical)")
                if self._is_state_valid(state):
                    print(f"{indent}    -> Valid, recursing...")
                    debug_backtrack(self, state)
                else:
                    print(f"{indent}    -> Invalid, pruning")
                state.remove_domino(placement)
            except ValueError as e:
                print(f"{indent}  Failed to place {domino} (vertical): {e}")
    
    debug_depth -= 1

PipsSolver._backtrack = debug_backtrack

# Create simplest puzzle: 1x2 grid, 1 domino
region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=7)
puzzle = Puzzle(rows=1, cols=2, regions=[region1])

print(f"Puzzle: {puzzle}\n")

# Try solving
solver = PipsSolver(puzzle)
solutions = solver.solve()

print(f"\n\nFinal: {len(solutions)} solutions found")
