from ..data_processing.dataset import DatasetTimeseries, NewsDataset

class Handler:

    def __init__(self, dataset: DatasetTimeseries, news: NewsDataset) -> None:
        self.dataset = dataset
        self.news = news
    
    def __iter__(self):

        for news in self.news:
            date = news["date"]
            