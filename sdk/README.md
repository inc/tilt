# Tilt - Cryptocurrency Payments Platform - SDK

## Software Development Kit

This Software Development Kit contains documentation and examples to help you integrate with Tilt and develop your own payment solution.

In order to test your integration with Tilt we recommend using TDOGE and requesting free coins from a Dogecoin Testnet Faucet.

## Examples

 - [Donation Example](examples/donate)

## API

Most of the API can be accessed directly from your website or app.

The API requests are available as both HTTPS GET and POST requests that return JSON data. See the Curl examples below for details about using the API directly.

The latest JavaScript library is available at https://tilt.cash/js/tilt.js.

### API Key

The API key should *not* be exposed to the public. Methods that require the API key should only be called from a private server and not directly from your website or app as they may expose private data such as your wallet balance.

### Curl Examples

#### Create an Address

This method will ask your wallet service to create a new address/key pair, the address will become monitored for transactions by the Tilt service and the address will be returned.

```
curl -X GET https://tilt.cash/api/v1/create_address?currency=btc&wallet=1234
```

->

```
{"address": "...", "ok": true}
```


#### Create a Payment Intent

This method creates an expected future payment with associated metadata and returns the address where the payment should be sent. The metadata object can contain any fields you choose. The metadata is stored on your private server and Tilt servers.

```
curl -X POST -H "Content-Type: application/json" -d '{"wallet":1234,"currency":"btc","meta":{"amount":0.0013,"email":"test@tilt.cash"}}' https://tilt.cash/api/v1/create_address

```

->

```
{"address": "...", "ok": true}
```

#### Create a Labelled Address

The create\_address methods support an optional "label" field that can be used to create an unlimited number of separate wallet namespaces. Using a label such as "\<mysite\>\_\<userid\>" will allow you to create a per-site per-user wallet namespace. The namespace is unique to the specified wallet and can contain any alpha-numeric characters plus underscores.

Note: You must use either the received\_label or received\_address method to get the total amount received by labelled addresses. The total amount received by labelled addresses will *not* be reflected by received\_wallet. The balance\_wallet method will retrieve the total amount unspent by both labelled and unlabelled addresses.

```
curl -X GET https://tilt.cash/api/v1/create_address?currency=btc&wallet=1234&label=mysite_user12345
```

->

```
{"address": "...", "ok": true}
```

#### Get Balance by Wallet

Retrieve the amount unspent for this wallet, including labelled and unlabelled addresses. Optionally specify the minimum number of required confirmations (the default is 6). An API key is required for this method. Do *not* call this directly from a website or app.

```
curl https://tilt.cash/api/v1/balance_wallet?wallet=1234&currency=btc&confs=1&apikey=1234
```

->

```
{"balance": 123.45678, "ok": true}
```


#### Get Balance by Address

Retrieve the amount unspent for this address. Optionally specify the minimum number of required confirmations (the default is 6).

```
curl https://tilt.cash/api/v1/balance_address?currency=btc&address=abcd&confs=1
```

->

```
{"balance": 0.1234, "ok": true}
```

#### Get Balance by Label

Retrieve the amount unspent with this label. Optionally specify the minimum number of required confirmations (the default is 6). An API key is required for this method. Do *not* call this directly from a website or app.

```
curl https://tilt.cash/api/v1/balance_label?currency=btc&wallet=1234&label=mysite_user12345&confs=60&apikey=1234
```

->

```
{"balance": 0.0054321, "ok": true}
```

#### Get Amount Received by Wallet

Retrieve amount received by this wallet. Optionally specify the minimum number of required confirmations (the default is 6). An API key is required for this method. Do *not* call this directly from a website or app.

Note: Unlike the balance\_wallet method, labelled addresses are *not* included in this total.

```
curl https://tilt.cash/api/v1/received_wallet?wallet=1234&currency=btc&confs=1&apikey=1234
```

->

```
{"received": 123.45678, "ok": true}
```

#### Get Amount Received by Address

Retrieve the amount received by this address. Optionally specify the minimum number of required confirmations (the default is 6).

```
curl https://tilt.cash/api/v1/received_address?currency=btc&address=abcd&confs=1
```

->

```
{"received": 0.1234, "ok": true}
```

#### Get Amount Received by Label

Retrieve the amount received with this label. Optionally specify the minimum number of required confirmations (the default is 6). An API key is required for this method. Do *not* call this directly from a website or app.

```
curl https://tilt.cash/api/v1/received_label?currency=btc&wallet=1234&label=mysite_user12345&confs=60&apikey=1234
```

->

```
{"received": 0.0054321, "ok": true}
```

#### Request a Price Quote

The quote method allows you to get a real-time quote for the exchange rate between different currencies.

```
GET https://tilt.cash/api/v1/quote?sym=btcusd
```

->

```
{"price": 2343.32, "price_str": "2343.320000000000", "ok": true}
```

### JavaScript

```
TILT.set_wallet_id(wallet_id)
TILT.create_address(currency, callback(res))
TILT.create_address(currency, meta, callback(res))
TILT.create_address(currency, meta, label, callback(res))
TILT.balance_address(currency, address, callback(res))
TILT.received_address(currency, address, callback(res))
TILT.quote(symbol, callback(res))
TILT.ping(wallet, callback(res))
```

### Python

```
import tilt.utils as tilt
tilt.create_address(currency)
tilt.create_address(currency, meta)
tilt.create_address(currency, meta, label)
tilt.balance_wallet(wallet, currency)
tilt.balance_address(wallet, currency, address)
tilt.balance_label(wallet, currency, label)
tilt.received_wallet(wallet, currency)
tilt.received_address(wallet, currency, address)
tilt.received_label(wallet, currency, label)
tilt.quote(symbol)
```
