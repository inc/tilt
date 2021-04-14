#!/bin/python3
#
# Tilt - Wallet Service
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import json
import time
import websocket
import logging
import subprocess
import time
import os
import signal
import zmq

import tilt.utils as tilt
from tilt.wlt.wallet import WalletManager

class WalletServiceMonitor():

    def __init__(self):
        tilt.setup()

    def start(self):
        tiltdir = os.path.expanduser("~/.tilt")
        if os.path.exists(tiltdir + "/tiltwlt.pid"):
            logging.error(tiltdir + "/tiltwlt.pid exists; try 'tilt stop'")
            exit(1)
        FLOG = open(tiltdir + "/tilt.log", "a")
        p = subprocess.Popen(["tilt", "server"],
            stdout=FLOG, stderr=subprocess.STDOUT)
        with open(tiltdir + "/tiltwlt.pid", "w") as f:
            f.write(str(p.pid))

    def status(self):
        tiltdir = os.path.expanduser("~/.tilt")
        if os.path.exists(tiltdir + "/tiltwlt.pid"):
            with open(tiltdir + "/tiltwlt.pid", "r") as f:
                pid = int(f.read())
            logging.info("tiltwlt is running as pid %s" % pid)
        else:
            logging.info("tiltwlt is not running")

    def stop(self):
        tiltdir = os.path.expanduser("~/.tilt")
        if not os.path.exists(tiltdir + "/tiltwlt.pid"):
            logging.error("tiltwlt is not running")
            exit(1)
        with open(tiltdir + "/tiltwlt.pid", "r") as f:
            pid = int(f.read())
            os.remove(tiltdir + "/tiltwlt.pid")
            os.kill(pid, signal.SIGTERM)

class WalletService():

    def __init__(self):
        tilt.setup()
        self.wallet_id = tilt.get_config("wallet_id")
        self.auth = tilt.get_config("srv_key")
        self.wm = WalletManager()

    def connect(self):
        self.ws = websocket.WebSocketApp("wss://tilt.cash/api/v1/ws",
            on_open = self.on_open,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)
        self.zmqctx = zmq.Context()
        self.zmqsock = self.zmqctx.socket(zmq.PUB)
        self.zmqsock.bind("tcp://*:9090")

    def run(self):
        while True:
            try:
                self.connect()
                self.ws.run_forever()
            except:
                logging.error("error; restarting")
            time.sleep(1)

    def on_message(self, ws, message):
        req = json.loads(message)
        self.zmqsock.send_string(message)

        if 'id' in req:
            logging.info("rpcreq %s" % req)
            self.rpcdispatch(req)
        else:
            logging.info("msg %s" % req)

    def rpcdispatch(self, req):

        if (req['method'] == 'ping'):
            self.rpcres(req['id'], {})

        if (req['method'] == 'create_address'):
            currency = req['args']['currency']
            meta = None
            label = None
            if 'meta' in req['args']:
                meta = req['args']['meta']
            if 'label' in req['args']:
                label = req['args']['label']
            address = self.wm.create(currency, meta, label)
            self.rpcres(req['id'], { 'address': address })

    def rpcres(self, rpcid, args):
        res = {
            'method': 'rpcres',
            'id': rpcid,
            'args': args
        }
        jsonres = json.dumps(res)
        self.zmqsock.send_string(jsonres)
        logging.info("rpcres %s" % res)
        self.ws.send(jsonres)

    def on_error(self, ws, error):
        logging.warning("connection error %s" % error)

    def on_close(self, ws):
        logging.info("connection closed")

    def on_open(self, ws):
        logging.info("connected")
        self.send("hello", { 'wallet': self.wallet_id, 'auth': self.auth })

    def send(self, method, args):
        req = { 'method': method, 'args': args }
        self.ws.send(json.dumps(req))

if __name__ == "__main__":
    wsrv = WalletService()
    wsrv.run()
