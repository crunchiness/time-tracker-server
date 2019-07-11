#!/usr/bin/env python3

__author__ = "Ingvaras Merkys"

import datetime
import unittest

from common import get_daily_totals, LOCAL_TIMEZONE


class FakeDB:
    def __init__(self, db):
        self._db = db

    def search(self, *args):
        return self._db


class TestUtil(unittest.TestCase):
    def test_get_daily_totals(self):
        now = 1562834567998
        fake_db = FakeDB([{'type': 'ts', 'toggle': False, 'timestamp': 1562828017912},
                          {'type': 'ts', 'toggle': False, 'timestamp': 1562832295820},
                          {'type': 'ts', 'toggle': True, 'timestamp': 1562832704992},
                          {'type': 'ts', 'toggle': False, 'timestamp': 1562832714766},
                          {'type': 'ts', 'toggle': False, 'timestamp': 1562834567998}])

        datetime_now = datetime.datetime.now(LOCAL_TIMEZONE)
        datetime_today = datetime_now.replace(hour=0, minute=0, second=0, microsecond=0)
        timestamp = datetime.datetime.timestamp(datetime_today) * 1000.

        days = get_daily_totals(fake_db, now)
        expected = {timestamp: 9774}
        self.assertDictEqual(days, expected)


if __name__ == '__main__':
    unittest.main()
