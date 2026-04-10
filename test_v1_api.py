
import requests
import json

BASE_URL = "http://localhost:8000"

def test_v1_engine():
    print("--- Testing Roadmap V1 Engine ---")
    
    # 1. Initialize Draft for 2023
    print("\n1. Initializing 2023 Draft...")
    init_res = requests.post(f"{BASE_URL}/draft/init", json={
        "year": 2023,
        "num_teams": 10,
        "num_rounds": 17
    })
    init_data = init_res.json()
    draft_id = init_data["draft_id"]
    print(f"Success! Draft ID: {draft_id}")
    
    # 2. Verify State (Roster Depth)
    state_res = requests.get(f"{BASE_URL}/draft/{draft_id}/state")
    state = state_res.json()
    print(f"Current Pick: {state['current_pick']}")
    print(f"User Turn: {state['is_user_turn']}")
    
    # 3. Make Human Pick (Aaron Judge - judgeaa01)
    print("\n2. Making Human Pick (Team 1 take Aaron Judge)...")
    pick_res = requests.post(f"{BASE_URL}/draft/{draft_id}/pick", json={
        "player_id": "judgeaa01"
    })
    print(f"Human Pick Result: {pick_res.json()['status']}")
    
    # 4. Make Bot Pick (Observe Personality/Dialogue)
    print("\n3. Triggering Bot Pick (Team 2)...")
    bot_res = requests.post(f"{BASE_URL}/draft/{draft_id}/pick")
    bot_data = bot_res.json()
    print(f"Bot Persona: {bot_data.get('persona', 'N/A')}")
    print(f"Bot Pick: {bot_data.get('pick', {}).get('player_name', 'N/A')}")
    print(f"Bot Quote: \"{bot_data.get('quote', '...')}\"")
    
    # 5. Evaluate Draft (The Oracle)
    print("\n4. Running 'The Oracle' Evaluation...")
    eval_res = requests.post(f"{BASE_URL}/draft/{draft_id}/evaluate")
    standings = eval_res.json()
    
    print("\n--- Preliminary Leaderboard (Actual 2023 Results) ---")
    for team in standings[:3]:
        print(f"{team['team_name']}: {team['total_points']} pts")

if __name__ == "__main__":
    try:
        test_v1_engine()
    except Exception as e:
        print(f"\nError: {e}")
        print("Make sure the FastAPI server is running with: cd backend && .venv/bin/python -m uvicorn main:app --reload")
