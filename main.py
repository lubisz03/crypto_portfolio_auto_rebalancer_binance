from dotenv import load_dotenv
import os
from binance.spot import Spot
from structure.Rebalancer import Rebalancer
import json


def load_portfolio(filename):
    with open(filename, 'r') as file:
        return json.load(file)


def run():
    load_dotenv()
    client = Spot(base_url="https://api4.binance.com", api_key=os.getenv('BINANCE_API_KEY'),
                  api_secret=os.getenv('BINANCE_API_SECRET'))

    portfolio_data = load_portfolio('./data/data.json')
    rebalancer = Rebalancer(client)
    rebalancer.create(portfolio_data)
    rebalancer.rebalance()


if __name__ == '__main__':
    run()
