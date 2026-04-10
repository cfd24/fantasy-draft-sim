
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
import pandas as pd
from typing import List, Dict, Optional

# Import local modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loader import load_full_player_pool, load_lahman_batting, load_lahman_pitching, HITTER_CATEGORIES, PITCHER_CATEGORIES
from data.valuation import get_point_in_time_pool
from draft.engine import DraftSession
from draft.bots.persona_bot import create_bot, ARCHETYPES
from draft.scoring import calculate_team_performance

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Fantasy Baseball Draft API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the site domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
active_drafts: Dict[str, Dict] = {}

class DraftInit(BaseModel):
    year: int
    num_teams: int = 10
    num_rounds: int = 17 # Roadmap V1 default
    user_team_index: int = 0
    ai_gm_enabled: bool = False

@app.post("/draft/init")
async def init_draft(config: DraftInit):
    try:
        # 1. Generate point-in-time pool
        print(f"Initializing draft for {config.year}...")
        hitters = get_point_in_time_pool(config.year, load_lahman_batting, HITTER_CATEGORIES)
        pitchers = get_point_in_time_pool(config.year, load_lahman_pitching, PITCHER_CATEGORIES, is_pitcher=True)
        
        if hitters is None or pitchers is None:
            raise HTTPException(status_code=500, detail="Failed to load historical data")
            
        # Combine & clean
        cols = ['playerID', 'name', 'POS', 'total_z', 'z_HR', 'z_SB', 'z_SO', 'z_W', 'z_ERA']
        h_limited = hitters.reindex(columns=cols).fillna(0)
        p_limited = pitchers.reindex(columns=cols).fillna(0)
        pool = pd.concat([h_limited, p_limited]).sort_values('total_z', ascending=False)
        
        # 2. Create Draft Session
        draft_id = str(uuid.uuid4())
        session = DraftSession(config.num_teams, config.num_rounds)
        
        # 3. Create Bots for other seats
        bots = []
        archetypes = list(ARCHETYPES.keys())
        for i in range(config.num_teams):
            if i == config.user_team_index:
                bots.append(None) # Human seat
            else:
                arch = archetypes[i % len(archetypes)]
                bots.append(create_bot(f"Bot {i+1}", arch))
        
        active_drafts[draft_id] = {
            "session": session,
            "pool": pool,
            "bots": bots,
            "config": config,
            "year": config.year
        }
        
        return {"draft_id": draft_id, "year": config.year, "status": "initialized"}
    except Exception as e:
        print(f"Init failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/draft/{draft_id}/state")
async def get_state(draft_id: str):
    if draft_id not in active_drafts:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    data = active_drafts[draft_id]
    session = data["session"]
    
    return {
        "current_pick": session.current_pick,
        "is_complete": session.is_complete,
        "current_team_index": session.get_current_team_index(),
        "is_user_turn": data["bots"][session.get_current_team_index()] is None,
        "user_team_index": data["config"].user_team_index,
        "year": data["year"],
        "picks": session.picks_log,
        "rosters": [t.players for t in session.teams]
    }

class PickRequest(BaseModel):
    player_id: str

@app.post("/draft/{draft_id}/pick")
async def make_pick(draft_id: str, pick: Optional[PickRequest] = None):
    if draft_id not in active_drafts:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    data = active_drafts[draft_id]
    session = data["session"]
    pool = data["pool"]
    bots = data["bots"]
    
    if session.is_complete:
        return {"status": "complete"}
        
    team_idx = session.get_current_team_index()
    bot = bots[team_idx]
    
    # Get Available Players
    picked_ids = set(p['playerID'] for p in session.picks_log if 'playerID' in p)
    # We need to make sure playerID is in session.picks_log
    # Let's fix engine.py briefly or just use player_name if unique (ID is better)
    
    available = pool[~pool['playerID'].isin(picked_ids)]
    
    # 1. Handle Human Pick
    if bot is None: 
        if not pick:
            raise HTTPException(status_code=400, detail="It is your turn. Please provide a player_id.")
        
        target = available[available['playerID'] == pick.player_id]
        if target.empty:
            raise HTTPException(status_code=404, detail="Player not available or already picked")
        
        player = target.iloc[0]
        if session.make_pick(player['playerID'], player['name'], player['POS']):
            # Add playerID to the log entry manually if engine didn't
            session.picks_log[-1]['playerID'] = player['playerID']
            return {"status": "success", "pick": session.picks_log[-1]}
        else:
            raise HTTPException(status_code=400, detail="Invalid pick (roster full at that position)")
            
    # 2. Handle Bot Pick
    else:
        # Bots use their own persona logic to pick the best fit from the pool
        # Passing round_num to match roadmap bot signature
        round_num = (session.current_pick - 1) // session.num_teams + 1
        player = bot.pick(available, session.teams[team_idx], round_num=round_num)
        
        if player is not None and session.make_pick(player['playerID'], player['name'], player['POS']):
            session.picks_log[-1]['playerID'] = player['playerID']
            
            # Catch the quote if it's a PersonaBot
            quote = getattr(bot, "last_quote", "")
            
            return {
                "status": "bot_success", 
                "pick": session.picks_log[-1], 
                "persona": getattr(bot, "archetype_name", "Bot"),
                "quote": quote
            }
        session.current_pick += 1
        return {"status": "bot_failed_skipped"}

@app.get("/draft/{draft_id}/available")
async def get_available(draft_id: str, limit: int = 50, position: Optional[str] = None):
    if draft_id not in active_drafts:
        raise HTTPException(status_code=404, detail="Draft not found")
    
    data = active_drafts[draft_id]
    session = data["session"]
    pool = data["pool"]
    
    picked_ids = set(p['playerID'] for p in session.picks_log if 'playerID' in p)
    available = pool[~pool['playerID'].isin(picked_ids)]
    
    if position:
        available = available[available['POS'] == position]
        
    return available.head(limit).to_dict(orient="records")

@app.post("/draft/{draft_id}/evaluate")
async def evaluate_draft(draft_id: str):
    if draft_id not in active_drafts:
        raise HTTPException(status_code=404, detail="Draft not found")
        
    data = active_drafts[draft_id]
    session = data["session"]
    
    if not session.is_complete:
        # For testing, we might want to evaluate early, but roadmap says after draft.
        # I'll allow it for now if picks > 0 just to see if it works.
        if len(session.picks_log) == 0:
            raise HTTPException(status_code=400, detail="Draft has no picks yet")
        
    # Format rosters for scoring
    rosters_dict = {t.team_name: t.players for t in session.teams}
    
    # Calculate performance for the draft year
    performance = calculate_team_performance(rosters_dict, data["year"])
    
    return performance.to_dict(orient="records")
