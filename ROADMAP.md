# Fantasy Baseball Draft Simulator — Full Product Roadmap
### The complete vision, feature list, and implementation guide

---

## What This Is

A web app where you simulate fantasy baseball snake drafts against AI bot personalities using real historical MLB data. The core hook: draft any year from 2015–2024 as if you don't know what happened, then see how your team actually performed. An AI GM can draft for you, or you can watch bots draft against each other with funny dialogue. Eventually: simulate future seasons with ML-powered player projections.

**The dream version**: a fully featured mock draft platform with accounts, saved drafts, bot personalities, season simulation, and multiplayer — but for baseball nerds who actually want to learn how to draft better.

---

## V1 — Core Draft Simulator (Summer 2026, your main focus)

### 1. Data Pipeline
**What it does**: pulls real MLB player stats for any historical year, builds a player pool, ranks players using z-score valuation.

**How to implement**:
- Use `pybaseball` to pull `batting_stats(year)` and `pitching_stats(year)` from FanGraphs
- Cache everything as CSVs in `backend/cache/` so you don't hammer the API
- For each player, compute z-scores across all 5x5 roto categories:
  - Hitters: HR, RBI, R, SB, AVG
  - Pitchers: W, SV, ERA, WHIP, K
- Sum z-scores → single "fantasy value" per player
- Apply position scarcity multiplier (SS/C are scarcer, OF/1B are deeper)
- Result: a ranked player pool that updates per year

**Point-in-time correctness (critical)**:
- When simulating year X, only use stats from years X-3 to X-1
- Never leak actual season results into the draft phase
- After draft completes, load actual year X stats to score teams

**Tech**: Python, pandas, pybaseball, cached CSVs

---

### 2. Snake Draft Engine
**What it does**: manages turn order, roster slots, position eligibility, and pick validation for a 10-team snake draft.

**How to implement**:
- Snake order: rounds alternate direction (1→10 in odd rounds, 10→1 in even rounds)
- Standard roster slots: C, 1B, 2B, 3B, SS, OF, OF, OF, SP, SP, RP, RP, UTIL, BN, BN, BN, BN
- Position eligibility: a player can only fill eligible slots (e.g. a 1B/OF can go in either slot)
- Each team tracks: roster, filled slots, remaining needs
- Available player pool updates after each pick
- Draft state is serializable (can save/restore mid-draft)

**Bot interface (keep this clean — everything else builds on it)**:
```python
class Bot:
    def pick(self, available_players, my_roster, round_num, all_rosters) -> Player:
        raise NotImplementedError
```
Every bot, including the AI GM, implements this one function. That's it.

**Tech**: Python, FastAPI endpoint `POST /draft/{id}/pick`

---

### 3. Bot Personalities
**What it does**: 6-8 AI opponents with distinct strategies AND funny dialogue that pops up when they pick.

**Bots to build**:

| Bot Name | Strategy | Sample Dialogue |
|---|---|---|
| **The Analytics Bro** | drafts by xFIP, barrel%, xwOBA only | "This pick optimizes my Statcast profile significantly" |
| **Old School Stan** | drafts by AVG, W, RBI, hates WAR | "You can't measure heart with a spreadsheet" |
| **Hometown Hero** | always reaches for his favorite team's players | "Had to get my boy, doesn't matter what round" |
| **The Reach King** | drafts 3-4 rounds early consistently | "I just really believe in this guy" |
| **Punt Everything Guy** | picks one insane strategy and commits | "I don't need ERA if I have 12 closers" |
| **The Injury Magnet** | bad luck, always ends up with hurt players | "He was healthy when I drafted him I swear" |
| **Sleeper Cell** | only targets late round fliers and breakout candidates | "Round 14 value right here, mark my words" |
| **Your AI GM** | LLM-powered, strategy defined by user in plain English | explains every pick with real Statcast reasoning |

**Dialogue implementation**:
- each bot has a list of ~20 dialogue strings per situation (good pick, reach, value pick, late round, etc.)
- randomly selected from pool based on pick context
- displayed in the draft board UI as a chat bubble next to the bot's avatar
- AI GM dialogue is generated live by the LLM

**Tech**: Python bot classes, simple dialogue JSON files per bot, LLM API for AI GM

