#coding:utf8
"""
播测任务列表请求
"""
import asyncio
import logging
import urllib3
import aiohttp
import time

from urllib3 import exceptions
from aiohttp import web

from ..check import _url_valid, _args_valid
from ._base import Request

logger = logging.getLogger("app.utils.service.dialtask")



class DialTask(Request):
    """播测任务类

    继承异步 Request 类
    """
    async def request(self, *, url=None, method="POST", data=None, json=None):
        """发出播测任务请求"""
        result = await super().request(url=url, method=method, data=data, json=json)
        return result
