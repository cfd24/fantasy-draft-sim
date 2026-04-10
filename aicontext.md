# AI Context: Fantasy Baseball Draft Simulator

**Purpose of this File:**
To provide quick context to any AI or human working on this specific project. **MANDATORY:** This file MUST be kept up to date whenever significant architectural changes, new scripts, or dependencies are added.

## Overview
This is a full-stack fantasy baseball draft backtesting platform. It allows users to simulate snake drafts using point-in-time historical data (e.g., draft like it's 2021, without knowing what actually happened). After a draft finishes, the system reveals the actual season stats to score the teams.

It also supports an LLM-powered AI GM bot that drafts on behalf of a team and explains its choices using underlying Statcast and FanGraphs data.

## Important Architectural Notes
- **Git Remote:** `git@github.com:cfd24/fantasy-draft-sim.git` (Main repo).
- **Point-in-Time Integrity:** It is strictly forbidden to leak future stats into the draft phase.
- **Valuation Method:** Player value is dynamically calculated via a z-score method across standard 5x5 Roto categories.
- **Environment Fix:** Fixed a critical `cryptography` architecture mismatch (`arm64` vs `x86_64`) on Mac by building from source.
- **Data Ingestion (`loader.py`):** Uses a **global requests patch** with browser-level headers to bypass 403 Forbidden errors on FanGraphs/BRef.
- **Caching:** Local cache in `backend/cache/` to minimize web requests.
- **Current Data Status:** Using Lahman Baseball Database (1871-2024) for historical backtesting.
- **V1 Core Engine:** Fully integrated with 17-man rosters, position scarcity multipliers (C: 1.25x), bot dialogue system, and "The Oracle" scoring engine.

## Next/Ongoing Steps Summary
Transitioning to **Phase 1: SF Launch**. The immediate priority is the **React Frontend** to visualize the draft board, player pool, and bot dialogue.


*For full project specifications and timelines, please consult the `README.md`.*
