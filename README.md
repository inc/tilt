# Tilt - Cryptocurrency Payments Platform

## Overview

Tilt enables you to easily accept cryptocurrencies from your website or app while retaining control of your private keys.

Tilt is a platform and API for developers that makes it easy to implement a cryptocurrency payment solution by giving you the ability to generate addresses, monitor addresses, get notified about transactions, keep track of payments, exchange rates and more.

See the [SDK](sdk) directory for API documentation and integration examples.

## Supported Currencies

 - Mainnet: BTC, LTC, DOGE
 - Testnet: TDOGE

## Supported Quote Symbols

 - BTCUSD, LTCUSD, DOGEUSD, BTCEUR, LTCEUR, DOGEEUR

## Getting Started

 1. Install Tilt (see Installation below).
 2. Run `tilt init` to create the ~/.tilt directory structure and wallet key.
 3. Run `tilt register` to provision Tilt server keys and a wallet ID.
 4. Run `tilt start` to start the wallet service in the background.
 5. Run `tilt ping` to test your setup.
 6. Integrate the SDK into your site or app.
 7. Begin accepting payments.
 8. Run `tilt monitor` to view transactions in real-time.
 9. Visit https://tilt.cash to access the web-based interface.

## Installation

```
$ sudo apt-get install build-essential python3 python3-dev python3-venv libgmp3-dev
$ git clone git://github.com/inc/tilt
$ cd tilt
$ python3 -mvenv env
$ source env/bin/activate
$ pip install --upgrade pip
$ pip install .
$ tilt info
```

## Wallet Service

The Tilt wallet service is designed to run on a private server (or always-on local computer) and act as a hot wallet. It maintains a constant WebSocket connection to the Tilt servers. Requests from your site or app are routed through the Tilt servers to your wallet service.

The private keys are generated and stored on your private server and therefore they are *not* be accessible to Tilt or anyone else.

## Tilt Directory

Tilt maintains a directory inside your home directory at ~/.tilt.

| File/Directory | Description |
| -------------- | ----------- |
| api\_key | Secret API key |
| site\_key | Secret key for importing your wallet on the Tilt website |
| srv\_key | Secret key for connecting to the Tilt service |
| tilt.log | Output of the wallet service |
| tiltwlt.pid | Pid of the wallet service |
| wallet/ | Directory containing addresses, encrypted keys and metadata |
| wallet\_id | Non-secret ID of your wallet |
| wallet\_key | Secret key used to encrypt your private keys |

