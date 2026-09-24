"""Checks on Partner B's weather API. These run automatically on every pull request.
Not built yet -> the tests SKIP (they don't fail). Built wrong -> they FAIL."""
import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import nws  # noqa: E402

READINGS = ["temp_f", "dewpoint_f", "humidity_pct", "wind_mph"]


@pytest.fixture(scope="module")
def obs():
    try:
        return nws.get_observations()
    except NotImplementedError:
        pytest.skip("Partner B hasn't built nws.py yet")


def test_has_every_reading(obs):
    for col in ["timestamp", "sky"] + READINGS:
        assert col in obs.columns, f"missing column: {col}"


def test_has_rows(obs):
    assert len(obs) > 0


def test_humidity_is_a_percent(obs):
    assert obs["humidity_pct"].dropna().between(0, 100).all()


def test_temperature_is_fahrenheit(obs):
    """Compare your newest temp_f to the raw Celsius from the API, converted by hand."""
    url = nws.OBS_URL.format(station=nws.STATION, limit=1)
    raw = requests.get(url, headers={"User-Agent": nws.USER_AGENT}, timeout=30).json()
    celsius = raw["features"][0]["properties"]["temperature"]["value"]
    if celsius is None:
        pytest.skip("the station's newest report has no temperature")
    expected = round(celsius * 9 / 5 + 32, 1)
    newest = obs.dropna(subset=["temp_f"]).iloc[-1]["temp_f"]
    assert abs(newest - expected) < 3, f"temp_f={newest} but the API says {celsius} C = {expected} F"
