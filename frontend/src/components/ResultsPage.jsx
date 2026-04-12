import React from 'react';
import { Trophy, TrendingUp, TrendingDown, Award, BarChart3 } from 'lucide-react';
import { motion } from 'framer-motion';
import { 
  Radar, RadarChart, PolarGrid, 
  PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer 
} from 'recharts';

function ResultsPage({ state, results }) {
  if (!results) return (
    <div className="flex-grow flex items-center justify-center">
      <div className="text-center italic opacity-50 animate-pulse">Consulting The Oracle...</div>
    </div>
  );

  const userTeamIndex = state?.user_team_index ?? 0;
  const userTeamName = `Team ${userTeamIndex + 1}`;
  const userResult = results.find(r => r.team_name === userTeamName);
  
  // Prepare Radar Data
  const categories = [
    { key: 'R', label: 'Runs' },
    { key: 'HR', label: 'HR' },
    { key: 'RBI', label: 'RBI' },
    { key: 'SB', label: 'SB' },
    { key: 'AVG', label: 'AVG' },
    { key: 'W', label: 'Wins' },
    { key: 'SO', label: 'K' },
    { key: 'SV', label: 'Saves' },
    { key: 'ERA', label: 'ERA' },
    { key: 'WHIP', label: 'WHIP' }
  ];

  const radarData = userResult ? categories.map(cat => ({
    subject: cat.label,
    value: userResult[`${cat.key}_pts`],
    fullMark: 10
  })) : [];

  return (
    <div className="flex-grow overflow-y-auto pr-2 custom-scrollbar">
      <header className="text-center mb-10">
        <motion.div
           initial={{ scale: 0.8, opacity: 0 }}
           animate={{ scale: 1, opacity: 1 }}
           className="inline-block p-4 rounded-full bg-amber-500/10 mb-4"
        >
          <Trophy size={48} className="text-amber-500 drop-shadow-[0_0_15px_#f59e0b]" />
        </motion.div>
        <h2 className="text-4xl font-black tracking-tighter mb-2">The Oracle's Verdict</h2>
        <p className="text-secondary">Historical analysis for the {state?.year} MLB Season.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-12">
        {/* Radar Chart Section */}
        <div className="glass-panel p-6 flex flex-col items-center">
          <h3 className="card-title self-start flex items-center gap-2">
            <BarChart3 size={18} className="text-accent-primary" />
            Your Roster Balance
          </h3>
          <div className="w-full h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                < PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                <PolarRadiusAxis angle={30} domain={[0, 10]} tick={false} axisLine={false} />
                <Radar
                  name="Points"
                  dataKey="value"
                  stroke="#6366f1"
                  fill="#6366f1"
                  fillOpacity={0.5}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
          <p className="text-xs text-secondary mt-4 text-center italic">
            Visualizing your strength across all 10 Roto categories.
          </p>
        </div>

        {/* Top Performers Section */}
        <div className="flex flex-col gap-4">
          <h3 className="card-title flex items-center gap-2">
            <Award size={18} className="text-accent-secondary" />
            Key Draft Insights
          </h3>
          
          <div className="glass-panel p-5 border-l-4 border-l-emerald-500">
             <div className="flex justify-between items-start mb-2">
               <span className="text-xs font-bold uppercase tracking-widest text-accent-success">Greatest Steal</span>
               <TrendingUp size={16} className="text-accent-success" />
             </div>
             <div className="text-xl font-bold">{userResult?.top_steal}</div>
             <div className="text-sm text-secondary">
               Drafted significantly later than his actual end-of-season value ranking.
               <span className="text-accent-success font-mono ml-2">+{userResult?.steal_diff} spots</span>
             </div>
          </div>

          <div className="glass-panel p-5 border-l-4 border-l-red-500">
             <div className="flex justify-between items-start mb-2">
               <span className="text-xs font-bold uppercase tracking-widest text-accent-danger">Biggest Bust</span>
               <TrendingDown size={16} className="text-accent-danger" />
             </div>
             <div className="text-xl font-bold">{userResult?.biggest_bust}</div>
             <div className="text-sm text-secondary">
               Failed to live up to his draft position based on historical output.
               <span className="text-accent-danger font-mono ml-2">{userResult?.bust_diff} spots</span>
             </div>
          </div>
        </div>
      </div>

      {/* Standings Table */}
      <h3 className="card-title mb-4">Final Standings</h3>
      <div className="space-y-2 pb-8">
        {results.map((res, i) => (
          <motion.div 
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: i * 0.05 }}
            key={res.team_name}
            className={`flex justify-between items-center p-4 rounded-xl border ${res.team_name === userTeamName ? 'bg-accent-primary/20 border-accent-primary/50 ring-1 ring-accent-primary/30' : 'bg-white/5 border-white/5'}`}
          >
            <div className="flex items-center gap-4">
              <span className={`text-2xl font-black w-8 ${res.team_name === userTeamName ? 'text-accent-primary' : 'opacity-20'}`}>#{i+1}</span>
              <div>
                <div className="text-lg font-bold">{res.team_name} {res.team_name === userTeamName && '(You)'}</div>
                <div className="text-xs text-secondary">Total category points across hitting & pitching</div>
              </div>
            </div>
            <div className="text-2xl font-mono font-bold text-accent-success">{res.total_points.toFixed(1)} <span className="text-xs uppercase opacity-50">pts</span></div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default ResultsPage;
