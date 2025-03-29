from .App_trade import *
from .Parser import *
from .App_kucoin import KuCoinAPI

from datetime import datetime


timeserials_amount = {
    "5m":72,
    "1H":24,
    "4H":42,
    "1D":30
}


class Handler:

    def __init__(self, URL: str, api_model: Api_model) -> None:

        self.URL = URL
        self.api_model = api_model
    
    def start_train(self, time_start: datetime) -> None:
        
        self.parser = Parser_kucoin(save=False)

        self.parser.start_web(self.URL, entry=False)
        for time in timeserials_amount.keys():
            df = self.parser.start_parser(time_start, timeserials_amount[time], time)
