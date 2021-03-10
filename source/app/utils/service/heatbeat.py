#coding:utf8
"""
脚本是解决心跳相关的问题
"""
import asyncio
import logging
import urllib3
import aiohttp
import time

from urllib3 import exceptions
from aiohttp import web

from ..check import _url_valid, _args_valid

# 设置 logger
logger = logging.getLogger("app.utils.service.heartbeat")

# 心态时间
NORM_RATE = 3 # 正常状态心跳频率
ABNORM_RATE = 5 # 异常状态心跳频率

class Heart:
    """心跳类
    
    Property:
    ---------------
    url:str 心跳地址 URL
    rate: int, 发送心跳请求后需要等待的时间
    method: int，发送心跳服务的方式，默认是 'POST'，其他类型请求和 API 请求方式保持一致
    _first: bool, 是否是第一次发送请求

    Methods:
    --------------
    beat: 发送心跳请求的方法
    reset: 重启心跳服务，修改 _first 属性值为 True

    Exceptions:
    ---------------
    无效 URL 会触发异常
    """
    def __init__(self, url=None, rate=NORM_RATE, method="POST"):
        try:
            _url_valid(url)
            self.url = url
            self.rate = rate
            logger.debug(f"心跳连接地址有效检验通过: {url}")
        except Exception as err:
            logger.error(f"心跳连接地址 '{url}' 错误: {err}")
            raise Exception(err)
        
        self.method = method
        self._first = True # 第一次测试标识


    async def beat(self, data=None, method=None):
        """心跳检验
        
        根据心跳服务端响应结果，确认心跳是否存活

        Args:
        --------
        data: 接口请求需要的数据
        method： 接口请求的方方
        """
        if self._first:
            logger.info("启动心跳测试")
            self._first = False

        method = self.method.lower() if method is None else method.lower()
        # 使用 aiohttp 以异步方式向心跳服务器发送请求
        try:
            # 设置请求事件间隔
            time.sleep(self.rate)
            async with aiohttp.ClientSession() as session:
                async with getattr(session, method)(self.url, json=data) as res:
                    result = await res.json()

                    if int(res.status) == 200:
                        logger.debug(f"服务端心跳正常")
                        # 请求正常的情况下，重置时间为 5s
                        self.rate = NORM_RATE
                    else:
                        logger.error(f"服务端心跳异常，请求地址是'{self.url}'")
                    return result
        except aiohttp.ClientConnectionError as err:
            logger.error(f"请求 '{self.url}' 异常，原因是 {err}")
            # 设置频率为 异常时间频率
            self.rate = ABNORM_RATE

        

    def reset(self):
        """重启设置第一次属性"""
        logger.debug("重启心跳服务")
        self._first = True


    def close(self):
        """关闭服务"""
        logger.info("关闭心跳服务")
        # TODO: 后续需要设置关闭相关操作
        self._first = False


