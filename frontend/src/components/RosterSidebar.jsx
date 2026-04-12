import React from 'react';
import { Users } from 'lucide-react';

function RosterSidebar({ state }) {
  return (
    <div className="glass-panel p-6 flex-grow">
      <h2 className="card-title flex items-center gap-2">
        <Users size={18} className="text-accent-secondary" />
        Your Roster
      </h2>
      <div className="space-y-2 max-h-[50vh] overflow-y-auto pr-2">
        {state?.rosters[state?.user_team_index]?.length === 0 && (
          <div className="py-12 text-center text-secondary text-sm border-2 border-dashed border-white/5 rounded-xl">
            Waiting for your first pick...
          </div>
        )}
        {state?.rosters[state?.user_team_index]?.map((player, i) => (
          <div key={i} className="flex justify-between items-center p-3 rounded-lg bg-white/5 border border-white/5 group hover:border-accent-primary/30 transition-all">
              <div>
              <div className="text-[10px] text-accent-secondary font-bold tracking-widest mb-1">{player.slot}</div>
              <div className="text-sm font-bold">{player.name}</div>
              </div>
              <div className="text-[10px] bg-white/10 px-1.5 py-0.5 rounded font-mono text-secondary">{player.pos}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default RosterSidebar;
