from structure import Rebalancer
from client import initialize_client


def run():
    client = initialize_client()
    rebalancer = Rebalancer(client, './data/data.json')
    rebalancer.run()


if __name__ == '__main__':
    run()
