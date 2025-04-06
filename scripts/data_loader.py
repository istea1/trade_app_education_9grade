import pandas as pd
from pathlib import Path


def load_data(file_name):
    myself = Path('../trade_app').resolve()
    data_name = f'{myself}\\data\\{file_name}'
    data = pd.read_csv(data_name, sep=';')
    return data


data = load_data("GAZP_240801_240827.csv")
print(data)



