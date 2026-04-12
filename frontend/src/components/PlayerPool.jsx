import React from 'react';
import { Search } from 'lucide-react';

function PlayerPool({ available, search, setSearch, state, handlePick }) {
  return (
    <>
      <div className="flex justify-between items-center mb-6">
        <h2 className="card-title mb-0 flex items-center gap-2">
          <Search size={18} className="text-accent-primary" />
          Available Players
        </h2>
        <div className="relative">
          <input 
            type="text" 
            placeholder="Search players..."
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 ring-accent-primary/50"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      <div className="overflow-y-auto flex-grow rounded-lg border border-white/5">
        <table className="w-full text-left">
          <thead className="sticky top-0 bg-bg-dark z-10">
            <tr className="text-xs font-bold text-secondary uppercase tracking-widest border-b border-white/5">
              <th className="p-4">Rank</th>
              <th className="p-4">Player</th>
              <th className="p-4">Pos</th>
              <th className="p-4">Val</th>
              <th className="p-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {available
              .filter(p => p.name.toLowerCase().includes(search.toLowerCase()) || p.POS.toLowerCase().includes(search.toLowerCase()))
              .map((p, idx) => (
              <tr key={p.playerID} className="hover:bg-white/[0.02] transition-colors group">
                <td className="p-4 font-mono text-secondary text-sm">{idx + 1}</td>
                <td className="p-4">
                  <div className="font-bold">{p.name}</div>
                  <div className="text-[10px] text-secondary">ID: {p.playerID}</div>
                </td>
                <td className="p-4">
                  <span className="bg-white/5 px-2 py-0.5 rounded text-[10px] font-bold border border-white/5">{p.POS}</span>
                </td>
                <td className="p-4 font-mono text-accent-success">{p.total_z.toFixed(2)}</td>
                <td className="p-4 text-right">
                  <button 
                    disabled={!state?.is_user_turn}
                    onClick={() => handlePick(p.playerID)}
                    className={`btn-primary py-1 px-4 text-[10px] ${!state?.is_user_turn ? 'opacity-20 cursor-not-allowed grayscale' : ''}`}
                  >
                    Draft
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default PlayerPool;
