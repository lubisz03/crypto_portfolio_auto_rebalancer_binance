from .Token import Token
from typing import List


class Rebalancer:
    def __init__(self, binance_client, threshold: float = 0.1):
        self.__holdings: List[Token] = []
        self.__threshold = threshold
        self.__total_wallet_value: float = 0.0
        self.__client = binance_client

    @property
    def holdings(self) -> List[Token]:
        return self.__holdings

    @property
    def threshold(self) -> float:
        return self.__threshold

    @property
    def total_wallet_value(self) -> float:
        return self.__total_wallet_value

    def __initiate_holdings(self, data: dict):
        total_allocation = 0.0
        for token in data:
            self.holdings.append(Token(
                name=token.get('name'),
                symbol=token.get('symbol'),
                ticker=token.get('ticker'),
                target_allocation=token.get('target_allocation')
            ))
            total_allocation += token.get('target_allocation')

        if total_allocation != 1.0:
            raise ValueError('Total allocation must be 1.0 (100%)')

    def __update_current_allocation(self):
        for token in self.holdings:
            token.set_current_allocation(self.total_wallet_value)

    def __fetch_update_data(self):
        self.__total_wallet_value = 0.0
        for token in self.holdings:
            token.fetch_data(self.__client)
            self.__total_wallet_value += token.value
        self.__update_current_allocation()

    def rebalance(self):

        positive_divergences = [
            token for token in self.holdings if token.divergence > self.threshold * token.target_allocation
        ]
        negative_divergences = [
            token for token in self.holdings if token.divergence < -self.threshold * token.target_allocation
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
                    neg_token.buy(self.__client, neg_buy_amount)
                except Exception as e:
                    raise ValueError(f"Error buying {neg_token.ticker}: {e}")

                print(
                    f"Rebalanced {neg_token.ticker} by buying {neg_buy_amount}. Updated divergence.")
                self.__fetch_update_data()
                remaining_sell -= neg_buy_amount

            if remaining_sell > 0:
                print(
                    f"Unallocated USD for {pos_token.ticker}: {remaining_sell}")

        # Final check for any remaining USD if full rebalancing isn't possible
        # remaining_usd = sum(
        #     token.divergence * self.total_wallet_value for token in positive_divergences if token.divergence > 0
        # )
        # if remaining_usd > 0:
        #     print("Warning: Unallocated USD remains. Adjust allocations or threshold.")

    def create(self, data: dict):
        self.__initiate_holdings(data)
        self.__fetch_update_data()

    def __str__(self):
        return str(self.holdings)
