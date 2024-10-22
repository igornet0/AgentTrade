import pandas as pd
from datetime import datetime, timedelta
from sktime.forecasting.base import ForecastingHorizon

def volume_to_float(item: str) -> float:
    if item == "x":
        return item
    
    volume_int = {"K": 10**3, "M": 1, "B": 10**(-3)}

    if item[-1] not in volume_int.keys():
        return float(item)
    
    return round(float(item.replace(item[-1], "")) / volume_int[item[-1]], 2)

def convert_volume(dataset: pd.DataFrame) -> pd.DataFrame:
    pop_list = []

    for index, row in dataset.iterrows():
        if isinstance(row["volume"], float):
            continue

        if row["volume"].isdigit():
            pop_list.append(index)
            continue

        dataset.at[index, "volume"] = volume_to_float(row["volume"])

    dataset.drop(pop_list, inplace=True)

    return dataset

def str_to_float(item: str) -> float:
    if item == "x" or not isinstance(item, str):
        return item
    
    result = item.replace(" ", "").replace(',', '.')
    if result:
        return float(result)
    else:
        return item


def clear_datetime_false(df: pd.DataFrame, datetime_column: str = "datetime") -> pd.DataFrame:
    if datetime_column not in df.columns:
        raise ValueError(f"Column '{datetime_column}' does not exist in the DataFrame.")

    # Преобразуем столбец в тип datetime, если он еще не в этом формате
    df[datetime_column] = pd.to_datetime(df[datetime_column], errors='coerce')

     # Итерируем по строкам DataFrame
    for i in range(1, len(df)):
        if df.at[i, datetime_column] is False:
            # Находим предыдущую строку
            previous_value = df.at[i - 1, datetime_column]
            
            # Если предыдущая строка тоже не является NaT (Not a Time)
            if pd.notna(previous_value):
                # Вычисляем разницу между предыдущими значениями
                time_difference = df.at[i - 1, datetime_column] - df.at[i - 2, datetime_column]
                
                # Записываем новое значение
                df.at[i, datetime_column] = previous_value + time_difference

    return df

def get_time_range(timetravel) -> dict:
        time_start = "07:00"

        if timetravel[-1] == "m":
            time_end = "18:55"

        elif timetravel == "1H":
            time_end = "18:00"

        elif timetravel == "4H":
            time_end = "15:00"

        elif timetravel == "1D":
            time_end, time_start = "00:00", "00:00"
    
        time_range = pd.date_range(start=time_start, end=time_end, freq=timetravel.replace("m", "T"))

        return time_range


def convert_timetravel(timetravel: str) -> int:
    if timetravel[-1] == "m":
        n = 1
    
    elif timetravel == "H":
        n = 60

    elif timetravel == "D":
        n = 60 * 24
    
    return int(timetravel[:-1]) * n

def conncat_missing_rows(df, timetravel: str = "5m") -> pd.DataFrame:

    timetravel = convert_timetravel(timetravel)

    df = df.sort_values('datetime', ignore_index=True)

    missing_rows = []
    buffer_rows = []

    for index, row in df.iterrows():
        if row["datetime"] is pd.NaT:
            time = df.iloc[index - 1]["datetime"] + timedelta(minutes=timetravel)

            row["datetime"] = time
            missing_rows.append(row)

        buffer_rows.append(row)

        if len(buffer_rows) == 2:
            delta = buffer_rows[1]["datetime"] - buffer_rows[0]["datetime"]

            if delta != timedelta(minutes=timetravel):
                new_dt = buffer_rows[0]["datetime"] + timedelta(minutes=timetravel)

                new_row = {'datetime': new_dt}

                for col in df.columns[1:]:
                    new_row[col] = 'x'

                missing_rows.append(new_row)
            
            buffer_rows.pop(0)

    return pd.concat([df, pd.DataFrame(missing_rows)])


def clear_dataset(dataset: pd.DataFrame, timetravel: str = "5m", sort: bool = False) -> None:
    dataset = clear_datetime_false(dataset)

    for col in dataset.columns:
        if col in ["datetime", "volume"]:
            continue

        dataset[col] = dataset[col].apply(str_to_float) 

    if "volume" not in dataset.columns:
        raise ValueError("Column 'volume' does not exist in the DataFrame.")

    dataset = convert_volume(dataset)

    dataset = conncat_missing_rows(dataset, timetravel=timetravel)

    dataset = dataset.drop_duplicates(subset=['datetime'], ignore_index=True)

    if sort:
        dataset = dataset.sort_values(by='datetime', 
                                        ignore_index=True,
                                        ascending=False)

    return dataset


if __name__ == "__main__":
    dataset = pd.read_csv(input("dataset: "), index_col="Unnamed: 0")
    clear_dataset(dataset)