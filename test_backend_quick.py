#!/usr/bin/env python
"""Quick test of backend endpoints."""

import json
from app import app

client = app.test_client()

print("Backend API Quick Test")
print("=" * 50)

# Test 1: Health
response = client.get('/health')
assert response.status_code == 200, "Health check failed"
print("✓ Health check")

# Test 2: Info
response = client.get('/')
assert response.status_code == 200, "Info endpoint failed"
data = response.get_json()
assert len(data.get('endpoints', {})) > 0, "No endpoints listed"
print(f"✓ API info ({len(data['endpoints'])} endpoints)")

# Test 3: Parse
puzzle_data = {
    "grid": [[0, 0], [1, 1]],
    "regions": {"0": {"sum": 7}, "1": {"sum": 5}}
}
response = client.post('/puzzle/parse', json=puzzle_data)
assert response.status_code == 200, f"Parse failed: {response.get_json()}"
print("✓ Parse puzzle (2x2)")

# Test 4: Generate
gen_params = {"width": 4, "height": 4, "difficulty": "easy", "max_attempts": 3}
response = client.post('/generate', json=gen_params)
assert response.status_code == 200, f"Generate failed: {response.get_json()}"
print("✓ Generate puzzle (4x4)")

# Test 5: Visualize
response = client.post('/visualize', json={"puzzle": puzzle_data})
assert response.status_code == 200, f"Visualize failed: {response.get_json()}"
data = response.get_json()
assert "visualization" in data, "No visualization data"
print("✓ Visualize puzzle")

print("=" * 50)
print("✓ All tests passed!")
