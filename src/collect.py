"""The collector the robot runs every 5 minutes (see .github/workflows/collect.yml).

It calls each partner's API, then UPSERTS the rows into a CSV:
  - rows it has never seen are added
  - rows it has seen are replaced with the newest version (ISO-NE revises recent values)
so it never matters if a run starts late, runs twice, or gets skipped - the next
run catches up. That is how real pipelines stay correct on an unreliable schedule.

Run it yourself:  python src/collect.py --out data
"""
import argparse
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import isone  # noqa: E402  Partner A
import nws    # noqa: E402  Partner B

SOURCES = [
    ("energy (Partner A)", isone.get_five_minute_load, "isone_5min.csv"),
    ("weather (Partner B)", nws.get_observations, "weather_obs.csv"),
]


def upsert(new, path, key="timestamp"):
    """Merge new rows into the CSV at path. Returns (rows added, total rows)."""
    new = new.copy()
    new[key] = new[key].astype(str)
    if os.path.exists(path):
        old = pd.read_csv(path, dtype={key: str})
        before = set(old[key])
        combined = pd.concat([old, new], ignore_index=True)
    else:
        before = set()
        combined = new
    combined = combined.drop_duplicates(subset=key, keep="last").sort_values(key)
    combined.to_csv(path, index=False)
    added = len(set(combined[key]) - before)
    return added, len(combined)


def main(out):
    os.makedirs(out, exist_ok=True)
    for name, fetch, filename in SOURCES:
        try:
            df = fetch()
        except NotImplementedError:
            print(f"{name}: not built yet - skipping (merge your PR and it starts flowing)")
            continue
        added, total = upsert(df, os.path.join(out, filename))
        print(f"{name}: fetched {len(df)}, added {added} new, {total} rows total -> {filename}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data", help="folder to write the CSVs into")
    main(ap.parse_args().out)
