import pandas as pd
from datetime import datetime
from kucoin.client import User, Trade, Market

class KuCoinAPI:

    def __init__(self, api_key, api_secret, api_passphrase):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.user = User(api_key, api_secret, api_passphrase)
        self.trade = Trade(api_key, api_secret, api_passphrase)
        self.market = Market(api_key, api_secret, api_passphrase)

    def get_account_summary_info(self):
        return self.user.get_account_summary_info()
    
    def get_kline(self, symbol, time: str = "5m"):
        """
        "1545904980", //Start time of the candle cycle "0.058", 
        //opening price "0.049", //closing price "0.058", //highest price "0.049", //lowest price "0.018", 
        //Transaction amount "0.000945" //Transaction volume 143676
        """

        if time[-1] == "m":
            time = time.replace("m", "min")
        elif time[-1] == "H":
            time = time.replace("H", "hour")
        elif time[-1] == "D":
            time = time.replace("D", "day")
        elif time[-1] == "W":
            time = time.replace("W", "week")

        data = self.market.get_kline(f"{symbol}-USDT", time)

        colums = ["datetime", "open", "high", "low", "close", "_", "volume"]

        df = pd.DataFrame(data, columns=colums).drop("_", axis=1)
        df["datetime"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(int(x)))
        
        df["datetime"] = pd.to_datetime(df['date'])
        if "day" in time or "week" in time:
            df["datetime"] = df["datetime"].dt.strftime('%Y-%m-%d')

        return df