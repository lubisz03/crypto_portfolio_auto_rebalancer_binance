class Token:
    def __init__(self, name: str, symbol: str, ticker: str, target_allocation: float):
        self.__name = name
        self.__symbol = symbol
        self.__ticker = ticker
        self.__target_allocation = target_allocation
        self.__price: float = 0.0
        self.__quantity: float = 0.0
        self.__value: float = 0.0
        self.__current_allocation: float = 0.0
        self.__divergence: float = 0.0

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def target_allocation(self) -> float:
        return self.__target_allocation

    @property
    def value(self) -> float:
        return self.__value

    @property
    def divergence(self) -> float:
        return self.__divergence

    def set_current_allocation(self, total_wallet_value: float):
        if total_wallet_value > 0:
            self.__current_allocation = self.__value / total_wallet_value
            self.__divergence = self.__current_allocation - self.__target_allocation

    def __update_value(self):
        self.__value = self.__price * self.__quantity

    def __update_quantity(self, binance_client):
        self.__quantity = float(binance_client.user_asset(
            needBtcValuation=True, asset=self.__symbol)[0].get('free', 0.0))

    def __update_price(self, binance_client):
        self.__price = float(binance_client.ticker_price(
            symbol=self.__ticker).get('price', 0.0))

    def fetch_data(self, binance_client):
        self.__update_price(binance_client)
        self.__update_quantity(binance_client)
        self.__update_value()

    def get_trade_fee(self, binance_client):
        return binance_client.trade_fee(symbol=self.__ticker).get('taker', 0.001)

    def buy(self, binance_client, amount: float):
        try:
            binance_client.new_order_test(
                symbol=self.__ticker, type="MARKET", side="BUY", quoteOrderQty=amount)
        except Exception as e:
            raise ValueError(f'Error buying {self.__ticker}: {e}')

    def sell(self, binance_client, amount: float):
        try:
            binance_client.new_order_test(
                symbol=self.__ticker, type="MARKET", side="SELL", quoteOrderQty=amount)
        except Exception as e:
            raise ValueError(f'Error selling {self.__ticker}: {e}')

    def __str__(self):
        return f'Token({self.__name} - {self.__ticker} - {self.__target_allocation})'
