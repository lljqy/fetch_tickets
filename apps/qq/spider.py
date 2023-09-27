import re
import time
import secrets
from typing import Dict
from pathlib import Path
from datetime import datetime
from urllib.parse import urljoin

import requests
import pandas as pd
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from utils.common import time_print, BASE_DIR
from core.base_processor import BaseProcessor


class QQProcessor(BaseProcessor):

    def __init__(self, stealth_file_name: str = 'stealth.min.js', set_proxy: bool = False) -> None:
        super().__init__(stealth_file_name, set_proxy)
        self._headers = {
            'authority': 'user.qzone.qq.com',
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://user.qzone.qq.com/657484368',
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        }
        self._qq_zone_url = "https://user.qzone.qq.com"
        self._cookies = dict()
        self._gk = self.EMPTY
        self._df_result = pd.DataFrame()

    @property
    def _comment_url(self):
        return urljoin(self._qq_zone_url, 'proxy/domain/ic2.qzone.qq.com/cgi-bin/feeds/feeds_html_act_all')

    @property
    def _target_url(self):
        return urljoin(self._qq_zone_url, self._conf.get('login.target_qq'))

    def _read_config(self, config_file_path: str = str(Path(BASE_DIR) / "configs" / "qq.ini")) -> Dict[str, str]:
        return super()._read_config(config_file_path)

    def _set_cookies(self) -> None:
        for elem in self._driver.get_cookies():
            self._cookies.__setitem__(elem['name'], elem['value'])

    def _set_gk(self) -> None:
        hashes = 5381
        for letter in self._cookies.get('p_skey', self.EMPTY):
            # ord()是用来返回字符的ascii码
            hashes += (hashes << 5) + ord(letter)
        self._gk = hashes & 0x7fffffff

    def _login(self) -> None:
        cookies_dir = Path(BASE_DIR) / 'apps' / 'qq' / 'preserve'
        cookies_dir.mkdir(exist_ok=True)
        cookies_file_path = cookies_dir / 'cookies.json'
        login_url = "https://i.qq.com/"
        self._driver.get(login_url)
        if cookies_file_path.exists():
            self.add_cookies(str(cookies_file_path))
        self._driver.get(self._target_url)
        if self._driver.current_url != self._target_url:
            self._driver.delete_all_cookies()
            self._driver.get(login_url)
            self._driver.switch_to.frame('login_frame')
            self._driver.find_element(value="switcher_plogin").click()
            self._driver.find_element(value='u').send_keys(self._conf.get('login.username'))
            # 等待访问网页是否加载
            while self._driver.current_url == login_url:
                continue
            # 切换到目标网址
            self._driver.get(self._target_url)
            # 等待访问网页是否加载
            WebDriverWait(timeout=self.TIME_OUT, driver=self._driver).until(
                ec.url_to_be(self._target_url))
            cookies = self._driver.get_cookies()
            for cookie in cookies:
                # 修改domain防止再次登录的时候报错
                cookie.__setitem__('domain', '.qq.com')
                cookie.pop('sameSite', self.EMPTY)
            self.save_cookies(cookies, str(cookies_file_path))
        self._set_cookies()
        self._set_gk()
        time_print("登录成功")

    @staticmethod
    def _get_clean_results(text: str, page_size: int) -> pd.DataFrame:
        text = text.strip()
        if not text:
            return pd.DataFrame({'nick_name': list(), 'created_time': list(), 'view_times': list(), 'content': list()})

        def _fill(data_: list) -> list:
            value = data_[-1]
            if isinstance(value, int):
                value = 0
            elif isinstance(value, datetime):
                value = datetime(1970, 1, 1)
            if len(data_) < page_size:
                return data_ + [value for _ in range(page_size - len(data_))]
            return data_

        data = text.strip().replace('_Callback', '').replace("\\x22", '"').replace("\\x3C", "<").replace(
            'undefined', '')[1:-2]
        htmls = re.findall('html:(.*?),opuin', data)
        contents = _fill(
            [''.join(etree.HTML(html).xpath("//div[@class='f-info qz_info_cut']/text()")) for html in htmls])
        created_times = re.findall('abstime:\'(.*?)\',', data)
        created_times = _fill(list(map(lambda x: datetime.fromtimestamp(int(x)), created_times)))
        view_times = _fill([int(view_time) if view_time else 0 for view_time in re.findall(r'浏览(\d*)次', data)])
        nick_names = _fill(re.findall('nickname:\'(.*?)\',', data))
        return pd.DataFrame(
            {'nick_name': nick_names, 'created_time': created_times, 'view_times': view_times, 'content': contents})

    def _crawl(self, pages: int = None):
        if not pages:
            pages = int(self._conf.get("crawl_info.pages"))
        page_size = 10
        params = {
            'uin': self._conf.get('login.username'),
            'hostuin': self._conf.get('login.target_qq'),
            'scope': '0',
            'filter': 'all',
            'flag': '1',
            'refresh': '0',
            'firstGetGroup': '0',
            'mixnocache': '0',
            'scene': '0',
            'begintime': time.time(),
            'icServerTime': '',
            'start': '10',
            'count': str(page_size),
            'sidomain': 'qzonestyle.gtimg.cn',
            'useutf8': '1',
            'outputhtmlfeed': '1',
            'refer': '2',
            'r': '0.6423955438089284',
            'g_tk': [
                self._gk,
                self._gk,
            ],
        }
        for page in range(pages):
            time_print(f"开始爬取第{page}页")
            params.__setitem__('start', str(page * page_size))
            params.__setitem__('begintime', time.time())
            try:
                response = requests.get(
                    self._comment_url,
                    params=params,
                    cookies=self._cookies,
                    headers=self._headers,
                )
                if response.status_code != requests.codes.ok:
                    time_print(f"爬取第{page}页失败")
                    continue
                df_cur = self._get_clean_results(response.text, page_size)
            except Exception as _:
                time_print(f"爬取第{page}页失败")
                continue
            self._df_result = pd.concat([self._df_result, df_cur])
            time_print(f"成功爬取第{page}页")
            time.sleep(secrets.choice(list(range(3, 5))))
        self._df_result = self._df_result.drop_duplicates().sort_values(by='created_time', ascending=False)

    def _save(self, path: Path = Path(BASE_DIR) / 'apps' / 'qq' / 'data' / '合工大QQ空间说说.xlsx'):
        self._df_result.to_excel(str(path), index=False)

    def run(self, debug: bool = False) -> None:
        self._login()
        self._crawl()
        self._save()
