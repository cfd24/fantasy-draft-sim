
import pandas as pd
import numpy as np
from loader import load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES

def calculate_team_performance(rosters, year):
    """
    Calculates the actual performance of each team based on the stats in the target year.
    Returns a rankings dataframe.
    """
    # 1. Load actual season stats for the year
    batting = load_lahman_batting(year)
    pitching = load_lahman_pitching(year)
    
    # 2. Score each team
    team_stats = []
    
    for team_name, players in rosters.items():
        # Get playerIDs for this team
        pids = [p['playerID'] for p in players]
        
        # Sum hitter stats
        team_batting = batting[batting['playerID'].isin(pids)]
        h_stats = {cat: team_batting[cat].sum() for cat in HITTER_CATEGORIES if cat != 'AVG'}
        # Hitter AVG is a special case (total H / total AB)
        h_stats['AVG'] = (team_batting['H'].sum() / team_batting['AB'].sum()) if team_batting['AB'].sum() > 0 else 0
        
        # Sum pitcher stats
        team_pitching = pitching[pitching['playerID'].isin(pids)]
        p_stats = {cat: team_pitching[cat].sum() for cat in PITCHER_CATEGORIES if cat not in ['ERA', 'WHIP']}
        
        # IP for averaging
        total_ip = team_pitching['IP'].sum()
        if total_ip > 0:
            # ERA: (ER * 9) / IP
            p_stats['ERA'] = (team_pitching['ER'].sum() * 9) / total_ip
            # WHIP: (H + BB) / IP
            p_stats['WHIP'] = (team_pitching['H'].sum() + team_pitching['BB'].sum()) / total_ip
        else:
            p_stats['ERA'] = 0
            p_stats['WHIP'] = 0
            
        # Combine
        combined_stats = {**h_stats, **p_stats}
        combined_stats['team_name'] = team_name
        team_stats.append(combined_stats)
        
    df = pd.DataFrame(team_stats)
    
    # 3. Calculate Roto Points (1-10 per category)
    num_teams = len(rosters)
    categories = HITTER_CATEGORIES + PITCHER_CATEGORIES
    
    points_df = pd.DataFrame()
    points_df['team_name'] = df['team_name']
    
    for cat in categories:
        ascending = (cat in ['ERA', 'WHIP'])
        if ascending:
            points_df[f'{cat}_pts'] = df[cat].rank(ascending=False)
        else:
            points_df[f'{cat}_pts'] = df[cat].rank(ascending=True)
            
    # Include raw stats in the breakdown for the UI
    for cat in categories:
        points_df[cat] = df[cat]

    # Sum points
    pts_cols = [c for c in points_df.columns if c.endswith('_pts')]
    points_df['total_points'] = points_df[pts_cols].sum(axis=1)
    
    # 4. Steals & Busts Analysis
    # We need to rank EVERY player in the dataset by actual season performance to find steals
    batting['full_z'] = (batting[HITTER_CATEGORIES].sub(batting[HITTER_CATEGORIES].mean()) / batting[HITTER_CATEGORIES].std()).sum(axis=1)
    pitching['full_z'] = (pitching[PITCHER_CATEGORIES].sub(pitching[PITCHER_CATEGORIES].mean()) / pitching[PITCHER_CATEGORIES].std()).sum(axis=1)
    
    all_players = pd.concat([batting[['playerID', 'name', 'full_z']], pitching[['playerID', 'name', 'full_z']]])
    all_players['actual_rank'] = all_players['full_z'].rank(ascending=False)
    
    steals_busts = []
    for team_name, players in rosters.items():
        team_analysis = []
        for p in players:
            actual = all_players[all_players['playerID'] == p['playerID']]
            if not actual.empty:
                rank = actual.iloc[0]['actual_rank']
                diff = p['pick_num'] - rank
                team_analysis.append({'name': p['name'], 'diff': diff, 'rank': rank, 'pick': p['pick_num']})
        
        if team_analysis:
            best = max(team_analysis, key=lambda x: x['diff'])
            worst = min(team_analysis, key=lambda x: x['diff'])
            steals_busts.append({
                'team_name': team_name,
                'top_steal': best['name'],
                'steal_diff': int(best['diff']),
                'biggest_bust': worst['name'],
                'bust_diff': int(worst['diff'])
            })
            
    sb_df = pd.DataFrame(steals_busts)
    points_df = points_df.merge(sb_df, on='team_name', how='left')

    # Sort by total points
    points_df = points_df.sort_values('total_points', ascending=False)
    
    return points_df
