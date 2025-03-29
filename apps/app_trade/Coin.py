class Coin:

    def __init__(self, name: str, history, price_now):
        self.name = name
        self.history = history
        self.price_now = None
        self.set_price_now(price_now)

    def get_price_now(self):
        return self.price_now

    def set_price_now(self, price_now):
        self.price_now = price_now