---

### 4. AI GM Bot
**What it does**: LLM-powered bot that drafts based on a strategy you define in plain English, explaining every pick with real data reasoning.

**How to implement**:
- User inputs strategy before draft: "prioritize stolen bases and batting average, don't care about saves"
- Each turn, send LLM a prompt containing:
  - Current available players (top 30 by value) with their stats
  - Your current roster and what positions you still need
  - The round number
  - Your defined strategy
  - What other teams have drafted (so it can react)
- LLM returns: chosen player + 1-2 sentence explanation
- Parse the response, validate the pick is legal, apply it

**Sample AI GM dialogue**:
> "Taking Trea Turner in round 3 — his sprint speed ranks top 1% of the league and his xBA last season was .295 vs his actual .260, suggesting he was unlucky on contact. Fits our stolen base priority perfectly."

**Cost management**: only call LLM for the AI GM's picks (not all 10 bots). With 15 rounds that's 15 LLM calls per draft. At ~$0.01/call = pennies per draft.

**Tech**: Anthropic or OpenAI API, FastAPI, prompt engineering

---

### 5. Results Page
**What it does**: after the draft, reveals how your team actually performed that season.

**Features**:
- Your team's actual season stats in each 5x5 category
- Final standings vs all 9 bot teams
- Player cards: projected value vs actual performance — who was a steal, who busted
- "Best pick" and "worst pick" of your draft highlighted
- Shareable result: "My 2021 draft finished 2nd out of 10 — 94th percentile"
- Comparison: "If you had taken X instead of Y in round 4, you would have finished 1st"

**How to implement**:
- after draft, pull actual full season stats for that year from pybaseball
- compute each team's totals in all 5 hitting + 5 pitching categories
- rank teams in each category (1-10 points each, max 50)
- sort final standings by total points
- highlight your team's rank

**Tech**: Python scoring engine, React results components, recharts for visualizations

---

### 6. Draft Board UI
**What it does**: the main visual interface — looks and feels like a real mock draft site.

**Features**:
- Live pick ticker showing all picks in order (like ESPN draft tracker)
- Player pool table with search, position filter, stat sort
- Your team panel on the right
- Bot dialogue panel — chat bubbles pop up when bots pick
- AI GM reasoning panel — streams text as it thinks
- Pick clock (optional — adds pressure)
- Color coding: green = great value, yellow = slight reach, red = big reach vs ADP

**How to implement**:
- React frontend, Tailwind CSS
- WebSocket connection so picks update in real time without page refresh
- Player pool sorted by z-score value by default
- Recharts for simple stat visualizations on player hover/click

**Tech**: React, Tailwind, WebSockets (FastAPI supports this natively), Recharts

---

## V2 — User Accounts + Draft History (Fall 2026 / side project)

### Features
- Sign up / log in (email or Google)
- Every draft you do is saved automatically
- Draft history page: see all your past drafts with year, strategy, final standing
- Stats across all your drafts: average finish, best draft, worst draft, favorite strategy
- "Your best ever draft was 2019 where you finished 1st out of 10 with a punt ERA strategy"
- Compare two of your past drafts side by side

### How to implement
- **Supabase** for auth + database (free tier, integrates perfectly with React + Vercel)
- Tables: `users`, `drafts`, `draft_picks`, `draft_results`
- Each draft saves: year, settings, all 150 picks in order, final standings
- Frontend auth with Supabase's built-in React hooks — takes like 2 hours to set up

**Tech**: Supabase, React, FastAPI

---

## V3 — Season Simulation (Senior Year / Big Feature)

### What it does
Instead of using historical results, simulate a future season from scratch. Draft the current year's players and see how your team performs across thousands of simulated seasons.

### Features
- Draft 2026 players using current projections
- Run 1000 Monte Carlo simulations of the season
- Each simulation: every player gets a randomly generated season based on their performance distribution
- Result: "your team wins the league 34% of the time across 1000 simulations"
- Injury simulation: players have injury probability based on historical data
- "Best case" and "worst case" scenarios for your team

