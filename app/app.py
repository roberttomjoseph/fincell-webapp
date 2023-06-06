from flask import Flask, render_template, request
import json
import requests
import time

from definitions import PORTFOLIO_DATA_FILE

app = Flask(__name__)

def get_price(symbol):
    api_key = 'JL4CMULKA8L7SEAK'
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    price = float(data['Global Quote']['05. price'])
    return price

def calculate_cost():
    with open(PORTFOLIO_DATA_FILE) as f:
        data = json.load(f)
    total_cost = 0
    for stock in data['stocks']:
        total_cost += stock['quantity'] * stock['avg_price']
    return total_cost

def calculate_pnl():
    with open(PORTFOLIO_DATA_FILE) as f:
        data = json.load(f)
    total_value = 0
    for stock in data['stocks']:
        total_value += stock['quantity'] * stock['ltp']
     
    return total_value - data['total_cost']

@app.route('/view_portfolio', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        with open(PORTFOLIO_DATA_FILE, 'r') as f:
            data = json.load(f)
            for stock in data['stocks']:
                price = get_price(stock['ticker'])
                stock['ltp'] = price
                stock['pnl'] = (price - stock['avg_price']) * stock['quantity']
            data['last_updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
            data['net_pnl'] = calculate_pnl()
            data['total_cost'] = calculate_cost()
        with open(PORTFOLIO_DATA_FILE, 'w') as f:
            json.dump(data, f)

        return render_template('view_portfolio.html', data=data)
    
    else:
        with open(PORTFOLIO_DATA_FILE, 'r') as f:
            data = json.load(f)
            return render_template('view_portfolio.html', data=data)

if __name__ == '__main__':
    print("http://127.0.0.1:5000/view_portfolio")
    app.run(debug=True)