import pytest
from .NN_dataset import DatasetTimeseries
from .MMM import MMM
from .Api import Api_model, TradingAgent

PATH_TEST_DATASET = r"./datasets_clear/launch_1/BTC_USDT-5m.csv"
timetravel = PATH_TEST_DATASET.split("-")[-1].replace(".csv", "")
timetravel = {"time": int(timetravel.replace("m", "").replace("H", "").replace("D", "")), 
              "type": timetravel.replace(timetravel.replace("m", "").replace("H", "").replace("D", ""), "")}

class TestMMM:
    dataset = DatasetTimeseries(PATH_TEST_DATASET, save=False)
    model = MMM(agents=5)

    def test_loader(self):
        dataset_clear = self.dataset.dataset_clear()
        loader = Api_model.get_loader(dataset_clear)
        assert len(list(loader)) == len(dataset_clear)

    def test_simulation(self):
        apM = Api_model(5, coins={"BTC": [self.dataset.dataset_clear(), timetravel["time"]]})
        simulation = apM.simulation_trade(1)
        

    def test_train(self):
        dataset_clear = self.dataset.dataset_clear()
        apM = Api_model(5)
        bath_size = 30
        split_train = 2
        loader_train = apM.train_agents(dataset_clear, bath_size=bath_size, split_train=split_train)
        for transaction in loader_train:
            for agent, data in transaction.items():
                type_trade, count, bath_test = data
                assert isinstance(agent, TradingAgent)
                assert len(bath_test) == bath_size//split_train
                assert "buy" in type_trade or "sell" in type_trade or "hold" in type_trade
                assert isinstance(count, int)