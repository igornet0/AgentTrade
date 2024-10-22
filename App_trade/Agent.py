import numpy as np
from .NN_model import ModelTrade

class TradingAgent:

    def __init__(self, balance: float = 1000.0) -> None:
        self.balance = balance
        self.transactions = []
        self.model = ModelTrade()

    def trade(self, state: np.array) -> tuple[float, float, float]:
        action = self.model.predict(state)
        return action