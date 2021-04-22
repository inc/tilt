#!/usr/bin/python3
#
# Tilt - Example - Digital Product Delivery - Fulfillment Server
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import argparse
import base64
import logging
import os
import json
import websocket
import zmq
import time

import sendgrid
from sendgrid.helpers.mail import *

import tilt.utils as tilt

class EBookServer():

    def __init__(self):
        self.orders = {}
        self.load()
        tilt.setup()
        self.tilt_api_key = os.environ["TILT_API_KEY"]
        self.sendgrid_api_key = os.environ["SENDGRID_API_KEY"]
        with open("web/config.json") as f:
            self.config = json.loads(f.read())
        self.tilt_wallet_id = self.config['wallet_id']
        self.from_email = self.config['mail_from']
        self.conf_check_secs = self.config['conf_check_secs']
        if not self.tilt_wallet_id:
            logging.error("wallet_id not set in web/config.json")
            exit(1)
        logging.info("config: %s" % self.config)

    def connect(self):
        self.ws = websocket.WebSocketApp("wss://tilt.cash/api/v1/ws_api",
            on_open = self.on_open,
            on_pong = self.on_pong,
            on_message = self.on_message,
            on_error = self.on_error,
            on_close = self.on_close)

    def on_pong(self, ws, message):
        self.fulfill()

    def start(self):
        while True:
            try:
                self.connect()
                self.ws.run_forever(ping_interval=self.conf_check_secs)
            except:
                logging.error("error; restarting")
            time.sleep(1)

    def on_message(self, ws, message):
        msg = json.loads(message)
        logging.info("received message: %s" % msg)

        if not 'type' in msg: return

        # when we first see the transaction, create a new order
        if msg['type'] == 'tx':
            if 'meta' in msg and 'type' in msg['meta']:
                if msg['meta']['type'] == 'ebook':
                    order_key = msg['currency'] + '.' + msg['address']
                    if order_key in self.orders: return
                    logging.info("*** new order: %s" % msg)
                    msg['delivered'] = False
                    self.orders[order_key] = msg
                    self.save()

    def on_error(self, ws, error):
        logging.warning("connection error %s" % error)

    def on_close(self, ws):
        logging.info("connection closed")

    def on_open(self, ws):
        logging.info("connected")
        self.send("hello", {
            'wallet': self.tilt_wallet_id, 'auth': self.tilt_api_key
        })

    def send(self, method, args):
        req = { 'method': method, 'args': args }
        self.ws.send(json.dumps(req))

    def load(self):
        if os.path.isfile("orders.json"):
            with open("orders.json") as f:
                self.orders = json.loads(f.read())

    def save(self):
        with open("orders.json", "w+") as f:
            f.write(json.dumps(self.orders))

    # attempt to fulfill any pending orders
    def fulfill(self):

        for order_key in self.orders:

            order = self.orders[order_key]

            if order['delivered']: continue

            currency = order['currency']
            address = order['address']
            to_email = order['meta']['email']
            sku = order['meta']['sku']
            minconfs = self.config['min_confs']

            if not sku in self.config['skus']:
                logging.warning("bad sku: %s" % sku)
                continue

            price = self.config['skus'][sku]['price']

            if not currency in self.config['accepted_currencies']: continue

            # get the balance for this address
            res = tilt.balance_address(currency, address, minconfs)

            balance = res['balance']

            # calculate the amount needed based on the configured price
            quote_res = tilt.quote(currency + self.config['price_currency'])
            amount_needed = price / quote_res['price']

            logging.info("address %s has %s needs %s %s (minconfs: %s)" % \
                (address, balance, amount_needed, currency, minconfs))

            # the address balance has sufficient funds, deliver the product
            if balance >= amount_needed:
                self.deliver(order_key, to_email, sku)
                
    def deliver(self, order_key, to_email, sku):
        logging.info("delivering %s to %s" % (sku, to_email))
        filename = self.config['skus'][sku]['file']
        filetype = self.config['skus'][sku]['type']
        with open(self.config['book_dir'] + '/' + filename, 'rb') as f:
            data = f.read()
        encoded_file = base64.b64encode(data).decode()
        content = Content("text/plain", self.config['mail_text'])
        msg = Mail(From(self.from_email), To(to_email),
            self.config['mail_subject'], content)
        msg.attachment = Attachment(
            FileContent(encoded_file),
            FileName(filename),
            FileType(filetype),
            Disposition('attachment')
        )
        try:
            sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
            res = sg.send(msg)
            logging.info("delivered to %s", to_email)
            self.orders[order_key]['delivered'] = True
            self.save()
        except Exception as e:
            logging.error("delivery failed: %s" % e)

def main():
    ebs = EBookServer()
    ebs.start()

if __name__ == "__main__":
    main()

