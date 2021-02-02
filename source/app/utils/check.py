#coding:utf8
"""
对窗口进行相关检查
"""
import logging
import sys
import re
from configparser import ConfigParser, NoOptionError, NoSectionError
from PyQt5 import QtCore, QtWidgets


logger = logging.getLogger("app.check")



def check_text(window, widget, wmsg=None):
    """检查窗口插件文本

    检查窗口中 window 的 widget 的文本是否存在。如果不存在则弹出警告信息

    args:
    -------
    window, 窗口对象
    widget, str，需要查询 widget 名称
    wmsg, str，弹出的警告信息，默认为 None
    """
    text = getattr(window, widget).text().strip()
    if not text:
        message = f"{widget} 内容缺失，请添加相关信息" if wmsg is None else wmsg
        QtWidgets.QMessageBox.warning(window, title="警告", text=message)
        logger.warn(f"{widget} 缺少相关配置内容")
        return False
    if ('ip' in widget or 'host' in widget) and _IPisvalid(text):
        QtWidgets.QMessageBox.warning(window, "警告", "Host 或者 IP 地址不合法")
        return False
    return True



def _IPisvalid(ip):
    """检查 IP 地址是否合法"""
    pattern = re.compile(
        r"""^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3} # ip 前三个断
        (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
        """,re.X
    )
    return bool(pattern.match(ip))