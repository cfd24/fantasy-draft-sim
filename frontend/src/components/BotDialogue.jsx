import React from 'react';
import { Users } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function BotDialogue({ state }) {
  // If we have recent picks, the latest pick might have quotes.
  // The backend might send the latest bot quote in the response, but
  // since `state` itself doesn't explicitly store quotes per pick yet,
  // we are showing a generalized AI loading state while `!is_user_turn` is true.
  
  return (
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
              "Analyzing the available talent pool and team needs..."
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default BotDialogue;
