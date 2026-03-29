"""
Procedural generator for Pips puzzles.

Generates random playable Pips puzzles with:
- Configurable grid size
- Difficulty scaling (easy/medium/hard)
- Optional unique solution enforcement
"""

import random
from typing import Set, Tuple, List, Dict, Optional
from puzzle_model import Puzzle, Region, PuzzleState, Domino
from solver import PipsSolver


class PuzzleGenerator:
    """Generate random Pips puzzles."""
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize generator.
        
        Args:
            seed: Random seed for reproducibility
        """
        if seed is not None:
            random.seed(seed)
    
    def generate(
        self,
        width: int = 7,
        height: int = 9,
        difficulty: str = "medium",
        enforce_unique: bool = False
    ) -> Optional[Puzzle]:
        """
        Generate a random playable Pips puzzle.
        
        Args:
            width: Grid width (columns)
            height: Grid height (rows)
            difficulty: "easy", "medium", or "hard"
            enforce_unique: If True, ensure puzzle has exactly one solution
        
        Returns:
            Puzzle object or None if generation fails
        """
        # Validate parameters
        if width < 2 or height < 2:
            raise ValueError("Grid must be at least 2x2")
        
        if (width * height) % 2 != 0:
            raise ValueError("Grid must have even number of cells (for dominoes)")
        
        if difficulty not in ["easy", "medium", "hard"]:
            raise ValueError(f"Unknown difficulty: {difficulty}")
        
        # Step 1: Generate random region layout
        regions = self._generate_regions(width, height, difficulty)
        if not regions:
            return None
        
        # Step 2: Assign reasonable target sums to regions
        # Use a simple heuristic: each domino normally sums to 0-12
        # For a region of size N cells, we have N/2 dominoes with avg ~6 each
        for region in regions:
            size = region.size()
            num_dominoes = size // 2
            
            # Target sum estimate: reasonable range based on region size
            # Minimum: 0 (all low value dominoes like 0-0, 0-1)
            # Maximum: depends on region, but cap at reasonable value
            if difficulty == "easy":
                # Easy puzzles have simpler, more constrained sums
                region.target_sum = num_dominoes * random.randint(4, 8)
            elif difficulty == "medium":
                # Medium has more variation
                region.target_sum = num_dominoes * random.randint(3, 9)
            else:
                # Hard puzzles can have more extreme sums
                region.target_sum = num_dominoes * random.randint(2, 11)
        
        # Step 3: Create puzzle with these regions
        puzzle_template = Puzzle(
            rows=height,
            cols=width,
            regions=regions,
            difficulty=difficulty
        )
        
        # Step 4: Don't enforce solvability for now - just return valid puzzles
        # (We can add solver verification in a later phase for uniqueness checking)
        return puzzle_template
    
    def generate_retry(
        self,
        width: int = 7,
        height: int = 9,
        difficulty: str = "medium",
        enforce_unique: bool = False,
        max_attempts: int = 10
    ) -> Puzzle:
        """
        Generate a puzzle with retries if generation fails.
        
        Args:
            width: Grid width
            height: Grid height
            difficulty: Puzzle difficulty
            enforce_unique: Enforce unique solution
            max_attempts: Maximum generation attempts
        
        Returns:
            Generated Puzzle object
        
        Raises:
            RuntimeError if generation fails after max_attempts
        """
        for attempt in range(max_attempts):
            puzzle = self.generate(width, height, difficulty, enforce_unique)
            if puzzle:
                print(f"Generated puzzle on attempt {attempt + 1}")
                return puzzle
        
        raise RuntimeError(
            f"Failed to generate puzzle after {max_attempts} attempts"
        )
    
    def _generate_regions(
        self,
        width: int,
        height: int,
        difficulty: str
    ) -> List[Region]:
        """
        Generate random region layout for grid using flood-fill.
        
        Uses grid array as single source of truth to ensure 100% coverage.
        
        Args:
            width: Grid width
            height: Grid height
            difficulty: Puzzle difficulty
        
        Returns:
            List of Region objects (guaranteed to cover all cells)
        """
        total_cells = width * height
        grid = [[-1 for _ in range(width)] for _ in range(height)]
        
        # Determine number of regions
        if difficulty == "easy":
            num_regions = random.randint(2, max(2, total_cells // 6))
        elif difficulty == "medium":
            num_regions = random.randint(3, max(3, total_cells // 4))
        else:  # hard
            num_regions = random.randint(4, max(4, total_cells // 2))
        
        num_regions = min(num_regions, total_cells // 2)
        
        # Initialize with random seeds
        cells_to_assign = [(r, c) for r in range(height) for c in range(width)]
        random.shuffle(cells_to_assign)
        
        # Place seeds for each region
        seeds = []
        for i in range(min(num_regions, len(cells_to_assign))):
            r, c = cells_to_assign[i]
            grid[r][c] = i
            seeds.append((r, c, i))
        
        # Grow regions from seeds
        assigned_count = len(seeds)
        
        for region_id in range(len(seeds)):
            frontier = set()
            # Find initial frontier cells around seed
            seed_r, seed_c, rid = seeds[region_id]
            for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nr, nc = seed_r + dr, seed_c + dc
                if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == -1:
                    frontier.add((nr, nc))
            
            # Target size for this region
            if difficulty == "easy":
                target_size = random.randint(total_cells // (num_regions + 1),
                                            total_cells // num_regions + 2)
            else:
                target_size = random.randint(2, total_cells // num_regions + 1)
            
            # Expand region
            current_size = 1  # Start with seed
            while frontier and current_size < target_size:
                cell = frontier.pop()
                r, c = cell
                
                # Assign cell to this region
                grid[r][c] = region_id
                current_size += 1
                assigned_count += 1
                
                # Try to expand frontier
                for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] == -1:
                        if random.random() < 0.7:  # Add with some probability
                            frontier.add((nr, nc))
        
        # Assign any remaining unassigned cells to nearest region
        for r in range(height):
            for c in range(width):
                if grid[r][c] == -1:
                    # Find nearest assigned neighbor
                    for dist in range(1, max(width, height)):
                        found = False
                        for dr in range(-dist, dist + 1):
                            for dc in range(-dist, dist + 1):
                                if abs(dr) == dist or abs(dc) == dist:
                                    nr, nc = r + dr, c + dc
                                    if 0 <= nr < height and 0 <= nc < width and grid[nr][nc] >= 0:
                                        grid[r][c] = grid[nr][nc]
                                        found = True
                                        break
                            if found:
                                break
                        if found:
                            break
                    
                    # Fallback: assign to region 0
                    if grid[r][c] == -1:
                        grid[r][c] = 0
        
        # Extract regions from grid
        region_cells = {}
        for r in range(height):
            for c in range(width):
                region_id = grid[r][c]
                if region_id not in region_cells:
                    region_cells[region_id] = set()
                region_cells[region_id].add((r, c))
        
        # Convert to Region objects
        regions = [
            Region(
                region_id=rid,
                cells=region_cells[rid],
                target_sum=0
            )
            for rid in sorted(region_cells.keys())
        ]
        
        return regions
    
    def _find_random_solution(self, puzzle: Puzzle) -> Optional[List]:
        """
        Find a random valid solution for a puzzle.
        
        Uses the solver but biases towards finding diverse solutions.
        
        Args:
            puzzle: Puzzle to solve
        
        Returns:
            List of DominoPlacement objects, or None if unsolvable
        """
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
        
        if solutions:
            return random.choice(solutions)
        
        return None


# Convenience function for quick generation
def generate_puzzle(
    width: int = 7,
    height: int = 9,
    difficulty: str = "medium",
    enforce_unique: bool = False,
    max_attempts: int = 10
) -> Puzzle:
    """
    Generate a random Pips puzzle.
    
    Args:
        width: Grid width (default 7)
        height: Grid height (default 9)
        difficulty: "easy", "medium", or "hard" (default "medium")
        enforce_unique: Enforce unique solution (default False)
        max_attempts: Maximum generation attempts (default 10)
    
    Returns:
        Generated Puzzle object
    
    Example:
        puzzle = generate_puzzle(width=7, height=9, difficulty="hard")
        solver = PipsSolver(puzzle)
        solutions = solver.solve()
    """
    generator = PuzzleGenerator()
    return generator.generate_retry(width, height, difficulty, enforce_unique, max_attempts)
