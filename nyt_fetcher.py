"""
Fetcher for NYT Pips puzzles.

Supports multiple methods:
1. Browser automation (requires Selenium and ChromeDriver)
2. Manual JSON file upload
3. Direct URL to puzzle JSON
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import requests
from pathlib import Path
from puzzle_model import Puzzle
from puzzle_parser import PuzzleParser


class NYTPipsFetcher:
    """Fetch Pips puzzles from NYT."""
    
    # NYT Games API endpoint (reconstructed from reverse engineering)
    NYT_PIPS_API = "https://www.nytimes.com/games-assets/pips/{date}.json"
    
    # Cache directory for storing fetched puzzles
    CACHE_DIR = Path(__file__).parent / "puzzle_cache"
    
    def __init__(self, cache_enabled: bool = True):
        """
        Initialize fetcher.
        
        Args:
            cache_enabled: Whether to cache fetched puzzles locally
        """
        self.cache_enabled = cache_enabled
        if cache_enabled:
            self.CACHE_DIR.mkdir(exist_ok=True)
    
    def fetch_today(self) -> Optional[Puzzle]:
        """Fetch today's Pips puzzle."""
        today = datetime.now().strftime("%Y/%m/%d")
        return self.fetch_by_date(today)
    
    def fetch_by_date(self, date_str: str) -> Optional[Puzzle]:
        """
        Fetch puzzle by date string (YYYY/MM/DD or YYYY-MM-DD).
        
        Args:
            date_str: Date in format 'YYYY/MM/DD' or 'YYYY-MM-DD'
        
        Returns:
            Puzzle object or None if fetch fails
        """
        # Normalize date format
        if '-' in date_str:
            date_str = date_str.replace('-', '/')
        
        # Check cache first
        if self.cache_enabled:
            cached = self._get_cached_puzzle(date_str)
            if cached:
                return cached
        
        # Try to fetch from NYT
        puzzle_json = self._fetch_from_nyt(date_str)
        if not puzzle_json:
            return None
        
        # Parse puzzle
        try:
            puzzle = PuzzleParser.from_json_dict(puzzle_json)
            
            # Cache it
            if self.cache_enabled:
                self._cache_puzzle(date_str, puzzle_json)
            
            return puzzle
        except Exception as e:
            print(f"Error parsing puzzle: {e}")
            return None
    
    def fetch_from_file(self, filepath: str) -> Optional[Puzzle]:
        """
        Load puzzle from local JSON file.
        
        Args:
            filepath: Path to JSON puzzle file
        
        Returns:
            Puzzle object or None if file doesn't exist or is invalid
        """
        try:
            return PuzzleParser.from_json_file(filepath)
        except FileNotFoundError:
            print(f"Puzzle file not found: {filepath}")
            return None
        except Exception as e:
            print(f"Error loading puzzle from file: {e}")
            return None
    
    def fetch_from_json_string(self, json_str: str) -> Optional[Puzzle]:
        """
        Parse puzzle from JSON string.
        
        Args:
            json_str: JSON string representation of puzzle
        
        Returns:
            Puzzle object or None if invalid
        """
        try:
            return PuzzleParser.from_json_string(json_str)
        except Exception as e:
            print(f"Error parsing puzzle JSON: {e}")
            return None
    
    def _fetch_from_nyt(self, date_str: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to fetch puzzle JSON from NYT.
        
        This is a fallback method. The NYT endpoint may require authentication
        or be blocked by rate limiting.
        
        Args:
            date_str: Date in format 'YYYY/MM/DD'
        
        Returns:
            Puzzle JSON dict or None if fetch fails
        """
        url = self.NYT_PIPS_API.format(date=date_str)
        
        try:
            print(f"Fetching from {url}...")
            response = requests.get(
                url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Successfully fetched puzzle from NYT")
                return data
            elif response.status_code == 404:
                print(f"Puzzle not found for date {date_str}")
                return None
            else:
                print(f"NYT returned status code {response.status_code}")
                return None
        
        except requests.RequestException as e:
            print(f"Network error fetching puzzle: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Invalid JSON response from NYT: {e}")
            return None
    
    def _get_cached_puzzle(self, date_str: str) -> Optional[Puzzle]:
        """Get puzzle from local cache if available."""
        # Normalize to YYYY-MM-DD format for filename
        if '/' in date_str:
            date_key = date_str.replace('/', '-')
        else:
            date_key = date_str
        
        cache_file = self.CACHE_DIR / f"pips_{date_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                puzzle = PuzzleParser.from_json_dict(data)
                print(f"Loaded puzzle from cache: {cache_file}")
                return puzzle
            except Exception as e:
                print(f"Error loading cached puzzle: {e}")
                return None
        
        return None
    
    def _cache_puzzle(self, date_str: str, puzzle_json: Dict[str, Any]) -> None:
        """Save puzzle JSON to local cache."""
        # Normalize to YYYY-MM-DD format for filename
        if '/' in date_str:
            date_key = date_str.replace('/', '-')
        else:
            date_key = date_str
        
        cache_file = self.CACHE_DIR / f"pips_{date_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(puzzle_json, f, indent=2)
            print(f"Cached puzzle: {cache_file}")
        except Exception as e:
            print(f"Error caching puzzle: {e}")


class BrowserAutomationFetcher:
    """
    Fetch Pips puzzles using browser automation (Selenium).
    
    Requires: selenium, chromedriver
    Install: pip install selenium
    Download ChromeDriver: https://chromedriver.chromium.org/
    """
    
    def __init__(self, chromedriver_path: Optional[str] = None):
        """
        Initialize browser fetcher.
        
        Args:
            chromedriver_path: Path to chromedriver executable
        """
        self.chromedriver_path = chromedriver_path
        self.selenium_available = self._check_selenium()
    
    def _check_selenium(self) -> bool:
        """Check if Selenium is available."""
        try:
            import selenium  # type: ignore
            return True
        except ImportError:
            print("Warning: selenium not installed. Browser automation unavailable.")
            print("Install with: pip install selenium")
            return False
    
    def fetch_today(self) -> Optional[Puzzle]:
        """Fetch today's puzzle using browser automation."""
        if not self.selenium_available:
            print("Selenium not available. Cannot use browser automation.")
            return None
        
        try:
            from selenium import webdriver  # type: ignore
            from selenium.webdriver.common.by import By  # type: ignore
            from selenium.webdriver.support.ui import WebDriverWait  # type: ignore
            from selenium.webdriver.support import expected_conditions as EC  # type: ignore
            
            # Initialize Chrome driver
            options = webdriver.ChromeOptions()
            options.add_argument('--start-maximized')
            
            if self.chromedriver_path:
                driver = webdriver.Chrome(
                    executable_path=self.chromedriver_path,
                    options=options
                )
            else:
                driver = webdriver.Chrome(options=options)
            
            try:
                # Navigate to NYT Pips game
                driver.get("https://www.nytimes.com/games/pips")
                
                # Wait for puzzle to load
                print("Loading NYT Pips... (please log in if prompted)")
                wait = WebDriverWait(driver, 30)
                
                # Try to extract puzzle data from page
                # This is a simplified approach and may need adjustment based on NYT's current structure
                script = """
                    // This attempts to extract puzzle data from the game state
                    // May need to be adjusted based on NYT's current implementation
                    return window.__PIPS_DATA__ || window.__GAME_DATA__ || null;
                """
                
                puzzle_data = driver.execute_script(script)
                
                if puzzle_data:
                    print("Extracted puzzle from browser")
                    puzzle = PuzzleParser.from_json_dict(puzzle_data)
                    return puzzle
                else:
                    print("Could not extract puzzle data from page")
                    print("Tip: You may need to manually copy the puzzle JSON from your browser's DevTools")
                    return None
            
            finally:
                driver.quit()
        
        except Exception as e:
            print(f"Error during browser automation: {e}")
            return None
