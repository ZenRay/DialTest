#coding:utf8
"""
服务请求的父类
"""
import json
import aiohttp
import warnings

from os import path
from collections import namedtuple

from ..check import _url_valid, _args_valid

# 错误信息报告，字段信息包括: 裁切后用户分析的文件路径、错误代码、文本内容、在图片中
# 标注出的位置点以及画框标注的图片
ERROR = namedtuple("error", "file code text position ffile", defaults=[[], [], None])

# 存储图片的临时文件夹
TEMP = path.abspath(path.join(path.dirname(__file__), "../../../temp"))


class Request:
    def __init__(self, url):
        if _url_valid(url):
            self.url = url


    async def request(self, url=None, method="POST", json=None, data=None, **kwargs):
        """发出请求

        根据方法不同发出不同请求, data 为需要提交的数据， method 为 API 请求常用方法，
        eg: 'POST'
        """
        if url is None:
            url = self.url
        async with aiohttp.ClientSession(**kwargs) as session:
            # 默认传入方法参数为大写的，如果没有改属性改为小写
            if hasattr(session, method):
                req = getattr(session, method) 
            else:
                req = getattr(session, method.lower())
            
            async with req(url, data=data, json=json) as res:
                try:
                    result = await res.json()
                except:
                    result = await res.text()

                # 请求成功是返回成功数据值
                if int(res.status) == 200:
                    return result




# =======
# TODO: 后续对于任务列表改用 hashmap 来处理
# ====
class Task:
    """任务类"""
    def __init__(self, mapping):
        self.task = mapping


    def __getitem__(self, key):
        msg = None
        kpath  = "" # 键路径
        if "." in key:
            value = None
            for attr in key.split("."):
                kpath += attr
                
                if value is None:
                    value = self.task[attr]
                elif isinstance(value, list):
                    # 列表中元素必需是嵌套字典
                    if not isinstance(value[0], dict):
                        raise KeyError(f"'{kpath}' 下值不是字典，不能解析到需要对应数据")

                    # 直接解析列表信息
                    value = [element[attr] for element in value]
                    msg = f"'{kpath}' 路径下键的的值是列表，直接返回相关: '{value}'"
                    warnings.warn(msg, UserWarning)
                    return value
                else:
                    value = value[attr]
                
                # 检查得到的结果是否是有数据值
                if value is None:
                    raise KeyError(f"'{kpath}' 没有获取导数据")
        else:
            value = self.task[key]

        return value


    def __str__(self):
        return f"<Task Object at {hex(id(self))}>"
