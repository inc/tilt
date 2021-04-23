#!/bin/python3
#
# Tilt - Wallet Manager
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import json
import os
import time
import glob
import logging
import sys
import pprint
import zipfile

import bitcoinlib
from bitcoinlib.keys import Key
from cryptography.fernet import Fernet

import tilt.utils as tilt

class WalletManager:

    def __init__(self):
        tilt.setup()
        self.tiltdir = os.path.expanduser("~/.tilt")
        self.walletdir = self.tiltdir + '/wallet'
        wallet_key = tilt.get_config("wallet_key")
        self.fernet = Fernet(wallet_key)
        return

    # create a new address/key pair, return the new address
    def create(self, currency, meta={}, label=None, unused=False):

        k = Key(network=self.currency_to_network(currency))

        address = k.address()

        wif_plain_bytes = k.wif().encode('utf-8')
        wif_cipher_bytes = self.fernet.encrypt(wif_plain_bytes).decode('utf-8')

        r = {
            'currency': currency,
            'address': address,
            'cipher_wif': wif_cipher_bytes,
            'meta': meta,
            'label': label,
            'unused': unused,
            'ts': int(time.time())
        }

        fn = self.walletdir + "/" + currency + "." + address + ".json"
        with open(os.open(fn, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as f:
            f.write(json.dumps(r))

        return address

    # create new unused address/key pairs, return the new address
    def create_unused(self, currency, quantity=1):
        addrs = []
        for i in range(quantity):
            addrs.append(self.create(currency, unused=True))
        return addrs

    def load(self, filename):
        with open(filename, "r") as f:
            return json.loads(f.read())

    def decrypt(self, filename):
        w = self.load(filename)
        wif_cipher_bytes = w['cipher_wif'].encode('utf-8')
        w['plain_wif'] = self.fernet.decrypt(wif_cipher_bytes).decode('utf-8')
        del w['cipher_wif']
        return w

    def exists(self, currency, address):
        fn = self.walletdir + "/" + currency + "." + address + ".json"
        return os.path.isfile(fn)

    def get(self, currency, address):
        fn = self.walletdir + "/" + currency + "." + address + ".json"
        return self.decrypt(fn)

    def show(self, currency, address):
        pp = pprint.PrettyPrinter()
        pp.pprint(self.get(currency, address))

    def list(self, currency, show_labels=False, show_balances=False,
        show_unused=False, confs=6):

        if currency:
            fn = self.walletdir + "/" + currency + ".*.json"
        else:
            fn = self.walletdir + "/*.json"

        balances = {}
        if show_balances:
            res = tilt.balances(confs)
            balances = res['balances']

        files = list(glob.iglob(fn))
        files.sort(key=os.path.getmtime)

        for fn in files:
            fs = os.path.basename(fn).split('.')

            with open(fn) as f:
                w = json.loads(f.read())

            if 'unused' in w and w['unused'] and not show_unused:
                continue

            print(fs[0], "\t", fs[1], end='')

            if fs[0] in balances and fs[1] in balances[fs[0]]:
                balance = balances[fs[0]][fs[1]]
            else:
                balance = 0

            if show_balances:
                print("\t", balance, end='')

            if show_labels:
                    label = ''
                    if 'label' in w and w['label']: label = w['label']
                    print("\t", label, end='')

            print('', flush=True)

    def freeze(self):
        zfn = 'tilt-freeze-' + str(int(time.time())) + '.zip'
        with zipfile.ZipFile(zfn, 'w') as z:
            files = list(glob.iglob(self.walletdir + '/*.json'))
            for f in files:
                an = os.path.basename(f)
                plainjson = json.dumps(self.decrypt(f))
                z.writestr('wallet/' + an, plainjson)
            logging.info("froze %s files" % len(files))

    def destroy(self, zfn):
        logging.warning("about to permanently delete every file in" \
            " ~/.tilt/wallet that also exists in " + zfn + \
            "; type 'yes' to proceed:")
        res = input()
        if res != "yes":
            print("aborted")
            return
        with zipfile.ZipFile(zfn, 'r') as z:
            files = z.namelist()
            for f in files:
                print("deleting", f)

    def currency_to_network(self, currency):
        if currency == "btc": return "bitcoin"
        if currency == "tbtc": return "testnet"
        if currency == "ltc": return "litecoin"
        if currency == "tltc": return "litecoin_testnet"
        if currency == "doge": return "dogecoin"
        if currency == "tdoge": return "dogecoin_testnet"
        raise Exception("unsupported currency", currency)
