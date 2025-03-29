from sys import argv, exit

from apps import HandlerParser, ParserKucoin
from core.config import settings_trade
from core.utils.configure_logging import setup_logging

import logging

logger = logging.getLogger(__name__)

def parser_missing_date(coin: str):
    logger.info("Start parser")
    parser_kucoin = ParserKucoin(save=True)

    handler = HandlerParser(URL=settings_trade.URL_KUCOIN.replace("{coin}", coin), 
                            parser=parser_kucoin)
    
    handler.run_parser(window_size=(780, 700))

if __name__ == "__main__":
    if len(argv) < 2:
        logger.error("Missing coin name")
        exit()

    setup_logging()
    parser_missing_date(argv[1])