import pandas as pd
from urllib.parse import urlencode
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
        //Transaction amount "0.000945" //Transaction volume
        """
        data = self.market.get_kline(symbol, time)

        colums = ["date", "open", "high", "low", "close", "_", "volume"]

        return pd.DataFrame(data, columns=colums)