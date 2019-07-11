#!/usr/bin/env python3

import datetime
import os

from tinydb import TinyDB, Query
from main import timestamp_to_today_limits, ON, OFF


db = TinyDB(os.path.dirname(os.path.realpath(__file__)) + '/db.json')

# Get local time zone
LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo


def print_past_week_totals():
    prev_ts = Query()
    datetime_now = datetime.datetime.now(LOCAL_TIMEZONE)
    datetime_today = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
    datetime_week_ago = datetime_today - datetime.timedelta(days=7)
    timestamp_week_ago = datetime.datetime.timestamp(datetime_week_ago)
    js_timestamp_week_ago = timestamp_week_ago * 1000
    results = db.search(prev_ts.timestamp >= js_timestamp_week_ago)

    days = {}

    prev_ts = results[0]['timestamp']
    prev_toggle = results[0]['toggleOn']
    prev_day, _ = timestamp_to_today_limits(prev_ts)

    for result in results[1:]:
        this_ts = result['timestamp']
        this_day, _ = timestamp_to_today_limits(this_ts)
        this_toggle = result['toggleOn']

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
        elif prev_toggle == OFF and this_toggle == ON:
            prev_ts = this_ts
            prev_toggle = this_toggle
            prev_day = this_day
        else:
            # do nothing
            pass

    for day_ts, time_num in days.items():
        day_date = datetime.datetime.fromtimestamp(day_ts / 1000., tz=LOCAL_TIMEZONE).date()
        time_timedelta = datetime.timedelta(microseconds=time_num)
        s = time_timedelta.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(day_date, '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)))


print_past_week_totals()
