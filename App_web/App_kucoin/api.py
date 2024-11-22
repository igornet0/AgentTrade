import pandas as pd
from datetime import datetime, timedelta
import time, threading
from kucoin.client import User, Trade, Market

from ..Log import Loger
from ..Parser import Device
from ..App_trade import Dataset
from ..Thread import Thread

timereavel_datetime = {"5m": timedelta(minutes=5),
                      "1H": timedelta(hours=1), 
                      "4H": timedelta(hours=4), 
                      "1D": timedelta(days=1)}


class KuCoinAPI:

    def __init__(self, api_key, api_secret, api_passphrase, logger: Loger=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.user = User(api_key, api_secret, api_passphrase)
        self.trade = Trade(api_key, api_secret, api_passphrase)
        self.market = Market(api_key, api_secret, api_passphrase)

        self.logger = logger if logger else Loger().off
        self.device = Device(logger=self.logger)

        keypress_thread = threading.Thread(target=self.device.kb.listen_for_keypress, daemon=True)
        keypress_thread.start()

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

        try:
            data = self.market.get_kline(f"{symbol}-USDT", time)
        except Exception as e:
            return None

        colums = ["datetime", "open", "high", "low", "close", "_", "volume"]

        df = pd.DataFrame(data, columns=colums).drop("_", axis=1)
        df["datetime"] = df["datetime"].apply(lambda x: datetime.fromtimestamp(int(x)))
        
        df["datetime"] = pd.to_datetime(df['datetime'])
        if "day" in time or "week" in time:
            df["datetime"] = df["datetime"].dt.strftime('%Y-%m-%d')

        return df
    
    def parser_coin(self, coin, t):
        
        df = self.get_kline(coin, time=t)
        if df is None:
            return False
        
        return Dataset(df, save=False)
    
    
    def process_buffer(self, buffer_thread):

        result = {}
        
        for timetravel, coins_thread in buffer_thread.items():

            for coin, thread in coins_thread.items():
                if isinstance(thread, datetime):
                    continue

                thread.join()
                # self.logger["INFO"](f"End parser {coin}")
                ds = thread.get_result()
                
                if not ds:
                    self.logger["ERROR"](f"Error coin {coin}")
                    ds = False

                buffer_thread[timetravel][coin] = ds
                
        return buffer_thread
    

    def parser_coins(self, coins_list: Dataset, timetravel_parser):
        coins = {}
        self.logger["INFO"]("Start parsing...")
        buffer_thread = {timetravel: {} for timetravel in timetravel_parser}
        bath_size = 100

        while True:	
            if self.device.kb.stop_loop:
                break

            coins_bath = [coins_list.get_dataset()[i:i + bath_size] for i in range(0, len(coins_list), bath_size)]
            for bath in coins_bath:
                for coin in bath["coins"].tolist():
                    self.logger["INFO"](f"Start parsing {coin}")
                    for timetravel in timetravel_parser:
                        if buffer_thread[timetravel].get(coin, False) and isinstance(buffer_thread[timetravel][coin], datetime):
                            if buffer_thread[timetravel][coin] >= datetime.now() - timereavel_datetime[timetravel]:
                                continue

                        buffer_thread[timetravel][coin] = Thread(self.parser_coin, coin, timetravel)
                        buffer_thread[timetravel][coin].start()

                buffer_thread = self.process_buffer(buffer_thread)

                for timetravel, coin_ds in buffer_thread.items():
                    for coin, ds in coin_ds.items():
                        if isinstance(ds, datetime) or not ds:
                            continue

                        if not coin in coins.keys():
                            coins.setdefault(coin, {timetravel: ds})
                        else:
                            if not timetravel in coins[coin].keys():
                                coins[coin].setdefault(timetravel, ds)
                            else:
                                coins[coin][timetravel].concat_dataset(ds)

                        if len(coins[coin][timetravel]) > 200:
                            self.logger["INFO"](f"Save dataset {datetime.now().strftime('%Y-%m-%d')} {coin} {timetravel}")
                            coins[coin][timetravel].save_dataset(f"{datetime.now().strftime('%Y-%m-%d')}_{coin}_{timetravel}.csv")

                        buffer_thread[timetravel][coin] = datetime.now()

            self.logger["INFO"](f"Parsing complete {datetime.now().strftime('%Y-%m-%d')} {len(coins)}")
            # if coins_trash:
            #     coin_list_new = coins_list.get_dataset().set_index("coins")
            #     coin_list_new = coin_list_new.drop(coins_trash, axis=0).reset_index()
            #     coins_list.set_dataset(coin_list_new)
            
            self.logger["INFO"](f"Wait 1 hour {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(60*60)
        
        coins_list.save_dataset("coins_ds.csv")