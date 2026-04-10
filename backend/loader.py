import os
import pandas as pd
import requests
import pybaseball
from pybaseball import (
    batting_stats, 
    pitching_stats, 
    statcast_pitcher_expected_stats,
    statcast_batter_expected_stats
)
import time
import io
import glob

# Standard 5x5 Categories
HITTER_CATEGORIES = ['R', 'HR', 'RBI', 'SB', 'AVG']
PITCHER_CATEGORIES = ['W', 'SO', 'SV', 'ERA', 'WHIP']

# Enable pybaseball caching
pybaseball.cache.enable()

CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache")
LAHMAN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "lahman")
os.makedirs(CACHE_DIR, exist_ok=True)

# Patch requests with a realistic browser User-Agent
# This helps bypass some basic bot detection that blocks default Python requests
REAL_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}

# Global session with headers
session = requests.Session()
session.headers.update(REAL_HEADERS)

# Monkeypatch requests.get for pybaseball to use
original_get = requests.get
def patched_get(*args, **kwargs):
    kwargs['headers'] = {**REAL_HEADERS, **kwargs.get('headers', {})}
    return original_get(*args, **kwargs)

# We actually need to patch requests.get GLOBALLY because pybaseball imported it
requests.get = patched_get

def get_batting_stats(year):
    cache_file = os.path.join(CACHE_DIR, f"batting_{year}.csv")
    
    if os.path.exists(cache_file):
        print(f"Loading cached batting statistics for {year}...")
        return pd.read_csv(cache_file)

    print(f"Fetching {year} batting stats from FanGraphs...")
    try:
        df = batting_stats(year)
        if df is not None and len(df) > 0:
            df.to_csv(cache_file, index=False)
            return df
    except Exception as e:
        print(f"FanGraphs failed: {e}")

    print("Trying fallback: Statcast Expected Stats (Baseball Savant)...")
    try:
        df = statcast_batter_expected_stats(year)
        if df is not None and len(df) > 0:
            print("Notice: Using Statcast Expected Stats fallback.")
            df.to_csv(cache_file, index=False)
            return df
    except Exception as e:
        print(f"Statcast fallback failed: {e}")
    
    return None

def get_pitching_stats(year):
    cache_file = os.path.join(CACHE_DIR, f"pitching_{year}.csv")
    
    if os.path.exists(cache_file):
        print(f"Loading cached pitching statistics for {year}...")
        return pd.read_csv(cache_file)

    print(f"Fetching {year} pitching stats from FanGraphs...")
    try:
        df = pitching_stats(year)
        if df is not None and len(df) > 0:
            df.to_csv(cache_file, index=False)
            return df
    except Exception as e:
        print(f"FanGraphs failed: {e}")

    print("Trying fallback: Statcast Expected Stats (Baseball Savant)...")
    try:
        df = statcast_pitcher_expected_stats(year)
        if df is not None and len(df) > 0:
            print("Notice: Using Statcast Pitching fallback.")
            df.to_csv(cache_file, index=False)
            return df
    except Exception as e:
        print(f"Statcast Pitching fallback failed: {e}")
        
    return None

def load_lahman_batting(year):
    """Load historical batting stats from Lahman CSV for a specific year."""
    file_path = os.path.join(LAHMAN_DIR, "Batting.csv")
    people_path = os.path.join(LAHMAN_DIR, "People.csv")
    
    if not os.path.exists(file_path):
        print(f"Lahman Batting file not found at {file_path}")
        return None
        
    df = pd.read_csv(file_path)
    df = df[df['yearID'] == year].copy()
    
    # Calculate AVG
    df['AVG'] = (df['H'] / df['AB']).fillna(0)
    
    # Merge with People to get full names
    if os.path.exists(people_path):
        people = pd.read_csv(people_path, usecols=['playerID', 'nameFirst', 'nameLast'])
        df = df.merge(people, on='playerID', how='left')
        df['name'] = df['nameFirst'] + " " + df['nameLast']
        
    return df

def load_lahman_pitching(year):
    """Load historical pitching stats from Lahman CSV for a specific year."""
    file_path = os.path.join(LAHMAN_DIR, "Pitching.csv")
    people_path = os.path.join(LAHMAN_DIR, "People.csv")
    
    if not os.path.exists(file_path):
        print(f"Lahman Pitching file not found at {file_path}")
        return None
        
    df = pd.read_csv(file_path)
    df = df[df['yearID'] == year].copy()
    
    # Calculate WHIP: (BB + H) / IP
    # Lahman has IPouts (innings pitched * 3)
    df['IP'] = df['IPouts'] / 3
    df['WHIP'] = ((df['BB'] + df['H']) / df['IP']).fillna(0)
    
    # Merge with People to get full names
    if os.path.exists(people_path):
        people = pd.read_csv(people_path, usecols=['playerID', 'nameFirst', 'nameLast'])
        df = df.merge(people, on='playerID', how='left')
        df['name'] = df['nameFirst'] + " " + df['nameLast']
        
    return df

def get_player_positions(year):
    """Get the primary position for each player in a given year based on games played."""
    file_path = os.path.join(LAHMAN_DIR, "Fielding.csv")
    if not os.path.exists(file_path):
        return None
        
    df = pd.read_csv(file_path)
    df = df[df['yearID'] == year].copy()
    
    if len(df) == 0:
        return None
    
    # For each player, find the position where they played the most games
    # POS values: P, C, 1B, 2B, 3B, SS, OF
    idx = df.groupby('playerID')['G'].idxmax()
    return df.loc[idx, ['playerID', 'POS']]

def load_full_player_pool(year):
    """Load both hitters and pitchers for a year with stats and positions."""
    batting = load_lahman_batting(year)
    pitching = load_lahman_pitching(year)
    positions = get_player_positions(year)
    
    if batting is not None and positions is not None:
        batting = batting.merge(positions, on='playerID', how='left')
    
    if pitching is not None:
        # Pitchers are always 'P' in valuation context for roster slots
        pitching['POS'] = 'P'
        
    return batting, pitching
