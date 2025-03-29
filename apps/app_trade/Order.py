from .Coin import Coin
from .Exceptions import OrderFulfilled

class Order:

    def __init__(self, coin: Coin, type: str, price: float, count: int):
        self.coin = coin
        self.price_order = price
        self.count_fulfilled = 0
        self.count = count
        self.type = None
        self.set_type(type)

    def get_type(self) -> str:
        return self.type

    def get_count(self):
        return self.count

    def add_count(self, amount: int):
        self.count += amount

    def is_fulfilled(self):
        return self.count_fulfilled == self.count

    def fulfilled(self, count):
        if self.is_fulfilled:
            raise OrderFulfilled()
        
        self.count_fulfilled += count

    def get_price(self):
        return self.price_order
    
    def get_amount(self):
        return self.get_count() * self.get_price()

    def set_type(self, new_type: str):
        if new_type in ["buy", "sell"]:
            self.type = new_type
        else:
            raise ValueError(f"Type not 'buy' or 'sell'")