// frontend/src/components/HistoryPage.jsx
import axios from 'axios';
import { supabase } from '../supabase';
import { Calendar, Trophy, ChevronRight, Loader2, ArrowLeft } from 'lucide-react';

const API_BASE = "https://fantasy-draft-sim-production.up.railway.app";

export default function HistoryPage({ user, onBack }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const res = await axios.get(`${API_BASE}/drafts/user/history`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      });
      setHistory(res.data);
    } catch (err) {
      setError("Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center p-20 text-slate-400">
      <Loader2 className="animate-spin mb-4" size={32} />
      <p>Loading your draft legacy...</p>
    </div>
  );

  return (
    <div className="animate-in fade-in duration-500">
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={onBack}
          className="p-2 hover:bg-white/5 rounded-full text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft size={24} />
        </button>
        <h2 className="text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
          My Draft History
        </h2>
      </div>

      {history.length === 0 ? (
        <div className="glass-panel p-12 text-center">
          <Calendar className="mx-auto mb-4 opacity-20" size={48} />
          <p className="text-slate-400">You haven't completed any drafts yet. Time to make history!</p>
          <button onClick={onBack} className="mt-6 btn-primary px-6 py-2">Start a New Draft</button>
        </div>
      ) : (
        <div className="grid gap-4">
          {history.map((draft) => (
            <div 
              key={draft.id} 
              className="glass-panel p-6 hover:border-cyan-500/50 transition-all group flex items-center justify-between cursor-pointer"
            >
              <div className="flex items-center gap-6">
                <div className="w-12 h-12 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400 font-bold">
                  {draft.year}
                </div>
                <div>
                  <h3 className="font-bold text-lg group-hover:text-cyan-400 transition-colors">
                    Draft {draft.id.slice(0, 8)}
                  </h3>
                  <div className="flex gap-4 text-sm text-slate-400 mt-1">
                    <span className="flex items-center gap-1">
                      <Calendar size={14} /> {new Date(draft.created_at).toLocaleDateString()}
                    </span>
                    <span>•</span>
                    <span>{draft.num_teams} Teams</span>
                    <span>•</span>
                    <span>{draft.num_rounds} Rounds</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-8">
                {draft.draft_results && draft.draft_results.length > 0 && (
                  <div className="text-right">
                    <div className="text-xs uppercase font-bold text-slate-500 mb-1">Your Rank</div>
                    <div className="text-2xl font-black text-white flex items-center gap-2">
                       <Trophy size={20} className="text-amber-400" />
                       #{draft.draft_results.find(r => r.is_user_team)?.rank || '-'}
                    </div>
                  </div>
                )}
                <ChevronRight className="text-slate-600 group-hover:text-white transition-colors" />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
