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

This method creates an expected future payment with associated metadata and returns the address where the payment should be sent.

```
curl -X POST -H "Content-Type: application/json" -d '{"wallet":1234,"currency":"btc","meta":{"amount":0.0013,"email":"test@tilt.cash"}}' https://tilt.cash/api/v1/create_address

```

->

```
{"address": "...", "ok": true}
```

#### Get Amount Received by Wallet

Retrieve amount received by this wallet. Optionally specify the minimum number of required confirmations (the default is 6). An API key is required for this method. Do *not* call this directly from a website or app.

```
curl https://tilt.cash/api/v1/received_wallet?currency=btc&confs=1&apikey=1234
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
TILT.received_address(wallet, currency, address, callback(res))
TILT.quote(symbol, callback(res))
TILT.ping(wallet, callback(res))
```

### Python

```
import tilt.utils as tilt
tilt.create_address(currency)
tilt.create_address(currency, meta)
tilt.received_wallet(wallet, currency)
tilt.received_address(wallet, currency, address)
tilt.quote(symbol)
```
