
import os
import pandas as pd
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loader import load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES, CACHE_DIR
from data.valuation import get_point_in_time_pool

def prime_year_cache(year):
    """
    Generates and saves the point-in-time valuation pool for a given year.
    """
    print(f"\n--- Priming Data for {year} ---")
    
    # Check if already cached (optional, but good for CLI)
    hitters_cache = os.path.join(CACHE_DIR, f"valuation_hitters_{year}.csv")
    pitchers_cache = os.path.join(CACHE_DIR, f"valuation_pitchers_{year}.csv")
    
    if os.path.exists(hitters_cache) and os.path.exists(pitchers_cache):
        print(f"Pool for {year} already primed in cache.")
        return

    # 1. Generate Pools
    print(f"Generating Hitter Pool for {year}...")
    hitters = get_point_in_time_pool(year, load_lahman_batting, HITTER_CATEGORIES)
    
    print(f"Generating Pitcher Pool for {year}...")
    pitchers = get_point_in_time_pool(year, load_lahman_pitching, PITCHER_CATEGORIES, is_pitcher=True)
    
    # 2. Save to Cache
    if hitters is not None:
        hitters.to_csv(hitters_cache, index=False)
        print(f"Saved {len(hitters)} hitters to {hitters_cache}")
        
    if pitchers is not None:
        pitchers.to_csv(pitchers_cache, index=False)
        print(f"Saved {len(pitchers)} pitchers to {pitchers_cache}")

if __name__ == "__main__":
    # Range of years for Time Machine
    target_years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    
    print(f"Starting bulk data priming for years: {target_years}")
    for y in target_years:
        prime_year_cache(y)
    print("\nBulk Priming Complete.")
