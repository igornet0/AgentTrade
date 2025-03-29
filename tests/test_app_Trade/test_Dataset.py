import pytest
# from .NN_dataset import DatasetTimeseries
from apps.app_trade import DatasetTimeseries
# from .Api import Api_model
from datetime import timedelta
import pandas as pd

# PATH_TEST_DATASET = r"./datasets_clear/launch_1/BTC_USDT-5m.csv"
# timetravel = PATH_TEST_DATASET.split("-")[-1].replace(".csv", "")
# timetravel = {"time": int(timetravel.replace("m", "").replace("H", "").replace("D", "")), 
#               "type": timetravel.replace(timetravel.replace("m", "").replace("H", "").replace("D", ""), "")}

from tests.test_settings import SettingsTest

settings = SettingsTest()

class TestDatasetTimeseries:
    dataset = DatasetTimeseries(settings.PATH_TEST_DATASET, save=False)

    def test_len(self):
        assert len(self.dataset) == len(self.dataset) 

    def test_process(self):

        dataset = DatasetTimeseries(settings.PATH_TEST_DATASET, save=False)
        self.dataset.process()

        for _, data in self.dataset.get_dataset_Nan().iterrows():
            assert not data["datetime"] in dataset["datetime"]

        for _, data in dataset.get_dataset().iterrows():
            assert not data["datetime"] in self.dataset["datetime"]
        delta = self.dataset["datetime"].diff().dt.total_seconds().mean()
        assert abs(delta // 60) == DatasetTimeseries.get_timetravel(settings.PATH_TEST_DATASET)["time"]

    # def test_save(self):
    #     dataset = DatasetTimeseries(PATH_TEST_DATASET, save=True, path_save="/".join(PATH_TEST_DATASET.split("/")[:-1]),
    #                                 file_name=PATH_TEST_DATASET.split("/")[-1])
        
    #     dataset_last = dataset.process()

    #     dataset = DatasetTimeseries(PATH_TEST_DATASET, save=True, path_save="/".join(PATH_TEST_DATASET.split("/")[:-1]),
    #                                 file_name=PATH_TEST_DATASET.split("/")[-1])
        
    #     assert len(dataset_last) == len(dataset) and (dataset_last["datetime"] == dataset["datetime"]).all()

    def test_concat_dataset(self):
        datasets_paths = DatasetTimeseries.concat_from_path("./datasets_clear")
        assert isinstance(datasets_paths, dict)
        max_perid = {}
        for name, dataset in datasets_paths.items():
            dt = DatasetTimeseries(dataset, save=False)
            count_not_Nan = 0
            for data in dt:
                if data["open"] == "x":
                    if max_perid.get(name, 0) < count_not_Nan:
                        max_perid[name] = count_not_Nan
                    count_not_Nan = 0
                else:
                    count_not_Nan += 1

        # print(f"{max_perid=}")

    # def test_plot_bath(self):
    #     dataset_clear = self.dataset.dataset_clear()
    #     loader = Api_model.get_loader(dataset_clear, period=timetravel["time"])
    #     for history in loader:
    #         self.dataset.plot_series(history)
        
    def test_data(self):
        
        buffer_data = []
        
        self.dataset.process()

        assert len(self.dataset) == len(self.dataset)

        for data in self.dataset.sort():
            if len(buffer_data) == 0:
                buffer_data.append(data.get("datetime"))
            else:
                assert data.get("datetime") - buffer_data[-1] == timedelta(minutes=DatasetTimeseries.get_timetravel(settings.PATH_TEST_DATASET)["time"])
                buffer_data = [data.get("datetime")]

            assert not data.get("datetime") is None
            assert not data.get("open") is None
            assert not data.get("max") is None
            assert not data.get("min") is None
            assert not data.get("close") is None
            assert not data.get("volume") is None

# TestDatasetTimeseries().test_process()