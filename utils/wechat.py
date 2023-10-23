import time
import random
import datetime

import pyautogui
from pywinauto.findwindows import ElementNotFoundError
from pywinauto.application import Application, ProcessNotFoundError

import win32api
import win32con


# 读取注册表找到微信的安装路径
def get_wx_install_path() -> str:
    try:
        # 注册表打开
        # RegOpenKey(key, subKey , reserved , sam)
        # key: HKEY_CLASSES_ROOT HKEY_CURRENT_USER HEKY_LOCAL_MACHINE HKEY_USERS HKEY_CURRENT_CONFIG
        # subkey: 要打开的子项
        # reserved: 必须为0
        # sam: 对打开的子项进行的操作,包括win32con.KEY_ALL_ACCESS、win32con.KEY_READ、win32con.KEY_WRITE等
        key = win32api.RegOpenKey(win32con.HKEY_CURRENT_USER, "SOFTWARE\Tencent\WeChat", 0, win32con.KEY_ALL_ACCESS)
        # 这里的key表示键值，后面是具体的键名，读取出来是个tuple
        value = win32api.RegQueryValueEx(key, "InstallPath")[0]
        # 用完之后记得关闭
        win32api.RegCloseKey(key)
        # 微信的路径
        value += "\\" + "WeChat.exe"
        return value
    except Exception as _:
        return ""


class Helper:
    """
    帮助类
    """

    @staticmethod
    def print(msg):
        """
        打印和记录消息
        :param msg:
        :return:
        """
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f'{msg} 当前时间：{time}')

    @staticmethod
    def get_time():
        """
        获取时间字符串%Y-%m-%d %H:%M:%S
        :return:
        """
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class AutoMsg:
    """
    定义自动化操作的结果类
    """

    def __init__(self):
        self.result = 0
        self.message = ""
        self.errcode = ""

    def get_result(self):
        """
        获取结果信息 1 成功 -1失败 0未知
        :return:
        """
        return self.result

    def get_errcode(self):
        """
        获取错误的编码
        :return:
        """
        return self.errcode


class UserNotFoundError(Exception):
    """
    微信用户没有找到异常
    """
    pass


class AppNotFoundError(Exception):
    """
    没有找到应用程序
    """
    pass


class EleNotFoundError(Exception):
    """
    没有找到应用程序
    """
    pass


