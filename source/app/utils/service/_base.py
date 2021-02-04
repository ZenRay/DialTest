#coding:utf8
"""
服务请求的父类
"""

import asyncio
import logging
import urllib3
import aiohttp
import time

from urllib3 import exceptions
from aiohttp import web

from ..check import _url_valid, _args_valid


class Request:
    def __init__(self, url):
        if _url_valid(url):
            self.url = url


    async def request(self, url=None, method="POST", data=None):
        """发出请求

        根据方法不同发出不同请求, data 为需要提交的数据， method 为 API 请求常用方法，
        eg: 'POST'
        """
        if url is None:
            url = self.url
        async with aiohttp.ClientSession() as session:
            # 默认传入方法参数为大写的，如果没有改属性改为小写
            if hasattr(session, method):
                req = getattr(session, method) 
            else:
                req = getattr(session, method.lower())
            
            async with req(url, json=data) as res:
                result = await res.json()

                # 请求成功是返回成功数据值
                if int(res.status) == 200:
                    return result