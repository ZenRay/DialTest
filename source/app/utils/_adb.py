#coding:utf8

"""
截屏：
Windows 下的配置依赖信息参考
https://testerhome.com/topics/22315
https://www.kanzhun.com/jiaocheng/360742.html
需要相关的配置信息
"""
import asyncio
import threading
import logging
import multiprocessing
import subprocess
import os

from os import path


REMOTE_HOST = "localabstract:minicap"
LOCAL_PORT = 8099
LIBRARY_PATH = "/data/local/tmp"
LIBRARY = "/data/local/tmp/minicap"
ORIENTATIONS = 0 # 表示设备旋转方向


logger = logging.getLogger("app.adb")
class CaptureScreen:
    def __init__(self, device):
        self.full_width = device.widnow_size().width
        self.full_height = device.widnow_size().height
        
        # 需要设置设备的端口转发
        if not any(elem.remote == REMOTE_HOST for elem in device.forward_list()):
            logger.info(f"添加设备端口映射到 minicap")
            device.forward(f"tcp:{LOCAL_PORT}", REMOTE_HOST)
         

    def start_service(self):
        cmd = "adb shell LD_LIBRARY_PATH={0} {1} -P {2}x{3}@{2}x{3}/{4}"

        cmd = cmd.format(LIBRARY_PATH, LIBRARY, self.full_width, \
            self.full_height, ORIENTATIONS)

        # 后台驻留进程方式处理"
        # TODO:尚未解决启动进程
        self._process = multiprocessing.Process(name="minicap", target="")
        self._process.daemon = True # 设置后台驻留
        logger.info("启动 minicap 后台服务成功")


    
    @property
    def minicap(self):
        """启动minicap 服务"""
        if not hasattr(self, "_process"):
            logger.debug("minicap 服务未启动，正在重启")
            self.start_service()
        return self._process

    @classmethod
    def screenshot(cls, name, cwd=None):
        """使用 adbutils 模块截图"""
        if cwd is None:
            cwd = path.abspath(path.curdir)

        cmd = f"python -m adbutils --screenshot {name}"
        (stdout, stderr) = subprocess.Popen(cmd, shell=True, cwd=cwd, \
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, \
                        stderr=subprocess.STDOUT).communicate()
        import ipdb; ipdb.set_trace()