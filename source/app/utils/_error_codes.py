#coding:utf8
errors = dict(
    disconnect = [404, "机顶盒设备无法连接或已断开"],
    unknown = [400, "未知错误"],
    id0001 = ['文本信息缺失或无法显示', '文本信息的文字字段为空'],
    id0002 = ['文本内容描述不合法', '文本相关信息内容描述不合法（涉黄、涉黑、涉暴）'],
    id0004 = ['海报图片缺失或无法显示', '海报图片链接url为空或url链接中海报图片缺失'],
    id0005 = ['海报图片内容展现和描述不合法', '海报图片相关内容展现和描述不合法（涉黄、涉黑、涉暴）'],
    id0010 = ['无法进行焦点切换', '焦点切换轨迹没有设置'],
    id0012 = ['页面无法访问', '页面链接url为空或链接返回404或者响应超时'],
    id0015 = ['视频内容无法播放', '视频文件播放错误或文件损坏']
)



import warnings
from collections import namedtuple

class ErrorCodes:
    _field = namedtuple("errorType", "name title message", defaults=[None])
    def __init__(self):
        # 遍历字典构建键值对
        for key, value in errors.items():
            setattr(self, key, self._field(key.upper(), value[0], value[1]))


    def __call__(self, *args):
        """以方法的方式获取键值

        Args:
        -------
        输入的参数长度只能是一个，该参数表示的是键的别名
        """
        if len(args) != 1:
            raise ValueError(f"参数数量为 {len(args)}，只能单独取一个键")
        
        if not hasattr(self, args[0].lower()):
            raise AttributeError(f"键盘没有相对应的key，输入的 key 为 '{args[0]}'")

        return getattr(self, args[0].lower())

    
    def __setitem__(self, key, value):
        warnings.warn("Object 不支持赋值", UserWarning)
        NotImplemented

    
    def __getitem__(self, key):
        """下标访问键"""
        if not hasattr(self, key.lower()):
            raise AttributeError(f"键盘没有相对应的key，输入的 key 为 '{key}'")

        return getattr(self, key.lower())


    def __str__(self) -> str:
        fmt = f"<ErrorCodes at {hex(id(self))}>"
        return fmt


error_codes = ErrorCodes()
del errors