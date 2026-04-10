
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from loader import load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES
from data.valuation import calculate_z_scores

def test_valuation(year):
    print(f"--- Testing Valuation for {year} ---")
    
    # Hitters
    batting = load_lahman_batting(year)
    if batting is not None:
        valued_hitters = calculate_z_scores(batting, HITTER_CATEGORIES)
        print("\nTop 10 Valued Hitters (5x5 Z-Scores):")
        print(valued_hitters[['name', 'total_z', 'HR', 'RBI', 'R', 'SB', 'AVG']].head(10))
        
    # Pitchers
    pitching = load_lahman_pitching(year)
    if pitching is not None:
        valued_pitchers = calculate_z_scores(pitching, PITCHER_CATEGORIES, is_pitcher=True)
        print("\nTop 10 Valued Pitchers (5x5 Z-Scores):")
        print(valued_pitchers[['name', 'total_z', 'W', 'SO', 'SV', 'ERA', 'WHIP']].head(10))

if __name__ == "__main__":
    test_valuation(2023)
