from scripts.strategy import *
from random import randint
import pyqtgraph as pq


class Visualizer:
    def __init__(self, data):
        self.closes = data['<CLOSE>']
        self.data = data
        self.dates = data
        self.strategist = Strategist(self.data)

    def change_index_to_day(self, period):
        FL_tick = []
        FF_tick = []
        for i in range(len(self.closes)):
            if i % (len(self.closes) // period) == 0:
                FL_tick.append(i)
                FF_tick.append(self.dates[i])
        return FL_tick, FF_tick

    def draw_prices(self):
        plot_ = pq.PlotWidget()
        plot_.plot([i for i in range(len(self.closes))], self.closes)
        return plot_

    def draw_sma(self, period, plot_, pen):
        self.strategist.strategy_by_sma(period)
        curve = plot_.plot([i for i in range(len(self.closes) - len(self.strategist.sma_lst), len(self.closes))],
                   self.strategist.sma_lst, pen=pen)
        return plot_, curve

    def draw_rsi(self, period, pen):
        plot_ = pq.PlotWidget()
        self.strategist.strategy_by_rsi(period)
        curve = plot_.plot([i for i in range(len(self.closes) - len(self.strategist.rsi_lst), len(self.closes))],
                   self.strategist.rsi_lst, pen=pen)
        return plot_, curve

    def draw_macd(self, fast, slow, signal, pen):
        plot_ = pq.PlotWidget()
        self.strategist.strategy_by_macd(fast, slow, signal)
        curve = plot_.plot([i for i in range(len(self.closes) - len(self.strategist.macd), len(self.closes))],
                   self.strategist.macd, pen=pen)
        # plot_.setTitle(
        #     f'<span style="color: {pen.color()}; font-size: 20pt">MACD, fast: {fast}, slow: {slow}, signal: {signal}</span>'
        # )
        return plot_, curve
