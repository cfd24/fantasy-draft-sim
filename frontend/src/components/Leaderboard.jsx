import React from 'react';
import { Trophy } from 'lucide-react';
import { motion } from 'framer-motion';

function Leaderboard({ state, results }) {
  return (
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
  );
}

export default Leaderboard;
