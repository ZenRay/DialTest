#coding:utf8
"""
解决报告结果的模块
"""
import logging
import copy
import aiohttp
import uuid
import datetime
import json
from io import BytesIO
from PIL import Image
from os import path
from configparser import ConfigParser

from ._base import Request
from ..check import _url_valid
from .._error_codes import error_codes


# 获取进度报告相关的接口
_target = path.join(path.dirname(__file__), "../../config")

parser = ConfigParser()
parser.read(path.join(_target, "report.ini"), encoding="utf8")

# 报告类接口
_urls = dict(
    task_start_url = parser.get("report", "task_start"),
    task_end_url = parser.get("report", "task_end"),
    capture_start_url = parser.get("report", "capture_start"),
    capture_end_url = parser.get("report", "capture_end"),
    file_upload_url = parser.get("report", "file_upload"),
    result_upload_url = parser.get("report", "result_upload"),
)

# =====TODO: 添加 Host，后期需要删除
with open(path.join(_target, "url.txt"), "r", encoding="utf8") as file:
    base = [line.strip() for line in file.readlines()]
    _urls['task_start_url'] = _urls['task_start_url'].format(base[0])
    _urls['task_end_url'] = _urls['task_end_url'].format(base[0])
    _urls['capture_start_url'] = _urls['capture_start_url'].format(base[0])
    _urls['capture_end_url'] = _urls['capture_end_url'].format(base[0])
    _urls['file_upload_url'] = _urls['file_upload_url'].format(base[0])
    _urls['result_upload_url'] = _urls['result_upload_url'].format(base[0])


## ========



logger = logging.getLogger("app.service.report")


class TaskStatusReport(Request):
    """统一管理任务进度报告"""
    def __init__(self, **kwargs):
        if not kwargs:
            kwargs = _urls

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
    def result_upload_url(self):
        """截图任务开始接口"""
        if hasattr(self, "_result_upload_url"):
            return self._result_upload_url
        else:
            raise AttributeError(f"不存在 result_upload_url 属性")


    async def task(self, url, id, type="开始", **kwargs):
        """提交任务报告
        
        通过 POST 方法提交任务ID，该 ID 在提出请求的任务响应的数据值为 planTaskId

        Args:
        ------
        url: 请求链接
        id: 任务 ID
        type: 任务类型，分为开始和结束
        """
        data = {'planTaskId': id}
        result = await super().request(url, json=data, **kwargs)

        if int(result['code']) == 200 and result.get("success"):
            logger.info(f"任务序列号 {id}: 播测任务{type}，状态修改成功")
        else:
            logger.error(f"任务序列号 {id}: 播测任务{type}，状态修改失败")
        
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
        
        result = await super().request(url, json=data)

        if int(result['code']) == 200 and result.get("success"):
            logger.info(f"截图序列: {id} 截屏任务{type}，状态修改成功")
        else:
            logger.error(f"截图序列: {id} 截屏任务{type}，状态修改失败")
        
        return result.get("surccess")



    async def upload_image_file(self, file, scale=0.5):
        """上传文件

        上传图像文件对象，需要根据需求将图像按比例压缩，默认是为缩放 50%
        """
        image = Image.open(file)
        _, extension = path.splitext(file)
        if "jpg" in extension.lower():
            format = "JPEG"
        else:
            format = extension.replace(".", "").upper()
        # 根据缩放比例将图像高和宽按比例缩放
        width, height = image.size
        image.thumbnail((int(width * scale), int(height * scale)))

        # 保存图像数据为字节型数据
        buffer = BytesIO()
        image.save(buffer, format)

        data = aiohttp.FormData()
        data.add_field("file", buffer.getvalue(), content_type=format.lower(),  
            filename=uuid.uuid4().hex + f".{format.lower()}")
        
        response = await super().request(self.file_upload_url, data=data)
        
        # 直接得到的是 URI 文本
        return response



    async def upload_report(self, task_info, error):
        """提交检测结果

        将播测任务信息、错误信息、错误类型，错误标题以及预警信息提交
        
        Args:
        -------
        task_info: dict, 是播测任务的任务信息，由任务请求获取道
        errors: ERROR 对象, 包括字段
            * file:裁切后用户分析的文件路径
            * code: 错误代码
            * text: 文本内容，用列表存储
            * position: 在图片中标注出的位置点，用列表存储
            * ffile: 画框标注的图片
        """
        # 需要将错误的图片上传，获取到 URL 位置值
        report = copy.deepcopy(task_info)
        del report['id']
        
        res = await self.upload_image_file(error.ffile)

        if not res:
            logger.error(f"上传报告图片失败")
        
        report['contentCode'] = error_codes[error.code].title
        report['contentName'] = error_codes[error.code].title
        report['earlyWarnTypeCode'] = error.code.upper()
        report['mediaContent'] = ''
        report['mediaType'] = 1
        report['desc'] = error_codes[error.code].message
        report['dialCollectionStatus'] = 1 if len(error.text) < 1 else len(error.text)
        report['sendRequestTime'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report['sumDialCount'] = 1
        report['screenshotPictureAttr'] = [res]

        headers = {'Content-Type': 'application/json'}
        
       
        response = await self.request(self.result_upload_url, data=json.dumps(report), headers=headers)
        msg = f"播测任务序列号:{report['dialPlanId']} 播测模板:{report['dialTemplate']} "
        if int(response['code']) == 200:
            status = "成功" if response.get('success', False) else "失败"
            logger.debug(f"检测完成，{msg}任务上报{status}，响应信息: {response['messages']}")
        else:
            logger.error(f"检测完成，{msg}任务不能上传，信息: {response}")
        
        return response
