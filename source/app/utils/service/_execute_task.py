#coding:utf8
"""
执行任务
"""
import logging
import cv2
import datetime
import hashlib
import time



from ._base import Task, ERROR, TEMP
from ._execute_check import Checker
from .. import adb
from os import path


logger = logging.getLogger("app.service.execute")


DIRECTIONS_MAPPING = {
    "x": lambda x: "right" if x > 0 else "left",
    "y": lambda y: "down" if y > 0 else "down"
}


# 提供检测方法对象
checker = Checker()

class EPGTaskExecute:
    def __init__(self, device):
        """

        task_res: 请求到的任务字典
        device: 已经连接设备

        """
        self.device = device
    

    def rollback(self, package, xs, ys, zs=0, pagename=None):
        """回滚操作

        回滚到测试页面需要进行的操作流程，操作流程上优先 y 方向移动。如果是多级操作，那么
        需要进行遍历

        Args:
        ---------
        package: str, 应用 ID 名称，eg: com.hzjy.svideo
        xs: list(int), 表示需要左右移动的步数，正数表示向右移动，负数表示向左移动
        ys: (int)，表示上下移动步数，正数向下，负数表示向上
        zs: (int)，表示是否需要按 enter 键，0 表示不需要，1 表示需要
        pagename: str, 用于提示需要回滚到的页面名称
        """
        if pagename is None:
            pagename = ""

        try:
            self.device.app_start(package)
            for x, y, z in zip(xs, ys, zs):
                # y 向移动
                self.process(x, y, z)
                
            logger.debug(f"移动到了目标页面 {pagename}")
        except Exception as err:
            logger.error(f"移动页面失败 {pagename}")
        

    def process(self, x, y, z):
        """单流程操作

        一个操作批次
        """
        self.cursor_move(DIRECTIONS_MAPPING['y'](y), y) 
        time.sleep(0.2)
        # x 向移动
        self.cursor_move(DIRECTIONS_MAPPING['x'](x), x)
        time.sleep(0.2)

        if z == 1:
            self.enter
            time.sleep(0.2)


    def capture_screen(self, name):
        """截屏
        
        截屏的同时保留文件名称

        Args:
        --------
        name: str，文件名称，不包括路径名

        Results：
        --------
        返回包括文件路径的文件名称
        """
        stdout, stderr = adb.catpture_current_screen(name, TEMP)
        time.sleep(0.2)
        if not stderr:
            logger.info(f"'{name}' 图片截取成功，文件位置为: {TEMP}")
        else:
            logger.error(f"'{name}'图片截取失败")

        filename = path.join(TEMP, name)
        return filename


    def crop_rectangle(self, name, rect, copy=False, frame=False):
        """裁剪图片数据
        
        利用 OpenCV 读取图片为 ndarray 之后，切片获取数据。

        Args:
        ---------
        name: 文件名称，需要全路径名
        rect: list, 截取的方框序列，顺序为 [top, right, down, left]
        copy: bool, 如果为 True，那需要保存副本，否则不保存，副本名称使用 md5 加密时
            当前间戳获取
        frame: bool，如果为 True， 那么需要将图片添加边框保存副本，否则不保存。副本名
            称使用 md5 加密时当前间戳获取

        Result:
        ---------
        返回结果包括截图后的数据，保存的文件副本以及加边框图。如果没有保存副本，返回的
        文件名称为 None，如果 frame 为 False，返回有边框名称为 None，否则返回文件名称
        (文件名称中有 fr 表示)
        """
        file = None
        ffile = None
        if not path.exists(name):
            raise FileNotFoundError(f"图片不存在")
        array = cv2.imread(name)
        # BGR to RGB
        array = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)

        top, right, down, left = rect
        # 切换回 opencv 读取模式以存储图片
        shape = cv2.cvtColor(array[left:right, top:down, :], cv2.COLOR_RGB2BGR)

        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode()
        new, extension = path.splitext(name)

        if copy:
            new += hashlib.md5(time).hexdigest()
            file = new + extension
            cv2.imwrite(file, shape)
        
        if frame:
            if isinstance(frame, str):
                ffile = f"{new}_fr_{frame}{extension}" 
            else:
                ffile = ffile = f"{new}_fr{extension}" 
            cv2.imwrite(ffile, self._frame(array, rect))
        
        return shape, file, ffile


    def _frame(self, array, rect, color='red', brand=5):
        """图片添加边框
        
        将图片的 array 数据值，根据边框大小添加一定宽度的颜色框

        Args:
        --------
        array: ndarray, 图片的像素数据值
        rect: list，边框位置，top, right, bottom 和 left
        color: str, 需要添加的边框颜色，使用 'red', 'green', 'blue'，默认为 'red'
        brand: int，边框添加的宽度
        """
        if color == "red":
            channel_value = [255, 0, 0]
        elif color == "green":
            channel_value = [0, 255, 0]
        elif color == "blue":
            channel_value = [0, 0, 255]
        else:
            raise ValueError(f"边框颜色不支持: {color}，请选择 'red', 'blue', 'green'")
        
        positions = ['top', 'right', 'bottom', 'left']
        mapping = {key:value for key, value in zip(positions, rect)}

        width, height, _ = array.shape
        brim = {key:0 for key in positions}
        
        # 调整边框，向外扩展
        for position in positions:
            if position == 'top':
                if mapping[position] - brand > 0:
                    brim[position] = mapping[position] - brand
            elif position == 'bottom':
                if mapping[position] + brand > height:
                    brim[position] = height
                else:
                    brim[position] = mapping[position] + brand
            elif position == 'left':
                if mapping[position] - brand > 0:
                    brim[position] = mapping[position] - brand
            elif position == 'right':
                if mapping[position] + brand > width:
                    brim[position] = width
                else:
                    brim[position] = mapping[position] + brand
        
        for channel, value in enumerate(channel_value):
            array[mapping['left']:mapping['right'], brim['top']:mapping['top'], channel] = value
            array[mapping['left']:mapping['right'], mapping['bottom']:brim['bottom'], channel] = value

            array[brim["left"]:mapping["left"], mapping['top']:mapping["bottom"], channel] = value
            array[mapping["right"]:brim["right"], mapping['top']:mapping["bottom"], channel] = value

        return cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
                    
            
    def cursor_move(self, direction, point):
        """移动光标

        根据 direction 确认需要移动的方向，point 需要移动的步数。direction 字符串
        只能表示移动方向的值，eg: 'up', 'left' 等
        """
        for step in range(abs(point)):
            if not hasattr(self, direction):
                raise ValueError(f"方向移动错误，不能以 '{direction}' 方式移动")

            getattr(self, direction)


    
    @property
    def enter(self):
        adb.remote_control(self.device, "enter")

    
    @property
    def left(self):
        adb.remote_control(self.device, "left")
    

    @property
    def right(self):
        adb.remote_control(self.device, "right")


    @property
    def up(self):
        adb.remote_control(self.device, "up")

    
    @property
    def down(self):
        adb.remote_control(self.device, "down")


    async def porn_text(self, file):
        """检测情色文本内容"""
        # 目前检测方案是检测图片中文本，和 porn_image 的差异在提交的错误代码不同
        errors = []
        res = await checker.ocr(file)
        if int(res['status']) == -1 or len(res['results']) == 0:
            logger.debug(f"图片文件未检测到文字或者没有文字: {file}")
            errors.append(ERROR(file, "ID0001"))
        elif int(res['status']) == 0 and len(res['results']) > 0:
            # 提取出文本内容检测情色文字
            text_list = [data['data'] for data in res['results']]
            texts = [[item['text'] for item in data] for data in text_list]
            porn_texts = []
            porn_positions = []
            for item in texts:
                res = await checker.porn(item)

                if int(res["status"]) == 0 and isinstance(res['results'], list):
                    for index, item in enumerate(res['results']):
                        if int(item['porn_detection_label']) == 1:
                            porn_texts.append(item['text'])
                            porn_positions.append(text_list[index]['text_box_position'])
            errors.append(
                ERROR(file, "ID0002", porn_texts, porn_positions)
            )

        return errors


    async def porn_image(self, file):
        """检查情色图片
        """
        # 现有方案是检测的图片中是否有情色文本内容，并非检测图片是否为情色图片
        errors = []
        res = await checker.ocr(file)
        if int(res['status']) == -1 or len(res['results']) == 0:
            logger.debug(f"图片文件未检测到文字或者没有文字: {file}")
            errors.append(ERROR(file, "ID0001"))
        elif int(res['status'] == 0) and len(res['results']['data']) > 0:
            # 提取出文本内容检测情色文字
            text_list = [data['data'] for data in res['results']]
            texts = [[item['text'] for item in data] for data in text_list]
            porn_texts = []
            porn_positions = []
            for item in texts:
                res = await checker.porn(item)

                if int(res["status"]) == 0 and isinstance(res['results'], list):
                    for index, item in enumerate(res['results']):
                        if int(item['porn_detection_label']) == 1:
                            porn_texts.append(item['text'])
                            porn_positions.append(text_list[index]['text_box_position'])
            errors.append(
                ERROR(file, "ID0002", porn_texts, porn_positions)
            )

        return errors


    async def task_bullet(self, type, file):
        """执行不同类型任务

        该框内需要处理的任务类型: 
        1: 情色文字检测（包括进行 OCR 和文本检测两个步骤
        2: 图片检测（包括检测图片缺失以及 情色图片检测
        3: 视频检测，目前暂未确认需要检测需求和检测方案
        """
        errors = []
        # 文本检测
        if type == 1:
            res = await self.porn_text(file)
            errors.extend(res)

        # 图片检测
        if type == 2:
            # 图片缺失监测报告
            res = checker.picture_lost(file)
            if res:
                errors.append(ERROR(file, "ID0004"))
            else:
                res = await self.porn_image(file)
                errors.extend(res)

        # 视频检测
        if type == 3:
            res = checker.video(file)
            
            # 视频缺失报告
            if res:
                errors.append(ERROR(file, "ID0015"))

        if type not in (1, 2, 3):
            logger.error(f"目前暂不支持除视频、文本以及图片检测以外检测")
        
        return errors

