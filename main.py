import os
from sys import argv

# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

from App_trade import *
# from App_kucoin import *
from Parser import *
from config import *
from concat_datasets import concat_datasets_files
from Statistics.Stat import print_nan

def get_data(data_folder: str):
    data = concat_datasets_files(data_folder)
    for key, dataset in data.items():
        print(f"[INFO] {key} {len(dataset)=}")

    return data

def start_parser(URL: str, dataset: Dataset = None, counter=10**6, save=False, tick=0):

    xpath_default = ["frame", "filename", "timetravel"]
    client_parser = Web_api(save=False,
                            tick=tick, xpath_default=xpath_default)
    
    client_parser.set_save_trach("images_trach")
    
    client_parser.start_web(URL, entry=False)

    last_datetime = dataset.get_datetime_last() if dataset is not None else None

    last_datetime, dataset_parser = client_parser.start_parser(datetime_last=last_datetime, counter=counter)

    if last_datetime is None:
        return

    file_name = client_parser.get_filename()

    dataset_parser = Dataset(dataset_parser, save=save, file_name=file_name)
    if dataset is not None:
        dataset_parser.concat_dataset(dataset)

    dataset_parser.process()

    return dataset_parser

def start_parser_dataset_nan(URL: str, dataset: Dataset, save=False, tick=0, client_parser=None):
    if client_parser is None:
        xpath_default = ["frame"]
        client_parser = Web_api(save=False,
                                tick=tick, xpath_default=xpath_default)
        
        client_parser.set_save_trach("images_trach")
    
    client_parser.set_filename(dataset.get_filename())

    client_parser.start_web(URL, entry=False)

    last_datetime, dataset_parser = client_parser.parser_for_df(dataset.get_dataset_Nan())

    if last_datetime is None:
        return

    file_name = client_parser.get_filename()

    dataset_parser = Dataset(dataset_parser, save=False, file_name=file_name)
    dataset.concat_dataset(dataset_parser)

    if save:
        dataset.save_dataset()

    return dataset

def handler_dataset_nan(data_path: str):

    tick = 0.1
    xpath_default = ["frame"]
    client_parser = Web_api(save=False,
                            tick=tick, xpath_default=xpath_default)
    
    client_parser.set_save_trach("images_trach")
    
    data = get_data(data_path)

    for key, dataset in data.items():
        coin = key.split("_")[0]
        URL = f"https://www.kucoin.com/ru/trade/{coin}-USDT"

        dataset = start_parser_dataset_nan(URL, dataset, save=True, client_parser=client_parser, tick=tick) 
        data[key] = dataset
        
def parser_kucoin():
    # data_path = "datasets_clear"
    # data = get_data(data_path)

    coin = input("Coin: ")
    dataset = None

    # if coin in data.keys():
    #     dataset: Dataset = data.get(f"{coin}_USDT-5m.csv")

    URL = f"https://www.kucoin.com/ru/trade/{coin}-USDT"
    
    counter = 100
    start_parser(URL, dataset, save=True, counter=counter)

def print_stat_nan(data_path: str):
    data = get_data(data_path)
    print_nan(list(data.values()))

def main(args):
    if args[1] == "kucoin":
        if args[2] == "start":
            parser_kucoin()

    elif args[1] == "start_nan":
        handler_dataset_nan(args[2])

    elif args[1] == "print_nan":
        print_stat_nan(args[2])

if __name__ == "__main__":
    main(argv)