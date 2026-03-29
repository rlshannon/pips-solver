"""Debug generator."""
from generator import PuzzleGenerator
from solver import PipsSolver

gen = PuzzleGenerator(seed=42)

print("Generating 4x4 puzzle...")
try:
    puzzle = gen.generate(width=4, height=4, difficulty="easy")
    
    if puzzle:
        print(f"Success! Puzzle: {puzzle}")
        print(f"Regions: {len(puzzle.regions)}")
        
        print("Solving...")
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        print(f"Solutions: {len(solutions)}")
    else:
        print("Failed to generate puzzle (returned None)")
except Exception as e:
    print(f"Exception during generation: {e}")
    import traceback
    traceback.print_exc()

print("\nTrying again with 2x2...")
try:
    puzzle2 = gen.generate(width=2, height=2, difficulty="easy")
    if puzzle2:
        print(f"Generated 2x2 puzzle")
        print(f"Regions: {puzzle2.regions}")
    else:
        print("Failed to generate 2x2 puzzle (returned None)")
except Exception as e:
    print(f"Exception: {e}")
    import traceback
    traceback.print_exc()
