# -*- coding: utf-8 -*-

import sys
import yaml
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
import time
import akshare as ak

config_file = "./config.yaml"


def read_config(key):
    with open(config_file, encoding='utf-8') as fp:
        content = yaml.load(fp, Loader=yaml.FullLoader)
        return content[key]


def stocks_info():
    stocks = read_config('stocks')
    return len(stocks), stocks


def stocks_data():
    _data = []

    fund_value_estimation_em_df = ak.fund_value_estimation_em(symbol="全部")
    funds = fund_value_estimation_em_df[fund_value_estimation_em_df['基金代码'].isin([str(i) for i in stocks_info()[1]])]
    for _, row in funds.iterrows():
        _data.append([row['基金名称'], row[3], row[4]])

    return _data


class BackendThread(QObject):
    # 通过类成员对象定义信号
    update_data = pyqtSignal(list)

    # 处理业务逻辑
    def flush_data(self):
        while True:
            _stocks_data = stocks_data()
            self.update_data.emit(_stocks_data)
            time.sleep(int(read_config('configuration')['flush_time']))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(185, 160)
        self.setWindowTitle("基金")
        self.setWindowOpacity(float(read_config('configuration')['WindowOpacity']))  # 透明度
        self.setWindowFlags(Qt.FramelessWindowHint)  # 无边框
        self.setWindowFlags(Qt.WindowMinimizeButtonHint |  # 使能最小化按钮
                            Qt.WindowCloseButtonHint |  # 使能关闭按钮
                            Qt.WindowStaysOnTopHint)  # 窗体总在最前端
        # self.setFixedSize(self.width(), self.height())            # 固定窗体大小
        self.create_table()

        self.setup_centralWidget()
        self.initUI()

    def create_table(self):
        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        HorizontalHeaderLabels = ["名称", "最新价", "涨跌幅%"]
        columns = len(HorizontalHeaderLabels)
        self.table.setColumnCount(columns)
        self.rows = stocks_info()[0]
        self.table.setRowCount(self.rows)  #
        self.headerWidth = (55, 55, 50)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:rgb(180,180,250);}")
        for i in range(columns):
            self.table.setColumnWidth(i, self.headerWidth[i])
        self.table.setHorizontalHeaderLabels(HorizontalHeaderLabels)

    def update_table(self, _stocks_data):
        for i in range(self.rows):
            item = QTableWidgetItem(_stocks_data[i][0][0:4])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(i, 0, item)

            item = QTableWidgetItem(str(_stocks_data[i][1]))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(i, 1, item)

            item = QTableWidgetItem(str(_stocks_data[i][2]))
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(i, 2, item)

    def initUI(self):
        # 创建线程
        self.backend = BackendThread()
        # 连接信号
        self.backend.update_data.connect(self.update_table)
        self.thread = QThread()
        self.backend.moveToThread(self.thread)
        # 开始线程
        self.thread.started.connect(self.backend.flush_data)
        self.thread.start()

    def setup_centralWidget(self):
        # 设置主窗口中心部件
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(self.table, "")
        self.setCentralWidget(self.tabWidget)  # 指定主窗口中心部件


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
