# Fantasy Baseball Draft Simulator
### A full-stack AI-powered fantasy baseball draft platform with historical backtesting

---

## Project Overview

A web application where users can simulate fantasy baseball snake drafts against AI bots using real historical MLB data. The core hook: draft any year from 2015–2024 as if you don't know what happened, then see how your team actually performed that season. An AI GM bot (powered by an LLM) can draft for you, explaining every pick in plain English using Statcast and FanGraphs data.

This is not a "who should I pick" assistant — those already exist (FantasyPros, RotoWire). This is a **draft simulator and backtesting platform**: a playground where you test strategies, run bots against each other, and see objectively which approaches win.

**Target user**: fantasy baseball players who want to get better at drafting, test strategies, and have fun doing mock drafts in the offseason.

**Resume pitch**: "Built a full-stack fantasy baseball draft simulator with historical backtesting, a pluggable bot framework, and an LLM-powered AI GM that reasons over real Statcast data. Used by X real users during 2026 NFL/MLB season."

---

## Tech Stack

### Backend
- **Python** — core language
- **pybaseball** — scrapes Statcast (Baseball Savant), FanGraphs, and Baseball Reference
- **FastAPI** — REST API server
- **pandas** — data manipulation
- **SQLite or PostgreSQL** — store draft sessions, results
- **Anthropic or OpenAI API** — powers the AI GM bot

### Frontend
- **React** — UI framework
- **Recharts or D3** — data visualizations
- **Tailwind CSS** — styling
- **Deployed on**: Vercel (frontend) + Railway or Render (backend)

### Data Sources
- `pybaseball.batting_stats(year)` — season-level hitting stats from FanGraphs
- `pybaseball.pitching_stats(year)` — season-level pitching stats from FanGraphs
- `pybaseball.statcast(start, end)` — pitch-level Statcast data (exit velo, xBA, sprint speed, etc.)
- ADP data — scraped from FantasyPros historical ADP CSVs (publicly available)

---

## Core Features — V1 (what gets built first)

### 1. Historical Draft Mode (Backtesting)
- User selects a past season (2015–2024)
- System loads player pool from that year with stats available *up to draft day* only (no future data leakage)
- Standard snake draft: 10 teams, 15 rounds, configurable roster slots (C, 1B, 2B, 3B, SS, OF x3, SP x2, RP, UTIL, BN x4)
- After draft completes, system scores each team using the actual stats from that season
- Scoring: standard 5x5 roto (AVG, R, HR, RBI, SB for hitters / ERA, WHIP, W, K, SV for pitchers)
- Results page: your team's final standings vs all other bot teams

### 2. Bot Framework
- Clean, extensible interface: every bot implements a single `pick(available_players, my_team, round)` function
- Built-in bots to start:
  - **ADP Bot** — always takes best available by ADP (baseline/benchmark)
  - **Positional Scarcity Bot** — weighs position depth when deciding value
  - **Punt Strategy Bot** — ignores one category entirely, loads up on others
  - **Stars and Scrubs Bot** — reaches for elite players early, fills with late-round fliers
- Bots are deterministic so drafts are reproducible

### 3. AI GM Bot
- Powered by Claude or GPT-4
- User defines strategy in plain English: "I want a balanced team but prioritize stolen bases and batting average, I don't care about saves"
- Bot picks each player and explains its reasoning in 1-2 sentences: "Taking Trea Turner here — his sprint speed ranks top 1% and his xBA last season was .295 vs his actual .260, suggesting he's due to bounce back. SB upside fits our strategy."
- Bot only sees data available as of draft day for that historical year (point-in-time correctness)

### 4. Draft Board UI
- Live draft board showing all picks as they happen
- Player pool with filters (position, team, stat category)
- Your team panel on the side
- AI GM panel showing reasoning for each pick in real time
- After draft: results summary + actual season outcome

---

## V2 Features (post-launch, future work)

- **Head-to-head weekly scoring** — instead of season totals, simulate weekly matchups like a real H2H league
- **Waiver wire simulation** — after draft, a simplified waiver wire runs through the season
- **Multi-sport support** — same framework extended to NFL (skill positions, PPR scoring), NBA, NHL
- **Bot vs bot simulation** — run 1000 drafts overnight comparing strategies, see win rates
- **Custom scoring settings** — user-defined categories and weights
- **User accounts** — save draft history, track which strategies you've tried
- **Live draft mode** — connect to actual Yahoo/ESPN league via API and have the AI GM advise in real time
- **Trade analyzer** — evaluate trade offers using projected rest-of-season value

---

## Data Pipeline — Important Design Decisions

