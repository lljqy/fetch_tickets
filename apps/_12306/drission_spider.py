import os
import sys
import json
import platform
import subprocess
from pathlib import Path
from typing import Optional

import winreg
from DrissionPage import ChromiumPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError, ElementLostError

from utils.common import time_print, TIME_FORMAT, BASE_DIR

TICKET_URL = "https://kyfw.12306.cn/otn/leftTicket/init"
LOGIN_URL = "https://kyfw.12306.cn/otn/resources/login.html"
INIT_URL = "https://kyfw.12306.cn/otn/view/index.html"
BUY_URL = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
PAY_URL = "https://kyfw.12306.cn/otn/payOrder/init"
DIR_PATH = Path(__file__).parent
COOKIE_DIR = DIR_PATH / 'preserve'
COOKIE_DIR.mkdir(exist_ok=True)
COOKIE_FILE_PATH = COOKIE_DIR / 'cookies.json'
import os
os.path.abspath()

class EdgeDriverFinder:

    def __init__(self) -> None:
        self._platform = platform.system()

    @staticmethod
    def find_edge_windows() -> Optional[str]:
        """
        在 Windows 系统中通过注册表查找 Edge 浏览器的路径。
        """
        try:
            # 打开注册表键
            reg_key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\msedge.exe"
            )
            # 读取默认值（即 Edge 的路径）
            edge_path, _ = winreg.QueryValueEx(reg_key, "")
            winreg.CloseKey(reg_key)
            return edge_path
        except Exception as e:
            print(f"无法通过注册表查找 Edge 路径: {e}")
            return None

    @staticmethod
    def find_edge_macos() -> Optional[str]:
        """
        在 macOS 系统中查找 Edge 浏览器的路径。
        """
        edge_path = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        if os.path.exists(edge_path):
            return edge_path
        return None

    @staticmethod
    def find_edge_linux() -> Optional[str]:
        """
        在 Linux 系统中查找 Edge 浏览器的路径。
        """
        # 尝试常见路径
        possible_paths = [
            "/usr/bin/microsoft-edge",
            "/opt/microsoft/msedge/msedge"
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def find_edge_path(self) -> Optional[str]:
        """
        根据当前操作系统查找 Edge 浏览器的路径。
        """
        if self._platform == "Windows":
            return self.find_edge_windows()
        elif self._platform == "Darwin":  # macOS
            return self.find_edge_macos()
        elif self._platform == "Linux":
            return self.find_edge_linux()
        else:
            print(f"不支持的操作系统: {self._platform}")
            return None


class TrainSpider:

    def __init__(self, driver_type: str = "chrome") -> None:
        params = dict()
        if driver_type.lower() == "edge":
            params = {"addr_or_opts": EdgeDriverFinder().find_edge_path()}
        self._page = ChromiumPage(**params)

    @staticmethod
    def read_cookie() -> list[dict]:
        with open(COOKIE_FILE_PATH, encoding='utf-8-sig') as f:
            return json.load(f)

    @staticmethod
    def write_cookie(cookies: list[dict]) -> None:
        for cookie in cookies:
            # 修改domain防止再次登录的时候报错
            cookie.__setitem__('domain', '.12306.cn')
            cookie.pop('sameSite', "")
        with open(COOKIE_FILE_PATH, 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps(cookies, ensure_ascii=False))

    def login(self):
        time_print("开始登录")
        if COOKIE_FILE_PATH.exists():
            self._page.set.cookies(self.read_cookie())
        self._page.get(INIT_URL)
        if not self._page.url.startswith(INIT_URL):
            self._page.ele('xpath://a[text()="扫码登录"]').click()
            while not self._page.url.startswith(INIT_URL):
                continue
            self.write_cookie(self._page.cookies())
            print("执行登录流程")
        time_print("登录成功")

    def select_train(self, train_nos: list[str]):
        print("选择车次")

    def submit(self):
        pass


def open_page(url: str, driver_path: str) -> None:
    # 配置浏览器选项
    co = ChromiumOptions()

    # 设置 Edge 浏览器的路径
    co.set_browser_path(driver_path)

    # 创建 ChromiumPage 对象，并传入配置
    page = ChromiumPage(addr_or_opts=co)

    # 打开一个网页
    page.get(url)

    # 获取页面标题
    title = page.title
    print(f"页面标题: {title}")

    # 使用 XPath 获取页面上的某个元素（例如第一个 <h1> 标签）
    h1_element = page.ele('xpath://h1')
    if h1_element:
        print(f"第一个 <h1> 标签的内容: {h1_element.text}")

    # 使用 XPath 获取页面上的所有链接
    links = page.eles('xpath://a')
    for link in links:
        print(f"链接文本: {link.text}, 链接地址: {link.attr('href')}")

    # 关闭浏览器
    page.close()


def main():
    """
    主函数：查找并打印 Edge 浏览器的路径。
    """
    driver_finder = EdgeDriverFinder()
    edge_path = driver_finder.find_edge_path()
    if edge_path:
        print(f"找到 Edge 浏览器的路径: {edge_path}")
        open_page("https://www.baidu.com", edge_path)
    else:
        print("未找到 Edge 浏览器。")


if __name__ == "__main__":
    ts = TrainSpider()
    ts.login()
