import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Users, Search, Activity, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = "http://localhost:8000";

function App() {
  const [draftId, setDraftId] = useState(null);
  const [state, setState] = useState(null);
  const [available, setAvailable] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Initialize Draft
  const initDraft = async (year = 2023) => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_BASE}/draft/init`, { year });
      setDraftId(res.data.draft_id);
      fetchState(res.data.draft_id);
    } catch (err) {
      setError("Failed to initialize draft. Is the backend running?");
    }
    setLoading(false);
  };

  const [results, setResults] = useState(null);

  const fetchResults = async (id) => {
    try {
      const res = await axios.post(`${API_BASE}/draft/${id}/evaluate`);
      setResults(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchState = async (id) => {
    try {
      const res = await axios.get(`${API_BASE}/draft/${id}/state`);
      setState(res.data);
      if (res.data.is_complete) {
        fetchResults(id);
        return;
      }
      if (!res.data.is_user_turn) {
        // Auto-handle bot turn
        setTimeout(() => handleBotPick(id), 1200);
      }
      fetchAvailable(id);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchAvailable = async (id) => {
    try {
      const res = await axios.get(`${API_BASE}/draft/${id}/available?limit=50`);
      setAvailable(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePick = async (playerId) => {
    if (!state?.is_user_turn) return;
    try {
      await axios.post(`${API_BASE}/draft/${draftId}/pick`, { player_id: playerId });
      fetchState(draftId);
    } catch (err) {
      alert("Invalid pick or slot full!");
    }
  };

  const handleBotPick = async (id) => {
    try {
      await axios.post(`${API_BASE}/draft/${id}/pick`);
      fetchState(id);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    // Start with 2023 as default
    initDraft();
  }, []);

  if (error) return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="glass-panel p-8 text-center max-w-md">
        <Activity className="mx-auto mb-4 text-red-500" size={48} />
        <h1 className="text-2xl font-bold mb-2">Backend Connection Error</h1>
        <p className="text-secondary mb-6">{error}</p>
        <button onClick={() => window.location.reload()} className="btn-primary">Retry Connection</button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen p-6">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Fantasy Draft Sim <span className="text-sm font-light uppercase tracking-widest ml-2 opacity-50">v1.0</span></h1>
          <p className="text-secondary flex items-center gap-2 mt-1">
            <Trophy size={14} className="text-accent-secondary" /> 
            Backtesting Draft Year: {state?.year || 2023}
          </p>
        </div>
        
        <div className="flex gap-4">
          <div className="glass-panel px-4 py-2 flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${state?.is_user_turn ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500 opacity-50'}`} />
            <span className="text-xs font-bold uppercase tracking-wider">{state?.is_user_turn ? 'Your Turn' : 'Bot Drafting...'}</span>
          </div>
        </div>
      </header>

      <main className="grid grid-cols-12 gap-6">
        {/* Player Pool Column */}
        <section className="col-span-12 lg:col-span-8">
          <div className="glass-panel p-6 h-[80vh] flex flex-col">
            {state?.is_complete ? (
              <div className="flex-grow flex flex-col items-center justify-center py-12">
                <Trophy size={64} className="text-amber-500 mb-6 drop-shadow-[0_0_15px_#f59e0b]" />
                <h2 className="text-4xl font-black mb-2 tracking-tighter">Draft Complete</h2>
                <p className="text-secondary mb-12">The Oracle has spoken. Here are the historical results for {state?.year}.</p>
                
                <div className="w-full max-w-2xl space-y-3">
                  {results ? results.map((res, i) => (
                    <motion.div 
                      initial={{ x: -20, opacity: 0 }}
                      animate={{ x: 0, opacity: 1 }}
                      transition={{ delay: i * 0.1 }}
                      key={res.team_name}
                      className={`flex justify-between items-center p-4 rounded-xl border ${i === 0 ? 'bg-amber-500/10 border-amber-500/30' : 'bg-white/5 border-white/5'}`}
                    >
                      <div className="flex items-center gap-4">
                        <span className="text-2xl font-black opacity-20 w-8">#{i+1}</span>
                        <div className="text-lg font-bold">{res.team_name} {res.team_name.includes(state?.user_team_index + 1) && '(You)'}</div>
                      </div>
                      <div className="text-2xl font-mono font-bold text-accent-success">{res.total_points.toFixed(1)} <span className="text-xs uppercase opacity-50">pts</span></div>
                    </motion.div>
                  )) : (
                    <div className="text-center italic opacity-50">Calculating final standings...</div>
                  )}
                </div>
              </div>
            ) : (
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
            )}
          </div>
        </section>

        {/* Roster & Dialogue Column */}
        <section className="col-span-12 lg:col-span-4 flex flex-col gap-6">
          {/* Bot Dialogue Box */}
          <AnimatePresence mode="wait">
            {!state?.is_user_turn && (
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="glass-panel p-6 border-accent-secondary/30 relative"
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-indigo-500 to-sky-500 flex items-center justify-center shadow-lg">
                    <Users size={20} className="text-white" />
                  </div>
                  <div>
                    <div className="text-sm font-bold uppercase tracking-tighter">Drafting Now</div>
                    <div className="text-xs text-secondary italic">Strategic Thinking...</div>
                  </div>
                </div>
                <div className="bg-white/5 p-4 rounded-xl border border-white/5 text-sm italic">
                   "Calculating optimal Statcast profiles for this roster slot..."
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Roster Summary */}
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
        </section>
      </main>
    </div>
  );
}

export default App;
