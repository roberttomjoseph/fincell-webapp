#remember to change the tradebook path to absolute path while uploading to pythonanywhere

from flask import Flask, render_template, request, redirect, flash, url_for
from jinja2 import Environment, select_autoescape
from helpers import place_equity_trade, get_ltp
from csv import reader
import json

app = Flask(__name__)
app.secret_key = 'matlab ye secret key hai'

env = Environment(autoescape=select_autoescape(['html', 'xml']))

def intcomma(value):
    return "{:,}".format(value)

app.jinja_env.filters['intcomma'] = intcomma

@app.route('/')
def index():
    pages = [
        {'url': '/equity', 'name': 'Short-term Trades'},
        {'url': 'https://fincell.org', 'name': 'Long-term Trades - Coming soon!'},
    ]
    return render_template('index.html', pages=pages)

@app.route('/equity')
def all_equity_pages():
    pages = [
        {'url': '/equity/view_tradebook', 'name': 'View Tradebook'},
        {'url': '/equity/place_trade', 'name': 'Place Trade'},
        {'url': '/equity/view_portfolio', 'name': 'View Positions'}
    ]
    return render_template('portfolio_index.html', portfolio_name = "Equity Portfolio", pages=pages)

@app.route('/equity/view_tradebook')
def view_tradebook():
    with open("data/equity_trade_book.csv", "r") as f:
    #with open("/home/fincell/mysite/data/equity_trade_book.csv", "r") as f:

        csv_reader = reader(f)
        tradebook = list(csv_reader)[1:]
    return render_template('trade_book.html', tradebook=tradebook)

@app.route('/equity/place_trade', methods=['GET', 'POST'])
def place_trade_page():
    if request.method == 'POST':
        scrip = request.form['scrip']
        quantity = request.form['quantity']
        entered_code = request.form['analyst_code']

        # Load the valid analyst codes
        with open('data/analyst_codes.json', 'r') as file:
        #with open('/home/fincell/mysite/data/analyst_codes.json', 'r') as file:
            valid_codes = list(json.load(file).values())

        # Check if the entered code is valid
        if entered_code not in valid_codes:
            flash('Invalid analyst code', 'error')
            return redirect(url_for('place_trade_page'))

        place_equity_trade(scrip=scrip, exchange="NS", quantity=quantity, trade_type="equity")
        return redirect("/equity/view_tradebook")
    else:
        return render_template('place_trade.html')

@app.route('/equity/view_portfolio', methods = ['GET', 'POST'])
def view_portfolio():
    with open("data/equity_trade_book.csv", "r") as f:
    #with open("/home/fincell/mysite/data/equity_trade_book.csv", "r") as f:

        csv_reader = reader(f)
        tradebook = list(csv_reader)[1:]

    portfolio = {}
    invested_amount = 0
    overall_pnl = 0
    portfolio_value = 0

    for trade in tradebook:
        scrip = trade[0]
        quantity = int(trade[2])
        price = float(trade[3])

        if scrip not in portfolio:
            portfolio[scrip] = {'quantity': 0, 'average_price': 0, 'current_price': price, 'total_cost': 0, 'value': 0, 'pnl': 0}

        if quantity > 0:
            portfolio[scrip]['quantity'] += quantity
            portfolio[scrip]['average_price'] = (portfolio[scrip]['average_price'] * (portfolio[scrip]['quantity'] - quantity) + quantity * price) / portfolio[scrip]['quantity']
            portfolio[scrip]['total_cost'] += quantity * price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += portfolio[scrip]['pnl']

        else:
            quantity = abs(quantity)
            portfolio[scrip]['quantity'] -= quantity
            portfolio[scrip]['average_price'] = (portfolio[scrip]['average_price'] * (portfolio[scrip]['quantity'] + quantity) - quantity * price) / portfolio[scrip]['quantity']
            portfolio[scrip]['total_cost'] -= quantity * price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += quantity * (price - portfolio[scrip]['average_price'])

        invested_amount += quantity * portfolio[scrip]['average_price']
        portfolio_value += portfolio[scrip]['value']

    if request.method == 'POST':
        for scrip in portfolio.keys():
            price = get_ltp(scrip+".NS")[0]
            portfolio[scrip]['current_price'] = price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += portfolio[scrip]['pnl']

    return render_template('portfolio.html', portfolio=portfolio, invested_amount=invested_amount, overall_pnl=overall_pnl, portfolio_value=portfolio_value)

if __name__ == '__main__':
    app.run(debug=True)