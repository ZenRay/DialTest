#coding:utf8
"""
执行任务
"""
import logging
import math
import cv2
import os
import datetime
import hashlib
from ._base import Task
from .. import adb
from os import path


logger = logging.getLogger("app.service.execute")
TEMP = path.join(path.dirname(__file__), "../../../temp")

DIRECTIONS_MAPPING = {
    "x": lambda x: "right" if x > 0 else "left",
    "y": lambda y: "down" if y > 0 else "down",
    "z": lambda z: "enter" if z == 1 else None
}

class EPGTaskExecute:
    def __init__(self, task_res, device):
        """

        task_res: 请求到的任务字典
        device: 已经连接设备

        """
        self.task = Task(task_res)
        self.device = device
    

    def capture_screen(self, name):
        """截屏"""
        stdout, stderr = adb.catpture_current_screen(name, TEMP)
        
        if not stderr:
            logger.info(f"'{name}' 图片截取成功，文件位置为: {TEMP}")
        else:
            logger.error(f"'{name}'图片截取失败")

        filename = path.join(TEMP, name)
        return filename


    def crop_rectangle(self, name, rect, copy=False):
        """截取图片数据
        
        利用 OpenCV 读取图片为 ndarray 之后，切片获取数据。

        Args:
        ---------
        name: 文件名称，需要全路径名
        rect: list, 截取的方框序列，顺序为 [top, right, down, left]
        copy: bool, 如果为 True，那需要保存副本，否则不保存
        """
        if not os.exists(name):
            raise FileNotFoundError(f"图片不存在")
        array = cv2.imread(name)
        # BGR to RGB
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)

        top, right, down, left = rect
        shape = array[left:right, top:down, :]

        if copy:
            time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
            new, extension = path.splitext(name)
            new += hashlib.md5(time).hexdigest()
            cv2.imwrite(new+extension, shape)
        
        return shape
        
