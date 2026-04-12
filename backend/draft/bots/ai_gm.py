import os
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
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except ImportError:
                print("google-genai package not installed.")

    def pick(self, available_players, my_roster, round_num=1, all_rosters=None):
        """
        Uses LLM to decide on a pick based on strategy and current roster needs.
        """
        top_candidates = available_players.head(20).to_dict(orient="records")
        roster_summary = [f"{p['slot']}: {p['name']} ({p['pos']})" for p in my_roster.players]
        
        fallback_player = available_players.iloc[0]

        if not self.client:
            self.last_reasoning = f"[FALLBACK] No API Key. Choosing {fallback_player['name']} as highest Z-Score."
            return fallback_player

        prompt = f"""
        You are a highly analytical fantasy baseball GM drafting for team: {self.team_name}.
        Your overall strategy: {self.strategy_text}
        Current Draft Round: {round_num}
        Your Current Roster: {roster_summary}
        
        Top Available Players (Ranked by Z-Score Value):
        {json.dumps(top_candidates, indent=2)}
        
        Please select ONE player to draft from the available list that best fits your strategy and current roster needs.
        Respond ONLY with a valid JSON object in this exact format:
        {{"playerID": "xyz1", "reasoning": "Brief explanation of why this player was chosen."}}
        """
        
        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                }
            )
            
            result = json.loads(response.text)
            chosen_id = result.get('playerID')
            self.last_reasoning = result.get('reasoning', 'No reasoning provided.')
            
            # Find the chosen player in the dataframe
            match = available_players[available_players['playerID'] == chosen_id]
            if not match.empty:
                return match.iloc[0]
            else:
                self.last_reasoning = f"[FALLBACK] AI chose invalid ID: {chosen_id}. Defaulting to top Z-score."
                return fallback_player
                
        except Exception as e:
            print(f"AI GM Error: {e}")
            self.last_reasoning = f"[FALLBACK] API Error occurred. Choosing {fallback_player['name']} automatically."
            return fallback_player
