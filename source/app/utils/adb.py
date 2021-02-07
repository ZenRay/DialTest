#coding:utf8
"""
关于 Android 下使用 adb 命令的脚本
"""
import adbutils
import logging

from .check import _IPisvalid
from ._key_codes import keycodes

# 以函数方式访问键盘的数字值

logger = logging.getLogger("app.adb")

def device_connected(serial):
    """检查 Android 设备连接状态

    Args:
    ---------
    serial: str, adbutils.AdbDevice 设备 IP 地址或者设备

    Results:
    ---------
    连接不成功，返回布尔值；成功则返回 device
    """
    result = False
    if isinstance(serial, str) and _IPisvalid(serial):
        device = adbutils.adb.device(serial)
        adbutils.adb.connect(serial)
    elif isinstance(serial, adbutils.AdbDevice):
        device = serial
        # 未连接设备重连接
        if not any([serial == device.serial for device in \
            adbutils.adb.device_list()]):
            adbutils.adb.connect(serial.serial)
    else:
        logger.error(f"设备检查仅通过字符串或者 device，不能通过{serial}") 

    try:
        msg = device.say_hello()
        serial = device.serial
        logger.debug(f"'{serial}' 连接设备成功: {msg}")
        result = device
    except adbutils.AdbError as error:
        logger.error(f"设备 {serial} 连接不成功")

    return result


def check_package(device, package):
    """检查设备中是否存在 package

    Args:
    --------
    device: adbutils.AdbDevice, 连接的 Android 设备
    package: str，需要检查的 package 名称, eg: com.hzjy.svideo

    Results:
    ---------
    存在 package 则 True，反之为 False
    """
    result = False
    if not(device_connected(device) or device_connected(device.serial)):
        logger.error(f"设备 '{device.serial}' 尝试两次连接失败，请检查设备 ADB 调试状态")
    
    result = any(package in name for name in device.list_packages())
    return result



def setup_package(device, package):
    """启动 package

    Args:
    --------
    device: adbutils.AdbDevice 或者 host, 连接的 Android 设备
    package: str，需要检查的 package 名称, eg: com.hzjy.svideo

    """
    if isinstance(device, str):
        device = device_connected(device)
        
    try:
        device.app_start(package)
        logger.info(f"'{package}' 正常启动")
    except Exception as err:
        logger.error(f"'{package}' 启动失败，检查应用 ID 是否正确")
    

def close_package(device, package):
    """关闭 package

    Args:
    --------
    device: adbutils.AdbDevice, 连接的 Android 设备
    package: str，需要检查的 package 名称, eg: com.hzjy.svideo
    """
    try:
        device.app_stop(package)
        logger.info("f'{package}' 正常关闭")
    except Exception as err:
        logger.error(f"'{package}' 未能正常关闭")

    
def remote_control(device, key):
    """以键盘方式控制输入

    通过键盘数字值进行键盘操作
    """
    key = keycodes[key]
    try:
        device.keyevent(key.value)
        logger.debug(f"成功输入键: {key.alias}")
    except Exception as err:
        logger.error(f"键 '{key.alias}' 输入响应失败")