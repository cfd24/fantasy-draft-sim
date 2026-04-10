
import math

class Roster:
    """
    Manages the roster for a single team.
    Standard roster slots (simplified for V1):
    H: 1B, 2B, 3B, SS, OF, OF, OF, UTIL
    P: SP, SP, RP
    BN: BN, BN, BN, BN
    Total: 15 spots
    """
    SLOTS = {
        'C': 1, '1B': 1, '2B': 1, '3B': 1, 'SS': 1, 'OF': 3, 'UTIL': 1,
        'SP': 2, 'RP': 2,
        'BN': 4
    }
    
    def __init__(self, team_name):
        self.team_name = team_name
        self.players = []
        self.filled_slots = {slot: 0 for slot in self.SLOTS}

    def add_player(self, player_id, player_name, position):
        """
        Adds a player to the first available eligible slot.
        """
        # Map Pitcher (P) to SP or RP based on slot availability
        target_pos = position
        if position == 'P':
            if self.filled_slots['SP'] < self.SLOTS['SP']:
                target_pos = 'SP'
            elif self.filled_slots['RP'] < self.SLOTS['RP']:
                target_pos = 'RP'
            else:
                target_pos = 'BN'
                
        # Try primary position
        if target_pos in self.SLOTS and self.filled_slots[target_pos] < self.SLOTS[target_pos]:
            self.filled_slots[target_pos] += 1
            self.players.append({'playerID': player_id, 'name': player_name, 'pos': position, 'slot': target_pos})
            return True
            
        # Try UTIL (Hitters only)
        hitters = ['1B', '2B', '3B', 'SS', 'OF', 'C']
        if position in hitters and self.filled_slots['UTIL'] < self.SLOTS['UTIL']:
            self.filled_slots['UTIL'] += 1
            self.players.append({'playerID': player_id, 'name': player_name, 'pos': position, 'slot': 'UTIL'})
            return True
            
        # Try BN
        if self.filled_slots['BN'] < self.SLOTS['BN']:
            self.filled_slots['BN'] += 1
            self.players.append({'playerID': player_id, 'name': player_name, 'pos': position, 'slot': 'BN'})
            return True
            
        return False # Roster full or no eligible slots

class DraftSession:
    def __init__(self, num_teams, num_rounds):
        self.num_teams = num_teams
        self.num_rounds = num_rounds
        self.teams = [Roster(f"Team {i+1}") for i in range(num_teams)]
        self.current_pick = 1
        self.picks_log = []
        
    @property
    def is_complete(self):
        return self.current_pick > (self.num_teams * self.num_rounds)

    def get_current_team_index(self):
        pick_idx = self.current_pick - 1
        round_num = math.floor(pick_idx / self.num_teams) + 1
        pos_in_round = pick_idx % self.num_teams
        
        if round_num % 2 == 1:
            # Odd round: 1 -> 10
            return pos_in_round
        else:
            # Even round: 10 -> 1
            return self.num_teams - 1 - pos_in_round

    def make_pick(self, player_id, player_name, position):
        if self.is_complete:
            return False
            
        team_idx = self.get_current_team_index()
        team = self.teams[team_idx]
        
        if team.add_player(player_id, player_name, position):
            self.picks_log.append({
                'pick': self.current_pick,
                'team': team.team_name,
                'player_name': player_name,
                'playerID': player_id,
                'pos': position
            })
            self.current_pick += 1
            return True
        return False
