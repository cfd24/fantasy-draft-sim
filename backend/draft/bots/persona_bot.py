
import json
import os
import random

class PersonaBot:
    """
    An advanced bot that uses category weights and dialogue based on ROADMAP.md personalities.
    All bots implement the signature: pick(available_players, my_roster, round_num, all_rosters)
    """
    def __init__(self, team_name, archetype_name="Balanced", weights=None):
        self.team_name = team_name
        self.archetype_name = archetype_name
        self.weights = weights or {}
        self.dialogue = self._load_dialogue(archetype_name)
        self.last_quote = ""

    def _load_dialogue(self, archetype_name):
        """Load bot-specific dialogue from JSON files."""
        # Convert "The Speedster" -> "speedster"
        filename = archetype_name.lower().replace(" ", "_").replace("the_", "") + ".json"
        
        # Look in dialogue directory relative to this file
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        file_path = os.path.join(base_path, "dialogue", filename)
        
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                return json.load(f)
        return {"name": archetype_name, "quotes": {"generic": ["Let's build a winner."]}}

    def get_quote(self, context="generic"):
        """Returns a random quote from the bot's dialogue library."""
        quotes = self.dialogue.get("quotes", {}).get(context, self.dialogue["quotes"].get("generic", []))
        if quotes:
            return random.choice(quotes)
        return ""

    def calculate_custom_value(self, player):
        """Calculate player value based on bot weights."""
        custom_val = 0.0
        z_cols = [c for c in player.index if c.startswith('z_')]
        for col in z_cols:
            stat_name = col.replace('z_', '')
            weight = self.weights.get(stat_name, 1.0)
            custom_val += player[col] * weight
        return custom_val

    def pick(self, available_players, my_roster, round_num=1, all_rosters=None):
        """
        Picks the best player based on custom valuation. 
        Matches roadmap signature.
        """
        if available_players.empty:
            return None
            
        pool = available_players.copy()
        pool['custom_value'] = pool.apply(self.calculate_custom_value, axis=1)
        pool = pool.sort_values('custom_value', ascending=False)
        
        # Choose the top player
        pick = pool.iloc[0]
        
        # Decide on a quote context
        # In V1, we'll just use random generic or specific logic
        self.last_quote = self.get_quote("generic")
        
        return pick

# Roadmap Archetypes
ARCHETYPES = {
    "Analytics Bro": {
        "HR": 1.2, "SO": 1.2, "AVG": 0.8 # Focus on power/K, ignore AVG
    },
    "Old School Stan": {
        "AVG": 2.0, "W": 2.0, "RBI": 1.5, "ERA": 0.5 # Focus on old school stats
    },
    "The Speedster": {
        "SB": 3.0, "R": 1.5
    },
    "The Power Hungry": {
        "HR": 3.0, "RBI": 2.0
    },
    "The Reach King": {
        # Strategically picks based on slightly modified rankings
    },
    "Hometown Hero": {
        # Overvalues hometown teams, handles inside dialogue logic if needed
        "total_z": 0.5
    },
    "Sleeper Cell": {
        # Focuses heavily on high variance or rookies
        "total_z": 0.8
    }
}

def create_bot(team_name, archetype_name):
    # Map from pre-defined archetypes or return Balanced if not found
    weights = ARCHETYPES.get(archetype_name, {})
    return PersonaBot(team_name, archetype_name=archetype_name, weights=weights)