### How to implement
- **Player performance distributions**: for each player, fit a distribution to their last 3 seasons of stats. Simple version: normal distribution centered on their average with historical variance.
- **Monte Carlo**: run N simulations, each time sample from each player's distribution to generate their season stats
- **Advanced version (ML)**: train a regression model on Statcast features (exit velocity, barrel%, sprint speed, age) to predict next season stats. Use the CSUA P100 GPUs for this.
- Libraries: scipy for distributions, numpy for fast simulation, scikit-learn for ML models

**Tech**: Python, numpy, scipy, scikit-learn, CSUA GPU server for training

---

## V4 — Waiver Wire + Injuries (V3 add-on)

### Features
- After draft, simulate a full season week by week
- Each week: some players get injured (following actual historical injury data for that year)
- Simplified waiver wire: top available player is auto-added when someone gets hurt
- Weekly matchup results if H2H league setting
- Trade offers from bots (simplified: bot offers you a player you need for one you have surplus of)

### How to implement
- Week-by-week simulation loop in Python
- Injury data from Baseball Reference (pybaseball has this)
- Waiver priority: reverse standings order (worst team gets first waiver claim)
- Bot trade logic: simple value comparison, offer trade if it improves both teams' weakest category

---

## V5 — Multiplayer Real Time Drafts (Big stretch goal)

### Features
- Create a draft room, share a link with friends
- Everyone joins and gets assigned a seat
- Live pick clock — 90 seconds per pick
- Real time updates for all participants
- Chat during the draft
- Auto-pick if someone's clock runs out (uses their AI GM)

### How to implement
- WebSockets for real time communication (already needed for V1)
- Room management: `POST /room/create`, `POST /room/join/{code}`
- Pick clock managed server-side
- This is essentially building a mini multiplayer game server
- Could use Redis for session state if it gets complex

---

## V6 — Multi Sport

### NFL (target: August 2026 launch — perfect timing for fantasy football season)
- Same exact framework, different data source
- Data: nflfastR (R package, has Python bindings) or Pro Football Reference via pybaseball-equivalent
- Scoring: PPR or standard, flex spots
- Bot personalities adapt: "The Running Back Zealot", "Zero RB Guy", "Quarterback Early Guy"
- Biggest difference from MLB: bye weeks matter, injury rate is higher, season is shorter

### NBA / NHL
- NBA: basketball-reference via nba_api Python package
- NHL: hockey-reference
- Each sport needs its own scoring system and position slots but the engine is identical

---

## V7 — ML-Powered Projections (The Research-Level Feature)

### What it does
Replace the simple z-score valuation with a real ML model trained on Statcast data that predicts next season performance.

### How to implement
- **Features**: exit velocity, barrel%, xBA, xSLG, sprint speed, age, injury history, park factors
- **Target**: next season fantasy points
- **Model**: start with gradient boosting (XGBoost or LightGBM), then try neural nets
- **Training data**: 2015-2023 Statcast data (8 years, ~1000 players per year = solid dataset)
- **Use CSUA P100 GPUs** for training if needed
- **Evaluation**: how well does the model predict 2024 performance when trained on 2015-2023?
- This is literally publishable research if it works well

---

## Full Tech Stack

### Backend
- **Python 3.11+**
- **FastAPI** — REST API + WebSockets
- **pybaseball** — all MLB data
- **pandas** — data manipulation
- **numpy / scipy** — statistical modeling
- **scikit-learn / XGBoost** — ML models (V7)
- **Supabase** — database + auth (V2+)
- **Anthropic or OpenAI API** — AI GM bot

### Frontend
- **React 19 + Vite** (matches your existing site)
- **Tailwind CSS** — styling
- **Recharts** — data visualizations
- **Supabase JS client** — auth (V2+)

### Infrastructure
- **Vercel** — frontend (already have)
- **CSUA soda.csua.berkeley.edu** — FastAPI backend (free, use this instead of Railway)
- **CSUA Latte** — Docker containers, GPU compute for ML (V7)
- **Domain**: crisostomodunn.com/draft

---

## File Structure

