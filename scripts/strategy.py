from scripts.indicators import *


class Strategist:
    def __init__(self, data):
        self.data = data
        self.closes = self.data['<CLOSE>']
        self.funcs_with_names = {
            'sma': [self.strategy_by_sma, self.check_sma_crosses],
            'rsi': [self.strategy_by_rsi, self.check_rsi_crosses],
            'macd': [self.strategy_by_macd, self.check_macd_crosses],
        }
        self.inds_signs = {}

    def strategy_by_sma(self, *args):
        self.sma_lst = calculate_sma(self.closes, args[0])

    def strategy_by_rsi(self, *args):
        self.rsi_lst = calculate_rsi(self.closes, args[0])

    def strategy_by_macd(self, *args):
        self.macd = calculate_macd(self.closes, args[0], args[1], args[2])

    def check_sma_crosses(self):
        res = []
        for i in range(1, len(self.sma_lst)):
            if self.sma_lst[i - 1]:
                if self.sma_lst[i - 1] < self.closes[i - 1] and self.sma_lst[i] > self.closes[i]:
                    res.append([True, i - 1])
                elif self.sma_lst[i - 1] > self.closes[i - 1] and self.sma_lst[i] < self.closes[i]:
                    res.append([False, i - 1])
        return res

    def check_rsi_crosses(self):
        res = []
        last_close = -1
        for i in range(1, len(self.rsi_lst)):
            if self.rsi_lst[i - 1]:
                if self.rsi_lst[i - 1] <= 70 < self.rsi_lst[i]:
                    if res:
                        if res[-1][0]:
                            if last_close < self.closes[i]:
                                res[-1][1] = i
                        else:
                            res.append([True, i])
                    else:
                        res.append([True, i])
                elif self.rsi_lst[i - 1] >= 30 > self.rsi_lst[i]:
                    if res:
                        if not res[-1][0]:
                            if last_close > self.closes[i]:
                                res[-1][1] = i
                        else:
                            res.append([False, i])
                    else:
                        res.append([False, i])
                    last_close = self.closes[i]
        return res

    def check_macd_crosses(self):
        res = []
        mn = True
        now_close = -1
        for i in range(1, len(self.macd)):
            if self.macd[i - 1]:
                if self.macd[i - 1] <= 0.0 <= self.macd[i]:
                    res.append([False, i - 1])
                    now_close = self.closes[i - 1]
                    mn = False
                elif self.macd[i - 1] >= 0.0 >= self.macd[i]:
                    res.append([True, i - 1])
                    now_close = self.closes[i - 1]
                    mn = True
                if res:
                    if mn:
                        if self.closes[i - 1] < now_close:
                            res[-1] = [False, i - 1]
                            now_close = self.closes[i - 1]
                    else:
                        if self.closes[i - 1] > now_close:
                            now_close = self.closes[i - 1]
                            res[-1] = [True, i - 1]
        return res

    def return_signals_volumes(self, indicators_names_with_args):
        self.inds_signs = {}
        for [name, args] in indicators_names_with_args:
            self.funcs_with_names[name][0](*args)
            self.inds_signs[name] = self.funcs_with_names[name][1]()

    def return_signals_file(self, inwa):
        myself = Path('../trade_app').resolve()
        data_name = f'{myself}\\res\\res.txt'
        file = open(data_name, 'w')
        self.return_signals_volumes(inwa)
        for indicator in self.inds_signs:
            file.write(f'{indicator} signals:\n')
            for signal in self.inds_signs[indicator]:
                date = str(self.data['<DATE>'][signal[1]])
                date = date[:2] + '.' + date[2:4] + '.' + date[4:]
                if signal[0]:
                    file.write(f'down-up_{date};')
                else:
                    file.write(f'up-down_{date};')
            file.write('\n')

    def buy(self, res_money, cost, comission, type_comission):
        if type_comission == 'for trade':
            money = res_money / (1 + comission)
        else:
            money = res_money * cost / (cost + comission)
        number_actions = money // cost
        money = money - number_actions * cost
        return money, number_actions

    def trade(self, cost, number_actions, comission, type_comission):
        money = number_actions * cost
        if type_comission == 'for trade':
            money -= money * comission
        else:
            money -= money * comission * number_actions
        return money

    def count_earned_money(self, start_money, comission, indicators_names_with_args, type_comission):
        self.return_signals_volumes(indicators_names_with_args)
        lst_indexes = []
        dict_signals = {}
        for name in self.inds_signs:
            for value, index in self.inds_signs[name]:
                lst_indexes.append(index)
                dict_signals[index] = value
        lst_indexes = sorted(lst_indexes)
        res_money = start_money
        number_actions = 0
        print(comission)
        for index in lst_indexes:
            print(self.closes[index])
            print(number_actions)

            if dict_signals[index]:
                print('sale')
                res_money += self.trade(self.closes[index], number_actions, comission, type_comission)
                number_actions = 0
            elif index != lst_indexes[-1]:
                print('buy')
                res_money, number_actions = self.buy(res_money, self.closes[index], comission, type_comission)
        print(res_money, number_actions)
        return res_money



