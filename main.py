from scripts.visualizer import *
import sys
import os
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel,
                             QTextEdit, QHBoxLayout, QVBoxLayout, QWidget, QComboBox,
                             QDialog, QMessageBox, QLineEdit)


def set_line_color():
    clr = (randint(0, 255), randint(0, 255), randint(0, 255))
    return clr


def return_data_list():
    directory = os.fsencode('data')
    res = []
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        res.append(filename)


class LineColorBox(QWidget):
    def __init__(self, size, color):
        super().__init__()
        self.size = size
        self.color = color
        self.setFixedSize(size, size)  # Устанавливаем фиксированный размер виджета

    def paintEvent(self, event):
        painter = QPainter(self)  # Создаем объект QPainter
        painter.setBrush(QColor(*self.color))  # Устанавливаем цвет квадрата
        painter.drawRect(0, 0, self.size, self.size)  # Рисуем квадрат


class ChartButton(QPushButton):
    def __init__(self, index_chart, index_btn, curve, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_chart = index_chart
        self.index_btn = index_btn
        self.curve = curve
        self.clicked.connect(self.delete_self)

    def delete_self(self):
        print(self.index_chart, self.index_btn)
        if self.index_chart == -1:
            window.plot.removeItem(self.curve)
        else:
            window.other_charts.itemAt(self.index_chart).widget().setParent(None)
            for i in range(window.charts_buttons_layout.count()):
                if window.charts_buttons_layout.itemAt(i).itemAt(0).widget().index_chart > self.index_chart:
                    window.charts_buttons_layout.itemAt(i).itemAt(0).widget().index_chart -= 1
        for i in range(3):
            window.charts_buttons_layout.itemAt(self.index_btn).itemAt(0).widget().setParent(None)
        window.charts_buttons_layout.itemAt(self.index_btn).layout().setParent(None)
        for i in range(self.index_btn, window.charts_buttons_layout.count()):
            window.charts_buttons_layout.itemAt(i).itemAt(0).widget().index_btn -= 1


class InputDialog(QDialog):
    def __init__(self, name_indicator):
        super().__init__()

        self.setWindowTitle("Всплывающее окно ввода")
        # self.setGeometry(100, 100, 300, 200)
        self.res = None
        # Создание вертикального слоя для размещения элементов
        layout = QVBoxLayout()
        # Пример нескольких строчных полей для ввода
        if name_indicator == 'sma' or name_indicator == 'rsi':
            self.input1 = QLineEdit(self)
            self.input1.setPlaceholderText("Введите период")
            layout.addWidget(self.input1)
        else:
            self.input1 = QLineEdit(self)
            self.input2 = QLineEdit(self)
            self.input3 = QLineEdit(self)
            self.input1.setPlaceholderText("Введите период")
            layout.addWidget(self.input1)
            self.input2.setPlaceholderText('Введите период')
            layout.addWidget(self.input2)
            self.input3.setPlaceholderText('Введите период')
            layout.addWidget(self.input3)

        # Создание кнопки для подтверждения ввода
        self.submit_button = QPushButton("Подтвердить", self)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)


