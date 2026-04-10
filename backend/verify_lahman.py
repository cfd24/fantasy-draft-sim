
import sys
import os

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from loader import load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES

def verify_data(year):
    print(f"--- Verifying Lahman Data for {year} ---")
    
    # Batting
    batting = load_lahman_batting(year)
    if batting is not None:
        print(f"Batting: Found {len(batting)} players.")
        # Top HR hitters in 2023 should be Acuna, Olson, etc. (Lahman 2024 might have Olson record)
        top_hr = batting.sort_values('HR', ascending=False).head(5)
        print("\nTop 5 HR Hitters:")
        print(top_hr[['name', 'HR', 'RBI', 'R', 'SB', 'AVG']])
    else:
        print("Batting: Failed to load.")

    # Pitching
    pitching = load_lahman_pitching(year)
    if pitching is not None:
        print(f"\nPitching: Found {len(pitching)} players.")
        # Top Wins/SO
        top_so = pitching.sort_values('SO', ascending=False).head(5)
        print("\nTop 5 SO Pitchers:")
        print(top_so[['name', 'W', 'SO', 'SV', 'ERA', 'WHIP']])
    else:
        print("Pitching: Failed to load.")

if __name__ == "__main__":
    verify_data(2023)
