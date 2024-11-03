from dotenv import load_dotenv
import os
from binance.spot import Spot


def initialize_client():
    load_dotenv()

    try:
        return Spot(base_url="https://api4.binance.com", api_key=os.getenv('BINANCE_API_KEY'),
                    api_secret=os.getenv('BINANCE_API_SECRET'))
    except Exception as e:
        raise ValueError(f'Error initializing client: {e}')
