# backend/db.py
# Supabase Database Utility for Fantasy Draft Simulator

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from .env
load_dotenv()

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    supabase: Client = None
else:
    supabase: Client = create_client(url, key)

def create_draft_record(user_id, year, num_teams, num_rounds):
    """Initializes a draft in the database."""
    if not supabase: return None
    
    data = {
        "user_id": user_id,
        "year": year,
        "num_teams": num_teams,
        "num_rounds": num_rounds,
        "status": "in_progress"
    }
    result = supabase.table("drafts").insert(data).execute()
    return result.data[0]["id"] if result.data else None

def save_pick(draft_id, pick_num, player_id, player_name, team_idx, pos, persona=None, quote=None):
    """Syncs a single pick to the database."""
    if not supabase: return
    
    data = {
        "draft_id": draft_id,
        "pick_num": pick_num,
        "player_id": player_id,
        "player_name": player_name,
        "team_idx": team_idx,
        "pos": pos,
        "persona": persona,
        "quote": quote
    }
    supabase.table("picks").insert(data).execute()

def save_final_results(draft_id, results_list):
    """Saves the final scoreboard and marks draft as complete."""
    if not supabase: return
    
    # results_list should be a list of dicts from the scoring engine
    formatted_results = []
    for res in results_list:
        formatted_results.append({
            "draft_id": draft_id,
            "team_name": res.get("team_name"),
            "total_points": res.get("total_points"),
            "rank": res.get("rank"),
            "is_user_team": res.get("is_user_team", False)
        })
    
    # 1. Save scores
    supabase.table("draft_results").insert(formatted_results).execute()
    
    # 2. Mark draft as completed
    supabase.table("drafts").update({"status": "completed"}).eq("id", draft_id).execute()

def get_user_draft_history(user_id):
    """Fetches a list of completed drafts for a specific user."""
    if not supabase: return []
    
    result = supabase.table("drafts") \
        .select("*, draft_results(*)") \
        .eq("user_id", user_id) \
        .eq("status", "completed") \
        .order("created_at", desc=True) \
        .execute()
    
    return result.data
