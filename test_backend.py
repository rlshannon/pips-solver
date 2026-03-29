#!/usr/bin/env python
"""Test Flask backend endpoints."""

import json
import sys
from pathlib import Path

# Import the app
from app import app

# Create test client
client = app.test_client()

print("Testing Flask Backend Endpoints")
print("=" * 60)

# Test 1: Health check
print("\n[1] Health Check")
response = client.get('/health')
print(f"  Status: {response.status_code}")
print(f"  Response: {response.get_json()}")

# Test 2: Index/Info
print("\n[2] API Info")
response = client.get('/')
print(f"  Status: {response.status_code}")
data = response.get_json()
print(f"  Endpoints available: {len(data.get('endpoints', {}))}")

# Test 3: Parse a 2x2 puzzle
print("\n[3] Parse Puzzle (2x2)")
test_puzzle = {
    "grid": [[0, 0], [1, 1]],
    "regions": {
        "0": {"sum": 7},
        "1": {"sum": 5}
    }
}
response = client.post(
    '/puzzle/parse',
    data=json.dumps(test_puzzle),
    content_type='application/json'
)
print(f"  Status: {response.status_code}")
data = response.get_json()
if response.status_code == 200:
    print(f"  ✓ Parsed successfully")
    puzzle = data.get('puzzle')
    print(f"    Grid: {puzzle['rows']}x{puzzle['cols']}")
    print(f"    Regions: {len(puzzle['regions'])}")
else:
    print(f"  ✗ Error: {data.get('error')}")

# Test 4: Generate a puzzle
print("\n[4] Generate Puzzle (4x4 easy)")
response = client.post(
    '/generate',
    data=json.dumps({
        "width": 4,
        "height": 4,
        "difficulty": "easy",
        "max_attempts": 5
    }),
    content_type='application/json'
)
print(f"  Status: {response.status_code}")
data = response.get_json()
if response.status_code == 200:
    print(f"  ✓ Generated successfully")
    puzzle = data.get('puzzle')
    print(f"    Grid: {puzzle['rows']}x{puzzle['cols']}")
    print(f"    Regions: {len(puzzle['regions'])}")
    generated_puzzle = puzzle  # Save for next test
else:
    print(f"  ✗ Error: {data.get('error')}")
    generated_puzzle = None

# Test 5: Solve the generated puzzle
if generated_puzzle:
    print("\n[5] Solve Generated Puzzle")
    response = client.post(
        '/solve',
        data=json.dumps(generated_puzzle),
        content_type='application/json'
    )
    print(f"  Status: {response.status_code}")
    data = response.get_json()
    if response.status_code == 200:
        count = data.get('solution_count', 0)
        print(f"  ✓ Solutions found: {count}")
    else:
        print(f"  ✗ Error: {data.get('error')}")

# Test 6: Visualize
print("\n[6] Visualize Puzzle")
response = client.post(
    '/visualize',
    data=json.dumps({"puzzle": test_puzzle}),
    content_type='application/json'
)
print(f"  Status: {response.status_code}")
data = response.get_json()
if response.status_code == 200:
    print(f"  ✓ Visualization prepared")
    vis = data.get('visualization')
    print(f"    Grid cells: {len(vis['grid']['cells'])}")
    print(f"    Regions: {len(vis['regions'])}")
else:
    print(f"  ✗ Error: {data.get('error')}")

print("\n" + "=" * 60)
print("✓ Backend API test complete")
