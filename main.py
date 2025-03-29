# from apps import (ParserApi, ParserNews, ParserKucoin, HandlerParser, 
#                   Dataset, HandlerDataset, DatasetTimeseries)
# from core.config import URL_SETTINGS, settings_trade, settings

# from core.utils.configure_logging import setup_logging
# import logging

# logger = logging.getLogger(__name__)

# # HandlerDataset(filename_dataset="BTC*.csv")
# def main():
#     # dataset:DatasetTimeseries = HandlerDataset.concat_dataset(Dataset.searh_path_dateset("BTC*.csv", root_dir=settings_trade.RAW_DATA_PATH),
#     #                                         backup=True)
#     dataset_path = Dataset.searh_path_dateset("clear_concat_BTC*.csv", root_dir=settings_trade.PROCESSED_DATA_PATH)
#     dataset: DatasetTimeseries = HandlerDataset.clear_dataset(dataset_path, backup=False)

#     logger.info(f"{len(dataset)} rows in dataset")
#     logger.info(f"{len(dataset.get_dataset_Nan())} Nan in dataset")
#     # print(type(dataset))

# # parser_new = ParserNews(setting=URL_SETTINGS)

# # data = parser_new.start_parser()
# # print(data)
# # def main():
# #     logger.info("Start parser")
# #     parser_kucoin = ParserKucoin(save=True)

# #     handler = HandlerParser(URL=settings_trade.URL_KUCOIN.replace("{coin}", "BTC"), 
# #                             parser=parser_kucoin)
# #     handler.start_parser(1_000_000, window_size=(780, 700))

# if __name__ == "__main__":
#     setup_logging()
#     main()

# from Apps import *
# from sys import argv


# def main(args):
#     if args[1] == "kucoin":
#         if args[2] == "start":
#             parser_kucoin()
    
#     elif args[1] == "market":
#         if args[2] == "start":
#             parser_marketcap()

#     elif args[1] == "start_nan":
#         handler_dataset_nan(args[2])

#     elif args[1] == "print_nan":
#         print_stat_nan(args[2])

#     elif args[1] == "web":
#         pass


# if __name__ == "__main__":
#     main(argv)

# from app_fastapi import create_app
# from core.utils.configure_logging import setup_logging, format_message
# from core.config import settings
# import logging

# if __name__ == "__main__":
#     import uvicorn

#     setup_logging()

#     logger = logging.getLogger(__name__)
#     logger.info("Start server")

#     uvicorn.run(
#         "app_fastapi:create_app",
#         host=settings.APP_HOST,
#         port=settings.APP_PORT,
#         reload=settings.DEBUG,  # Автоматически включаем reload в DEBUG режиме
#         factory=True,
#         # log_config=None,  # Отключаем стандартное логирование Uvicorn
#         # access_log=False  # Мы сами обрабатываем access-логи
#     )