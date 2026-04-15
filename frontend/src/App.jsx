import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Trophy, Activity, Calendar } from 'lucide-react';
import PlayerPool from './components/PlayerPool';
import ResultsPage from './components/ResultsPage';
import BotDialogue from './components/BotDialogue';
import RosterSidebar from './components/RosterSidebar';
import HistoryPage from './components/HistoryPage';
import AuthModal from './components/AuthModal';
import { supabase } from './supabase';
import { User as UserIcon, LogOut, History } from 'lucide-react';

const API_BASE = "https://fantasy-draft-sim-production.up.railway.app";

function App() {
  const [draftId, setDraftId] = useState(null);
  const [state, setState] = useState(null);
  const [available, setAvailable] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedYear, setSelectedYear] = useState(2023);

  const [results, setResults] = useState(null);
  const [user, setUser] = useState(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [showHistory, setShowHistory] = useState(false);

  useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
    });

    return () => subscription.unsubscribe();
  }, []);

  const getHeaders = async () => {
    const { data: { session } } = await supabase.auth.getSession();
    if (session?.access_token) {
      return { 'Authorization': `Bearer ${session.access_token}` };
    }
    return {};
  };

  const availableYears = [2018, 2019, 2020, 2021, 2022, 2023, 2024];

  // Initialize Draft
  const initDraft = async (year = selectedYear) => {
    setLoading(true);
    setResults(null);
    setState(null);
    setAvailable([]);
    try {
      const headers = await getHeaders();
      const res = await axios.post(`${API_BASE}/draft/init`, { year }, { headers });
      setDraftId(res.data.draft_id);
      fetchState(res.data.draft_id);
    } catch (err) {
      setError("Failed to initialize draft. Is the backend running?");
    }
    setLoading(false);
  };

  const fetchResults = async (id) => {
    try {
      const headers = await getHeaders();
      const res = await axios.post(`${API_BASE}/draft/${id}/evaluate`, {}, { headers });
      setResults(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchState = async (id) => {
    try {
      const headers = await getHeaders();
      const res = await axios.get(`${API_BASE}/draft/${id}/state`, { headers });
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
      const headers = await getHeaders();
      const res = await axios.get(`${API_BASE}/draft/${id}/available?limit=50`, { headers });
      setAvailable(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handlePick = async (playerId) => {
    if (!state?.is_user_turn) return;
    try {
      const headers = await getHeaders();
      await axios.post(`${API_BASE}/draft/${draftId}/pick`, { player_id: playerId }, { headers });
      fetchState(draftId);
    } catch (err) {
      alert("Invalid pick or slot full!");
    }
  };

  const handleBotPick = async (id) => {
    try {
      const headers = await getHeaders();
      await axios.post(`${API_BASE}/draft/${id}/pick`, {}, { headers });
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
            {user ? (
              <div className="flex gap-3 items-center">
                <button 
                  onClick={() => setShowHistory(true)}
                  className="p-2 text-slate-400 hover:text-cyan-400 transition-colors"
                  title="My Drafts"
                >
                  <History size={20} />
                </button>
                <div className="h-8 w-[1px] bg-white/10 mx-1" />
                <div className="flex flex-col items-end mr-2">
                  <span className="text-[10px] uppercase font-bold text-slate-500">Hunter</span>
                  <span className="text-xs font-semibold text-slate-300">{user.email.split('@')[0]}</span>
                </div>
                <button 
                  onClick={() => supabase.auth.signOut()}
                  className="p-2 text-slate-400 hover:text-red-400 transition-colors"
                >
                  <LogOut size={18} />
                </button>
              </div>
            ) : (
              <button 
                onClick={() => setIsAuthOpen(true)}
                className="btn-primary px-4 py-2 flex items-center gap-2"
              >
                <UserIcon size={16} />
                Sign In to Save
              </button>
            )}

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
        
        {showHistory ? (
          <div className="col-span-12">
            <HistoryPage user={user} onBack={() => setShowHistory(false)} />
          </div>
        ) : (
          <>
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
          </>
        )}
      </main>

      <AuthModal 
        isOpen={isAuthOpen} 
        onClose={() => setIsAuthOpen(false)} 
        onAuthSuccess={(user) => setUser(user)} 
      />
    </div>
  );
}

export default App;

