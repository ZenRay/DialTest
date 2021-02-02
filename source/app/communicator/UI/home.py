#coding:utf8
"""
Form implementation generated from reading ui file 'home.ui'

Created by: PyQt5 UI code generator 5.15.1

WARNING: Any manual changes made to this file will be lost when pyuic5 is
run again.  Do not edit this file unless you know what you are doing.
"""
import asyncio
import threading
import uuid

import sys
import json
import logging
from io import BytesIO
from os import path
from PyQt5 import QtCore, QtWidgets
from aiohttp import FormData

logger = logging.getLogger("app.communicator.UI")

class MainWindow:
    """
    拨测连接测试主界面
    """
    def __init__(self):
        # self.area = ""
        # self.unique_code = ""
        # self.iptv_host = ""
        self.loop_task = False
        self.loop = asyncio.new_event_loop()
        self.loop_frequency = 1


    def setupUI(self, window):
        """启动界面"""
        window.setObjectName("MainWindow")
        window.resize(356, 195)

        centralwidget = QtWidgets.QWidget(window)
        centralwidget.setObjectName("centralwidget")
        self.label_area = QtWidgets.QLabel(centralwidget)
        self.label_area.setGeometry(QtCore.QRect(20, 20, 71, 21))
        self.label_area.setAlignment(QtCore.Qt.AlignCenter)
        self.label_area.setObjectName("label_area")
        
        self.edit_area = QtWidgets.QLineEdit(centralwidget)
        self.edit_area.setGeometry(QtCore.QRect(100, 20, 221, 20))
        self.edit_area.setObjectName("edit_area")

        self.edit_unique_code = QtWidgets.QLineEdit(centralwidget)
        self.edit_unique_code.setGeometry(QtCore.QRect(100, 60, 221, 20))
        self.edit_unique_code.setObjectName("edit_unique_code")

        self.label_unique_code = QtWidgets.QLabel(centralwidget)
        self.label_unique_code.setGeometry(QtCore.QRect(20, 60, 71, 21))
        self.label_unique_code.setAlignment(QtCore.Qt.AlignCenter)
        self.label_unique_code.setObjectName("label_unique_code")

        self.label_iptv = QtWidgets.QLabel(centralwidget)
        self.label_iptv.setGeometry(QtCore.QRect(20, 100, 71, 21))
        self.label_iptv.setAlignment(QtCore.Qt.AlignCenter)
        self.label_iptv.setObjectName("label_iptv")

        self.edit_iptv = QtWidgets.QLineEdit(centralwidget)
        self.edit_iptv.setGeometry(QtCore.QRect(100, 100, 221, 20))
        self.edit_iptv.setObjectName("edit_iptv")

        self.btn_save_config = QtWidgets.QPushButton(centralwidget)
        self.btn_save_config.setGeometry(QtCore.QRect(130, 140, 90, 31))
        self.btn_save_config.setObjectName("btn_save_config")

        self.btn_service = QtWidgets.QPushButton(centralwidget)
        self.btn_service.setGeometry(QtCore.QRect(231, 140, 90, 31))
        self.btn_service.setObjectName("btn_service")

        self.btn_check_connect = QtWidgets.QPushButton(centralwidget)
        self.btn_check_connect.setGeometry(QtCore.QRect(30, 140, 90, 31))
        self.btn_check_connect.setObjectName("btn_check_connect")

        window.setCentralWidget(centralwidget)

        self.statusbar = QtWidgets.QStatusBar(window)
        self.statusbar.setObjectName("statusbar")
        window.setStatusBar(self.statusbar)

        self.retranslateUI(window)
        QtCore.QMetaObject.connectSlotsByName(window)


    def retranslateUI(self, window):
        """重构界面

        将界面转换为中文字符标识
        """
        _translate = QtCore.QCoreApplication.translate
        window.setWindowTitle(_translate("MainWindow", "拨测工具"))
        self.label_area.setText(_translate("MainWindow", "区    域"))
        self.label_unique_code.setText(_translate("Mainwindow", "唯 一 码"))
        self.label_iptv.setText(_translate("MainWindow", "机顶盒IP"))
        self.btn_save_config.setText(_translate("MainWindow", "保存配置"))
        self.btn_service.setText(_translate("MainWindow", "开启服务"))
        self.btn_check_connect.setText(_translate("MainWindow", "检查设备"))
        
        logger.info("初始化界面成功")


    # def apply(self, func, args, *, callback=None):
    #     """回调函数

    #     实现统一接口，接收函数或者参数处理相应的程序封装了该函数
    #     """
    #     func(args)

    # TODO: 后续需要解决异步调用封装