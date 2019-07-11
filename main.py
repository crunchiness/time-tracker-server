#!/usr/bin/env python3

__author__ = "Ingvaras Merkys"

import cgi
import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from tinydb import TinyDB

from common import get_daily_totals, timestamp_to_today_limits

db = TinyDB(os.path.dirname(os.path.realpath(__file__)) + '/db.json')
table = db.table()


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
            toggle_off = not message['toggle']
            last_toggle_off = not table.get(doc_id=len(table))['toggle']
            # but don't record a repeated OFF signal
            if not (toggle_off and last_toggle_off):
                table.insert(message)

            # Acknowledge
            self._set_headers()
            self.wfile.write(json.dumps({'ok': True}).encode('utf-8'))
        elif msg_type == 'req':
            # Based on received timestamp get total time that day
            ts = message['timestamp']
            ts_day_start, ts_day_end = timestamp_to_today_limits(ts)
            days = list(get_daily_totals(db, ts_day_start / 1000.).items())
            total_time = 0 if len(days) == 0 else days[0][1]
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
