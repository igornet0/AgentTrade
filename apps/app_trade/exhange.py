from .Agent import TradingAgent
from ..data_processing.dataset import DatasetTimeseries


class Exhange:

    def __init__(self, coin_list=[]):
        self.coin_list: list = coin_list
        self.transactions: dict[float, list] = {}

    def add_coin(self, coin):
        self.coin_list.append(coin)

    def remove_coin(self, coin):
        self.coin_list.remove(coin)

    def create_transaction(self, coin, amount, price):
        self.transactions.setdefault(coin, [])
        self.transactions[coin].append((amount, price))

        return self.transactions[coin][-1]
    
    def simulate(self, agent: TradingAgent, timeseries: DatasetTimeseries):

         

        coin, amount, price = agent.trade()
