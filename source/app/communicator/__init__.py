#coding:utf8
import sys
import json
import datetime
import logging
import time
import asyncio
import warnings
from os import path
from configparser import ConfigParser
from functools import partial
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from PyQt5.QtWidgets import QMainWindow


from .UI.home import MainWindow
from ..utils.check import check_text
from ..utils import adb
from ..utils import load_config, write_config
from ..utils.service import Heart, NORM_RATE, ABNORM_RATE, DialTask


# 解析配置信息
_communicator_file = path.join(path.dirname(__file__), "../config/communicator.ini")
communicator_parser = ConfigParser()
communicator_parser.read(_communicator_file, encoding="utf8")

logger = logging.getLogger("app")

# 任务队列
_Queue = asyncio.Queue(20)



class Button(QtCore.QThread):
    """按钮控件线程"""
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
        


class CheckConnect(Button):
    """线程监听形式检查文本内容"""
    def run(self):
        host = None
        host_label = ""
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(self.widget, str):
            status = check_text(self.window, self.widget)
            if "ip" in self.widget.lower() or "host" in self.widget.lower():
                host_label = self.widget.lower()
        elif isinstance(self.widget, list):
            status = all(check_text(self.window, widget) for widget in self.widget)

            labels = list(filter(lambda x: "ip" in x or "host" in x, self.widget))
            if labels:
                host_label = labels[0]
        
        # 检测状态失败才发送数据
        if status:
            logger.debug(f"'{self._alias}' 控件 Text 内容监测通过，申请时间: {time}")
            widget = dict() # 传输空 widget

            # 保存设备 Host 地址
            if host_label:
                host = getattr(self.window, host_label).text()
        else:
            logger.error(f"'{self._alias}' 在 {time} 监测内容失败")
            widget = {"title": "警告", "msg": "缺失配置信息"}
    
        # 检查设备连接情况
        if host:
            device = adb.device_connected(host)
            if device:
                widget = {"title": "提示", "msg": "设备连接成功"}
            else:
                logger.error(f"'{host}' 设备连接失败")
                widget = {"title": "提示", "msg": "连接失败，请检查设备设置"}        
        else:
            widget = dict()
        data = json.dumps({"status": status, "widget": widget})
        self._signal.emit(data)


class StoreConfig(Button):
    """保存配置按钮控件事件"""
    def run(self):
        try:
            write_config(self.window, communicator_parser, _communicator_file)
            # 写入配置成功信息提示
            widget = {"title": "提示", "msg": "配置保存成功"}
            status = True
            
        except Exception as err:
            widget = {"title": "警告", "msg": f"配置保存失败，原因: {err}"}
            status = False
        finally:
            data = json.dumps({"status": status, "widget": widget})
            self._signal.emit(data)


class DialService(Button):
    """播测服务按钮控件事件
    
    set_params: 修改需要发送请求的参数，即为 API 接口需要的数据
    """
    def __init__(self, window, widget, alias=None, forever=True, **kwargs):
        super().__init__(window, widget, alias=alias)

        # 播测任务请求相关配置
        self.task_url = kwargs.pop("dial_url") 
        self.task_method = kwargs.get("task_method", "POST")
        post_data = ["areaCode"]
        self.task_data = self.set_params(keys=post_data, **kwargs)
        self.device_serial = kwargs.get("device_serial")
        self.app_id = kwargs.get("app") # 需要启动的程序 id，例如:com.hzjy.svideo
        self._task = DialTask(url=self.task_url)
        
        # 心跳请求相关配置
        self.heart_url = kwargs.pop("heart_url")
        self.heart_method = kwargs.get("heart_method", "POST")
        post_data = ["areaCode", "deviceCode", "deviceName"] # 心跳请求需要传输数据
        self.heart_data = self.set_params(keys=post_data, **kwargs)
        self._heart = Heart(url=self.heart_url, method=self.heart_method)

        # 循环指示
        self.forever = forever


    def set_params(self, keys=[], delete=False, update=False, **kwargs):
        """修改传入的参数值
        
        Args:
        ---------
        keys: 需要更新的键，默认是 空列表。是列表的类型，表示只需要根据 keys 返回结果
            如果是字典，表示需要更新的值
        delete: 是否需要从关键字参数中删除相关键，一般必需和 keys 是列表时作为判断是否
            删除键的依据
        update: 表示更新 keys 字典
        """
        if isinstance(keys, list):
            result = {}
            for key in keys:
                result[key] = kwargs.get(key) if not delete else kwargs.pop(key)
            return result

        if isinstance(keys, dict):
            for key in kwargs:
                if key in keys:
                    keys[key] = kwargs.get(key)
                elif key not in keys and update:
                    warnings.warn(f"更新了新参数 '{key}'", UserWarning)
                    keys[key] = kwargs.get(key)
            logger.debug(f"心跳请求参数更新")


    @property
    def heart_rate(self):
        """心跳频率"""
        return self._heart.rate


    @heart_rate.setter
    def heart_rate(self, value):
        """调整心跳频率"""
        self._heart.rate = value


    def run(self):
        #TODO: 后续需要采用设备序列号缺失情况下，返回相关信息，采取回调机制处理
        if not self.device_serial:
            logger.error(f"缺少设备 Host")
    
        self.device = adb.device_connected(self.device_serial)

        if adb.check_package(self.device, self.app_id):
            logger.debug(f"启动应用页面成功: {self.app_id}")
            adb.setup_package(self.device, self.app_id)

        # 消费者生产者模式
        asyncio.run(self.product(), debug=False)
        # asyncio.run(self.consum(), debug=True)

        data = json.dumps({'status':False, 'widget': ""})
        self._signal.emit(data)


    async def product(self, **kwargs):
        """任务队列生产者"""
        while self.forever:
            result = await self._heart.beat(data=self.heart_data)
            task = await self._task.request(method=self.task_method, \
                data=self.task_data)
            # 根据返回的任务详情安排后续播测流程
            if int(task['code']) != 200:
                fmt = f"任务请求出错，状态码 '{task['code']}', 链接 '{self.task_url}'"
                raise ConnectionError(fmt)
            
            # if not task['data'].get("dialPlanTask"):
            #     logger.info(f"没有播测任务，{ABNORM_RATE}s 之后重试")
            #     self.heart_rate = ABNORM_RATE
            #     time.sleep(ABNORM_RATE)
            #     continue
            if task['data'].get("dialPlanTask"):
                self.heart_rate = NORM_RATE
    
            else:
                # 应用修改之后需要重新启动
                app_id = kwargs.get("app_id")
                if app_id and self.device.current_app()['package'] != app_id:
                    logger.debug(f"启动应用页面成功: '{app_id}'")
                    adb.setup_package(self.device, self.app_id)
                import ipdb; ipdb.set_trace()


        


