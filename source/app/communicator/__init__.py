#coding:utf8
import sys
import json
import datetime
import logging
from os import path
from configparser import ConfigParser
from functools import partial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QMainWindow


from .UI.home import MainWindow
from ..utils.check import check_text
from ..utils import load_config


# 解析配置信息
_communicator_file = path.join(path.dirname(__file__), "../config/communicator.ini")
communicator_parser = ConfigParser()
communicator_parser.read(_communicator_file, encoding="utf8")

logger = logging.getLogger("app")


class CheckConnect(QtCore.QThread):
    """线程监听形式检查文本内容"""
    _signal = QtCore.pyqtSignal(str)
    
    def __init__(self, window, widget, alias=None):
        """线程初始化

        Properties:
        window: adbutils.AdbDevice，abd device 对象，是 widget 的 parent
        widget: str, list，需要监控的 widget 名称或者 widget 名称列表
        alias: str, widget 控件的别名
        """
        super().__init__()
        self.window = window
        self.widget = widget
        self._alias = alias if alias is not None else widget
        


    def run(self):
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(self.widget, str):
            status = check_text(self.window, self.widget)
        elif isinstance(self.widget, list):
            status = all(check_text(self.window, widget) for widget in self.widget)
        
        # 检测状态失败才发送数据
        if status:
            logger.debug(f"'{self._alias}' 控件 Text 内容监测通过，申请时间: {time}")
        else:
            logger.error(f"'{self._alias}' 在 {time} 监测内容失败")
            widget = {"title": "警告", "msg": "缺失配置信息"}
            data = json.dumps({"status": status, "widget": widget})
            self._signal.emit(data)
            return 
    



class Home(QMainWindow, MainWindow):
    def __init__(self, parent=None):
        super(Home, self).__init__(parent)
        self.setupUI(self)

        # 加载配置信息
        load_config(self, communicator_parser)

        # 创建按钮的监控事件
        widgets = ["edit_area", "edit_iptv_host", "edit_unique_code"]
        self.btn_check_connect.clicked.connect(partial(self._device_check, dict(alias="设备检查", widget=widgets)))
        

    def _device_check(self, widget_mapping):
        """创建点击设备监控
        
        args:
        ------------
        widget_mapping: dict，键是触发控件的文本名称，值是控件属性名或者属性名的列表
        """
        widget = widget_mapping.get("widget", "")
        name = f"{widget}_thread" if not isinstance(widget, list) else "thread"
        setattr(self, name, CheckConnect(self, **widget_mapping))
        thread = getattr(self, name)
        thread._signal.connect(self.callback)

        thread.start()


    def callback(self, msg):
        """回调函数

        用于处理运行后程序， msg 是一个 JSON 数据:
        status: bool，运行状态
        widget: dict, 窗口信息，包括 title 和 msg，分别表示窗口标题和提示信息
        
        """
        data = json.loads(msg)
        if not data['status']:
            QtWidgets.QMessageBox.warning(self, data['widget']['title'], data['widget']['msg'])
        