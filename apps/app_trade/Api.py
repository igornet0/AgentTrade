from tkinter import N
from turtle import st
from typing import Union
from os import path, listdir
import random
import pandas as pd
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor

from .exhange import Exhange
from ..data_processing.clear_datasets import convert_timetravel, timedelta
from . import TradingAgent, Dataset, Order, Coin

from .Strategy import *

#(prices, open_prices, close_prices, lows, highs, volumes, current_price)
#(prices, open_prices, close_prices, lows, highs, volumes, current_price, news_sentiment=0.7)
strategies = {
        "DayTrading": DayTradingStrategy,
        "Scalping": ScalpingStrategy,
        "SwingTrading": SwingTradingStrategy,
        "PositionTrading": PositionTradingStrategy,
        "Arbitrage": ArbitrageStrategy,
        "TrendFollowing": TrendFollowingStrategy,
        "CounterTrend": CounterTrendStrategy,
        "GridTrading": GridTradingStrategy,
        "DCA": DCAStrategy,
        "NewsTrading": NewsTradingStrategy,
        "AlgoBot": AlgoBotTradingStrategy,
        "HFT": HighFrequencyTradingStrategy,
        "CapitalManagement": CapitalManagementStrategy
    }

class Api_model:

    def __init__(self, agents_count: int = 100, coins: dict = {}):
        self.coins = coins
        self.manager = mp.Manager()
        self.agents = self.manager.list()

        self.creat_agent(agents_count)
        # self.orders: dict[Coin:dict[TradingAgent: list[Order]]] = {}
        self.transactions = {}

    def add_coin(self, name, dataset, timetravel):
        self.coins.setdefault(name, [dataset, timetravel])

    def creat_agent(self, agents_count: int = 1):
        for i in range(agents_count):
            strategy = list(strategies.keys())[random.randint(0, len(strategies.keys())-1)]
            strategy = strategies[strategy]
            balance = random.randint(1000, 1_000_000)
            agent = TradingAgent(i, f"Agent_{i}", strategy, balance)
            self.agents.append(agent)
    
    def update_bath_len(self, bath_len_min: int = 30, bath_len_max: int = 100):
        for agent in self.agents:
            agent.bath_len = random.randint(bath_len_min, bath_len_max)

    @classmethod
    def get_loader(cls, dataset: pd.DataFrame | Dataset, bath_size: int | None = None, period: int | None = None):
        if isinstance(dataset, pd.DataFrame):
            dataset = Dataset(dataset, save=False)
    
        bath = []
        for data in dataset:
            if not bath_size is None and period is None:
                bath.append(data)
                if len(bath) == bath_size:
                    yield bath
                    bath = []
                continue
            elif not period is None and bath:
                delta = bath[-1]["datetime"] - data["datetime"]

                if delta == timedelta(minutes=period):
                    if not bath_size is None:
                        if len(bath) == bath_size:
                            yield bath
                            bath = []
                else:
                    if not bath_size is None:
                        if len(bath) == bath_size:
                            yield bath
                    else:
                        yield bath
                
                    bath = []

                bath.append(data)
                continue

            elif not period is None and not bath:
                bath.append(data)
                continue
            
            yield data

        if bath:
            if not bath_size is None:
                if len(bath) == bath_size:
                    yield bath
            else:
                yield bath

    def get_loader_coins(self, epoth: int = 1, bath_limit: int | None = None, bath_size: int | None = None):
        for _ in range(epoth):
            for coin, data in self.coins.items():
                dataset, timetravel = data
                timetravel = convert_timetravel(timetravel)
                for bath_period in self.get_loader(dataset, period=timetravel, 
                                                bath_size=bath_size):
                    if not bath_limit is None:
                        bath_limit -= 1
                        if bath_limit == 0:
                            return coin, bath_period
                        
                    yield coin, bath_period

    @classmethod
    def execute_order(cls, agent: TradingAgent, order: Order):
        return agent.execute_order(order)

    # @classmethod
    # def open_order(cls, orders: dict, agent: TradingAgent, coin: Coin, price: float, type_order: str = "buy", count: int = 1):
    #     orders.setdefault(coin, {})
    #     orders_agent = orders[coin].get(agent)
    #     if not orders_agent is None:
    #         for order in orders_agent:
    #             if order.get_type() == type_order and order.get_price() == price:
    #                 order.add_count(count)
    #                 return order
        
    #     order = Order(coin, type_order, price, count)
    #     orders[coin].setdefault(agent, [])
    #     orders[coin][agent].append(order)

    #     return orders, order

    def trade_agent(self, bath: list, agent: TradingAgent | None = None, 
                    bath_size: int = 30, split_train: int = 2):
        
        if agent is None:
            transaction_target = {}
            if not split_train is None:
                bath_train = bath[:bath_size//split_train]
                bath_test = bath[bath_size//split_train:]
            else:
                bath_train = bath[:]
                bath_test = None

            for agent in self.agents:
                type_trade, count = agent.trade(bath_train)
                transaction_target[agent] = (type_trade, count, bath_test)

            return transaction_target
        else:
            return agent.trade(bath)

    def train_agents(self, dataset, timetravel="5m", bath_size: int = 30, split_train: int = 2):
        timetravel = convert_timetravel(timetravel)

        for bath_period in self.get_loader(dataset, period=timetravel, bath_size=bath_size):
            if len(bath_period) >= bath_size:
                yield self.trade_agent(bath_period, 
                                       bath_size=bath_size, split_train=split_train)
            else:
                assert len(bath_period) < bath_size

    @classmethod
    def print_state(cls, states: dict):
        state_avg = {}
        for agent_id, states in states.items():
            print(f"Agent_{agent_id}, {states}")
            for state in states:
                type_order, count = state["order_type"], state["bath_len"]
                state_avg.setdefault(agent_id, {})
                state_avg[agent_id].setdefault(type_order, [0, 0])
                state_avg[agent_id][type_order][0] += count
                state_avg[agent_id][type_order][1] += 1
        
        for agent_id, data in state_avg.items():
            for type_order, data in data.items():
                len_bath, count = data
                print(f"Agent_{agent_id} {type_order}: {len_bath/count}")

    @classmethod
    def open_order_agent(cls, args):
        agent = args["agent"]
        coin = args["coin"]
        bath_period = args["bath_period"]

        # for i in range(5, len(bath_period)+1):
        type_order, count = agent.trade(bath_period)

        # if not "hold" in type_order:
        if not "hold" in type_order:
            price = bath_period[-1]["close"]
            order = agent.open_order(type_order, coin, price, count)
        else:
            order = None
        # agent.execute_order(order)
        return agent.id, order, agent.state

    def simulation_trade(self, epoth=5, randon_bath_len: tuple = (30, 100)):
        state = {}
        for coin, bath_period in self.get_loader_coins(epoth=epoth, bath_limit=10):
            if 100 < len(bath_period) > 1000:
                continue
            # processes = []
            # num_processes = 5 
            task_list = []
            self.agents = sorted(self.agents, key= lambda x: x.bath_len, reverse=True)

            for agent in self.agents:
                task_list.append({"agent": agent, "coin": coin, "bath_period": bath_period})
                if randon_bath_len:
                    self.update_bath_len(*randon_bath_len)
                    
            with mp.Pool(processes=mp.cpu_count()) as pool:
              agent_order = {agent_id: data_order for agent_id, *data_order in list(pool.map(self.open_order_agent, task_list))}
            
            for agent in self.agents:
                if agent.id in agent_order:
                    order, order_data = agent_order[agent.id]
                    if order is not None:
                        # print(f"{agent.name} {order=}")
                        self.execute_order(agent, order)
                    
                    state.setdefault(agent.id, [])
                    state[agent.id].extend(order_data)

                    # agent.execute_order(agent_order[agent.id][1])
            # self.print_state(state)
            # print(state)
            print("Sum_state=", {f"Agent_{agent.id}": len(state[agent.id]) for agent in self.agents})
            # # print()
            # for agent in self.agents:
            #     if agent.state:
            #         print(f"{agent.name}", end=":\n")
            #         self.print_state(agent.state)
            # for agent in self.agents:
            #     print(f"{agent.name} {agent.profit=}")
            # print(f"{len(bath_period)=}")
            # print(f"{len(self.orders)=}")

        self.print_state(state)

        for agent in self.agents:
            for coin, data in agent.coins.items():
                count, _ = data
                print(f"{agent.name} {count=}")
                dataset, _ = self.coins[coin]
                price = dataset["close"].iloc[-1]

                agent.add_coins(coin, price, -count)

        print("-"*40)

        self.agents = sorted(self.agents, key= lambda x: x.get_profit_coins(), reverse=True)

        for agent in self.agents:
            print(f"{agent.name} {agent.bath_len=} {agent.profit=}")
