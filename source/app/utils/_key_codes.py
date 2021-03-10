#coding:utf8
"""
硬件设备的按键编码信息，可以参考
https://blog.csdn.net/love_xsq/article/details/72468739
"""

"""电话键"""
call_keyboard = dict(
    KEYCODE_CALL = 5, # 拨号键 
    KEYCODE_ENDCALL = 6, # 挂机键 
    KEYCODE_HOME = 3, # 按键Home 
    KEYCODE_MENU = 82, # 菜单键 
    KEYCODE_BACK = 4, # 返回键 
    KEYCODE_SEARCH = 84, # 搜索键 
    KEYCODE_CAMERA = 27, # 拍照键 
    KEYCODE_FOCUS = 80, # 拍照对焦键 
    KEYCODE_POWER = 26, # 电源键 
    KEYCODE_NOTIFICATION = 83, # 通知键 
    KEYCODE_MUTE = 91, # 话筒静音键 
    KEYCODE_VOLUMEMUTE = 164, # 扬声器静音键 
    KEYCODE_VOLUMEUP = 24, # 音量增加键 
    KEYCODE_VOLUMEDOWN = 25, # 音量减小键 
)

"""控制键"""
control_keyboard = dict(
    KEYCODE_ENTER = 66, # 回车键 
    KEYCODE_ESCAPE = 111, # ESC键 
    KEYCODE_DPAD_CENTER = 23, # 导航键 确定键 
    KEYCODE_DPAD_UP = 19, # 导航键 向上 
    KEYCODE_DPAD_DOWN = 20, # 导航键 向下 
    KEYCODE_DPAD_LEFT = 21, # 导航键 向左 
    KEYCODE_DPAD_RIGHT = 22, # 导航键 向右 
    KEYCODE_MOVE_HOME = 122, # 光标移动到开始键 
    KEYCODE_MOVE_END = 123, # 光标移动到末尾键 
    KEYCODE_PAGEUP = 92, # 向上翻页键 
    KEYCODE_PAGEDOWN = 93, # 向下翻页键 
    KEYCODE_DEL = 67, # 退格键 
    KEYCODE_FORWARDDEL = 112, # 删除键 
    KEYCODE_INSERT = 124, # 插入键 
    KEYCODE_TAB = 61, # Tab键 
    KEYCODE_NUMLOCK = 143, # 小键盘锁 
    KEYCODE_CAPSLOCK = 115, # 大写锁定键 
    KEYCODE_BREAK = 121, # Break/Pause键 
    KEYCODE_SCROLLLOCK = 116, # 滚动锁定键 
    KEYCODE_ZOOMIN = 168, # 放大键 
    KEYCODE_ZOOMOUT = 169, # 缩小键 
)


"""基本"""
alpha_number_keyboard = dict(
    KEYCODE_0 = 7, # 按键0 
    KEYCODE_1 = 8, # 按键1 
    KEYCODE_2 = 9, # 按键2 
    KEYCODE_3 = 10, # 按键3 
    KEYCODE_4 = 11, # 按键4 
    KEYCODE_5 = 12, # 按键5 
    KEYCODE_6 = 13, # 按键6 
    KEYCODE_7 = 14, # 按键7 
    KEYCODE_8 = 15, # 按键8 
    KEYCODE_9 = 16, # 按键9 
    KEYCODE_A = 29, # 按键’A’ 
    KEYCODE_B = 30, # 按键’B’ 
    KEYCODE_C = 31, # 按键’C’ 
    KEYCODE_D = 32, # 按键’D’ 
    KEYCODE_E = 33, # 按键’E’ 
    KEYCODE_F = 34, # 按键’F’ 
    KEYCODE_G = 35, # 按键’G’ 
    KEYCODE_H = 36, # 按键’H’ 
    KEYCODE_I = 37, # 按键’I’ 
    KEYCODE_J = 38, # 按键’J’ 
    KEYCODE_K = 39, # 按键’K’ 
    KEYCODE_L = 40, # 按键’L’ 
    KEYCODE_M = 41, # 按键’M’ 
    KEYCODE_N = 42, # 按键’N’ 
    KEYCODE_O = 43, # 按键’O’ 
    KEYCODE_P = 44, # 按键’P’ 
    KEYCODE_Q = 45, # 按键’Q’ 
    KEYCODE_R = 46, # 按键’R’ 
    KEYCODE_S = 47, # 按键’S’ 
    KEYCODE_T = 48, # 按键’T’ 
    KEYCODE_U = 49, # 按键’U’ 
    KEYCODE_V = 50, # 按键’V’ 
    KEYCODE_W = 51, # 按键’W’ 
    KEYCODE_X = 52, # 按键’X’ 
    KEYCODE_Y = 53, # 按键’Y’ 
    KEYCODE_Z = 54, # 按键’Z’ 
)

import warnings
from collections import namedtuple

class KeyCodes:
    _field = namedtuple("keyboard", "alias value verbose", defaults=[None])
    def __init__(self):
        # 遍历字典构建键值对
        for keys in (call_keyboard, control_keyboard, alpha_number_keyboard):
            for key, value in keys.items():
                alias = key.split("_")[-1].lower()
                setattr(self, alias, self._field(alias, value, key))


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


keycodes = KeyCodes()
del call_keyboard, control_keyboard, alpha_number_keyboard

__all__ = ["keycodes"]