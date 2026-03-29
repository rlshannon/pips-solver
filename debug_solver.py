"""Debug script to trace solver execution."""

from puzzle_model import Puzzle, Region, PuzzleState
from solver import PipsSolver

# Create simplest puzzle: 1x2 grid, 1 domino
region1 = Region(region_id=1, cells={(0, 0), (0, 1)}, target_sum=7)
puzzle = Puzzle(rows=1, cols=2, regions=[region1])

print(f"Puzzle: {puzzle}")
print(f"Grid size: {puzzle.size()}")
print(f"Regions: {puzzle.regions}")

# Try solving
solver = PipsSolver(puzzle)
solutions = solver.solve()

print(f"\nSolver complete!")
print(f"Backtrack calls: {solver.call_count}")
print(f"Solutions found: {len(solutions)}")

if solutions:
    for i, sol in enumerate(solutions):
        print(f"\nSolution {i+1}:")
        for placement in sol:
            print(f"  {placement}")
else:
    print("\nNo solutions found!")
    
    # Debug: can we place a single domino?
    state = PuzzleState(puzzle)
    print(f"\nInitial state: {state}")
    print(f"Available dominoes: {len(state.available_dominoes)}")
    
    # Try placing domino 3-4 horizontally
    from puzzle_model import Domino, DominoPlacement
    domino = Domino(3, 4)
    placement = DominoPlacement(domino, (0, 0), (0, 1))
    state.place_domino(placement)
    print(f"\nPlaced domino 3-4")
    print(f"Region sum: {state.get_region_sum(region1)}")
    print(f"Region target: {region1.target_sum}")
    print(f"Is valid: {state.get_region_sum(region1) == region1.target_sum}")
