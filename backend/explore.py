import pandas as pd
from loader import get_batting_stats, get_pitching_stats

# Tell Pandas not to cut off columns so you can see everything in your terminal
pd.set_option('display.max_columns', None)

print("Fetching 2023 Batter Stats. This might take a few seconds (fetching from web)...")
batters_2023 = get_batting_stats(2023)

if batters_2023 is not None:
    print("\n================== 2023 BATTERS ==================")
    print(f"Total Batters found: {len(batters_2023)}")
    
    # Normalize column names between sources (FanGraphs vs Bref vs Savant)
    cols = batters_2023.columns.tolist()
    
    # Print every single column name available
    print("\nAVAILABLE COLUMNS (first 20):")
    print(cols[:20])

    # Try to find common 5x5 categories or fallbacks
    # FanGraphs uses AVG, Bref uses BA
    mapper = {
        'AVG': 'BA',
        'last_name, first_name': 'Name',
        'hr': 'HR',
        'rbi': 'RBI',
        'sb': 'SB'
    }
    
    # Standard 5x5 categories for hitters
    display_cols = []
    for c in ['Name', 'HR', 'RBI', 'SB', 'BA', 'OBP', 'AVG']:
        if c in cols:
            display_cols.append(c)
        elif mapper.get(c) in cols:
            # Add a copy if we use a mapping
            batters_2023[c] = batters_2023[mapper.get(c)]
            display_cols.append(c)

    print("\nSAMPLE DATA (Top 15):")
    if display_cols:
        print(batters_2023[display_cols].head(15))
    else:
        print(batters_2023.head(15))
else:
    print("Failed to fetch 2023 Batters.")

print("\n\nFetching 2023 Pitcher Stats...")
pitchers_2023 = get_pitching_stats(2023)

if pitchers_2023 is not None:
    print("\n================== 2023 PITCHERS ==================")
    print(f"Total Pitchers found: {len(pitchers_2023)}")
    
    # Try common 5x5 categories for pitchers
    p_cols = pitchers_2023.columns.tolist()
    
    # Map for pitchers
    p_mapper = {
        'last_name, first_name': 'Name',
        'xera': 'ERA',
        'xwoba': 'WHIP' # xwoba is roughly analogous to WHIP in value tracking if ERA is also handled
    }
    
    p_display_cols = []
    # Standard 5x5 categories + fallback metrics
    for c in ['Name', 'W', 'ERA', 'WHIP', 'SO', 'SV', 'K', 'xera', 'xwoba']:
        if c in p_cols:
            p_display_cols.append(c)
        elif p_mapper.get(c) in p_cols:
            pitchers_2023[c] = pitchers_2023[p_mapper.get(c)]
            p_display_cols.append(c)

    print("\nSAMPLE DATA (Top 15):")
    if p_display_cols:
        print(pitchers_2023[p_display_cols].head(15))
    else:
        print(pitchers_2023.head(15))

else:
    print("Failed to fetch 2023 Pitchers.")

