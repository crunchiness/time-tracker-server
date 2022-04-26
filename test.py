#!/usr/bin/env python3

__author__ = "Ingvaras Merkys"

import datetime
import unittest

from common import get_daily_totals, LOCAL_TIMEZONE, timestamp_to_today_limits


class FakeDB:
    def __init__(self, db):
        self._db = db

    def search(self, *args):
        return self._db


class TestUtil(unittest.TestCase):
    def test_get_daily_totals(self):
        now = 1562834567998
        fake_db = FakeDB([{'type': 'ts', 'toggle': True, 'timestamp': 1562832704992},
                          {'type': 'ts', 'toggle': False, 'timestamp': 1562832714766},
                          {'type': 'ts', 'toggle': False, 'timestamp': 1562834567998}])

        now_day, _ = timestamp_to_today_limits(now)

        days = get_daily_totals(fake_db, now)
        expected = {now_day: 9774}
        self.assertDictEqual(days, expected)

    # def test_again(self):
    #     now = 1563983055155
    #     data = [{'type': 'ts', 'toggle': True, 'timestamp': 1563957671480},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563957672408},
    #             {'type': 'ts', 'toggle': True, 'timestamp': 1563969784618},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563970599642},
    #             {'type': 'ts', 'toggle': True, 'timestamp': 1563971251110},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563971387878},
    #             {'type': 'ts', 'toggle': True, 'timestamp': 1563971652642},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563971756050},
    #             {'type': 'ts', 'toggle': True, 'timestamp': 1563980695372},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563980803804},
    #             {'type': 'ts', 'toggle': True, 'timestamp': 1563981163810},
    #             {'type': 'ts', 'toggle': False, 'timestamp': 1563983055154}]
    #     fake_db = FakeDB(data)
    #
    #     data_ = map(lambda x: x['timestamp'], data)
    #
    #     now_day, _ = timestamp_to_today_limits(now)
    #     days = get_daily_totals(fake_db, now)
    #     expected = {}
    #     self.assertDictEqual(days, expected)

    def test_get_daily_totals_day_off(self):
        now = 1564474106187
        data = [{'type': 'ts', 'toggle': False, 'timestamp': 1564435261672}]
        fake_db = FakeDB(data)
        now_day, _ = timestamp_to_today_limits(now)
        actual_days = get_daily_totals(fake_db, now_day)
        expected_days = {now_day: 1564435261672 - now_day}
        self.assertDictEqual(actual_days, expected_days)


if __name__ == '__main__':
    unittest.main()
