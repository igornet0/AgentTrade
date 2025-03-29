from App_web import DatasetTimeseries, Api_model, Coin


PATH_TEST_DATASET = r"./datasets_clear/launch_1/BTC_USDT-5m.csv"
timetravel = PATH_TEST_DATASET.split("-")[-1].replace(".csv", "")
timetravel = {"time": int(timetravel.replace("m", "").replace("H", "").replace("D", "")), 
            "type": timetravel.replace(timetravel.replace("m", "").replace("H", "").replace("D", ""), "")}

if __name__ == "__main__":
    dataset = DatasetTimeseries(PATH_TEST_DATASET, save=False)
    # model = MMM(agents=5)

    apM = Api_model(10, coins={"BTC": [dataset.dataset_clear(), timetravel["time"]]})
    simulation = apM.simulation_trade(1)