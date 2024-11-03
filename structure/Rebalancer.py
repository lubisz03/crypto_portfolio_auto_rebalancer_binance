from .Token import Token
from typing import List
import schedule
import time
import json
import math


class Rebalancer:
    def __init__(self, binance_client, file_path: str, threshold: float = 0.1):
        self.__holdings: List[Token] = []
        self.__threshold = threshold
        self.__total_wallet_value: float = 0.0
        self.__client = binance_client

        if file_path:
            self.__create(file_path)
        else:
            raise ValueError('File path not provided')

    def __initiate_holdings(self, data: dict):
        total_allocation = 0.0
        for token in data:
            self.__holdings.append(Token(
                name=token.get('name'),
                symbol=token.get('symbol'),
                ticker=token.get('ticker'),
                target_allocation=token.get('target_allocation')
            ))
            total_allocation += token.get('target_allocation')

        if total_allocation != 1.0:
            raise ValueError('Total allocation must be 1.0 (100%)')

    def __update_current_allocation(self):
        for token in self.__holdings:
            token.set_current_allocation(self.__total_wallet_value)

    def __fetch_update_data(self):
        self.__total_wallet_value = 0.0
        for token in self.__holdings:
            token.fetch_data(self.__client)
            self.__total_wallet_value += token.value
        self.__update_current_allocation()

    def __rebalance(self):
        self.__fetch_update_data()

        positive_divergences = [
            token for token in self.__holdings if token.divergence > self.__threshold * token.target_allocation
        ]
        negative_divergences = [
            token for token in self.__holdings if token.divergence < -self.__threshold * token.target_allocation
        ]

        positive_divergences.sort(key=lambda x: x.divergence, reverse=True)
        negative_divergences.sort(key=lambda x: x.divergence)

        for pos_token in positive_divergences:
            remaining_sell = pos_token.divergence * self.total_wallet_value

            for neg_token in negative_divergences:
                if remaining_sell <= 0:
                    break

                neg_buy_amount = min(abs(neg_token.divergence)
                                     * self.total_wallet_value, remaining_sell)
                # TODO rethink - choose either upper or lower bound
                neg_buy_amount = round(neg_buy_amount, 2)

                try:
                    pos_token.sell(self.__client, neg_buy_amount)
                except Exception as e:
                    raise ValueError(f"Error selling {pos_token.ticker}: {e}")

                try:
                    neg_token.buy(self.__client, neg_buy_amount *
                                  math.floor((1 - pos_token.get_trade_fee(self.__client)) * 100 / 100))
                except Exception as e:
                    raise ValueError(f"Error buying {neg_token.ticker}: {e}")

                print(
                    f"Rebalanced {neg_token.ticker} by buying {neg_buy_amount}. Updated divergence.")
                self.__fetch_update_data()
                remaining_sell -= neg_buy_amount

            if remaining_sell > 0:
                print(
                    f"Unallocated USD for {pos_token.ticker}: {remaining_sell}")

    def __create(self, file_path: str):
        self.__initiate_holdings(self.__load_portfolio(file_path))
        self.__fetch_update_data()

    def __load_portfolio(self, file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return json.load(file)

    def run(self, interval_minutes: int = 30):

        def rebalance_job():
            print("Running scheduled rebalance...")
            self.__rebalance()

        schedule.every(interval_minutes).minutes.do(rebalance_job)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def __str__(self):
        return str(self.__holdings)
