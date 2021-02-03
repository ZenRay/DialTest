#coding:utf8
"""
对窗口进行相关检查
"""
import urllib3
import aiohttp

from urllib3 import exceptions
import logging
import sys
import re
import json
import datetime
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
        logger.warn(f"{widget} 缺少相关配置内容: {message}")
        return False
    if ('ip' in widget or 'host' in widget):
        if not _IPisvalid(text):
            logger.warn(f"{widget} 缺少相关配置内容或者 Host 或者 IP 地址不合法")
            return False
        else:
            logger.debug(f"Host 或者 IP 地址监测通过")

    return True



def _IPisvalid(ip):
    """检查 IP 地址是否合法"""
    pattern = re.compile(
        r"""^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3} # ip 前三个断
        (?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
        """,re.X
    )
    return bool(pattern.match(ip))



def _url_valid(url):
    """检查 URL 是否有效
    
    URL 有效性检验参考了 requests 模块 models 检验的代码
    """
    # Support for unicode domain names and paths.
    try:
        scheme, auth, host, port, path, query, fragment = urllib3.util.parse_url(url)
    except exceptions.LocationParseError as e:
        raise exceptions.InvalidURL(*e.args)

    if not scheme:
        error = ("Invalid URL {0!r}: No schema supplied. Perhaps you meant http://{0}?")
        error = error.format(url)

        raise exceptions.MissingSchema(error)

    if not host:
        raise exceptions.InvalidURL("Invalid URL %r: No host supplied" % url)

    # In general, we want to try IDNA encoding the hostname if the string contains
    # non-ASCII characters. This allows users to automatically get the correct IDNA
    # behaviour. For strings containing only ASCII characters, we need to also verify
    # it doesn't start with a wildcard (*), before allowing the unencoded hostname.
    if not host:
        raise exceptions.InvalidURL('URL has an invalid label.')
    elif host.startswith('*'):
        raise exceptions.InvalidURL('URL has an invalid label.')


