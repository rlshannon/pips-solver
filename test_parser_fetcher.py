"""
Unit tests for puzzle parser and NYT fetcher.
"""

import unittest
import json
import tempfile
from pathlib import Path
from puzzle_parser import PuzzleParser, SAMPLE_PUZZLE_1x2_JSON, SAMPLE_PUZZLE_2x2_JSON
from puzzle_model import Puzzle, Region
from nyt_fetcher import NYTPipsFetcher


class TestPuzzleParser(unittest.TestCase):
    """Test puzzle parser."""
    
    def test_parse_1x2_puzzle(self):
        """Test parsing a simple 1x2 puzzle."""
        puzzle = PuzzleParser.from_json_string(SAMPLE_PUZZLE_1x2_JSON)
        
        self.assertEqual(puzzle.rows, 1)
        self.assertEqual(puzzle.cols, 2)
        self.assertEqual(len(puzzle.regions), 1)
        self.assertEqual(puzzle.regions[0].target_sum, 7)
        self.assertEqual(puzzle.regions[0].size(), 2)
    
    def test_parse_2x2_puzzle(self):
        """Test parsing a 2x2 puzzle with 2 regions."""
        puzzle = PuzzleParser.from_json_string(SAMPLE_PUZZLE_2x2_JSON)
        
        self.assertEqual(puzzle.rows, 2)
        self.assertEqual(puzzle.cols, 2)
        self.assertEqual(len(puzzle.regions), 2)
        
        # Verify region data
        region_sums = {r.target_sum for r in puzzle.regions}
        self.assertEqual(region_sums, {5, 7})
    
    def test_puzzle_roundtrip(self):
        """Test that puzzle can be serialized and deserialized."""
        original_puzzle = PuzzleParser.from_json_string(SAMPLE_PUZZLE_2x2_JSON)
        
        # Convert to JSON and back
        json_str = PuzzleParser.to_json_string(original_puzzle)
        reconstructed = PuzzleParser.from_json_string(json_str)
        
        # Verify dimensions match
        self.assertEqual(original_puzzle.rows, reconstructed.rows)
        self.assertEqual(original_puzzle.cols, reconstructed.cols)
        self.assertEqual(len(original_puzzle.regions), len(reconstructed.regions))
    
    def test_parse_from_file(self):
        """Test parsing puzzle from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(SAMPLE_PUZZLE_1x2_JSON)
            temp_file = f.name
        
        try:
            puzzle = PuzzleParser.from_json_file(temp_file)
            self.assertEqual(puzzle.rows, 1)
            self.assertEqual(puzzle.cols, 2)
        finally:
            Path(temp_file).unlink()
    
    def test_save_to_file(self):
        """Test saving puzzle to file."""
        original = PuzzleParser.from_json_string(SAMPLE_PUZZLE_1x2_JSON)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        try:
            PuzzleParser.to_json_file(original, temp_file)
            
            # Read back
            loaded = PuzzleParser.from_json_file(temp_file)
            self.assertEqual(original.rows, loaded.rows)
            self.assertEqual(original.cols, loaded.cols)
        finally:
            Path(temp_file).unlink()
    
    def test_invalid_puzzle_missing_region(self):
        """Test that parser rejects puzzles with missing region sums."""
        bad_json = """{
            "grid": [[1, 1]],
            "regions": {}
        }"""
        
        with self.assertRaises(ValueError):
            PuzzleParser.from_json_string(bad_json)
    
    def test_invalid_puzzle_mismatched_rows(self):
        """Test that parser rejects puzzles with mismatched row lengths."""
        bad_json = """{
            "grid": [
                [1, 1],
                [2]
            ],
            "regions": {
                "1": {"sum": 5},
                "2": {"sum": 7}
            }
        }"""
        
        with self.assertRaises(ValueError):
            PuzzleParser.from_json_string(bad_json)


class TestNYTPipsFetcher(unittest.TestCase):
    """Test NYT Pips fetcher."""
    
    def setUp(self):
        """Set up test fetcher."""
        self.fetcher = NYTPipsFetcher(cache_enabled=False)
    
    def test_fetch_from_json_string(self):
        """Test fetching puzzle from JSON string."""
        puzzle = self.fetcher.fetch_from_json_string(SAMPLE_PUZZLE_1x2_JSON)
        
        self.assertIsNotNone(puzzle)
        self.assertEqual(puzzle.rows, 1)
        self.assertEqual(puzzle.cols, 2)
    
    def test_fetch_from_file(self):
        """Test fetching puzzle from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(SAMPLE_PUZZLE_1x2_JSON)
            temp_file = f.name
        
        try:
            puzzle = self.fetcher.fetch_from_file(temp_file)
            self.assertIsNotNone(puzzle)
            self.assertEqual(puzzle.rows, 1)
        finally:
            Path(temp_file).unlink()
    
    def test_fetch_nonexistent_file(self):
        """Test fetching from non-existent file returns None."""
        puzzle = self.fetcher.fetch_from_file("/nonexistent/path/puzzle.json")
        self.assertIsNone(puzzle)
    
    def test_fetch_invalid_json_string(self):
        """Test fetching invalid JSON returns None."""
        puzzle = self.fetcher.fetch_from_json_string("not valid json")
        self.assertIsNone(puzzle)
    
    def test_cache_directory_creation(self):
        """Test that cache directory is created when enabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fetcher = NYTPipsFetcher(cache_enabled=True)
            cache_dir = fetcher.CACHE_DIR
            self.assertTrue(cache_dir.exists())


if __name__ == '__main__':
    unittest.main()
