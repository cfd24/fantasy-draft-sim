# AI Context: Fantasy Baseball Draft Simulator

## Status
- **Phase 1 (Backtesting Engine & Analytics)**: COMPLETE ✅
- **Phase 2 (Deployment & Integration)**: COMPLETE ✅
- **Backend URL**: [fantasy-draft-sim-production.up.railway.app](https://fantasy-draft-sim-production.up.railway.app)
- **Live Portfolio**: [crisostomodunn.com/draft](https://www.crisostomodunn.com/draft)

## Overview
This is a full-stack fantasy baseball draft backtesting platform. It allows users to simulate snake drafts using point-in-time historical data (e.g., draft like it's 2021, without knowing what actually happened). After a draft finishes, the system reveals the actual season stats to score the teams.

## Architectural Notes
- **Git Remote:** `git@github.com:cfd24/fantasy-draft-sim.git`
- **Railway Deployment**: Configured via UI **Root Directory: /backend** and **Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT**.
- **Portfolio Integration**: Serves production built assets from `my-website/public/draft/`.
- **Valuation Method:** Dynamic z-score method across standard 5x5 Roto categories.
- **Scoring Engine**: Compares draft positions vs. end-of-season actual performance to identify "Steals" and "Busts".

## Next Milestones (Phase 3)
- **Supabase Integration**: Automate draft saving to a persistent database.
- **Auth**: User accounts to track personal draft history.
