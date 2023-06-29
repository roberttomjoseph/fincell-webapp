import requests
from csv import writer

def get_stock_info(ticker):
    api_key = "JL4CMULKA8L7SEAK" # Replace with your Alpha Vantage API key
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    cost = float(data["Global Quote"]["05. price"])
    time = data["Global Quote"]["07. latest trading day"]
    return [cost, time]

def place_trade(scrip, exchange, quantity):
    trade_details = [scrip, exchange, quantity] + get_stock_info(f"{scrip}.{exchange}")
    with open("data/trade_book.csv", "a", newline='') as f:
        csv_writer = writer(f)
        csv_writer.writerow(trade_details)
        f.close()
    print(f"Trade placed successfully! - {trade_details}")