from tkinter import N
import numpy as np
from random import randint
from .NN_model import ModelTrade
from .Order import Coin, Order
from .Strategy import BaseStrategy, NewsTradingStrategy

class TradingAgent:

    def __init__(self, _id: int, name: str ,strategy: BaseStrategy, 
                 balance: float = 1000.0, count_min=1, count_max=20, bath_len: int = 30) -> None:
        
        self.id = _id
        self.name = name
        self.strategy = strategy
        self.balance = float(balance)
        self.transactions = []

        self.count_min = count_min
        self.count_max = count_max

        self.coins = {}
        self.state = []
        self.orders = {}
        self.profit: dict[Coin, float] = {}

        self.bath_len = bath_len
        
        # self.model = ModelTrade()

    def remove_balance(self, value):
        self.balance -= value

    def add_balance(self, value):
        self.balance += value

    def get_count(self) -> int:
        return randint(self.count_min, self.count_max)
    
    def close_short(self, coin: Coin, price, count=1):
        self.add_balance(price * count)
        self.add_coins(coin, price, count)

    def close_long(self, coin: Coin, price, count=1):
        self.add_balance(price * count)
        self.add_coins(coin, price, -count)

    def get_profit_coins(self, all: bool | None = None) -> dict[Coin, float] | float:
        profit = 0

        if all:
            return self.profit
        
        for coin, profit_coin in self.profit:
            profit += profit_coin

        return profit
    
    def close_position(self, coin: Coin, trade_type, price, count=1):
        if self.coins.get(coin, 0) == 0:
            return None, "Position not found"
        
        last_count = min(abs(self.coins[coin][0]), count)
        
        if self.coins[coin][0] < 0 and trade_type == "buy":
            self.close_short(coin, price, last_count)
        elif self.coins[coin][0] > 0 and trade_type == "sell":
            self.close_long(coin, price, last_count)
        else:
            return True, count
            
        return True, count - last_count
    
    def open_order(self, type_order, coin: Coin, price: float, count=1):
        orders_agent = self.orders.get(coin)
        if not orders_agent is None:
            for order in orders_agent:
                if order.get_type() == type_order and order.get_price() == price:
                    order.add_count(count)
                    return order
        
        order = Order(coin, type_order, price, count)
        self.orders.setdefault(coin, [])
        self.orders[coin].append(order)

        return order
    
    def execute_order(self, order: Order):
        result = self.close_position(order.coin, order.get_type(), 
                                     order.get_price(), order.get_count())

        if not result[0] is None or result[1] == 0:
            return result

        elif result[0]:
            quantity = result[1]
        else:
            quantity = int(order.get_count())

        quantity = quantity if "buy" in order.get_type()else -quantity

        self.add_coins(order.coin, order.get_price(), quantity)

        return True
    
    def add_coins(self, coin: Coin, price: float, count: int):
        if count == 0:
            return
        
        assert not isinstance(price, float)
        assert not isinstance(count, int)
        
        self.coins.setdefault(coin, [0, 0])

        self.coins[coin][1] = self.coins[coin][0] * self.coins[coin][1] + price * count
        self.coins[coin][0] += count

        if self.coins[coin][0] == 0:
            self.profit.setdefault(coin, 0)
            self.profit[coin] -= self.coins[coin][1]
            del self.coins[coin]

    @staticmethod
    def update_state(func):

        def wrapper(self, *args, **kwargs):
            order_type, count = func(self, *args, **kwargs)
            self.state.append({"order_type": order_type, "bath_len": self.bath_len})
            return order_type, count 
        
        return wrapper

    @update_state
    def trade(self, data: list) -> str:
        open_prices = []
        close_prices = []
        max_prices = []
        min_prices =[]
        volume_prices = []
        for row in data[:self.bath_len]:
            open_prices.append(float(row["open"]))
            close_prices.append(float(row["close"]))
            max_prices.append(float(row["max"]))
            min_prices.append(float(row["min"]))
            volume_prices.append(float(row["volume"]))

        now_price = float(data[-1]["close"])

        if isinstance(self.strategy, NewsTradingStrategy):
            news_sentiment = 0.2
            return self.strategy(open_prices, close_prices, 
                             min_prices, max_prices, volume_prices, now_price, news_sentiment).signal(), self.get_count()
        
        return self.strategy(open_prices, close_prices, 
                             min_prices, max_prices, volume_prices, now_price).signal(), self.get_count()
        # action = self.model.predict(state)
        return action
    
    def save(self, name_model: str = None):
        self.model.save(name_model)