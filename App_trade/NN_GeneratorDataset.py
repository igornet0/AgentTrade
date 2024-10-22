import numpy as np
import pandas as pd
import tensorflow as tf

class GeneratorDataset(tf.keras.utils.Sequence):
    def __init__(self, dataset: pd.DataFrame, batch_size=32, shuffle=True):
        # Initialization
        self.batch_size = batch_size
        self.shuffle = shuffle

        self.dataset: pd.DataFrame = dataset
        self.datalen = len(dataset)
        self.indexes = np.arange(self.datalen)

        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __getitem__(self, index):
        indices = self.indexes[index]
        if indices + self.batch_size >= self.datalen:
            indices = self.datalen - self.batch_size

        batch_data = self.dataset.iloc[indices : indices + self.batch_size]
        batch_label = self.dataset.iloc[indices + self.batch_size]

        return batch_data, batch_label
    
    def __len__(self):
        # Denotes the number of batches per epoch
        return self.datalen // self.batch_size

    def on_epoch_end(self):
        # Updates indexes after each epoch
        self.indexes = np.arange(self.datalen)
        if self.shuffle:
            np.random.shuffle(self.indexes)