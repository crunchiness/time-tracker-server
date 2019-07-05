#!/usr/bin/env python3

import cgi
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging
import os

from tinydb import TinyDB, Query


LOCAL_TIMEZONE = datetime.datetime.now().astimezone().tzinfo


db = TinyDB(os.path.dirname(os.path.realpath(__file__)) + '/db.json')


def js_timestamp_to_today_limits(ts):
    datetime_ts = datetime.datetime.fromtimestamp(ts / 1000., tz=LOCAL_TIMEZONE)
    datetime_day_start = datetime_ts.replace(hour=0, minute=0, second=0, microsecond=0)
    datetime_day_end = datetime_day_start + datetime.timedelta(hours=24)
    timestamp_day_start = datetime.datetime.timestamp(datetime_day_start) * 1000
    timestamp_day_end = datetime.datetime.timestamp(datetime_day_end) * 1000
    return timestamp_day_start, timestamp_day_end


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_headers()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        logging.info('Received: {}'.format(message))

        msg_type = message['type']

        if msg_type == 'ts':
            # Record
            db.insert(message)
            # Acknowledge
            self._set_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
        elif msg_type == 'req':
            # Based on received timestamp get total time that day
            ts = message['timestamp']
            ts_day_start, ts_day_end = js_timestamp_to_today_limits(ts)
            q = Query()
            results = db.search((q.timestamp >= ts_day_start) & (q.timestamp < ts_day_end))
            total_time = 0
            prev_ts = 0
            for result in results:
                ts = result['timestamp']
                assert ts > prev_ts
                toggle = result['toggleOn']
                if not toggle and prev_ts != 0:  # toggle off
                    total_time += ts - prev_ts
                elif not toggle and prev_ts == 0:
                    total_time += ts - ts_day_start
                prev_ts = ts
            self._set_headers()
            self.wfile.write(json.dumps({'total': total_time}).encode('utf-8'))


def run():
    logging.basicConfig(level=logging.INFO)
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, Handler)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')


if __name__ == '__main__':
    run()