## FAQ

 - Q: Why should I use Tilt?
 - A: Tilt makes it easy for you to accept crypto payments while maintaining control of your private keys. Tilt avoids the _"Not Your Keys, Not Your Coins"_ problem by ensuring that only you have access to the private keys.

 - Q: Why do I need Tilt?
 - A: You don't, but some aspects of this infrastructure are complicated and potentially expensive to operate and maintain. Tilt is intended for those who don't have the time, expertise or desire to develop an end-to-end solution on their own but still want to retain complete control over their private keys.

 - Q: Why can't I just distribute my crypto address and let people send me money?
 - A: It is recommended to generate a new address for each transaction. Additionally, by generating a new address for each transaction you will be able to track who paid you and what the payment was for, which is important for certain types of payment solutions (online stores, subscriptions, etc.)

 - Q: How much does Tilt cost?
 - A: Tilt is completely free during the beta testing phase. Basic usage of Tilt will remain free with some limitations in the future. Tilt will use a freemium pricing model that scales with your usage. Find the latest details at https://tilt.cash.

 - Q: Why should I trust you?
 - A: Tilt doesn't have or want access to your private keys. The wallet portion of Tilt is open-source and we encourage everyone to audit the source code and contact us regarding any potential security issues. It is in our interest for you to continue using Tilt as your needs grow. To that end, it is also in our interest to operate in an honest and reliable manner.

 - Q: What if the Tilt service is discontinued?
 - A: Your private keys and copies of your metadata are stored on your own servers, so you wouldn't lose anything of value except access to our API.

 - Q: Who operates Tilt?
 - A: Tilt is a service provided by [Lone Dynamics Corporation](https://lonedynamics.com).

## Security

Hot wallets are potentially vulnerable to attacks from hackers and it is not recommended to store private keys on computers connected to the Internet longer than necessary.

Virtual private servers (VPS) may be potentially vulnerable to certain types of attacks that could compromise your keys.

Private keys are stored encrypted as an additional level of security which means that you *must* back up your ~/.tilt/wallet\_key along with your address and keys.

You can also use the 'tilt freeze' command which will create a zip file containing all of your wallet data without any encryption. You can then copy this file to another computer and verify it's contents before removing the keys from your hot wallet using 'tilt destroy'.

## Command Line Interface

### Init

This command creates a new Tilt wallet. You only need to do this once. This will create a ~/.tilt directory containing your wallet key.

```
$ tilt init 
```

### Register

This command registers your wallet with the Tilt service. You only need to do this once. This will create a wallet ID, API key, and allow you to use to the Tilt service.

```
$ tilt register
```

### Info

This command displays information about your Tilt instance.

```
$ tilt info
```

### Start

This command will start the wallet service in the background.

```
$ tilt start
```

### Status

This command will report whether or not the wallet service is running.

```
$ tilt status
```

### Stop

This command will stop the wallet service.

```
$ tilt stop
```

### Ping

The ping command can be used to determine if your wallet server instance is running and communicating correctly with the Tilt service. It sends a request to the Tilt API which is routed back to your local wallet server instance, which will then send a reply to Tilt, which will then complete the API request. If your local service isn't running or isn't connected, you'll see an error.

```
$ tilt ping
```

### Create Address/Key Pair

This command creates a new address and private key for the specified currency and stores them in your wallet. The private key is stored encrypted using your wallet key. The address is also registered with the Tilt service so that you will receive transaction notifications.

You can optionally include a label that will assign the address to a separate wallet namespace. The total amount received of labelled addresses is not be reflected by the `tilt received` command and instead you must use either the `tilt received-label` or `tilt received-address` command.

```
$ tilt create <currency> [label]
```

### Display Amount Received (Wallet)

This command displays the total amount received by your wallet for the specified currency. You can optionally specify the number of confirmations required for a transaction to be included in the total amount received.

```
$ tilt received <currency> [confirmations]
```

### Display Amount Received (Address)

This command displays the total amount received by a specific address. You can optionally specify the number of confirmations required for a transaction to be included in the total amount received.

```
$ tilt received-address <currency> <addr> [confirmations]
```

### Display Amount Received (Label)

This command displays the total amount received by a specific label. You can optionally specify the number of confirmations required for a transaction to be included in the total amount received.

```
$ tilt received-label <currency> <label> [confirmations]
```

### Display Address/Key Pair

This command displays the wallet entry for the given address, including the decrypted private key, any associated metadata and label.

```
$ tilt show <currency> <addr>
```

### List Addresses

This command displays a list of all of your addresses.

```
$ tilt show [currency]
```

### Quote

This command displays a price quote for a given symbol (i.e. BTCUSD).

```
$ tilt quote <sym>
```

### Monitor Activity

This command will display real-time activity between the Tilt service and your local wallet service, including notifications of transactions.

```
$ tilt monitor
```

### Freeze

This command creates a zip file containing all of your wallet data without any encryption. This command does not remove any keys, see 'destroy' for that.

```
$ tilt freeze
```

### Destroy

This command will permanently erase files from your hot wallet for those keys that are found in a previously frozen zip file. Use this after you have moved your keys to a cold wallet and unzipped the frozen file. You will be prompted for confirmation.

```
$ tilt destroy <frozen zip> --i-know-what-i-am-doing
```