class Wechat:
    """
    微信的自动化处理
    """

    def __init__(self):
        """
        创建微信自动化的实例
        :param path:
        :return:
        """
        self.__path = get_wx_install_path()
        # 微信的主窗口对象
        self.__main_win = None
        # 微信输入框的对象
        self.__input_msg_box = None
        # 查询输入框对象
        self.__search_box = None
        # 微信默认显示的会话列表框
        self.__dia_list = None
        # 输入框的标题的button
        self.__input_title_btn = None
        # 右侧面板
        self.__right_panel = None

    @staticmethod
    def __get_main_win(path):
        """
        获取微信的主窗口
        :param path:传入微信的安装路径
        :return:
        """
        # 获取进程ID
        try:
            app = Application(backend='uia').connect(path=path)
        except ProcessNotFoundError:
            raise AppNotFoundError("微信程序还没有打开")
        main_win = app.window(class_name='WeChatMainWndForPC')
        # if not app.top_window():
        Helper.print(f'     获取主程序 pid为{app.process}')
        return main_win

    def __is_latest_user(self, username):
        """
        是否为最近聊天的用户
        :param username:微信聊天的用户
        :return:
        """
        result = False
        if self.__dia_list and self.__input_title_btn:
            # 检查会话框是不是选中当前用户
            item_list = self.__dia_list.get_items()
            for item in item_list:
                if item.is_selected() and item.element_info.name == username:
                    # 会话选中当前用户
                    result = True
                    break
            if result:
                # 如果输入框对象存在并且等于当前用户
                result = self.__input_title_btn.window_text().strip() == username
        if result:
            Helper.print("     ~~~~对话用户没变~~~~")
        return result

    def __auto_by_search(self, parent_ele, username):
        """
        先选择搜索框，再进行发送信息
        :param parent_ele:父窗口的对象
        :param username:发送的用户
        :return:
        """
        # 搜索框的名称
        Helper.print('      ===通过搜索查找用户===')
        # select_item = self.__search_box = select_item
        # selectItem.draw_outline(colour='red')
        self.__search_box.click_input()
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.hotkey('delete')
        Helper.print('      输入筛选词语')
        self.__search_box.type_keys(username, with_spaces=False)
        Helper.print("      等待2秒出筛选结果")
        # 等待筛选结果出来
        time.sleep(2)
        # 选择下来项目
        Helper.print('      选择第一个搜索出来的用户')
        # 通过列表来查询
        select_item = None
        target_ele = parent_ele.children()[1].children()[0]
        items = target_ele.get_items()
        for item in items:
            if item.element_info.name == username:
                select_item = item
                break
        Helper.print("      ------从搜索列表中找到用户------")
        if select_item:
            Helper.print('      用户列表查找完毕，点击控件')
            select_item.click_input()
        else:
            raise UserNotFoundError(f"没有找到名称为\"{username}\"的用户")

    def __auto_by_list(self, username):
        """
        直接寻找用户的控件
        :param username:发送的用户
        :return:
        """
        if not self.__dia_list:
            self.__dia_list = self.__main_win.child_window(title="会话", control_type="List").wrapper_object()
        dia_list = self.__dia_list
        Helper.print(f"      查找\"{username}\"的控件")
        select_item = None
        for item in dia_list.get_items():
            if item.element_info.name == username:
                select_item = item
                break
        if select_item and select_item.is_visible():
            # 如果已经找到下拉控件
            select_item.click_input()
        else:
            # 根据会话框找到上级窗口(参照Inspect)
            parent_ele = dia_list.parent().parent().parent().parent()
            self.__auto_by_search(parent_ele, username)

    def __init_elements(self, username):
        """
        获取用户控件，初始化各个参数
        :param username:
        :return:
        """
        if not self.__path:
            raise Exception("微信exe路径不能为空！")
        if not self.__main_win:
            self.__main_win = Wechat.__get_main_win(self.__path)
        try:
            self.__main_win.set_focus()
        except ElementNotFoundError:
            raise EleNotFoundError("核心窗口对象没有找到，请检测微信是否已经登录")
        if not self.__search_box:
            self.__search_box = self.__main_win.child_window(title='搜索', control_type="Edit").wrapper_object()
        # 获取Edit控件的值，判断是否为空
        if len(self.__search_box.get_value().strip()) > 0:
            # 如果正在搜索中，删除按钮会出现
            del_btn = self.__search_box.parent().children()[-1]
            del_btn.click_input()
        # ----1、尝试选择下拉控件----
        if not self.__is_latest_user(username):
            self.__auto_by_list(username)
            # 等待右边的输入框的显示
            time.sleep(1)
        if not self.__input_msg_box:
            self.__input_msg_box = self.__main_win.child_window(title="输入", control_type="Edit").wrapper_object()
        if not self.__right_panel:
            # 根据元素位置来进行编程(参照inspect)
            self.__right_panel = self.__input_msg_box.parent().parent().parent().parent().parent().parent()
        # ----2、如果已经获取到输入框，则检查一下信息框是否存在----
        if not self.__input_title_btn:
            # Helper.print("      input_title_btn为空，查找一下控件")
            # 如果还没有找到这个输入框的标题控件
            item_list = self.__right_panel.children()
            if len(item_list) > 0:
                # 从右侧面板的第一个控件(右侧顶部面板)开始查找(参照inspect)
                item_list = item_list[0].descendants(title=username, control_type="Button")
                if len(item_list) == 0:
                    raise Exception("没有找到当前用户的对话框！")
                self.__input_title_btn = item_list[0]
        # Helper.print("      input_title_btn element_info.name is " + self.__input_title_btn.element_info.name)
        if self.__input_title_btn.element_info.name != username:
            # 如果输入框的标题不是当前用户
            raise Exception("没有找到当前用户的对话框！")
        # Helper.print(f"      \"{username}\"对话框已经找到，查找用户正确！")

    def __send_message(self, username, send_msg):
        """
        向特定的用户发送消息
        :param username: 对方微信的用户名称
        :param send_msg: 发送的消息
        :return:
        """
        # 打开微信的快捷键
        Helper.print("--开始发送信息--")
        self.__init_elements(username)
        # ----3、到了用户对话框，才开始输入对话信息----
        self.__input_msg_box.click_input()
        self.__input_msg_box.type_keys(send_msg, with_spaces=True)
        # 回车发送

        pyautogui.hotkey('enter')
        Helper.print("--结束发送信息--")

    def __get_message(self, username, other_side=False):
        """
        获取最后的会话信息
        :param username: 微信用户名称
        :param other_side: 只读取对方的信息，只适合双人会话
        :return:
        """
        message = None
        Helper.print("--开始查找信息--")
        self.__init_elements(username)
        dia_list = self.__right_panel.descendants(title="消息", control_type="List")
        if len(dia_list) > 0:
            # 获取List中最后一个控件
            last_item = dia_list[0].get_item(-1)
            message = last_item.element_info.name
            if other_side:
                # 检测是否为对方的输入
                btn_list = last_item.descendants(title=username, control_type="Button")
                if len(btn_list) == 0:
                    # 如果不是对方的输入信息
                    message = None
        Helper.print("--结束查找信息--")
        return message

    @staticmethod
    def __wrap_errcode(exception):
        """
        判断异常的类型，并设置错误代码
        :param exception:
        :return:
        """
        result = ""
        if isinstance(exception, UserNotFoundError):
            result = "3-01用户不存在"
        elif isinstance(exception, EleNotFoundError):
            result = "2-01控件不存在"
        elif isinstance(exception, AppNotFoundError):
            result = "1-01程序没启动"
        return result

    def get_last_msg(self, username, other_side=False):
        """
        获取最后的会话
        :param username: 微信用户名称
        :param other_side: 只读取对方的信息，只适合双人会话，适合自动回复场景
        :return:
        """
        auto_msg = AutoMsg()
        try:
            message = self.__get_message(username, other_side)
            auto_msg.result = 1
            auto_msg.message = message
        except Exception as e:
            auto_msg.result = -1
            auto_msg.message = str(e)
            auto_msg.errcode = Wechat.__wrap_errcode(e)
        if other_side and auto_msg.message is None:
            # 如果要读取对方的信息，并且读不到。
            auto_msg.result = -1
        return auto_msg

    def send_msg(self, username, send_msg):
        """
        向特定的用户发送消息
        :param username: 对方微信的用户名称
        :param send_msg: 发送的消息
        :return:
        """
        auto_msg = AutoMsg()
        try:
            self.__send_message(username, send_msg)
        except Exception as e:
            auto_msg.result = -1
            auto_msg.message = str(e)
            auto_msg.errcode = Wechat.__wrap_errcode(e)
        if auto_msg.result == 0:
            auto_msg.result = 1
        return auto_msg


if __name__ == '__main__':
    # 消息内容
    num = random.randint(10000, 40000)
    send_msg = f"验证码过期，请手动验证.{num}"
    chat = Wechat()
    user_name = '文件传输助手'
    info = chat.send_msg(user_name, send_msg)
    if info.result == -1:
        print(f"错误代码是：{info.errcode}，错误信息是：{info.message}")
