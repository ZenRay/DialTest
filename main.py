#coding:utf8
import sys
import logging
from os import path


from source.app import (
    MainWindow, Home, QApplication
)
from source.app.utils import check_text, load_config, write_config, keycodes


from configparser import ConfigParser

# 解析全局配置信息
parser = ConfigParser()
parser.read(r"./dial.ini", encoding="utf8")
project = parser.get('project', 'name') # 项目名称
level = parser.get('log', 'level') # log 等级
heart_url = parser.get("heart", "url") # 心跳接口地址
dial_url = parser.get("task", "url") # 播测任务请求接口地址
app_id = parser.get("package", "app_id") # 初始启动的应用页面 ID



logging.basicConfig(level=getattr(logging, level))
logger = logging.getLogger(project)


# TODO: 开发阶段配置连接代码，后续需要删除
# ======
with open(path.join(path.dirname(__file__), "./url.txt"), "r", encoding="utf8") as file:
    base = [line.strip() for line in file.readlines()]
    heart_url = heart_url.format(base[0])
    dial_url = dial_url.format(base[0])


# =====

if __name__ == '__main__':
    logger.debug("启动程序")
    try:
        app = QApplication(sys.argv)
        home = Home(heart_url=heart_url, dial_url=dial_url, app_id=app_id)
        home.show()

        sys.exit(app.exec_())
    finally:
        logger.debug("程序关闭")