from flask import Flask, render_template, request, redirect
from helpers import place_trade, get_stock_info
from csv import reader

app = Flask(__name__)

@app.route('/view_tradebook')
def view_tradebook():
    with open("data/trade_book.csv", "r") as f:
        csv_reader = reader(f)
        tradebook = list(csv_reader)[1:]
    return render_template('trade_book.html', tradebook=tradebook)

from flask import Flask, render_template, request
from helpers import place_trade

@app.route('/place_trade', methods=['GET', 'POST'])
def place_trade_page():
    if request.method == 'POST':
        scrip = request.form['scrip']
        quantity = request.form['quantity']
        place_trade(scrip, "BSE", quantity)
        return redirect("/view_tradebook")
    else:
        return render_template('place_trade.html')

@app.route('/view_portfolio', methods = ['GET', 'POST'])
def view_portfolio():
    with open("data/trade_book.csv", "r") as f:
        csv_reader = reader(f)
        tradebook = list(csv_reader)[1:]

    portfolio = {}
    overall_investment = 0
    overall_pnl = 0

    for trade in tradebook:
        scrip = trade[0]
        quantity = int(trade[2])
        price = float(trade[3])

        if scrip not in portfolio:
            portfolio[scrip] = {'quantity': 0, 'average_price': 0, 'current_price': price, 'total_cost': 0, 'value': 0, 'pnl': 0}

        if quantity > 0:
            portfolio[scrip]['quantity'] += quantity
            overall_investment += quantity * price
            portfolio[scrip]['average_price'] = (portfolio[scrip]['average_price'] * (portfolio[scrip]['quantity'] - quantity) + quantity * price) / portfolio[scrip]['quantity']
            portfolio[scrip]['total_cost'] += quantity * price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += portfolio[scrip]['pnl']

        else:
            quantity = abs(quantity)
            portfolio[scrip]['quantity'] -= quantity
            overall_investment -= quantity * price
            portfolio[scrip]['average_price'] = (portfolio[scrip]['average_price'] * (portfolio[scrip]['quantity'] + quantity) - quantity * price) / portfolio[scrip]['quantity']
            portfolio[scrip]['total_cost'] -= quantity * price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += quantity * (price - portfolio[scrip]['average_price'])

    if request.method == 'POST':
        for scrip in portfolio.keys():
            price, _ = get_stock_info(scrip+".BSE")
            portfolio[scrip]['current_price'] = price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += portfolio[scrip]['pnl']

    return render_template('portfolio.html', portfolio=portfolio, overall_investment=overall_investment, overall_pnl=overall_pnl)
    
@app.route('/')
def all_pages():
    pages = [
        {'url': '/view_tradebook', 'name': 'View Tradebook'},
        {'url': '/place_trade', 'name': 'Place Trade'},
        {'url': '/view_portfolio', 'name': 'View Portfolio'}
    ]
    return render_template('index.html', pages=pages)
    
if __name__ == '__main__':
    app.run(debug=True)