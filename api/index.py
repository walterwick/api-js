from flask import Flask, jsonify
from binance.client import Client
from dotenv import load_dotenv
import os
import requests

# Load environment variables
load_dotenv()

# Get API keys from .env file
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

app = Flask(__name__)

@app.route('/')
def index():
    total_value_in_usd = 0.0

    # Create Binance client
    client = Client(api_key, api_secret)

    # Get account information
    account_info = client.get_account()

    for balance in account_info['balances']:
        asset = balance['asset']
        free_balance = float(balance['free'])
        
        if free_balance > 0:
            # Get each cryptocurrency's price in USD
            try:
                if asset != 'USDT':
                    price = client.get_symbol_ticker(symbol=f"{asset}USDT")['price']
                    value_in_usd = free_balance * float(price)
                else:
                    value_in_usd = free_balance  # Already in USDT
            except Exception as e:
                print(f"Could not get price for {asset}: {e}")
                continue

            total_value_in_usd += value_in_usd

    # Get USDT/TRY price from Binance API
    try:
        usdt_try_price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTTRY").json()['price'])
        total_value_in_try = total_value_in_usd * usdt_try_price
    except Exception as e:
        print(f"Could not get USDT/TRY price: {e}")
        total_value_in_try = None

    # Return JSON response
    return jsonify({
        "total_usd_value": total_value_in_usd,
        "total_try_value": total_value_in_try
    })

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
