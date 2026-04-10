
import pandas as pd
import numpy as np

def calculate_z_scores(df, categories, is_pitcher=False):
    """
    Calculate Z-Scores for the specified categories.
    Z = (x - mean) / std
    """
    if df is None or len(df) == 0:
        return df
        
    # Create a copy to avoid modifying the original
    df = df.copy()
    
    # We only want to calculate Z-scores for players with significant playing time
    # This prevents extreme outliers (e.g., a guy with 1 AB and 1 H having a high Z-score for AVG)
    if is_pitcher:
        # Minimum 20 Innings Pitched for pitchers
        mask = df['IP'] >= 20
    else:
        # Minimum 150 At Bats for hitters
        mask = df['AB'] >= 150
        
    filtered_df = df[mask]
    
    if len(filtered_df) == 0:
        return df

    z_score_columns = []
    
    for cat in categories:
        mean = filtered_df[cat].mean()
        std = filtered_df[cat].std()
        
        col_name = f'z_{cat}'
        df[col_name] = (df[cat] - mean) / std
        
        # Invert Z-score for ERA and WHIP (lower is better)
        if cat in ['ERA', 'WHIP']:
            df[col_name] = -df[col_name]
            
        z_score_columns.append(col_name)
    
    # Sum of Z-scores is the total value
    df['total_z'] = df[z_score_columns].sum(axis=1)
    
    # Return only the players who met the criteria
    res_df = df[mask].copy()
    
    # Sort by total value
    res_df = res_df.sort_values('total_z', ascending=False)
    
    return res_df

def calculate_projected_stats(player_stats_by_year, categories):
    """
    Calculate projected stats for the next year based on a weighted 3-year average.
    Weights: T-1 (50%), T-2 (30%), T-3 (20%)
    """
    weights = [0.5, 0.3, 0.2]
    projected = {cat: 0.0 for cat in categories}
    total_weight = 0.0
    
    for i, year_df in enumerate(player_stats_by_year):
        if year_df is not None and not year_df.empty:
            weight = weights[i]
            for cat in categories:
                projected[cat] += year_df[cat].iloc[0] * weight
            total_weight += weight
            
    if total_weight > 0:
        # Normalize in case some years were missing
        for cat in categories:
            projected[cat] /= total_weight
            
    return projected

def get_point_in_time_pool(draft_year, loader_func, categories, is_pitcher=False):
    """
    Returns a player pool with projected valuations based ONLY on stats 
    prior to the draft_year. Use this to ensure bots don't use future knowledge.
    """
    from loader import get_player_positions
    
    # 1. Load historical data
    years_to_load = [draft_year - 1, draft_year - 2, draft_year - 3]
    historical_data = [loader_func(y) for y in years_to_load]
    
    # Load positions for the most recent year
    positions = get_player_positions(draft_year - 1)
    
    # 2. Identify all players in the previous year (base pool)
    base_year_df = historical_data[0]
    if base_year_df is None:
        return None
        
    # Deduplicate base year: Sum stats for players who changed teams
    # We group by playerID and name, and sum all numeric columns
    numeric_cols = base_year_df.select_dtypes(include=[np.number]).columns.tolist()
    base_year_df = base_year_df.groupby(['playerID', 'name'])[numeric_cols].sum().reset_index()
        
    if positions is not None and not is_pitcher:
        base_year_df = base_year_df.merge(positions, on='playerID', how='left')
        
    projected_records = []
    
    # 3. For each player in the base year, calculate projected stats
    for _, player in base_year_df.iterrows():
        pid = player['playerID']
        name = player['name']
        pos = player.get('POS', 'P' if is_pitcher else 'UTIL')
        
        # Get this specific player's stats across historical years
        player_years = []
        for df in historical_data:
            if df is not None:
                p_stat = df[df['playerID'] == pid]
                player_years.append(p_stat if not p_stat.empty else None)
            else:
                player_years.append(None)
                
        proj_stats = calculate_projected_stats(player_years, categories)
        proj_stats['playerID'] = pid
        proj_stats['name'] = name
        proj_stats['POS'] = pos
        # We need AB/IP for the mask in calculate_z_scores
        proj_stats['AB'] = player.get('AB', 0) if not is_pitcher else 0
        proj_stats['IP'] = player.get('IP', 0) if is_pitcher else 0
        
        projected_records.append(proj_stats)
        
    projected_df = pd.DataFrame(projected_records)
    
    # 4. Calculate Z-Scores based on these projected stats
    valued_pool = calculate_z_scores(projected_df, categories, is_pitcher=is_pitcher)
    
    # 5. Apply Position Scarcity Adjustments
    valued_pool = apply_position_adjustments(valued_pool)
    
    return valued_pool

def apply_position_adjustments(df):
    """
    Applies position scarcity multipliers to the total_z score.
    Catchers (C) and Shortstops (SS) are traditionally scarcer than 
    First Basemen (1B) or Outfielders (OF).
    """
    multipliers = {
        'C': 1.25,
        'SS': 1.1,
        '2B': 1.05,
        '3B': 1.05,
        'OF': 0.95,
        '1B': 0.9,
        'P': 1.0   # Baseline for pitchers
    }
    
    if 'POS' not in df.columns:
        return df
        
    def get_mult(pos):
        return multipliers.get(pos, 1.0)
        
    df['total_z'] = df.apply(lambda row: row['total_z'] * get_mult(row['POS']), axis=1)
    
    # Re-sort after adjustments
    df = df.sort_values('total_z', ascending=False)
    
    return df
