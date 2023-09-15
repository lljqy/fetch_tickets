import sys
import codecs
import secrets
from typing import Dict
from pathlib import Path
from configparser import ConfigParser
from abc import abstractmethod, ABCMeta

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as ec

from utils.proxy_utils import ProxyHandler
from configs.dictionaries import CONF_ITEMS
from utils.common import _time_print, BASE_DIR
from utils.exceptions import HasNotSpecifyAppNameError, AppNameNotExistsError


class BaseProcessor(metaclass=ABCMeta):
    APP_NAME = None
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
            self._proxies = ProxyHandler().get_latest_kdl_free_ips(limit=10, browser=self._conf.get('driver_name'))
        else:
            self._proxies = list()
        options = self._get_selenium_config(is_show_browser=int(self._conf.get('is_show_browser', 0)))
        # 设置diver参数
        self._driver = self.DRIVER_MAP.get(self._conf.get('driver_name'))(options)
        browser = self._conf.get('driver_name', 'chrome')
        if browser == 'chrome':
            with open(Path(BASE_DIR) / 'libs' / stealth_file_name, mode='r', encoding='utf-8') as f:
                # 移除selenium当中爬虫的特征
                self._driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': f.read()})
        else:
            self._driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self._driver.maximize_window()

    @staticmethod
    def _load_driver_path() -> None:
        drivers_path = str(Path(sys.argv[0]).parent.parent / 'drivers')
        sys.path.append(drivers_path)

    def _get_selenium_config(self, is_show_browser: int = 0) -> webdriver.ChromeOptions:
        # 浏览器适配对象
        driver_name = self._conf.get("driver_name", "edge")
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
        if not self.APP_NAME:
            raise HasNotSpecifyAppNameError("没有指定`APP_NAME`")
        _time_print("开始加载配置文件")
        cp = ConfigParser()
        try:
            cp.read_file(codecs.open(config_file_path, 'r', 'utf-8-sig'))
        except IOError as _:
            config_file_name = Path(config_file_path).name
            _time_print(f"打开配置文件失败{config_file_name}失败，请先创建一份{config_file_name}")
            sys.exit()
        conf_item = CONF_ITEMS.get(self.APP_NAME)
        if not conf_item:
            raise AppNameNotExistsError(f"`{self.APP_NAME}`不存在")
        config_dictionary = dict()
        for title, infos in conf_item.items():
            for info in infos:
                if cp.get(title, info).strip():
                    config_dictionary.__setitem__(info.strip(), cp.get(title, info).strip())
        return config_dictionary


    def exists(self, by=By.ID, value: str = '') -> bool:
        confirm_phone_func = ec.visibility_of_element_located((by, value))
        try:
            cb = confirm_phone_func(self._driver)
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
