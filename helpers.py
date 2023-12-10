from csv import writer
import yfinance as yf
from datetime import datetime
import time


def get_ltp(symbol):

    def round_to_nearest_05(n):
        return round(n * 20) / 20

    def truncate_to_two_decimal_points(n):
        return "{:.2f}".format(n)

    ticker = yf.Ticker(symbol)
    todays_data = ticker.history(period='1d')
    ltp = todays_data['Close'].iloc[0]
    ltp = round_to_nearest_05(ltp)
    ltp = float(truncate_to_two_decimal_points(ltp))
    formatted_time = datetime.fromtimestamp(time.time()).strftime('%H:%M:%S %d/%m/%Y')
    return [ltp, formatted_time]

def place_equity_trade(scrip, exchange, quantity, trade_type):
    trade_details = [scrip, exchange, quantity] + get_ltp(f"{scrip}.{exchange}")
    with open("data/equity_trade_book.csv", "a", newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerow(trade_details)
        f.close()
    print(f"Trade placed successfully! - {trade_details}")