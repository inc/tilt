#!/usr/bin/python3
#
# Tilt - Example - Digital Product Delivery - Web Server
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import argparse
import tornado.web

class WebServer:

    def __init__(self, args):
        self.args = args

    def start(self):
        app = tornado.web.Application([
            (r"/(.*)", tornado.web.StaticFileHandler,
                { "path": "./web", "default_filename": "index.html" }),
        ])
        app.listen(self.args.port)
        tornado.ioloop.IOLoop.current().start()

def main():

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('--port', type=int, default=8000,
        help='web server port')

    args = parser.parse_args()

    ws = WebServer(args)
    ws.start()

if __name__ == "__main__":
    main()

