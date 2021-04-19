#!/usr/bin/python3
#
# Tilt - Command Line Interface
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import argparse
import os
import logging
import zmq

import tilt.utils as tilt

from tilt.wlt.wallet import WalletManager
from tilt.wlt.server import WalletService
from tilt.wlt.server import WalletServiceMonitor

class TiltCLI:

    def __init__(self):
        tilt.setup()
        self.zmqctx = zmq.Context()
        self.zmqsock = self.zmqctx.socket(zmq.SUB)
        self.commands = {
            'help': self.do_help,
            'init': self.do_init,
            'register': self.do_register,
            'info': self.do_info,
            'start': self.do_start,
            'status': self.do_status,
            'stop': self.do_stop,
            'server': self.do_server,
            'ping': self.do_ping,
            'monitor': self.do_monitor,
            'create': self.do_wallet_create,
            'show': self.do_wallet_show,
            'list': self.do_wallet_list,
            'freeze': self.do_freeze,
            'destroy': self.do_destroy,
            'balance': self.do_balance_wallet,
            'balance-address': self.do_balance_address,
            'balance-label': self.do_balance_label,
            'received': self.do_received_wallet,
            'received-address': self.do_received_address,
            'received-label': self.do_received_label,
            'quote': self.do_quote,
        }
        self.parse_args()

    def parse_args(self):

        self.parser = argparse.ArgumentParser()
        sp = self.parser.add_subparsers(dest="command")

        sp_help = sp.add_parser("help", help="Display help.")
        sp_init = sp.add_parser("init",
            help="Create the ~/.tilt directory and generate wallet key.")
        sp_register = sp.add_parser("register",
            help="Register this wallet with the Tilt service.")
        sp_info = sp.add_parser("info",
            help="Display info about this Tilt instance.")

        sp_start = sp.add_parser("start",
            help="Start the wallet service in the background.")

        sp_status = sp.add_parser("status",
            help="Display the status of the wallet service.")

        sp_stop = sp.add_parser("stop",
            help="Stop the wallet service.")

        sp_server = sp.add_parser("server",
            help="Start the wallet service in the foreground.")

        sp_monitor = sp.add_parser("monitor",
            help="Monitor activity between the Tilt service.")

        sp_ping = sp.add_parser("ping",
            help="Ping the wallet service via the Tilt service.")

        sp_wallet_create = sp.add_parser("create",
            help="Create a new address and private key.")

        sp_wallet_create.add_argument("currency")
        sp_wallet_create.add_argument("label", nargs='?')

        sp_wallet_show = sp.add_parser("show",
            help="Display private key and metadata for this address.")
        sp_wallet_show.add_argument("currency")
        sp_wallet_show.add_argument("addr")

        sp_wallet_list = sp.add_parser("list",
            help="Display list of all addresses in this wallet.")
        sp_wallet_list.add_argument("currency", nargs='?')
        sp_wallet_list.add_argument("--show-labels", action='store_true') 

        sp_wallet_freeze = sp.add_parser("freeze",
            help="Create a zip file containing decrypted wallet data.")

        sp_wallet_destroy = sp.add_parser("destroy",
            help="Delete ~/.tilt/wallet files that exist in zip file.")
        sp_wallet_destroy.add_argument("zipfile")
        sp_wallet_destroy.add_argument("--i-know-what-i-am-doing",
            action="store_true")

        sp_balance_wallet = sp.add_parser("balance",
            help="Display the balance for this wallet.")
        sp_balance_wallet.add_argument("currency")
        sp_balance_wallet.add_argument("confs", nargs='?')

        sp_balance_address = sp.add_parser("balance-address",
            help="Display the balance for this address.")
        sp_balance_address.add_argument("currency")
        sp_balance_address.add_argument("address")
        sp_balance_address.add_argument("confs", nargs='?')

        sp_balance_label = sp.add_parser("balance-label",
            help="Display the balance for this label.")
        sp_balance_label.add_argument("currency")
        sp_balance_label.add_argument("label")
        sp_balance_label.add_argument("confs", nargs='?')

        sp_received_wallet = sp.add_parser("received",
            help="Display total amount received by unlabelled addresses.")
        sp_received_wallet.add_argument("currency")
        sp_received_wallet.add_argument("confs", nargs='?')

        sp_received_address = sp.add_parser("received-address",
            help="Display total amount received by this address.")
        sp_received_address.add_argument("currency")
        sp_received_address.add_argument("address")
        sp_received_address.add_argument("confs", nargs='?')

        sp_received_label = sp.add_parser("received-label",
            help="Display total amount received with this label.")
        sp_received_label.add_argument("currency")
        sp_received_label.add_argument("label")
        sp_received_label.add_argument("confs", nargs='?')

        sp_quote = sp.add_parser("quote",
            help="Get a price quote for the specified symbol.")
        sp_quote.add_argument("sym")

        self.args = self.parser.parse_args()

    def run(self):
        if self.args.command:
            self.do(self.args.command)
        else:
            self.do_help()

    def do(self, command):
        if command in self.commands:
            self.commands[command]()
        else:
            do_help(self)

    def do_init(self):
        tilt.init_config()

    def do_register(self):
        tilt.register()
        self.do_info()

    def do_info(self):
        logging.info("tilt version: %s" % tilt.VERSION)

        if not tilt.has_config("wallet_key"):
            logging.info("no wallet_key found")

        if tilt.has_config("wallet_id"):
            wallet_id = tilt.get_config("wallet_id")
            logging.info("wallet_id: %s" % wallet_id)
        else:
            logging.info("no wallet_id found")

        if tilt.has_config("api_key"):
            api_key = tilt.get_config("api_key")
            logging.info("api_key: %s" % api_key)
        else:
            logging.info("no api_key found")

        if tilt.has_config("site_key"):
            api_key = tilt.get_config("site_key")
            logging.info("site_key: %s" % api_key)
        else:
            logging.info("no site_key found")

    def do_monitor(self):
        self.zmqsock.connect("tcp://localhost:9090")
        self.zmqsock.setsockopt_string(zmq.SUBSCRIBE, "")
        logging.info("monitoring ...")
        while True:
            msg = self.zmqsock.recv_string()
            logging.info(msg)

    def do_ping(self):
        logging.info(tilt.ping())

    def do_start(self):
        wsm = WalletServiceMonitor()
        wsm.start()

    def do_status(self):
        wsm = WalletServiceMonitor()
        wsm.status()

    def do_stop(self):
        wsm = WalletServiceMonitor()
        wsm.stop()

    def do_server(self):
        ws = WalletService()
        ws.run()

    def do_wallet_create(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        logging.info(tilt.create_address(self.args.currency, self.args.label))

    def do_wallet_show(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        if not self.args.addr:
            print("addr not specified; exiting")
            exit(1)
        wm = WalletManager()
        wm.show(self.args.currency, self.args.addr)

    def do_wallet_list(self):
        wm = WalletManager()
        wm.list(self.args.currency, show_labels=self.args.show_labels)

    def do_freeze(self):
        wm = WalletManager()
        wm.freeze()

    def do_destroy(self):
        if not self.args.zipfile:
            print("zip file not specified; exiting")
            exit(1)
        if not self.args.i_know_what_i_am_doing:
            print("did not confirm that you know what you're doing; exiting")
            exit(1)
        wm = WalletManager()
        wm.destroy(self.args.zipfile)

    def do_balance_wallet(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        logging.info(tilt.balance_wallet(self.args.currency, self.args.confs))

    def do_balance_address(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        if not self.args.address:
            print("address not specified; exiting")
            exit(1)
        logging.info(tilt.balance_address(self.args.currency,
            self.args.address, self.args.confs))

    def do_balance_label(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        if not self.args.label:
            print("label not specified; exiting")
            exit(1)
        logging.info(tilt.balance_label(self.args.currency, self.args.label,
            self.args.confs))

    def do_received_wallet(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        logging.info(tilt.received_wallet(self.args.currency, self.args.confs))

    def do_received_address(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        if not self.args.address:
            print("address not specified; exiting")
            exit(1)
        logging.info(tilt.received_address(self.args.currency,
            self.args.address, self.args.confs))

    def do_received_label(self):
        if not self.args.currency:
            print("currency not specified; exiting")
            exit(1)
        if not self.args.label:
            print("label not specified; exiting")
            exit(1)
        logging.info(tilt.received_label(self.args.currency, self.args.label,
            self.args.confs))

    def do_quote(self):
        if not self.args.sym:
            print("sym not specified; exiting")
            exit(1)
        logging.info(tilt.quote(self.args.sym))

    def do_help(self):
        self.parser.print_help()

def main():
    cli = TiltCLI()
    cli.run()
