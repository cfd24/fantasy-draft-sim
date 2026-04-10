
import sys
import os
import pandas as pd

# Add backend to path
sys.path.append(os.path.abspath("backend"))

from loader import load_full_player_pool, HITTER_CATEGORIES, PITCHER_CATEGORIES
from data.valuation import calculate_z_scores
from draft.engine import DraftSession
from draft.bots.adp_bot import ADPBot

def run_simulation(year=2023, num_teams=10, num_rounds=15):
    print(f"--- FANTASY BASEBALL DRAFT SIMULATOR ({year}) ---")
    
    # 1. Load Data
    print("Loading player pool and calculating valuations...")
    batting, pitching = load_full_player_pool(year)
    
    # 2. Calculate Valuations
    valued_hitters = calculate_z_scores(batting, HITTER_CATEGORIES)
    valued_pitchers = calculate_z_scores(pitching, PITCHER_CATEGORIES, is_pitcher=True)
    
    # Combine into a single pool for the draft
    cols = ['playerID', 'name', 'POS', 'total_z']
    pool = pd.concat([valued_hitters[cols], valued_pitchers[cols]])
    pool = pool.sort_values('total_z', ascending=False)
    
    # 3. Initialize Draft
    draft = DraftSession(num_teams, num_rounds)
    
    print(f"Starting draft: {num_teams} teams, {num_rounds} rounds.")
    print("-" * 50)
    
    # 4. Run Draft
    picked_ids = set()
    
    while not draft.is_complete:
        team_idx = draft.get_current_team_index()
        
        # Get subset of available players
        available_players = pool[~pool['playerID'].isin(picked_ids)]
        
        # Simple Logic: Try to pick the best player that fits the roster
        top_candidates = available_players.head(50)
        found_player = False
        
        for _, player in top_candidates.iterrows():
            if draft.make_pick(player['playerID'], player['name'], player['POS']):
                picked_ids.add(player['playerID'])
                pick_data = draft.picks_log[-1]
                print(f"Pick {pick_data['pick']}: {pick_data['team']} takes {pick_data['player_name']} ({pick_data['pos']})")
                found_player = True
                break
        
        if not found_player:
            # If no player can fit, we might be in trouble (drafting too many pitchers?)
            # For simplicity, we just skip (or draft a BN if possible)
            draft.current_pick += 1

    print("-" * 50)
    print("Draft Complete!")
    
    # 5. Show a sample roster
    print("\nSample Roster (Team 1):")
    for p in draft.teams[0].players:
        print(f"  {p['slot']}: {p['name']} ({p['pos']})")

if __name__ == "__main__":
    run_simulation()
