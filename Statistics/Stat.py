from App_trade import Dataset

def print_nan(dataset: Dataset) -> None:
    if hasattr(dataset, "__iter__"):
        for d in dataset:
            print_nan(d)
        return
    elif not isinstance(dataset, Dataset):
        return None
    
    print(f"[INFO] {dataset.get_filename()}: {len(dataset.get_dataset_Nan())=}")


class Stat:

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset
        print_nan(dataset)

