
import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from loader import load_full_player_pool, load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES
from data.valuation import get_point_in_time_pool
from draft.bots.persona_bot import create_bot

def verify_persona_draft(draft_year=2023):
    print(f"--- Verifying Point-in-Time Pool for {draft_year} ---")
    
    # Get projected pool (no future knowledge of 2023)
    hitters = get_point_in_time_pool(draft_year, load_lahman_batting, HITTER_CATEGORIES)
    pitchers = get_point_in_time_pool(draft_year, load_lahman_pitching, PITCHER_CATEGORIES, is_pitcher=True)
    
    # Combine and handle missing columns (e.g., Hitters don't have z_SO, Pitchers don't have z_SB)
    cols = ['playerID', 'name', 'POS', 'total_z', 'z_HR', 'z_SB', 'z_SO', 'z_W', 'z_ERA']
    
    h_limited = hitters.reindex(columns=cols).fillna(0)
    p_limited = pitchers.reindex(columns=cols).fillna(0)
    
    pool = pd.concat([h_limited, p_limited]).sort_values('total_z', ascending=False)
    
    print("\nTop 5 Overall (Predicted for 2023):")
    print(pool[['name', 'total_z']].head(5))

    # Test Speedster Persona
    speedster = create_bot("Bot 1", "The Speedster")
    speed_pick = speedster.pick(pool, None)
    
    print(f"\nSpeedster's #1 Pick: {speed_pick['name']} (z_SB: {speed_pick['z_SB']:.2f})")
    
    # Test Power Persona
    power_bot = create_bot("Bot 2", "The Power Hungry")
    power_pick = power_bot.pick(pool, None)
    
    print(f"Power Bot's #1 Pick: {power_pick['name']} (z_HR: {power_pick['z_HR']:.2f})")

if __name__ == "__main__":
    verify_persona_draft(2023)