class WindowChoiceIndicators(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("indicators")
        # self.setGeometry(100, 100, 300, 200)
        self.res = []
        self.res_dict = {}
        self.indicators_on_plot_count = 0
        self.other_indicators_count = 0
        # Создание вертикального слоя для размещения элементов
        layout = QVBoxLayout()
        # Пример нескольких строчных полей для ввода
        self.sma = QPushButton('sma')
        self.sma_args_w = InputDialog('sma')
        self.sma.clicked.connect(self.sma_args_w.show)
        self.sma_args_w.submit_button.clicked.connect(self.sma_read)
        self.rsi = QPushButton('rsi')
        self.rsi_args_w = InputDialog('rsi')
        self.rsi.clicked.connect(self.rsi_args_w.show)
        self.rsi_args_w.submit_button.clicked.connect(self.rsi_read)
        self.macd = QPushButton('macd')
        self.macd_args_w = InputDialog('macd')
        self.macd.clicked.connect(self.macd_args_w.show)
        self.macd_args_w.submit_button.clicked.connect(self.macd_read)
        layout.addWidget(self.sma)
        layout.addWidget(self.rsi)
        layout.addWidget(self.macd)
        # Создание кнопки для подтверждения ввода
        self.submit_button = QPushButton("Подтвердить", self)
        self.submit_button.clicked.connect(self.make_res)
        layout.addWidget(self.submit_button)

        self.setLayout(layout)

    def show_many_times(self):
        self.res_dict = {}
        self.show()

    def sma_read(self):
        self.res_dict['sma'] = [int(self.sma_args_w.input1.text())]
        self.sma_args_w.close()

    def rsi_read(self):
        self.res_dict['rsi'] = [int(self.rsi_args_w.input1.text())]
        self.rsi_args_w.close()

    def macd_read(self):
        self.res_dict['macd'] = [int(self.macd_args_w.input1.text()),
                                 int(self.macd_args_w.input2.text()),
                                 int(self.macd_args_w.input3.text())]
        self.macd_args_w.close()

    def make_res(self):
        self.res = []
        for key in self.res_dict:
            self.res.append([key, self.res_dict[key]])
            if key == 'sma':
                self.indicators_on_plot_count += 1
            else:
                self.other_indicators_count += 1
        self.close()


class MainWindow(QMainWindow):  # Создаем класс Window, который наследует все от класса QMainWindow
    def __init__(self):  # Создаем конструктор
        super().__init__()  # С помощью функции super вызывем конструктор из родительского класса
        self.func_with_names = {'sma': self.draw_sma,
                                'rsi': self.draw_rsi,
                                'macd': self.draw_macd}
        myself = Path('../trade_app').resolve()
        self.V = None
        self.filenames_lst = []
        directory = os.fsencode(f'{myself}\\data')
        for file in os.listdir(directory):
            filename = os.fsdecode(file)
            self.filenames_lst.append(filename)
        self.setWindowTitle("TRADER")

        MainHwidget = QWidget()
        HLayout = QHBoxLayout()
        left_Layout = QVBoxLayout()
        chartVLayout = QVBoxLayout()

        self.charts_layout = QVBoxLayout()
        self.plot = None
        self.plot_layout = QVBoxLayout()
        self.other_charts = QVBoxLayout()
        self.plot_layout.addWidget(self.plot)
        self.charts_layout.addLayout(self.plot_layout)
        self.charts_layout.addLayout(self.other_charts)
        self.charts_buttons_layout = QVBoxLayout()

        self.sma_args_w = InputDialog('sma')
        self.sma_args_w.submit_button.clicked.connect(self.draw_sma)
        self.rsi_args_w = InputDialog('rsi')
        self.rsi_args_w.submit_button.clicked.connect(self.draw_rsi)
        self.macd_args_w = InputDialog('macd')
        self.macd_args_w.submit_button.clicked.connect(self.draw_macd)

        filenames = QComboBox()
        filenames.addItems(self.filenames_lst)
        filenames.activated.connect(self.change_file)

        chartVLayout.addLayout(self.charts_layout)
        left_Layout.addLayout(chartVLayout)
        left_Layout.addWidget(filenames)

        right_Layout = QVBoxLayout()
        buttons_layout = QVBoxLayout()
        add_chart_btn = QPushButton('add_chart')
        add_chart_btn.clicked.connect(self.add_chart)
        indicators_for_res_btn = QPushButton('indicators_for_res')
        res_btn = QPushButton('make_res')
        self.res_indicators_window = WindowChoiceIndicators()
        indicators_for_res_btn.clicked.connect(self.res_indicators_window.show_many_times)
        res_btn.clicked.connect(lambda: self.V.strategist.return_signals_file(self.res_indicators_window.res))

        buttons_layout.addWidget(add_chart_btn)
        buttons_layout.addWidget(indicators_for_res_btn)
        buttons_layout.addWidget(res_btn)

        money_count_layout = QVBoxLayout()
        label_money = QLabel('Start money, $')
        input_money = QLineEdit()
        type_comission_box = QComboBox()
        self.type_lst = ['for stock', 'for trade']
        type_comission_box.addItems(self.type_lst)
        type_comission_box.activated.connect(self.change_comis_type)
        self.type_comission = 'for trade'
        label_comission = QLabel('Comission, %')
        input_comission = QLineEdit()
        indicators_choice_for_money_res = QPushButton('indicators_for_money_res')
        self.money_res_indicators_window = WindowChoiceIndicators()
        indicators_choice_for_money_res.clicked.connect(self.money_res_indicators_window.show_many_times)
        money_res_btn = QPushButton('count_earned_money')
        money_res_btn.clicked.connect(lambda: self.show_earned_money(int(input_money.text()),
                                                                     int(input_comission.text()) / 100)
                                      )
        self.money_res_label = QLabel("$")
        self.money_res_label.setStyleSheet('border-style: solid; border-width: 1px; border-color: black;')

        money_count_layout.addWidget(label_money)
        money_count_layout.addWidget(input_money)
        money_count_layout.addWidget(type_comission_box)
        money_count_layout.addWidget(label_comission)
        money_count_layout.addWidget(input_comission)
        money_count_layout.addWidget(indicators_choice_for_money_res)
        money_count_layout.addWidget(money_res_btn)
        money_count_layout.addWidget(self.money_res_label)

        right_Layout.addLayout(self.charts_buttons_layout)
        right_Layout.addLayout(buttons_layout)
        right_Layout.addLayout(money_count_layout)

        HLayout.addLayout(left_Layout)
        HLayout.addLayout(right_Layout)
        MainHwidget.setLayout(HLayout)

        self.setCentralWidget(MainHwidget)

    def change_comis_type(self, index):
        self.type_comission = self.type_lst[index]

    def change_file(self, index):
        self.s = self.filenames_lst[index]
        self.V = Visualizer(load_data(self.s))
        if self.plot:
            self.plot_layout.itemAt(0).widget().setParent(None)
        for i in range(self.other_charts.count()):
            self.other_charts.itemAt(0).widget().setParent(None)
        for i in range(self.charts_buttons_layout.count()):
            for j in range(self.charts_buttons_layout.itemAt(0).layout().count()):
                self.charts_buttons_layout.itemAt(0).itemAt(0).widget().setParent(None)
            self.charts_buttons_layout.itemAt(0).layout().setParent(None)
        self.plot = self.V.draw_prices()
        self.plot.setMinimumHeight(self.height() // 2)
        self.plot_layout.addWidget(self.plot)

    def add_chart(self):
        self.add_chart_window = WindowChoiceIndicators()
        self.add_chart_window.submit_button.clicked.connect(self.charts_added)
        self.add_chart_window.show()

    def charts_added(self):
        self.add_chart_window.make_res()
        self.draw_charts()

    def draw_charts(self):
        i = 0
        j = 0
        o_c = self.other_charts.count()
        b_l_c = self.charts_buttons_layout.count()
        for indicator in self.add_chart_window.res:
            clr = set_line_color()
            crv = self.func_with_names[indicator[0]](pq.mkPen(color=clr), *indicator[1])
            if indicator[0] != 'sma':
                btn = ChartButton(index_chart=i+o_c,
                                  index_btn=j+b_l_c,
                                  curve=crv,
                                  text=indicator[0])
                i += 1
            else:
                btn = ChartButton(index_chart=-1,
                                  index_btn=j+b_l_c,
                                  curve=crv,
                                  text=indicator[0])
            l = QHBoxLayout()
            l.addWidget(btn)
            l.addWidget(QLabel(f'periods: {indicator[1]}'))
            clr_box = LineColorBox(10, clr)
            l.addWidget(clr_box)
            self.charts_buttons_layout.addLayout(l)
            j += 1

    def draw_sma(self, clr, *args):
        self.plot, crv = self.V.draw_sma(*args, self.plot, clr)
        return crv

    def draw_rsi(self, clr, *args):
        plt, crv = self.V.draw_rsi(*args, clr)
        plt.setMaximumHeight(self.plot.height())
        self.other_charts.addWidget(plt)
        return crv

    def draw_macd(self, clr, *args):
        plt, crv = self.V.draw_macd(*args, clr)
        plt.setMaximumHeight(self.plot.height())
        self.other_charts.addWidget(plt)
        return crv

    def show_earned_money(self, start_money, comission):
        money = self.V.strategist.count_earned_money(start_money,
                                             comission,
                                             self.money_res_indicators_window.res,
                                             self.type_comission)
        self.money_res_label.setText(f'{int(money)}$')


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
