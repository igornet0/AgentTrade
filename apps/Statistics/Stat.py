from App_web import *


class Stat:

    def __init__(self, dataset: DatasetTimeseries) -> None:
        self.dataset = dataset
    
    def print_nan(self) -> None:
    
        if hasattr(self.dataset, "__iter__"):
            for d in self.dataset:
                self.print_nan(d)
            return
        elif not isinstance(self.dataset, DatasetTimeseries):
            return None
        
        print(f"[INFO] {self.dataset.get_filename()}: {len(self.dataset.get_dataset_Nan())=}")

