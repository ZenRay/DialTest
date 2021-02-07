#coding:utf8
"""
解决报告结果的模块
"""
import logging
import os
import aiohttp
import uuid


from io import BytesIO
from PIL import Image
from os import path


from ._base import Request
from ..check import _url_valid, _args_valid



logger = logging.getlogger("app.service.report")


class TaskReport(Request):
    """统一管理任务报告"""
    def __init__(self, **kwargs):
        for key, url in kwargs.items():
            if _url_valid(url):
                setattr(self, f"_{key}", url)


    @property
    def task_start_url(self):
        """任务开始接口"""
        if hasattr(self, "_task_start_url"):
            return self._task_start_url
        else:
            raise AttributeError(f"不存在 task_start_url 属性")


    @property
    def task_end_url(self):
        """任务结束接口"""
        if hasattr(self, "_task_end_url"):
            return self._task_end_url
        else:
            raise AttributeError(f"不存在 task_end_url 属性")

    
    @property
    def capture_start_url(self):
        """截图任务开始接口"""
        if hasattr(self, "_capture_start_url"):
            return self._capture_start_url
        else:
            raise AttributeError(f"不存在 capture_start_url 属性")


    @property
    def capture_end_url(self):
        """截图任务结束接口"""
        if hasattr(self, "_capture_end_url"):
            return self._capture_end_url
        else:
            raise AttributeError(f"不存在 capture_end_url 属性")


    @property
    def file_upload_url(self):
        """截图任务开始接口"""
        if hasattr(self, "_file_upload_url"):
            return self._file_upload_url
        else:
            raise AttributeError(f"不存在 file_upload_url 属性")


    @property
    def data_upload_url(self):
        """截图任务开始接口"""
        if hasattr(self, "_data_upload_url"):
            return self._data_upload_url
        else:
            raise AttributeError(f"不存在 data_upload_url 属性")


    async def task(self, url, id, type="开始"):
        """提交任务报告
        
        通过 POST 方法提交任务ID，该 ID 在提出请求的任务响应的数据值为 planTaskId

        Args:
        ------
        url: 请求链接
        id: 任务 ID
        type: 任务类型，分为开始和结束
        """
        data = {'planTaskId': id}
        result = await super().request(self.task_start_url, json=data)

        if int(result.code) == 200 and result.get("surccess"):
            logger.info(f"{id} 播测任务{type}，状态修改成功")
        else:
            logger.error(f"{id} 播测任务{type}，状态修改失败")
        
        return result.get("surccess")
    

    async def capture(self, url, id, type="开始", **kwargs):
        """提交截屏任务状态报告

        通过 POST 方法提交截屏任务 ID，该 ID 在提出请求任务响应的数据值为 screenshotId

        Args:
        ---------
        url: 请求链接
        id: 截屏任务 ID
        type: 任务类型，分为开始和结束，如果是结束类任务，还需要通过 kwargs 提供 
            'serviceImgUrl' 和 'localImgUrl' 参数，相关参数需要上传文件之后得到一个
            返回值
        """
        data = {'screenshotId': id}

        if type == "结束":
            for key in ['serviceImgUrl', 'localImgUrl']:
                if key not in kwargs:
                    raise Exception(f"'{key}' 参数缺失，不能提交结束任务")
                data[key] = kwargs[key]
        
        result = await super().request(self.task_start_url, json=data)

        if int(result.code) == 200 and result.get("surccess"):
            logger.info(f"{id} 截屏任务{type}，状态修改成功")
        else:
            logger.error(f"{id} 截屏任务{type}，状态修改失败")
        
        return result.get("surccess")



    async def upload_image_file(self, file, scale=0.5):
        """上传文件

        上传图像文件对象，需要根据需求将图像按比例压缩，默认是为缩放 50%
        """
        image = Image.open(file)
        _, extension = path.splitext(file)
        # 根据缩放比例将图像高和宽按比例缩放
        width, height = image.size
        image.thumbnail((int(width * scale), int(height * scale)))

        # 保存图像数据为字节型数据
        buffer = BytesIO()
        image.save(buffer, extension.upper())

        data = aiohttp.FormData()
        data.add_field("file", buffer.getvalue(), filename=uuid.uuid4().hex, \
            content_type=extension.lower())

        response = await super().request(self.file_upload_url, data=data)
        
        # TODO: 这里还有一个请求响应数据，需要后续检验一次具体的值是什么
        return response


