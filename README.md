# PC Build Battle

A fully offline Python desktop PC-building game. Pick a challenge, assemble eight components, and win over three opinionated judges.

## Run

Requires Python 3.10 or later.

```powershell
python -m pip install -r requirements.txt
python app.py
```

On this workspace, PySide6 is already installed in `.deps`; simply run `python app.py` or double-click `Launch PC Build Battle.bat`.

## Play

1. Start the featured challenge on Home, or choose a mode in Challenges.
2. Select a category on the workbench, filter the catalog, and add a part. Adding another part in the same slot replaces it.
3. Watch the live budget, power, mission checklist, and compatibility warnings. Every build needs all eight slots, including a cooler.
4. Submit to receive a weighted score, judge feedback, XP, and achievements. Incompatible and over-budget builds are allowed but penalized.
5. Revisit results from Home. Your history, leaderboard entries, settings, XP, achievements, and active draft survive restarts.

Nine modes include budget, gaming, productivity, AI, compact builds, quiet PCs, efficiency, RGB, and fictional customers. The daily challenge rotates by local date. Generated requests can be rerolled freely. Enable optional market events in Settings; click the workbench event button to trigger at most one event per build.

## Scoring

The default weights are performance 30%, value 15%, compatibility 20%, efficiency 10%, requirements 20%, and aesthetics 5%. Quiet/efficiency challenges put 25% into efficiency; RGB challenges put 20% into aesthetics. Workstation and AI modes use their respective performance metrics. Objective bonuses add points, incompatibilities and overspending subtract points, and the final score is capped at 0–100. Levels require 500 XP each. All prices, power estimates, and benchmarks are approximate simulation values, not real-time hardware advice.

## Data and architecture

SQLite progress lives in `%LOCALAPPDATA%\PCBuildBattle\progress.sqlite3` on Windows, or `~/PCBuildBattle/progress.sqlite3` elsewhere. Back up that file while the app is closed to preserve your game. No network calls occur at runtime. Initial leaderboard entries are labeled fictional exhibition competitors.

- `models.py`: components, challenges, build state
- `seed_data.py`: 120 components
- `database.py`: catalog, drafts, atomic result/XP/achievement persistence
- `challenges.py`: modes, customer requests, deterministic daily rotation
- `services.py`: compatibility, metrics, scoring, achievements
- `ui/`: Qt pages, theme, reusable widgets, procedural PC illustration

The desktop layout supports windows from 1050 × 720 upward, with adjustable builder columns and scrolling content.

## Verify

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
python tests/smoke_ui.py
```

The smoke test uses a temporary database and Qt's offscreen platform to exercise navigation, a complete build, results, history, and restart persistence. It writes screenshots to `screenshots/`.