### Point-in-Time Data (Critical)
The whole backtesting concept depends on NOT leaking future data into the draft simulation. Implementation:
- For a 2021 backtest, the bot sees: 2018, 2019, 2020 stats + 2021 spring training projections (from FanGraphs Steamer/ZiPS, which are publicly archived)
- After draft completes, system loads actual 2021 full-season stats to score teams
- This is the technically interesting part — getting this right is what separates a real backtest from a fake one

### Player Valuation
- Base layer: z-score method — for each counting stat, calculate how many standard deviations above/below league average a player is, sum across all 5 categories → single value score
- This is the standard sabermetric approach (SGP — Standings Gain Points — is the more advanced version, implement later)
- Position scarcity adjustment: multiply value by position adjustment factor (SS and C are scarcer, OF and 1B are deeper)

### Scoring
- After draft, pull actual season stats for every drafted player
- Calculate team totals in each of 5x5 categories
- Rank all 10 teams in each category (1-10 points per category)
- Sum category points for final standings (max 50 points)

---

## File Structure (planned)

```
fantasy-draft-sim/
├── backend/
│   ├── main.py                  # FastAPI app, routes
│   ├── data/
│   │   ├── loader.py            # pybaseball wrappers, caching
│   │   ├── valuation.py         # player scoring / z-score logic
│   │   └── cache/               # cached CSVs so we don't hammer pybaseball
│   ├── draft/
│   │   ├── engine.py            # snake draft logic, turn management
│   │   ├── bots/
│   │   │   ├── base.py          # Bot interface / abstract class
│   │   │   ├── adp_bot.py       # always picks best ADP
│   │   │   ├── scarcity_bot.py  # positional scarcity aware
│   │   │   └── ai_gm.py        # LLM-powered bot
│   │   └── scoring.py           # end-of-season team scoring
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DraftBoard.jsx
│   │   │   ├── PlayerPool.jsx
│   │   │   ├── MyTeam.jsx
│   │   │   ├── AIPanel.jsx
│   │   │   └── ResultsPage.jsx
│   │   └── App.jsx
│   └── package.json
└── README.md
```

---

## Timeline

### Phase 0 — Now through July 8 (Spain, ~30 min/day)
Goal: understand the data, have core backend logic working before you get to SF.

**Week 1–2: Data Exploration**
- Install pybaseball: `pip install pybaseball`
- Pull batting_stats(2023) and pitching_stats(2023), look at what columns exist
- Understand what stats are available year-by-year going back to 2015
- Find and download historical ADP CSVs from FantasyPros

**Week 3–4: Player Valuation**
- Implement z-score valuation: for each of the 5x5 categories, compute z-scores across all players
- Sum z-scores → single "fantasy value" number per player
- Rank all players → this becomes your first draft ranking
- Sanity check: does your ranking roughly match known ADP? (Shohei, Judge should be top 5)

**Week 5–8: Snake Draft Engine (Python only, no UI)**
- Implement snake draft order (rounds alternate direction)
- Implement roster slots and eligibility rules (a player can only fill eligible positions)
- Implement ADP Bot (picks best available by your z-score ranking)
- Run a full 10-team, 15-round draft in the terminal and print the results
- Implement end-of-season scoring: given 10 teams of players, rank them by 5x5 categories

**By July 8 you have**: a working draft simulator in Python that runs in the terminal. No UI, no LLM, but the hard logic is done.

---

### Phase 1 — July 8 through mid-August (SF, full time)
Goal: ship a real web product.

**Week 1: Backend API**
- Wrap your Python draft engine in FastAPI
- Endpoints: `POST /draft/start`, `GET /draft/{id}/state`, `POST /draft/{id}/pick`, `GET /draft/{id}/results`
- Add data caching so pybaseball isn't scraped every request
- Add the AI GM bot: call LLM API with player context + team needs, parse response

**Week 2: Frontend — Draft Experience**
- React app with draft board component
- Player pool table with search and position filter
- My team panel
- Connect to backend API
- AI GM panel that streams reasoning text

**Week 3: Frontend — Results + Polish**
- Results page: your team stats vs other teams, final standings
- Historical outcome reveal: "here's what actually happened that season"
- Mobile-friendly layout
- Deploy: Vercel (frontend) + Railway (backend)

**Week 4: Bot vs Bot Mode + README**
- UI to run fully automated drafts (all 10 seats are bots)
- Watch bots draft against each other in fast-forward
- Write a solid README with screenshots, how it works, tech decisions
- Add to crisostomodunn.com

**Week 5: Buffer**
- Bug fixes, performance, edge cases
- Write a short blog post about one interesting technical decision (point-in-time data, or the z-score valuation system) — this alone makes recruiters stop scrolling
