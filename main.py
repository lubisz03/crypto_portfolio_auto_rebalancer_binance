from structure import Rebalancer
from client import initialize_client


def run():
    client = initialize_client()
    rebalancer = Rebalancer(client, './data/data.json')
    rebalancer.run()


if __name__ == '__main__':
    run()


# TODO 1: Develop custom exceptions
# TODO 2: Develop tests
# TODO 3: Develop logging
# TODO 4: Develop a robust error handling
