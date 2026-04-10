
import os
import requests
import json

class AIGMBot:
    """
    LLM-powered AI GM that drafts based on user-defined strategy.
    """
    def __init__(self, team_name, strategy_text="Best available balanced team"):
        self.team_name = team_name
        self.strategy_text = strategy_text
        self.last_reasoning = ""
        self.api_key = os.getenv("LLM_API_KEY")

    def pick(self, available_players, my_roster, round_num=1, all_rosters=None):
        """
        Uses LLM to decide on a pick based on strategy and current roster needs.
        """
        # 1. Format the context for the LLM
        roster_summary = [f"{p['slot']}: {p['name']} ({p['pos']})" for p in my_roster.players]
        top_candidates = available_players.head(20).to_dict(orient="records")
        
        prompt = f"""
        Drafting for: {self.team_name}
        Strategy: {self.strategy_text}
        Round: {round_num}
        Current Roster: {roster_summary}
        
        Top Available Players (Z-Score Ranked):
        {json.dumps(top_candidates, indent=2)}
        
        Based on the strategy and roster needs, who should I pick? 
        Respond with JSON: {{"playerID": "...", "reasoning": "..."}}
        """
        
        # 2. Call LLM (Placeholder for now, returns top Z-score if no API key)
        if not self.api_key:
            top_player = available_players.iloc[0]
            self.last_reasoning = f"Choosing {top_player['name']} as the best available player for round {round_num}."
            return top_player
            
        # Realistic implementation for OpenAI/Anthropic would go here
        # For now, we return top player to keep the demo functional
        top_player = available_players.iloc[0]
        self.last_reasoning = f"Simulating AI reasoning: {top_player['name']} is the optimal pick."
        return top_player