class Home(QMainWindow, MainWindow):
    def __init__(self, parent=None, *, heart_url=None, dial_url=None, app_id=None):
        super(Home, self).__init__(parent)
        self.setupUI(self)
        self.update_config = False # 说明配置参数是否更新过
        # 心跳服务器地址
        if heart_url:
            self.heart_url = heart_url
        else:
            logger.warn("缺少心跳接口链接")

        # 播测任务请求地址
        if dial_url:
            self.dial_url = dial_url
        else:
            logger.warn("缺少播测任务请求接口链接")
        
        # 播测应用的 ID
        if app_id:
            self.app_id = app_id
        else:
            logger.warn("缺少启动的应用 ID, eg: 'com.hzjy.svideo'")

        # 加载配置信息
        load_config(self, communicator_parser)

        # 创建设备连接按钮的监控事件
        widgets = ["edit_area", "edit_iptv_host", "edit_unique_code"]
        self.btn_check_connect.clicked.connect(partial(self._click_event, dict(alias="设备检查", widget=widgets), \
            CheckConnect))
        
        # 创建配置保存按钮的监控事件
        self.btn_save_config.clicked.connect(partial(self._click_event, \
            dict(alias="保存配置", widget="btn_save_config"), StoreConfig))

        # 创建服务按钮的监控事件
        self.btn_service.clicked.connect(self._click_service_btn)


    def _click_event(self, widget_mapping, func):
        """创建按钮点击监控事件
        
        args:
        ------------
        widget_mapping: dict，键是触发控件的文本名称，值是控件属性名或者属性名的列表
        func: function，提供功能的函数或类
        """
        widget = widget_mapping.get("widget", "")
        name = f"{widget}_event" if not isinstance(widget, list) else "event"
        setattr(self, name, func(self, **widget_mapping))
        event = getattr(self, name)
        event._signal.connect(self.callback)
        event.start()

        # 如果是保存配置那么需要更新参数更新状态
        if widget_mapping.get("alias") == "保存配置":
            self.update_config = True



    def _click_service_btn(self, **kwargs):
        """创建按钮点击监控事件
        """
        # 没有播测服务线程时，添加线程
        if not hasattr(self, "service_event"):
            kwargs = dict(
                areaCode=self.edit_area.text(),
                deviceCode=self.edit_unique_code.text(),
                deviceName=self.edit_iptv_host.text(),
            )
            self.service_event = DialService(self, "btn_service", "播测服务", \
                heart_url=self.heart_url, dial_url=self.dial_url, **kwargs)

        # 根据现有状态，修改按钮标签内容
        if self.btn_service.text() == "开启服务":
            # 心跳首次是 False 需要重启
            if not self.service_event._heart._first:
                self.service_event._heart.reset()
        
            self.btn_service.setText("关闭服务")
            self.service_event.forever = True

            # 更新心跳服务请求
            if self.update_config:
                kwargs = dict(
                    areaCode=self.edit_area.text(),
                    deviceCode=self.edit_unique_code.text(),
                    deviceName=self.edit_iptv_host.text(),
                )

                self.service_event.set_params(self.service_event.heart_data, \
                    update=False, **kwargs)
                # 需要将配置状态修改为 False
                self.update_config = False

            # 更新监听事件中设备 Host
            self.service_event.device_serial = self.edit_iptv_host.text().strip()
            # 更新需要启动的应用 ID
            self.service_event.app_id = kwargs.get("app_id", self.app_id)

            # 启动服务
            self.service_event._signal.connect(self.callback)
            self.service_event.start()
        elif self.btn_service.text() == "关闭服务":
            self.btn_service.setText("开启服务")
            self.service_event._heart.close()
            self.service_event.forever = False



    def callback(self, msg):
        """回调函数

        用于处理运行后程序， msg 是一个 JSON 数据:
        status: bool，运行状态
        widget: dict, 窗口信息，包括 title 和 msg，分别表示窗口标题和提示信息
        """
        data = json.loads(msg)
        widget = data.get("widget")
        if widget:
            QtWidgets.QMessageBox.warning(self, widget['title'], widget['msg'])
        