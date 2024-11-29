import numpy as np
import os 

from .NN_model import ModelTrade

class TradingAgent:

    def __init__(self, path_agent, balance: float = 1000.0) -> None:
        self.path_agent = path_agent
        self.balance = float(balance)
        self.transactions = []
        
        self.model = ModelTrade()

    def trade(self, state: np.array) -> tuple[float, float, float]:
        action = self.model.predict(state)
        return action
    
    def save(self, name_model: str = None):
        self.model.save(os.path.join(self.path_agent, name_model))