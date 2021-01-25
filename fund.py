# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt
import requests
import re
import json
import time
from configparser import ConfigParser

fund_file = 'fund.ini'
config_file = 'conf.ini'


def read_cfg(pram):
    cfg = ConfigParser()
    cfg.read(config_file)
    _pram = cfg.get('configuration', pram)
    return _pram


def query_fund(code, name='', gszzl='', gztime=''):
    url = "http://fundgz.1234567.com.cn/js/%s.js" % code

    # 浏览器头
    headers = {'content-type': 'application/json',
               'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100101 Firefox/22.0'}

    try:
        r = requests.get(url, headers=headers)
        # 返回信息
        content = r.text

        # 正则表达式
        pattern = r'^jsonpgz\((.*)\)'

        # 查找结果
        search = re.findall(pattern, content)

        name = json.loads(search[0])["name"]
        gszzl = json.loads(search[0])["gszzl"]
        gztime = json.loads(search[0])["gztime"][-5:]

        return name, gszzl, gztime
    except:
        return name, gszzl, gztime


def fund_count():
    with open(fund_file, 'r') as f:
        funds = f.readlines()
        return len(funds)


def fund_data():
    _data = []
    with open(fund_file, 'r') as f:
        funds = f.readlines()
        for i in range(len(funds)):
            data = query_fund(funds[i].strip())
            _data.append(data)
    return _data


class BackendThread(QObject):
    # 通过类成员对象定义信号
    update_data = pyqtSignal(list)

    # 处理业务逻辑
    def flush_data(self):
        while True:
            _fund_data = fund_data()
            self.update_data.emit(_fund_data)
            time.sleep(int(read_cfg("flush_time")))


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(185, 160)
        self.setWindowTitle("Fund")
        self.setWindowOpacity(float(read_cfg("WindowOpacity")))  # 透明度
        # self.setWindowFlags(Qt.FramelessWindowHint)               # 无边框
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
        HorizontalHeaderLabels = ["基金名称", "涨幅(%)", "时间"]
        columns = len(HorizontalHeaderLabels)
        self.table.setColumnCount(columns)
        self.rows = fund_count()
        self.table.setRowCount(self.rows)  #
        self.headerWidth = (60, 50, 50)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section{background-color:rgb(180,180,250);}")
        for i in range(columns):
            self.table.setColumnWidth(i, self.headerWidth[i])
        self.table.setHorizontalHeaderLabels(HorizontalHeaderLabels)

    def update_table(self, _fund_data):
        for i in range(self.rows):
            item = QTableWidgetItem(_fund_data[i][0][0:4])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(i, 0, item)
            item = QTableWidgetItem(_fund_data[i][1])
            item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.table.setItem(i, 1, item)
            item = QTableWidgetItem(_fund_data[i][2])
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
