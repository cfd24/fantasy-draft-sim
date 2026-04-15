# AI Context: Fantasy Baseball Draft Simulator

## Status
- **Phase 3 (Auth & Persistence)**: COMPLETE ✅
- **Backend URL**: [fantasy-draft-sim-production.up.railway.app](https://fantasy-draft-sim-production.up.railway.app)
- **Live Portfolio**: [crisostomodunn.com/draft](https://www.crisostomodunn.com/draft)
- **Supabase Project ID**: `oekmxqjidpbtgtmudcej`

## Overview
This is a full-stack fantasy baseball draft backtesting platform. It allows users to simulate snake drafts using point-in-time historical data.

## Architectural Notes
- **Git Remote:** `git@github.com:cfd24/fantasy-draft-sim.git`
- **Database (Supabase)**: Uses PostgreSQL for persistent storage of `drafts`, `picks`, and `draft_results`.
- **Auth (Supabase)**: Handles user Login/Signup with email verification.
- **Railway Deployment**: Root: `/backend`, Start: `uvicorn main:app`.
- **Valuation Method:** Dynamic z-score method across standard 5x5 Roto categories.

## Next Milestones (Phase 4)
- **Season Simulation**: Monte Carlo based forecasting.
- **Waiver Wire**: Dynamic mid-season roster changes.
