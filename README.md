# OPIM 5512 · Lab 3 — Build a live data robot

New England's grid publishes its electricity demand **every 5 minutes**. The weather station at your
campus airport reports **every 5 minutes** too. Tonight you and your partner each write a tiny
**API** for one of those feeds, merge them through the same branch → PR → review → merge loop as
Labs 1 and 2, and hand them to a **robot** that runs every 5 minutes in the cloud — forever, for free,
while you sleep.

| Who | Builds | File | One clean function |
|---|---|---|---|
| **Partner A** | the energy API (ISO-NE) | `src/isone.py` | `get_five_minute_load()` → one row per 5 minutes |
| **Partner B** | the weather API (National Weather Service) | `src/nws.py` | `get_observations()` → one row per weather report |
| **The robot** | runs both, keeps only new rows | `src/collect.py` + `.github/workflows/collect.yml` | *(given — you don't edit it)* |

## Why an "API"?
ISO-NE's official API needs an account; its public report needs a cookie-and-referer dance. The weather
service returns nested JSON in Celsius and km/h. **Nobody downstream should have to know any of that.**
Your module hides the mess behind one function that returns a tidy DataFrame. That's all an API is:
a clean promise about what you get back.

## Where things live
- **`main`** — the code. Protected: changes only arrive through a reviewed pull request.
- **`data`** — the data. The robot creates this branch on its first run and commits new rows to it
  every 5 minutes. Nobody else commits there. (That's why the robot doesn't clutter your network graph.)

```
data branch
├── isone_5min.csv      timestamp, total_load_mw, …, total_load_with_solar_mw, …
└── weather_obs.csv     timestamp, temp_f, dewpoint_f, humidity_pct, wind_mph, sky
```

## How the robot stays correct on a sloppy schedule
GitHub runs scheduled jobs *roughly* every 5 minutes — sometimes late, sometimes skipped when it's busy.
So `collect.py` never asks "what happened in the last 5 minutes?" It pulls **the whole recent window**
every time and **upserts**: new rows are added, rows it already has are replaced with the newest version.
A late or skipped run just catches up next time. Real data pipelines work exactly this way.

## Checks on every pull request
`tests/` runs automatically when you open a PR — that's the green ✓ or red ✗ your reviewer sees.
A file that isn't built yet is **skipped**, not failed, so your partner's unfinished half never blocks you.

## Run it yourself
```bash
pip install -r requirements.txt
python src/isone.py            # Partner A: prints the newest rows
python src/nws.py              # Partner B: prints the newest rows
python -m pytest -v tests      # the same checks your PR runs
python src/collect.py --out data   # what the robot does, into a local folder
```

## Watch it grow
Open `notebooks/Lab3_Watch_Your_Live_Data.ipynb` in Colab, set your repo name, **Run all** —
then come back tomorrow and run it again.
