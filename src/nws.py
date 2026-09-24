"""Partner B (weather): your own little National Weather Service API.

api.weather.gov is free and needs no key, but it asks every caller to identify
itself in the User-Agent header. It returns nested JSON with METRIC units.
This module hides that behind one clean function:

    get_observations()  ->  a DataFrame, one row per weather report

The collector bot (src/collect.py) calls it every run.

YOUR JOB: fill in TODO 1-2, delete the `raise NotImplementedError` line,
then test it:   python src/nws.py
"""
import os

import pandas as pd
import requests

STATION = "KBDL"  # Bradley (Hartford campus). Stamford campus: "KBDR" (Sikorsky / Bridgeport)
OBS_URL = "https://api.weather.gov/stations/{station}/observations?limit={limit}"
USER_AGENT = f"opim5512-lab3 (github.com/{os.environ.get('GITHUB_REPOSITORY', 'student')})"


def c_to_f(c):
    return None if c is None else round(c * 9 / 5 + 32, 1)


def kmh_to_mph(kmh):
    return None if kmh is None else round(kmh * 0.621371, 1)


def round_or_none(x):
    return None if x is None else round(x, 1)


def get_observations(station=STATION, limit=50):
    """Recent weather observations at one station, oldest first (local time, ET)."""
    raise NotImplementedError("Partner B: fill in TODO 1-2, then delete this line")

    url = OBS_URL.format(station=station, limit=limit)

    # TODO 1: GET the url. Send headers={"User-Agent": USER_AGENT, "Accept": "application/geo+json"}
    #         and timeout=30. Save the response as resp.
    resp = None
    resp.raise_for_status()

    rows = []
    for feature in resp.json()["features"]:
        p = feature["properties"]
        rows.append({
            "timestamp": p["timestamp"],
            # TODO 2: the API gives Celsius and km/h. Fill in the four readings below
            #         using the helpers above, e.g.  c_to_f(p["temperature"]["value"])
            #   temp_f       <- p["temperature"]["value"]        (Celsius -> use c_to_f)
            #   dewpoint_f   <- p["dewpoint"]["value"]           (Celsius -> use c_to_f)
            #   humidity_pct <- p["relativeHumidity"]["value"]   (percent -> use round_or_none)
            #   wind_mph     <- p["windSpeed"]["value"]          (km/h    -> use kmh_to_mph)
            "sky": p["textDescription"],
        })

    df = pd.DataFrame(rows)
    # the API speaks UTC; convert to local Eastern time so it lines up with ISO-NE
    df["timestamp"] = (pd.to_datetime(df["timestamp"], utc=True)
                       .dt.tz_convert("America/New_York")
                       .dt.tz_localize(None))
    return df.sort_values("timestamp").reset_index(drop=True)


if __name__ == "__main__":
    obs = get_observations()
    print(obs.tail())
    print(len(obs), "rows")
