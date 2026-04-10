
class ADPBot:
    """
    A simple bot that always picks the highest-valued player available.
    """
    def __init__(self, team_name):
        self.team_name = team_name

    def pick(self, available_players, my_roster):
        """
        Picks the top overall player from available_players.
        available_players is assumed to be sorted by total_z descending.
        """
        if available_players.empty:
            return None
            
        # Simplistic: just take the top one. 
        # Future: could check roster needs (e.g. dont draft 4 SPs if slots are full)
        for _, player in available_players.iterrows():
            # Check if this player can fit in our roster
            # We don't have the Roster object logic here yet, but we can try
            return player
            
        return available_players.iloc[0]
