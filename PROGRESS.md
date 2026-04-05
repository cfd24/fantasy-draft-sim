# Daily Progress Log - Fantasy Baseball Draft Simulator

This file tracks the day-by-day evolution of the project. **MANDATORY:** Update this at the end of every working session.

---

## 2026-04-05: Phase 0 Kickoff & Data Ingestion Fix

### What Happened
- **Project Initialized**: Confirmed the repository structure and AI Context for the `fantasy-draft` sub-project.
- **Data Source Challenge**: Discovered that Baseball Reference and FanGraphs have implemented aggressive bot detection (403 Forbidden), breaking standard `pybaseball` stats fetching.
- **Architectural Solution**: 
  - Created `backend/loader.py` to centralize all data fetching.
  - Implemented a **global requests patch** with browser-like headers to bypass simple scraping blocks.
  - Added a **CSV Caching layer** (`backend/cache/`) to store data locally after the first pull.
  - Implemented **Statcast (Baseball Savant) fallbacks** for when primary leaderboard sources fail.
- **Success**: The `explore.py` script is now fully functional, pulling 2023 season data (Batters & Pitchers) and saving it to your local machine.

### Next Steps
- [ ] **Z-Score Valuation**: Implement the core player ranking logic using the z-score method across 5x5 Roto categories.
- [ ] **Data Cleaning**: Map the fallback Statcast metrics (like `xera`) more precisely to standard Roto categories for one-to-one comparison.
- [ ] **Phase 0 Draft Engine**: Start building the terminal-based snake draft logic once player rankings are refined.

### Stopping Point Status
- **Code**: `explore.py` is green and running.
- **Data**: 2023 Batting/Pitching CSVs are safely in your `cache/` folder.
- **Context**: AI Context is fully updated and aware of the new `loader.py` architecture.
