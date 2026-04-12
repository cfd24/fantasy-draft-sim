import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Activity, Calendar } from 'lucide-react';
import PlayerPool from './components/PlayerPool';
import ResultsPage from './components/ResultsPage';
import BotDialogue from './components/BotDialogue';
import RosterSidebar from './components/RosterSidebar';

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

function App() {
  const [draftId, setDraftId] = useState(null);
  const [state, setState] = useState(null);
  const [available, setAvailable] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState(2023);

  const [results, setResults] = useState(null);

  const availableYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024];

  // Initialize Draft
  const initDraft = async (year = selectedYear) => {
    setLoading(true);
    setResults(null);
    setState(null);
    setAvailable([]);
    try {
      const res = await axios.post(`${API_BASE}/draft/init`, { year });
      setDraftId(res.data.draft_id);
      fetchState(res.data.draft_id);
    } catch (err) {
      setError("Failed to initialize draft. Is the backend running?");
    }
    setLoading(false);
  };

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
      const res = await axios.get(`${API_BASE}/get_state` ? `${API_BASE}/draft/${id}/state` : `${API_BASE}/draft/${id}/state`);
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
    initDraft(2023);
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
          <h1 className="text-3xl font-bold gradient-text">Fantasy Draft Sim <span className="text-sm font-light uppercase tracking-widest ml-2 opacity-50">v1.1</span></h1>
          <p className="text-secondary flex items-center gap-2 mt-1">
            <Calendar size={14} className="text-accent-secondary" /> 
            Backtesting Draft Year: {state?.year || selectedYear}
          </p>
        </div>
        
        <div className="flex gap-4 items-center">
          {!draftId && (
             <div className="flex gap-2 items-center mr-4">
               <span className="text-xs uppercase opacity-50 font-bold">Time Machine:</span>
               <select 
                value={selectedYear}
                onChange={(e) => setSelectedYear(parseInt(e.target.value))}
                className="bg-white/5 border border-white/10 rounded px-2 py-1 text-xs focus:ring-1 focus:ring-accent-primary outline-none"
               >
                 {availableYears.map(y => <option key={y} value={y} className="bg-bg-dark">{y}</option>)}
               </select>
               <button onClick={() => initDraft()} className="btn-primary px-3 py-1 text-[10px]">Jump</button>
             </div>
          )}

          {draftId && (
            <div className="glass-panel px-4 py-2 flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${state?.is_user_turn && !state?.is_complete ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-amber-500 opacity-50 animate-pulse'}`} />
              <span className="text-xs font-bold uppercase tracking-wider">
                {state?.is_user_turn && !state?.is_complete ? 'Your Turn' : state?.is_complete ? 'Simulation Complete' : 'Bot Drafting...'}
              </span>
            </div>
          )}
        </div>
      </header>

      <main className="grid grid-cols-12 gap-6 relative">
        {loading && (
          <div className="absolute inset-0 z-50 flex items-center justify-center bg-bg-dark/40 backdrop-blur-sm">
             <div className="text-center font-bold tracking-tighter text-2xl animate-bounce">Initializing Reality...</div>
          </div>
        )}
        
        {/* Player Pool Column */}
        <section className="col-span-12 lg:col-span-8">
          <div className="glass-panel p-6 h-[80vh] flex flex-col">
            {state?.is_complete ? (
              <ResultsPage state={state} results={results} />
            ) : (
              <PlayerPool 
                available={available} 
                search={search} 
                setSearch={setSearch} 
                state={state} 
                handlePick={handlePick} 
              />
            )}
          </div>
        </section>

        {/* Roster & Dialogue Column */}
        <section className="col-span-12 lg:col-span-4 flex flex-col gap-6">
          <BotDialogue state={state} />
          <RosterSidebar state={state} />
        </section>
      </main>
    </div>
  );
}

export default App;

