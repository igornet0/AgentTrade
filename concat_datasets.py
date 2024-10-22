import os
import pandas as pd
from App_web import *

def concat_datasets_files(path_to_folder: str, save: bool = False) -> dict[str:pd.DataFrame]:
    data = {}

    for launch in os.listdir(path_to_folder):
        if not launch.startswith("launch"):
            continue

        path_to_launch = os.path.join(path_to_folder, launch)
        dataset = DatasetTimeseries(path_to_launch, save=False)

        file = dataset.get_filename()

        if file not in data:
            dataset.process()
            data[file] = dataset 
        else:
            data[file].concat_dataset(dataset)

    if save:
        for key, dataset in data.items():
            dataset.save_dataset()

    return data
