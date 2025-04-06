from scripts.data_loader import *
import pandas_ta as pdt


def calculate_sma(data, period):
    sma = pdt.sma(data, period)
    return sma


def calculate_ema(data, period):
    ema = pdt.ema(data, period)
    return ema


def calculate_rsi(data, period):
    rsi = pdt.rsi(data, period)
    return rsi


def calculate_macd(data, fast, slow, signal):
    macd = pdt.macd(data, fast, slow, signal)[f'MACD_{fast}_{slow}_{signal}']
    return macd

# data = load_data("GAZP_240801_240827.csv")
# macd = calculate_sma(data['<CLOSE>'], 12)
# print(macd)
