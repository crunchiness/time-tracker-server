#!/usr/bin/env python3

import datetime
import os

from tinydb import TinyDB, Query

from common import get_daily_totals

db = TinyDB(os.path.dirname(os.path.realpath(__file__)) + '/db.json')

# Get local time zone
LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo


def print_past_week_totals():
    datetime_now = datetime.datetime.now(LOCAL_TIMEZONE)
    datetime_today = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
    datetime_week_ago = datetime_today - datetime.timedelta(days=7)
    timestamp_week_ago = datetime.datetime.timestamp(datetime_week_ago)

    days = get_daily_totals(db, timestamp_week_ago)

    for day_ts, time_num in days.items():
        day_date = datetime.datetime.fromtimestamp(day_ts / 1000., tz=LOCAL_TIMEZONE).date()
        time_timedelta = datetime.timedelta(milliseconds=time_num)
        s = time_timedelta.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        print(day_date, '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds)))


print_past_week_totals()


def print_todays_results():
    datetime_now = datetime.datetime.now(LOCAL_TIMEZONE)
    datetime_today = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp = datetime.datetime.timestamp(datetime_today) * 1000.
    for r in db.search(Query().timestamp > timestamp):
        print(r)

# print_todays_results()
