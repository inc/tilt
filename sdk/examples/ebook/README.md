# Tilt - Cryptocurrency Payments Platform - Digital Product Deilvery Example

## E-Book Store

This is an example of an online store that sells e-books and uses the Tilt service to help facilitate the acceptance of cryptocurrencies and to automatically fulfill orders.

You will need a SendGrid API key to deliver the email.

## Files

| File/Directory | Description |
| -------------- | ----------- |
| webserver.py | Serves the HTML, JS and config files on port 8000 |
| fulfill.py | Detects transactions and fulfills orders |
| orders.json | Created by fulfill.py |
| web/ | HTML and JS files |
| web/config.json | Configuration options |
| books/ | Example e-books |

## Installation

Install Tilt and activate the environment as described in the main README file.

Then install the additional requirements for this example:

```
pip install -r requirements.txt
```

## Usage

1. Edit config.json and add your Tilt wallet\_id.

2. Run the following commands:

```
export TILT_API_KEY="..."
export SENDGRID_API_KEY="..."

$ python3 webserver.py &
$ python3 fulfill.py

```

3. Visit https://localhost:8000 from your web browser.
