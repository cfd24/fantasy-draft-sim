
import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_results_analytics():
    print("--- Testing Results Analytics ---")
    
    # 1. Start a draft
    try:
        init_res = requests.post(f"{API_BASE}/draft/init", json={"year": 2023, "num_teams": 2, "num_rounds": 2})
        draft_id = init_res.json()["draft_id"]
        print(f"Draft initialized: {draft_id}")
        
        # 2. Make some picks
        # Get available players
        avail = requests.get(f"{API_BASE}/draft/{draft_id}/available?limit=5").json()
        for i in range(4):
            # Human pick (seat 0) or Bot (handled by main.py logic if we call /pick without ID)
            # Actually main.py /pick handles bot automatically if it's bot turn.
            requests.post(f"{API_BASE}/draft/{draft_id}/pick", json={"player_id": avail[i]["playerID"]})
            print(f"Pick {i+1} made.")
            time.sleep(0.5)

        # 3. Evaluate
        eval_res = requests.post(f"{API_BASE}/draft/{draft_id}/evaluate")
        results = eval_res.json()
        
        print("\nResults Sample:")
        first_team = results[0]
        print(json.dumps(first_team, indent=2))
        
        if "top_steal" in first_team:
            print("\n✅ SUCCESS: Analytics (Steals/Busts) are present in the results.")
        else:
            print("\n❌ FAILURE: Analytics missing from results.")
            
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_results_analytics()
