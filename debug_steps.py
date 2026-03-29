#!/usr/bin/env python
"""Debug the generate() function step by step."""

import sys

# Remove cached modules to ensure fresh load
for mod in list(sys.modules.keys()):
    if 'generator' in mod or 'puzzle' in mod or 'solver' in mod:
        del sys.modules[mod]

from generator import PuzzleGenerator
from puzzle_model import Puzzle

gen = PuzzleGenerator(seed=42)

print('Step 1: Generate regions')
regions = gen._generate_regions(4, 4, 'easy')
print(f'  OK: {len(regions)} regions, {sum(len(r.cells) for r in regions)} cells')

print('Step 2: Assign target sums')
for region in regions:
    region.target_sum = 12
print('  OK')

print('Step 3: Create Puzzle manually')
puzzle = Puzzle(rows=4, cols=4, regions=regions, difficulty='easy')
print(f'  OK: Puzzle created')

print('Step 4: Call generate()')
try:
    puzzle2 = gen.generate(4, 4, 'easy')
    print(f'  OK: Generated puzzle with {len(puzzle2.regions)} regions')
except Exception as e:
    print(f'  ERROR: {e}')
    import traceback
    traceback.print_exc()
