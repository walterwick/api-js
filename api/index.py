from flask import Flask, render_template_string
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
    balances = []

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
            
            balances.append({
                'coin': asset,
                'balance': free_balance,
                'value_in_usd': value_in_usd
            })
            total_value_in_usd += value_in_usd

    # Get USDT/TRY price from Binance API
    try:
        usdt_try_price = float(requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTTRY").json()['price'])
        total_value_in_try = total_value_in_usd * usdt_try_price
    except Exception as e:
        print(f"Could not get USDT/TRY price: {e}")
        total_value_in_try = None

    # HTML content with enhanced CSS styling and dark mode support
    html_content = '''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ total_value_in_usd }}</title>
        <style>
            /* Reset some default styling */
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            /* Base styling */
            body {
                font-family: Arial, sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 20px;
                background-color: #f4f4f9;
                color: #333;
            }

            h1 {
                font-size: 2.5em;
                margin-bottom: 20px;
                color: #0073e6;
            }

            form {
                margin-bottom: 20px;
            }

            input[type="submit"] {
                padding: 12px 25px;
                font-size: 1.1em;
                color: #fff;
                background-color: #0073e6;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                transition: background-color 0.3s ease, transform 0.2s ease;
                box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            }

            input[type="submit"]:hover {
                background-color: #005bb5;
                transform: scale(1.05);
            }

            table {
                width: 80%;
                max-width: 700px;
                border-collapse: separate;
                border-spacing: 0;
                overflow: hidden;
                box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                margin-top: 20px;
            }

            th, td {
                padding: 15px;
                text-align: left;
                border-bottom: 1px solid #ddd;
                transition: background-color 0.3s;
            }

            th {
                background-color: #0073e6;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
                font-size: 0.9em;
            }

            tr:nth-child(even) {
                background-color: #f9f9f9;
            }

            tr:hover td {
                background-color: #e0f1ff;
            }

            td {
                font-size: 1em;
            }

            h3 {
                margin-top: 20px;
                color: #555;
                font-size: 1.1em;
            }

            /* Dark mode styles */
            @media (prefers-color-scheme: dark) {
                body {
                    background-color: #1e1e1e;
                    color: #f5f5f5;
                }

                h1 {
                    color: #4dabf7;
                }

                input[type="submit"] {
                    background-color: #4dabf7;
                    color: #1e1e1e;
                }

                input[type="submit"]:hover {
                    background-color: #3a8cc7;
                }

                table {
                    border: 1px solid #333;
                    background-color: #2a2a2a;
                }

                th {
                    background-color: #4dabf7;
                }

                tr:nth-child(even) {
                    background-color: #333;
                }

                tr:hover td {
                    background-color: #3a3a3a;
                }

                h3 {
                    color: #ddd;
                }
            }
        </style>
    </head>
    <body>
        <h1>Binance Bakiye Kontrol</h1>
        <form method="GET">
            <input type="submit" value="Bakiye Kontrol Et">
        </form>

        {% if balances %}
            <h2>Bakiye Bilgileri</h2>
            <table>
                <tr>
                    <th>Coin</th>
                    <th>Bakiye</th>
                    <th>Değer (USD)</th>
                </tr>
                {% for balance in balances %}
                <tr>
                    <td>{{ balance.coin }}</td>
                    <td>{{ balance.balance }}</td>
                    <td>{{ balance.value_in_usd }}</td>
                </tr>
                {% endfor %}
            </table>
            <h3>Toplam Değer (USD): {{ total_value_in_usd }}</h3>
            {% if total_value_in_try is not none %}
                <h3>Toplam Değer (TRY): {{ total_value_in_try }}</h3>
            {% endif %}
        {% endif %}
    </body>
    </html>
    '''

    return render_template_string(html_content, balances=balances, total_value_in_usd=total_value_in_usd, total_value_in_try=total_value_in_try)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