```
fantasy-draft-sim/
├── backend/
│   ├── main.py                     # FastAPI app, all routes
│   ├── data/
│   │   ├── loader.py               # pybaseball wrappers + caching
│   │   ├── valuation.py            # z-score ranking logic
│   │   └── cache/                  # cached CSVs by year
│   ├── draft/
│   │   ├── engine.py               # snake draft logic
│   │   ├── scoring.py              # end of season team scoring
│   │   └── bots/
│   │       ├── base.py             # Bot abstract class
│   │       ├── adp_bot.py          # best available ADP
│   │       ├── analytics_bro.py    # Statcast stats only
│   │       ├── old_school.py       # AVG/RBI/W traditionalist
│   │       ├── reach_king.py       # always reaches
│   │       ├── punt_bot.py         # punts one category
│   │       └── ai_gm.py           # LLM-powered bot
│   ├── dialogue/
│   │   ├── analytics_bro.json      # dialogue strings per bot
│   │   ├── old_school.json
│   │   └── ...
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DraftBoard.jsx      # main draft UI
│   │   │   ├── PlayerPool.jsx      # filterable player table
│   │   │   ├── MyTeam.jsx          # your roster panel
│   │   │   ├── BotDialogue.jsx     # chat bubble panel
│   │   │   ├── AIPanel.jsx         # AI GM reasoning stream
│   │   │   ├── ResultsPage.jsx     # post-draft results
│   │   │   └── DraftHistory.jsx    # saved drafts (V2)
│   │   └── App.jsx
│   └── package.json
├── ROADMAP.md                      # this file
├── PROGRESS_LOG.md                 # daily session log
└── README.md
```

---

## Timeline

### Phase 0 — Spain (Now → July 8, 30 min/day)
- ✅ Week 1: repo setup, data ingestion working, CSVs cached
- Week 2: z-score valuation working, player rankings make sense
- Week 3: snake draft engine in terminal, ADP bot picks correctly
- Week 4-8: 2-3 more bot strategies, end-of-season scoring working
- **Goal by July 8**: full terminal draft simulation working. 10 bots, 15 rounds, correct scoring.

### Phase 1 — SF (July 8 → mid August, full time)
- Week 1: FastAPI backend, all draft logic behind REST endpoints
- Week 2: React frontend — draft board, player pool, team panel
- Week 3: AI GM bot integrated, bot dialogue working, WebSockets for live updates
- Week 4: Results page, deployment on CSUA + Vercel
- Week 5: Polish, README, blog post about one interesting technical decision

### Phase 2 — Senior Year (side project)
- Supabase auth + saved draft history
- Season simulation (Monte Carlo)
- NFL support (launch before August 2027 fantasy season)

---

## What This Shows Recruiters

| Skill | Where it shows |
|---|---|
| Data pipelines | pybaseball, point-in-time correctness, CSV caching |
| Algorithm design | z-score valuation, snake draft engine, position scarcity |
| LLM integration | AI GM with contextual Statcast reasoning |
| System design | pluggable bot framework, extensible to any sport |
| Full stack | FastAPI + React + WebSockets |
| ML (V3+) | Monte Carlo simulation, performance distributions |
| Product thinking | real use case, real users, launched at right time |
| Domain expertise | shows genuine baseball knowledge, not a generic project |

---

## Resume Bullet (fill in numbers when real)

"Built a full-stack fantasy baseball draft simulator with historical backtesting across 10 seasons, a pluggable AI bot framework with distinct personalities and LLM-powered reasoning over real Statcast data, and a Monte Carlo season simulator. Deployed at crisostomodunn.com/draft, used by X players during 2026 fantasy season."

---

## Notes for GitHub Copilot

- All MLB data comes from **pybaseball** — do not suggest manual scraping
- Player valuation uses **z-score method across 5x5 roto** (HR, RBI, R, SB, AVG / W, SV, ERA, WHIP, K)
- Every bot implements a single `pick(available_players, my_roster, round_num, all_rosters) -> Player` method
- **Point-in-time data is critical**: draft year X only sees stats from years prior to X
- Snake draft order: picks go 1→10 in odd rounds, 10→1 in even rounds
- Backend is **FastAPI**, frontend is **React + Vite + Tailwind**
- Database is **Supabase** (V2+)
- Do NOT use paid data APIs — pybaseball is free
- Start with terminal draft before touching API or UI
- Bot dialogue is stored in JSON files in `backend/dialogue/`
- The AI GM calls the LLM API once per pick — keep prompts concise to manage cost
