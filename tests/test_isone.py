"""Checks on Partner A's ISO-NE API. These run automatically on every pull request.
Not built yet -> the tests SKIP (they don't fail). Built wrong -> they FAIL."""
import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import isone  # noqa: E402


@pytest.fixture(scope="module")
def load():
    try:
        return isone.get_five_minute_load()
    except NotImplementedError:
        pytest.skip("Partner A hasn't built isone.py yet")


def test_has_every_column(load):
    for col in isone.COLUMNS:
        assert col in load.columns, f"missing column: {col}"


def test_has_rows(load):
    assert len(load) > 0, "no rows came back - did TODO 3 keep the '\"D\"' lines?"


def test_load_looks_like_megawatts(load):
    # New England's load lives roughly between 8,000 and 26,000 MW
    assert load["total_load_mw"].between(3000, 35000).all()


def test_one_row_every_five_minutes(load):
    gaps = pd.to_datetime(load["timestamp"]).diff().dropna()
    assert gaps.median() == pd.Timedelta(minutes=5)
