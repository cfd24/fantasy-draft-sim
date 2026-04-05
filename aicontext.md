# AI Context: Fantasy Baseball Draft Simulator

**Purpose of this File:**
To provide quick context to any AI or human working on this specific project. **MANDATORY:** This file MUST be kept up to date whenever significant architectural changes, new scripts, or dependencies are added.

## Overview
This is a full-stack fantasy baseball draft backtesting platform. It allows users to simulate snake drafts using point-in-time historical data (e.g., draft like it's 2021, without knowing what actually happened). After a draft finishes, the system reveals the actual season stats to score the teams.

It also supports an LLM-powered AI GM bot that drafts on behalf of a team and explains its choices using underlying Statcast and FanGraphs data.

## Important Architectural Notes
- **Point-in-Time Integrity:** It is strictly forbidden to leak future stats into the draft phase. For a 2021 backtest, only 2018-2020 stats and 2021 pre-season projections can be used to make decisions.
- **Valuation Method:** Player value is dynamically calculated via a z-score method across standard 5x5 Roto categories (AVG, R, HR, RBI, SB for hitters; ERA, WHIP, W, K, SV for pitchers), not arbitrary points.
- **Deployment & Infra:**
  - **Backend:** Python + FastAPI. Heavy use of the `pybaseball` library. 
  - **Data Ingestion (`loader.py`):** Due to aggressive bot detection on Baseball Reference and FanGraphs, all data fetching MUST pass through `backend/loader.py`. It implements robust `requests` patching (custom headers) and fallbacks to Statcast (Baseball Savant) data.
  - **Caching:** A local cache is maintained in `backend/cache/` to prevent repeated web requests and bypass 403 blocks.
  - **Frontend:** React + Vite + Tailwind CSS. Hosted on Vercel.

## Next/Ongoing Steps Summary
Currently operating under "Phase 0": Building out the core backend `pybaseball` ingestion, data exploration, computing z-score player valuation, and the snake draft engine logic entirely within Python/Terminal before any UI is built.

*For full project specifications and timelines, please consult the `README.md`.*
