#coding:utf8
"""
关于 Android 下使用 adb 命令的脚本
"""
import adbutils
import logging
from os import path
import subprocess

from .check import _IPisvalid
from ._key_codes import keycodes

# 以函数方式访问键盘的数字值

logger = logging.getLogger("app.adb")

def device_connected(serial, reconnected=False):
    """检查 Android 设备连接状态

    Args:
    ---------
    serial: str, adbutils.AdbDevice 设备 IP 地址或者设备
    reconnected: bool, 未连接的情况下是否需要重新连接

    Results:
    ---------
    连接不成功，返回布尔值；成功则返回 device
    """
    result = False
    if isinstance(serial, str) and _IPisvalid(serial):
        device = adbutils.adb.device(serial)
    elif isinstance(serial, adbutils.AdbDevice):
        device = serial
    else:
        raise TypeError(f"设备检查仅通过字符串或者 device，不能通过{serial}") 

    # 需要重连接时，在检测
    if reconnected:
        # 未连接设备重连接
        if not any([serial == device.serial for device in \
            adbutils.adb.device_list()]):
            adbutils.adb.connect(device.serial)

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
    # 满足其中一个条件需要重连：device 是 adbdevice 但是不能连接，或者 device 是字符串
    condition1 = isinstance(device, adbutils.AdbDevice) and not device.say_hello()
    condition2 = isinstance(device, str)
    if condition1 or condition2:
        device = device_connected(device, True) or device_connected(device, True)
    
    if not device:
        logger.error(f"设备 '{device.serial}' 尝试两次连接失败，请检查设备 ADB 调试状态")
    
    result = any(package in name for name in device.list_packages())
    return result



def setup_package(device, package, reconnected=False):
    """启动 package

    Args:
    --------
    device: adbutils.AdbDevice 或者 host, 连接的 Android 设备
    package: str，需要检查的 package 名称, eg: com.hzjy.svideo
    reconnected: bool, 需要重新连接
    """
    if isinstance(device, str) and reconnected:
        device = device_connected(device, True)
        
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


def catpture_current_screen(name, cwd=None):
    """使用 adbutils 模块截图
    
    adbutils 源码截图方案：
    if args.minicap:
        def adb_shell(cmd: list):
            print("Run:", " ".join(["adb", "shell"] + cmd))
            return d.shell(cmd).strip()
        json_output = adb_shell([
            "LD_LIBRARY_PATH=/data/local/tmp", "/data/local/tmp/minicap",
            "-i", "2&>/dev/null"
        ])
        if not json_output.startswith("{"):
            raise RuntimeError("Invalid json format", json_output)
        data = json.loads(json_output)
        
        w, h, r = data["width"], data["height"], data["rotation"]
        d.shell([
            "LD_LIBRARY_PATH=/data/local/tmp", "/data/local/tmp/minicap",
            "-P", "{0}x{1}@{0}x{1}/{2}".format(w, h, r), "-s",
            ">/sdcard/minicap.jpg"
        ])
        d.sync.pull("/sdcard/minicap.jpg", args.screenshot)
    else:
        remote_tmp_path = "/data/local/tmp/screenshot.png"
        d.shell(["rm", remote_tmp_path])
        d.shell(["screencap", "-p", remote_tmp_path])
        d.sync.pull(remote_tmp_path, args.screenshot)
    """
    # TODO: 需要调整为直接使用 adbutils 的源码提供方案
    if cwd is None:
        cwd = path.abspath(path.curdir)

    cmd = f"python -m adbutils --screenshot {name}"
    (stdout, stderr) = subprocess.Popen(cmd, shell=True, cwd=cwd, \
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, \
                    stderr=subprocess.STDOUT).communicate()
    
    return stdout, stderr