#coding:utf8
"""
和检测相关的任务，任务可以通过异步方式执行，同时提供分析类方法
"""
import logging
import math
import colorsys
import io
import base64
import cv2
import time
import numpy as np
from configparser import ConfigParser
from os import path
from typing import Text
from PIL import Image


from ._base import Request, TEMP
from ..check import _url_valid
from .. import adb


# 获取 AI 检测相关的接口
_target = path.abspath(path.join(path.dirname(__file__), "../../config"))

parser = ConfigParser()
parser.read(path.join(_target, "api.ini"), encoding="utf8")
# OCR 和 PORN Image 检测
ocr_check_url = parser.get("api","ocr_text_check")
porn_check_url = parser.get("api","porn_image_check")


# =====TODO: 添加 Host，后期需要删除
with open(path.join(_target, "url.txt"), "r", encoding="utf8") as file:
    _base = [line.strip() for line in file.readlines()]
    ocr_check_url = ocr_check_url.format(_base[1])
    porn_check_url = porn_check_url.format(_base[1])

## ========

# 图片缺失检测像素点占比阈值
EMPTY_THRESHOLD = .85
# 视频检测，两个相同图片相似度阈值
SIMILARITY_THRESHOLD = 0.95

logger = logging.getLogger("app.service.checktask")

def _cosine(arr1, arr2):
    """余弦相似度"""
    if arr1.shape != arr2.shape:
        raise RuntimeError("array {} shape not match {}".format(arr1.shape, arr2.shape))
    if arr1.ndim==1:
        norm1 = np.linalg.norm(arr1)
        norm2 = np.linalg.norm(arr2)
    elif arr1.ndim==2:
        norm1 = np.linalg.norm(arr1, axis=1, keepdims=True)
        norm2 = np.linalg.norm(arr2, axis=1, keepdims=True)
    else:
        raise RuntimeError("array dimensions {} not right".format(arr1.ndim))
    similiarity = np.dot(arr1, arr2.T)/(norm1 * norm2)
    dist = 1. - similiarity
    return dist



class Checker(Request):
    """检测类

    有两种类型：1）使用 API 接口方式检测，主要使用异步方式检测；2）本地直接提供算法方式
        检测，根据具体的情况是否使用异步检测方式
    """
    def __init__(self):
        if _url_valid(ocr_check_url):
            self.ocr_url = ocr_check_url
        
        if _url_valid(porn_check_url):
            self.porn_url = porn_check_url
    

    async def ocr(self, file):
        """图片文字识别
        
        """
        if not path.exists(file):
            raise FileNotFoundError(f"'{file}' not found")

        # 图片 OCR 检测数据传输需要使用 base64 处理
        buffer = io.BytesIO()
        image = Image.open(file)
        _, extension = path.splitext(file)
        if "jpg" in extension.lower():
            format = "JPEG"
        else:
            format = extension.replace(".", "").upper()
        # format = "PNG"
        image.save(buffer, format)

        data = {'images': [base64.b64encode(buffer.getvalue()).decode()]}
        
        headers = {'Content-Type': 'application/json'}
        result = await super().request(self.ocr_url, json=data, headers=headers)

        if not result:
            logger.error("图片 OCR 鉴定接口请求失败")
        return result

    
    async def porn(self, texts):
        """情色文本内容鉴定"""
        batch = max(len(text) for text in texts)

        if batch == 0:
            raise ValueError(f"提供了空文本，需要检查内容")

        data = {"texts": texts, "batch_size": batch, "use_gpu": False}

        result = await super().request(self.porn_url, json=data)

        if not result:
            logger.error("情色内容鉴定接口请求失败")
        return result


    def picture_lost(self, file, thumbnail=(200, 200)):
        """图片缺失鉴定"""
        # 读取图片，将图片处理为缩略图
        image = Image.open(file).convert("RGBA")
        image.thumbnail(thumbnail)

        max_score = 0
        color = None
        for freq, (r, g, b, _) in image.getcolors(math.prod(image.size)):
            _, saturation, _ = colorsys.rgb_to_hsv(r/255, g/255,b/255)

            # 筛除高亮像素
            y = min((r * 2104 + g * 4130 + b * 802 + 4096 + 131072) >> 13, 235)
            y = (y - 16) / (235 -16)
            if y > .9:
                continue

            # Calculate the score, preferring highly saturated colors.
            # Add 0.1 to the saturation so we don't completely ignore grayscale
            # colors by multiplying the count by zero, but still give them a low
            # weight.
            score = (saturation + 0.1) * freq

            # 获取像素最大的 RGB 值
            if score > max_score:
                max_score = score
                color = (r, g, b)
            
        # 计算颜色占比
        total = 0
        for freq, (r, g, b, _) in image.getcolors(math.prod(image.size)):
            if (r, g, b) == color:
                total += freq

        return (total / math.prod(image.size)) > EMPTY_THRESHOLD


    def video(self, name, rect=None, sleep=2):
        """检测视频
        
        通过前后两帧图片对比是否一致来检查
        """
        file, extension = path.splitext(name)
        
        time.sleep(sleep)
        first = f"{file}_1{extension}"
        # 截图
        adb.catpture_current_screen(first, TEMP)
        # 拼接
        first = path.join(TEMP, first)
        if rect is not None:
            _, first, _ = self.crop_rectangle(first, rect, True, False)
        
        # 休眠时间，以确保屏幕在当前情况下是存在变化的
        time.sleep(sleep)
        second = f"{file}_2{extension}"
        # 截图
        adb.catpture_current_screen(second, TEMP)
        # 拼接
        second = path.join(TEMP, second)
    
        if rect is not None:
            _, second, _ = self.crop_rectangle(second, rect, True, False)
        
        if not(path.exists(first) and path.exists(second)):
            logger.error(f"截取视频失败，未保存到图片")

        # 利用余弦相似度计算是否相似
        array1 = cv2.imread(first).flatten()
        array2 = cv2.imread(second).flatten()
        cosine = _cosine(array1, array2)

        return cosine >= SIMILARITY_THRESHOLD