import pandas as pd

from apps.data_processing.dataset import Dataset, DatasetTimeseries, NewsDataset

def get_dataset_type(dataset: pd.DataFrame | str) -> type[Dataset]:
    if isinstance(dataset, str):
        dataset = pd.read_csv(dataset)
        
    if "max" in dataset.columns and "min" in dataset.columns and "volume" in dataset.columns:
        return DatasetTimeseries
    elif "news" in dataset.columns:
        return NewsDataset
    else:
        return Dataset