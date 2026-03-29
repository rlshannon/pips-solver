"""
Puzzle data models for NYT Pips solver.

Defines core classes for representing:
- Domino: A single domino tile with two pip values
- Region: A cage/region in the puzzle with constraint sum
- Puzzle: The complete puzzle state and grid
"""

from dataclasses import dataclass, field
from typing import Set, List, Tuple, Dict, Optional
from enum import Enum


class Domino:
    """Represents a single domino tile with two pip values (0-6)."""
    
    def __init__(self, pip1: int, pip2: int):
        """Initialize domino with two pip values (order independent)."""
        self.pips = tuple(sorted([pip1, pip2]))
    
    def __repr__(self) -> str:
        return f"Domino({self.pips[0]}-{self.pips[1]})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Domino) and self.pips == other.pips
    
    def __hash__(self) -> int:
        return hash(self.pips)
    
    def sum_pips(self) -> int:
        """Return total pips on domino."""
        return self.pips[0] + self.pips[1]
    
    def contains(self, value: int) -> bool:
        """Check if domino contains a specific pip value."""
        return value in self.pips


@dataclass
class Region:
    """Represents a cage/region in the puzzle."""
    
    region_id: int
    cells: Set[Tuple[int, int]]  # Set of (row, col) tuples
    target_sum: int
    
    def __post_init__(self):
        """Validate region has cells."""
        if not self.cells:
            raise ValueError(f"Region {self.region_id} has no cells")
    
    def size(self) -> int:
        """Return number of cells in region."""
        return len(self.cells)
    
    def __repr__(self) -> str:
        return f"Region(id={self.region_id}, size={self.size()}, sum={self.target_sum})"


@dataclass
class Puzzle:
    """Represents a complete Pips puzzle."""
    
    rows: int
    cols: int
    regions: List[Region]
    puzzle_id: Optional[str] = None
    difficulty: Optional[str] = None  # "easy", "medium", "hard"
    
    def __post_init__(self):
        """Validate puzzle structure."""
        if self.rows <= 0 or self.cols <= 0:
            raise ValueError(f"Invalid grid size: {self.rows}x{self.cols}")
        
        # Verify total cells
        total_cells = sum(r.size() for r in self.regions)
        expected_cells = self.rows * self.cols
        if total_cells != expected_cells:
            raise ValueError(
                f"Region cells ({total_cells}) don't match grid size ({expected_cells})"
            )
        
        # Verify all cells covered exactly once
        all_cells = set()
        for region in self.regions:
            overlap = all_cells & region.cells
            if overlap:
                raise ValueError(f"Cells {overlap} assigned to multiple regions")
            all_cells.update(region.cells)
        
        if len(all_cells) != expected_cells:
            raise ValueError("Not all grid cells assigned to regions")
    
    def get_region_at(self, row: int, col: int) -> Optional[Region]:
        """Get region containing the given cell."""
        for region in self.regions:
            if (row, col) in region.cells:
                return region
        return None
    
    def size(self) -> Tuple[int, int]:
        """Return puzzle dimensions as (rows, cols)."""
        return (self.rows, self.cols)
    
    def __repr__(self) -> str:
        return f"Puzzle({self.rows}x{self.cols}, {len(self.regions)} regions)"


@dataclass
class DominoPlacement:
    """Represents a placement of a domino on the grid."""
    
    domino: Domino
    cell1: Tuple[int, int]  # (row, col)
    cell2: Tuple[int, int]  # (row, col)
    
    def cells(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Return both cells occupied by this domino."""
        return (self.cell1, self.cell2)
    
    def __repr__(self) -> str:
        return f"Placement({self.domino} at {self.cell1}-{self.cell2})"


class PuzzleState:
    """Tracks the current state of a puzzle being solved."""
    
    def __init__(self, puzzle: Puzzle):
        self.puzzle = puzzle
        self.placements: List[DominoPlacement] = []
        self.grid: Dict[Tuple[int, int], DominoPlacement] = {}  # Maps cell -> placement
        self.used_dominoes: Set[Domino] = set()
        self.available_dominoes: Set[Domino] = self._create_domino_set()
    
    @staticmethod
    def _create_domino_set() -> Set[Domino]:
        """Create the standard double-6 domino set (0-0 through 6-6)."""
        dominoes = set()
        for i in range(7):
            for j in range(i, 7):
                dominoes.add(Domino(i, j))
        return dominoes
    
    def place_domino(self, placement: DominoPlacement) -> None:
        """Place a domino on the grid."""
        if placement.cell1 in self.grid or placement.cell2 in self.grid:
            raise ValueError(f"Cell already occupied: {placement.cell1} or {placement.cell2}")
        
        if placement.domino not in self.available_dominoes:
            raise ValueError(f"Domino {placement.domino} already used")
        
        self.placements.append(placement)
        self.grid[placement.cell1] = placement
        self.grid[placement.cell2] = placement
        self.used_dominoes.add(placement.domino)
        self.available_dominoes.remove(placement.domino)
    
    def remove_domino(self, placement: DominoPlacement) -> None:
        """Remove a domino from the grid."""
        if placement.cell1 not in self.grid or placement.cell2 not in self.grid:
            raise ValueError("Placement not found on grid")
        
        del self.grid[placement.cell1]
        del self.grid[placement.cell2]
        self.placements.remove(placement)
        self.used_dominoes.remove(placement.domino)
        self.available_dominoes.add(placement.domino)
    
    def is_cell_occupied(self, row: int, col: int) -> bool:
        """Check if a cell is already occupied by a domino."""
        return (row, col) in self.grid
    
    def get_placement_at(self, row: int, col: int) -> Optional[DominoPlacement]:
        """Get the domino placement at a specific cell."""
        return self.grid.get((row, col))
    
    def get_empty_cell(self) -> Optional[Tuple[int, int]]:
        """Find the first empty cell (for backtracking)."""
        for row in range(self.puzzle.rows):
            for col in range(self.puzzle.cols):
                if (row, col) not in self.grid:
                    return (row, col)
        return None
    
    def is_complete(self) -> bool:
        """Check if all cells are filled with dominoes."""
        return self.get_empty_cell() is None
    
    def get_region_sum(self, region: Region) -> int:
        """Calculate current sum of pips in a region."""
        total = 0
        counted_placements = set()
        for cell in region.cells:
            placement = self.get_placement_at(cell[0], cell[1])
            if placement and id(placement) not in counted_placements:
                total += placement.domino.sum_pips()
                counted_placements.add(id(placement))
        return total
    
    def is_region_complete(self, region: Region) -> bool:
        """Check if all cells in a region are filled."""
        return all(self.is_cell_occupied(r, c) for r, c in region.cells)
    
    def copy(self) -> "PuzzleState":
        """Create a deep copy of the current state."""
        new_state = PuzzleState(self.puzzle)
        for placement in self.placements:
            new_state.placements.append(placement)
            new_state.grid[placement.cell1] = placement
            new_state.grid[placement.cell2] = placement
            new_state.used_dominoes.add(placement.domino)
        new_state.available_dominoes = self.available_dominoes.copy()
        return new_state
    
    def __repr__(self) -> str:
        filled = len(self.placements)
        total = self.puzzle.rows * self.puzzle.cols // 2
        return f"State({filled}/{total} dominoes placed)"
