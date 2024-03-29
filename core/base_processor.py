import sys
import json
import codecs
import secrets
from pathlib import Path
from typing import List, Dict
from configparser import ConfigParser
from abc import abstractmethod, ABCMeta

import execjs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec

from utils.proxy_utils import ProxyHandler
from utils.common import time_print, BASE_DIR


class BaseProcessor(metaclass=ABCMeta):
    EMPTY = ''
    DRIVER_MAP = {
        'chrome': webdriver.Chrome,
        'firefox': webdriver.Firefox,
        'safari': webdriver.safari,
        'edge': webdriver.Edge
    }
    TIME_OUT = 600
    SMALL_INTERVAL = 0.05
    MIDDLE_INTERVAL = 0.3
    BIG_INTERVAL = 5
    SEP_PATTERN = r'[,，]'

    def __init__(self, stealth_file_name: str = 'stealth.min.js', set_proxy: bool = False) -> None:
        self._load_driver_path()
        self._conf = self._read_config()
        if set_proxy:
            self._proxies = ProxyHandler().get_latest_kdl_free_ips(limit=10,
                                                                   browser=self._conf.get('path_info.driver_name',
                                                                                          'edga'))
        else:
            self._proxies = list()
        options = self._get_selenium_config(is_show_browser=int(self._conf.get('login.is_show_browser', 0)))
        # 设置diver参数
        self._driver = self.DRIVER_MAP.get(self._conf.get('path_info.driver_name'))(options)
        browser = self._conf.get('path_info.driver_name', 'chrome')
        if browser == 'chrome':
            with open(Path(BASE_DIR) / 'libs' / stealth_file_name, mode='r', encoding='utf-8') as f:
                # 移除selenium当中爬虫的特征
                self._driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': f.read()})
        else:
            self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.maximize_window()

    @staticmethod
    def _load_driver_path() -> None:
        drivers_path = str(Path(sys.argv[0]).absolute().parent / 'drivers')
        sys.path.append(drivers_path)

    def _get_selenium_config(self, is_show_browser: int = 0) -> webdriver.ChromeOptions:
        # 浏览器适配对象
        driver_name = self._conf.get("path_info.driver_name", "edge")
        options = getattr(webdriver, "ChromeOptions" if driver_name == "chrome" else "EdgeOptions")()
        # 设置无头
        if is_show_browser == 0:
            options.add_argument("--headless")
        # 设置代理
        if self._proxies:
            options.add_argument(f"--proxy-server={secrets.choice(self._proxies)}")
        # 屏蔽'CHROME正受到组件控制'的提示
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 屏保保存密码提示框
        prefs = {'credentials_enable_service': False, 'profile.password_manager_enable': False}
        options.add_experimental_option('prefs', prefs)
        # 反爬虫特征处理
        options.add_argument('--disable-blink-features=AutomationControlled')
        return options

    def _read_config(self, config_file_path: str = str(Path(BASE_DIR) / "configs" / "12306.ini")) -> Dict[str, str]:
        time_print("开始加载配置文件")
        cp = ConfigParser()
        try:
            cp.read_file(codecs.open(config_file_path, 'r', 'utf-8-sig'))
        except IOError as _:
            config_file_name = Path(config_file_path).name
            time_print(f"打开配置文件失败{config_file_name}失败，请先创建一份{config_file_name}")
            sys.exit()
        config_dictionary = dict()
        for head, info_dict in cp.items():
            for attr, value in info_dict.items():
                value = value.strip()
                if value:
                    config_dictionary.__setitem__(f"{head}.{attr}", value)
        return config_dictionary

    @staticmethod
    def save_cookies(cookies: List[Dict], path: str) -> None:
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps(cookies, ensure_ascii=False))

    @staticmethod
    def load_cookies(path: str) -> List[Dict[str, str]]:
        with open(path, 'r', encoding='utf-8-sig') as f:
            cookies = json.load(f)
        return cookies

    def add_cookies(self, path: str) -> None:
        cookies = self.load_cookies(path)
        for cookie in cookies:
            self._driver.add_cookie(cookie)

    def compatible(self, by=By.ID, value: str = '') -> bool:
        """
        有些元素可能出现了，也有可能没有出现，兼容处理
        :param by:
        :param value:
        :return:
        """
        confirm = ec.visibility_of_element_located((by, value))
        try:
            cb = confirm(self._driver)
            if cb:
                cb.click()
            return True
        except NoSuchElementException as _:
            pass
        return False

    @abstractmethod
    def run(self) -> None:
        """
        执行抢票的动作，子类中一定要执行
        :return:
        """


class BaseCrawlPackageProcessor:
    EMPTY = ''

    def __init__(self, js_path: str = None) -> None:
        self._js = self._get_js(js_path) if js_path else None

    def _get_js(self, js_path: str) -> execjs.ExternalRuntime.Context:
        with open(js_path, mode='r') as f:
            js_code = execjs.compile(f.read())
        return js_code

    def deep_get(self, name: str, d: Dict) -> str:
        ans = self.EMPTY
        for k in name.split('.'):
            d = d.get(k, dict())
            if isinstance(d, dict) and not d:
                return self.EMPTY
            ans = d
        return ans
