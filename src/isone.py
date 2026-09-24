"""Partner A (energy): your own little ISO-NE API.

ISO-NE's official web-services API needs an account. The public five-minute
system load report does not - but you have to "visit" the report page first to
pick up a session cookie, then ask for the CSV with that page as the Referer.
This module hides all of that behind one clean function:

    get_five_minute_load()  ->  a DataFrame, one row per 5 minutes

The collector bot (src/collect.py) calls it every run. Nobody else needs to know
about cookies, referers, or the "C/H/D/T" row codes in the raw file.

YOUR JOB: fill in TODO 1-3 (one or two lines each), delete the
`raise NotImplementedError` line, then test it:   python src/isone.py
"""
import datetime as dt
import io
import os
from zoneinfo import ZoneInfo

import pandas as pd
import requests

REPORT_PAGE = "https://www.iso-ne.com/isoexpress/web/reports/load-and-demand/-/tree/dmnd-five-minute-sys"
CSV_URL = "https://www.iso-ne.com/transform/csv/fiveminutesystemload?start={start}&end={end}"
USER_AGENT = f"opim5512-lab3 (github.com/{os.environ.get('GITHUB_REPOSITORY', 'student')})"

# the raw file's data columns, renamed to snake_case with units
COLUMNS = [
    "timestamp",
    "total_load_mw",
    "native_load_mw",
    "asset_related_load_mw",
    "total_load_with_solar_mw",
    "native_load_with_solar_mw",
]


def get_five_minute_load(start=None, end=None):
    """Five-minute New England system load, one row per 5 minutes (local time, ET).

    start, end: datetime.date. Default = yesterday through today, so a run just
    after midnight still catches the last few minutes of yesterday.
    """
    raise NotImplementedError("Partner A: fill in TODO 1-3, then delete this line")

    today = dt.datetime.now(ZoneInfo("America/New_York")).date()
    if end is None:
        end = today
    if start is None:
        start = end - dt.timedelta(days=1)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    # TODO 1: "visit" the report page so the server hands your session a cookie.
    #         One line: call session.get(...) on REPORT_PAGE (use timeout=30).

    url = CSV_URL.format(start=start.strftime("%Y%m%d"), end=end.strftime("%Y%m%d"))

    # TODO 2: ask for the CSV with the SAME session, telling the server which page you came from.
    #         One line: resp = session.get(url, headers={"Referer": REPORT_PAGE}, timeout=30)
    resp = None
    resp.raise_for_status()

    # TODO 3: keep only the data rows. The raw file has comment rows ("C"), header rows ("H"),
    #         a trailer ("T"), and the data rows you want, which start with "D" in quotes.
    #         Loop over resp.text.splitlines() and append every line that starts with '"D"'.
    data_rows = []

    df = pd.read_csv(io.StringIO("\n".join(data_rows)), header=None, names=["row_type"] + COLUMNS)
    df = df.drop(columns="row_type")
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="%m/%d/%Y %H:%M:%S")
    return df


if __name__ == "__main__":
    load = get_five_minute_load()
    print(load.tail())
    print(len(load), "rows")
