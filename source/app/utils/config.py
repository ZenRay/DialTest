#coding:utf8
"""
处理配置信息，主要包括两个部分：
1. 加载配置信息
2. 写入配置信息
"""
import logging
import sys
from configparser import ConfigParser, NoOptionError, NoSectionError
from os import path


logger = logging.getLogger("app.config")

def load_config(window, parser):
    """加载播测需要配置信息
    
    configparser 解析对象，传递参数。
    Args:
    ----------------
    parser: ConfigParser 对象，section 以 communicator 开始

    Exception:
    ----------------
    TypeError: 得到的参数类型不是 ConfigParser
    """
    if not isinstance(parser,  (ConfigParser)):
        raise TypeError(f"Argument should be 'ConfigParser', but get {type(parser)}")
    
    try:
        window.edit_area.setText(parser.get('communicator', 'area'))
        window.edit_unique_code.setText(parser.get('communicator', 'unique_code'))
        window.edit_iptv_host.setText(parser.get('communicator', 'iptv_host'))
        logger.info("加载配置信息成功")
    except (NoOptionError, NoSectionError) as err:
        logger.debug(f"加载配置信息失败，缺少配置信息: {err}")
    except Exception as err:
        logger.debug(f"加载配置信息失败: {err}", exc_info=sys.exc_info())


def write_config(window, parser, file):
    """存储播测配置信息
    """
    try:
        area = window.edit_area.text()
        unique_code = window.edit_unique_code.text()
        iptv_host = window.edit_iptv_host.text()

        parser.set('communicator', 'area', str(area))
        parser.set('communicator', 'unique_code', str(unique_code))
        parser.set('communicator', 'iptv_host', str(iptv_host))

        # 写回文件
        with open(file, "w", encoding="utf8") as pfile:
            parser.write(pfile)
        logger.info(f"信息写入文件: '{file}'")
    except Exception as err:
        logger.debug(f"写入信息失败: {err}", exc_info=sys.exc_info())
