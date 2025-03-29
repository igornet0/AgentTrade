from App_web import *
from Statistics import Stat
from config import *
from concat_datasets import concat_datasets_files

from sys import argv

def get_data(data_folder: str):
	data = concat_datasets_files(data_folder)
	for key, dataset in data.items():
		print(f"[INFO] {key} {len(dataset)=}")

	return data

def start_parser(URL: str, dataset = None, counter=10**6, save=False, tick=0):

	xpath_default = ["frame", "filename", "timetravel"]
	client_parser = Parser_api(save=False,
							tick=tick, xpath_default=xpath_default)
	
	client_parser.set_save_trach("images_trach")
	
	client_parser.start_web(URL)

	last_datetime = dataset.get_datetime_last() if dataset is not None else None

	last_datetime, dataset_parser = client_parser.start_parser(datetime_last=last_datetime, counter=counter)

	if last_datetime is None:
		return

	file_name = client_parser.get_filename()

	dataset_parser = DatasetTimeseries(dataset_parser, save=save, file_name=file_name)
	if dataset is not None:
		dataset_parser.concat_dataset(dataset)

	dataset_parser.process()

	return dataset_parser

def start_parser_dataset_nan(URL: str, dataset, save=False, tick=0, client_parser=None):
	if client_parser is None:
		xpath_default = ["frame"]
		client_parser = Parser_api(save=False,
								tick=tick, xpath_default=xpath_default)
		
		client_parser.set_save_trach("images_trach")
	
	client_parser.set_filename(dataset.get_filename())

	client_parser.start_web(URL)

	last_datetime, dataset_parser = client_parser.parser_for_df(dataset.get_dataset_Nan())

	if last_datetime is None:
		return

	file_name = client_parser.get_filename()

	dataset_parser = DatasetTimeseries(dataset_parser, save=False, file_name=file_name)
	dataset.concat_dataset(dataset_parser)

	if save:
		dataset.save_dataset()

	return dataset

def handler_dataset_nan(data_path: str):

	tick = 0.1
	xpath_default = ["frame"]
	client_parser = Parser_api(save=False,
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

	# if coin in data.keys():
	#	 dataset: Dataset = data.get(f"{coin}_USDT-5m.csv")

	URL = f"https://www.kucoin.com/ru/trade/{coin}-USDT"
	
	counter = 100
	# parser = Parser_kucoin(save=False, path_save="datasets_parser")
	# parser.start_web(URL)
	# parser.start_parser(counter=counter)
	kuc = KuCoinAPI(api_key, api_secret, api_passphrase)
	time = ["5m", "1H", "4H", "1D"]
	for t in time:
		df = kuc.get_kline(coin, time=t)
		df.to_csv(f"datasets_parser/{coin}_{t}.csv", index=False)
		print(df.head(5))
		

def print_stat_nan(data_path: str):
	data = get_data(data_path)
	Stat.print_nan(list(data.values()))


def parser_marketcap():
	URL = "https://coinmarketcap.com"

	parser = Parser_marketcap(save=True)
	parser.set_filename("coins.csv")
	parser.start_web(URL)

	parser.start_parser()


def parser_news():
	
	domains = Dataset("datasets_news/domains.csv", save=False)
	URLS = domains.get_dataset()["domain"].tolist()

	parser = Parser_news(URLS, save=False)
	# parser.set_filename("news.csv")
	# parser.start_web(URL show_browser=False)
	d = parser.start_parser()
	print(d)
 
def main(args):
	
	if args[1] == "kucoin":
		if args[2] == "start":
			parser_kucoin()
	
	if args[1] == "market":
		if args[2] == "start":
			parser_marketcap()

	if args[1] == "news":
		if args[2] == "start":
			parser_news()

	if args[1] == "start_nan":
		handler_dataset_nan(args[2])

	if args[1] == "print_nan":
		print_stat_nan(args[2])

	# if args[1] == "rec":
	# 	parser_rec_xpath(args[2])


if __name__ == "__main__":
	main(argv)