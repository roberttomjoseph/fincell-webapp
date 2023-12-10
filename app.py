from flask import Flask, render_template, request, redirect
from helpers import place_equity_trade, get_ltp
from csv import reader

app = Flask(__name__)

@app.route('/equity')
def all_equity_pages():
    pages = [
        {'url': '/equity/view_tradebook', 'name': 'View Tradebook'},
        {'url': '/equity/place_trade', 'name': 'Place Trade'},
        {'url': '/equity/view_portfolio', 'name': 'View Portfolio'}
    ]
    return render_template('index.html', portfolio_name = "Equity Portfolio", pages=pages)

@app.route('/equity/view_tradebook')
def view_tradebook():
    with open("data/equity_trade_book.csv", "r") as f:
        csv_reader = reader(f)
        tradebook = list(csv_reader)[1:]
    return render_template('trade_book.html', tradebook=tradebook)

@app.route('/equity/place_trade', methods=['GET', 'POST'])
def place_trade_page():
    if request.method == 'POST':
        scrip = request.form['scrip']
        quantity = request.form['quantity']
        place_equity_trade(scrip=scrip, exchange="NS", quantity=quantity, trade_type="equity")
        return redirect("/equity/view_tradebook")
    else:
        return render_template('place_trade.html')

@app.route('/equity/view_portfolio', methods = ['GET', 'POST'])
def view_portfolio():
    with open("data/equity_trade_book.csv", "r") as f:
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
            price = get_ltp(scrip+".NS")[0]
            portfolio[scrip]['current_price'] = price
            portfolio[scrip]['value'] = portfolio[scrip]['quantity'] * price
            portfolio[scrip]['pnl'] = portfolio[scrip]['value'] - portfolio[scrip]['total_cost']
            overall_pnl += portfolio[scrip]['pnl']

    return render_template('portfolio.html', portfolio=portfolio, overall_investment=overall_investment, overall_pnl=overall_pnl)

if __name__ == '__main__':
    app.run(debug=True)