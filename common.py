#!/usr/bin/env python3

__author__ = "Ingvaras Merkys"

import datetime
from typing import Dict

from tinydb import Query, TinyDB

LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo
ON = True
OFF = False


def timestamp_to_today_limits(ts, js=True):
    ts = ts / 1000. if js else ts
    datetime_ts = datetime.datetime.fromtimestamp(ts, tz=LOCAL_TIMEZONE)
    datetime_day_start = datetime_ts.replace(hour=0, minute=0, second=0, microsecond=0)
    datetime_day_end = datetime_day_start + datetime.timedelta(hours=24)
    timestamp_day_start = datetime.datetime.timestamp(datetime_day_start)
    timestamp_day_end = datetime.datetime.timestamp(datetime_day_end)
    if js:
        timestamp_day_start *= 1000
        timestamp_day_end *= 1000
    return timestamp_day_start, timestamp_day_end


def get_daily_totals(db: TinyDB, ts_start: float) -> Dict[float, float]:
    """
    :param db: Database
    :param ts_start: Timestamp from which to get totals (in seconds)
    :return: Dictionary where keys - date timestamps (JS), values - milliseconds
    """
    prev_ts = Query()
    if ts_start is not None:
        js_ts_start = ts_start * 1000
        results = db.search(prev_ts.timestamp >= js_ts_start)
    else:
        results = db.all()

    if len(results) == 0:
        return {}

    days = {}

    prev_ts = results[0]['timestamp']
    prev_toggle = results[0]['toggle']
    prev_day, _ = timestamp_to_today_limits(prev_ts)

    for result in results[1:]:
        this_ts = result['timestamp']
        this_day, _ = timestamp_to_today_limits(this_ts)
        this_toggle = result['toggle']

        if prev_toggle == ON and this_toggle == OFF:
            # same day
            if this_day == prev_day:
                try:
                    days[this_day] += this_ts - prev_ts
                except KeyError:
                    days[this_day] = this_ts - prev_ts
            # over 2 days
            elif this_day > prev_day:
                try:
                    days[prev_day] += this_day - prev_ts
                except KeyError:
                    days[prev_day] = this_day - prev_ts
                try:
                    days[this_day] += this_ts - this_day
                except KeyError:
                    days[this_day] = this_ts - this_day
            prev_toggle = this_toggle
        elif prev_toggle == OFF and this_toggle == ON:
            prev_ts = this_ts
            prev_toggle = this_toggle
            prev_day = this_day
        else:
            # do nothing
            pass
    return days
