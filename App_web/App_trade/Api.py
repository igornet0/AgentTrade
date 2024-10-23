from typing import Union
from os import path, listdir

from .exhange import Exhange
from . import TradingAgent

class Api_model:

    def __init__(self, agents: Union[list[TradingAgent], str]) -> None:
        if isinstance(agents, str):
            if path.exists(agents):
                self.path = agents
                agents = [self.inint_agent(path.join(agents, f)) for f in listdir(agents)]
            else:
                raise ValueError("File not found")
            
        elif not isinstance(agents[0], TradingAgent):
            raise ValueError("Agents must be list of TradingAgent")
        else:
            self.path = "Agents"    

        self.agents = agents
        self.exhange = Exhange()

    def inint_agent(self, path_agent: str) -> TradingAgent:
        return TradingAgent(path_agent) 
    
    def get_agents(self) -> list[TradingAgent]:
        return self.agents