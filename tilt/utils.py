#!/bin/python3
#
# Tilt - Utility Functions
# Copyright (c) 2021 Lone Dynamics Corporation. All rights reserved.
#

import os
import json
import logging
import requests

from cryptography.fernet import Fernet

VERSION = "0.0.1"

def setup():
    logging.basicConfig(format='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)

## --

def ping():
    req = {
        'wallet': get_config("wallet_id"),
    }
    r = requests.post('https://tilt.cash/api/v1/ping', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def create_address(currency, label):
    req = {
        'wallet': get_config("wallet_id"),
        'currency': currency
    }
    if label: req['label'] = label
    r = requests.post('https://tilt.cash/api/v1/create_address', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def balance_wallet(currency, confs):
    req = {
        'wallet': get_config("wallet_id"),
        'api_key': get_config("api_key"),
        'currency': currency
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/balance_wallet', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def balance_address(currency, address, confs):
    req = {
        'address': address,
        'currency': currency
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/balance_address', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def balance_label(currency, label, confs):
    req = {
        'wallet': get_config("wallet_id"),
        'api_key': get_config("api_key"),
        'currency': currency,
        'label': label
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/balance_label', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def received_wallet(currency, confs):
    req = {
        'wallet': get_config("wallet_id"),
        'api_key': get_config("api_key"),
        'currency': currency
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/received_wallet', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def received_address(currency, address, confs):
    req = {
        'address': address,
        'currency': currency
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/received_address', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def received_label(currency, label, confs):
    req = {
        'wallet': get_config("wallet_id"),
        'api_key': get_config("api_key"),
        'currency': currency,
        'label': label
    }
    if confs: req['confs'] = int(confs)
    r = requests.post('https://tilt.cash/api/v1/received_label', json=req)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

def quote(sym):
    r = requests.get('https://tilt.cash/api/v1/quote?sym=' + sym)
    try:
        return(r.json())
    except:
        logging.error("request failed; is tiltwlt running?")

## --

def init_config():

    logging.info("initializing wallet")

    tiltdir = os.path.expanduser("~/.tilt")

    if os.path.exists(tiltdir):
        logging.error("~/.tilt already exists; exiting")
        exit(1)

    os.mkdir(tiltdir, mode=0o700)
    os.mkdir(tiltdir + "/wallet", mode=0o700)

    put_config("wallet_key", Fernet.generate_key().decode('utf-8'))

    logging.info("initialized")

def register():
    logging.info("registering wallet")
    r = requests.get('https://tilt.cash/api/v1/register')
    res = r.json()   
    if res['ok']:
        put_config("wallet_id", res['wallet'])
        put_config("api_key", res['api_key'])
        put_config("srv_key", res['srv_key'])
        put_config("site_key", res['site_key'])
        logging.info("registered")

def has_config(key):

    tiltdir = os.path.expanduser("~/.tilt")

    if not os.path.exists(tiltdir):
        return False

    cfg_file = tiltdir + "/" + key

    if not os.path.exists(cfg_file):
        return False
    
    return True 

def get_config(key):

    tiltdir = os.path.expanduser("~/.tilt")

    if not os.path.exists(tiltdir):
        logging.error(tiltdir + " directory missing; exiting")
        exit(1)

    cfg_file = tiltdir + "/" + key

    if not os.path.exists(cfg_file):
        logging.error(cfg_file + " missing; exiting")
        exit(1)

    with open(cfg_file) as f:
        return f.readline().strip()

def put_config(key, val):

    tiltdir = os.path.expanduser("~/.tilt")

    if not os.path.exists(tiltdir):
        logging.error(tiltdir + " directory missing; exiting")
        exit(1)

    cfg_file = tiltdir + "/" + key

    if os.path.exists(cfg_file):
        logging.error(cfg_file + " already exists; exiting")
        exit(1)

    with open(os.open(cfg_file, os.O_CREAT | os.O_WRONLY, 0o600), 'w') as f:
        f.write(val)
