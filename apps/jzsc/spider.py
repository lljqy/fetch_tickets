import sys
import json
import time
import secrets
import binascii
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from dataclasses import dataclass

import requests
import pandas as pd
from Crypto.Cipher import AES
from selenium import webdriver
from Crypto.Util import Padding
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from utils.wechat import Wechat
from utils.proxy_utils import ProxyHandler
from utils.common import TIME_FORMAT, time_print
from core.base_processor import BaseCrawlPackageProcessor


@dataclass
class Params:
    province: str = None
    city: str = None
    qualification_type: str = None
    qualification_name: str = None


class JZSC(BaseCrawlPackageProcessor):
    _headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://jzsc.mohurd.gov.cn/data/company?complexname=",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/118.0.0.0 Safari/537.36",
        "accessToken": "",
        "sec-ch-ua": "\"Chromium\";v=\"118\", \"Google Chrome\";v=\"118\", \"Not=A?Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "timeout": "30000"
    }
    _province_to_region_id = {'北京': '110000', '天津': '120000', '河北': '130000', '山西': '140000', '内蒙古': '150000',
                              '辽宁': '210000', '吉林': '220000', '黑龙江': '230000', '上海': '310000', '江苏': '320000',
                              '浙江': '330000', '安徽': '340000', '福建': '350000', '江西': '360000', '山东': '370000',
                              '河南': '410000', '湖北': '420000', '湖南': '430000', '广东': '440000', '广西': '450000',
                              '海南': '460000', '重庆': '500000', '四川': '510000', '贵州': '520000', '云南': '530000',
                              '西藏': '540000', '陕西': '610000', '甘肃': '620000', '青海': '630000', '宁夏': '640000',
                              '新疆': '650000', '新疆生产建设兵团': '660000'}
    _qualification_to_type = {
        "勘察企业": "QY_ZZ_ZZZD_003",
        "设计企业": "QY_ZZ_ZZZD_004",
        "建筑业企业": "QY_ZZ_ZZZD_001",
        "监理企业": "QY_ZZ_ZZZD_002",
        "设计与施工一体化企业": "QY_ZZ_ZZZD_005",
        "造价咨询企业": "QY_ZZ_ZZZD_007",

    }
    _qualification_to_name = {
        "工程勘察": "B",
        "工程设计": "A",
        "建筑业企业资质": "D",
        "工程监理": "E",
        "工程招标代理": "F",
        "设计与施工一体化": "C",
        "工程招架咨询": "I",
    }
    WAIT_TIME_WHEN_BE_BLOCKED = 60 * 3
    ERROR_REGION_ID = "-100"
    ERROR_QY_TYPE = "-101"
    ERROR_APT_CODE = "XXX"
    _ROOT_PATH = Path(sys.argv[0]).parent / 'data'
    _ROOT_PATH.mkdir(exist_ok=True)

    def __init__(self, js_path: str = None) -> None:
        super().__init__(js_path)
        self._df_results = pd.DataFrame()
        self._df_detail_results = pd.DataFrame()
        self._cookie = None
        self._ips = ProxyHandler().get_latest_kdl_free_ips()
        # self.refresh_cookie()

    @staticmethod
    def _get_selenium_config() -> webdriver.ChromeOptions:
        # 浏览器适配对象
        options = webdriver.EdgeOptions()
        # 设置无头
        options.add_argument("--headless")
        # 设置代理，后续完成
        # 屏蔽'CHROME正受到组件控制'的提示
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        # 屏保保存密码提示框
        prefs = {'credentials_enable_service': False, 'profile.password_manager_enable': False}
        options.add_experimental_option('prefs', prefs)
        # 反爬虫特征处理
        options.add_argument('--disable-blink-features=AutomationControlled')
        return options

    @staticmethod
    def decrypt(data: str, encoding: str = 'utf-8') -> Dict[str, object]:
        iv = bytes("0123456789ABCDEF".encode(encoding))
        keys = [bytes(key.encode(encoding)) for key in ("Dt8j9wGw%6HbxfFn", "jo8j9wGw%6HbxfFn")]
        n = binascii.b2a_base64(binascii.unhexlify(data)).decode(encoding)
        result = dict()
        for key in keys:
            try:
                aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
                result = json.loads(Padding.unpad(aes.decrypt(binascii.a2b_base64(n)), AES.block_size).decode(encoding))
            except Exception as _:
                continue
        return result

    def refresh_cookie(self):
        self._cookie = None
        options = self._get_selenium_config()
        driver = webdriver.Edge(options)
        driver.get("https://jzsc.mohurd.gov.cn/data/company/detail")
        while True:
            try:
                driver.find_element(by=By.XPATH, value='//div[@class="el-dialog__body"]/span/text()')
                self._cookie = driver.get_cookies()
                break
            except NoSuchElementException as _:
                continue

    def _get_qy_region_by_province(self, province: str) -> str:
        return self._province_to_region_id.get(province, self.ERROR_REGION_ID)

    def _get_city_qy_regions_by_province(self, province: str) -> Dict[str, str]:
        params = {"region_id": self._get_qy_region_by_province(province)}
        url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/region/index"
        response = requests.get(url, headers=self._headers, params=params)
        json_data = self._js.call('extract', response.text)
        return {item['region_name']: item['region_id'] for item in json_data['data']}

    def _get_qy_type_by_qualification_type(self, qualification_type: str) -> str:
        return self._qualification_to_type.get(qualification_type, self.ERROR_QY_TYPE)

    def _get_apt_codes(self, p: Params) -> List[str]:
        apt_type = self._get_qy_type_by_qualification_type(p.qualification_type)
        params = dict()
        if p.qualification_name:
            params.__setitem__("apt_root", self._qualification_to_name.get(p.qualification_name, self.ERROR_APT_CODE))
        url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/qualapt/aptData"
        response = requests.get(url, headers=self._headers, params=params)
        json_data = self._js.call('extract', response.text)
        if apt_type == self.ERROR_QY_TYPE:
            return sorted(set([item['APT_CODE'] for item in json_data['data']['pageList']]))
        return sorted(
            set([item['APT_CODE'].strip() for item in json_data['data']['pageList'] if item['APT_TYPE'] == apt_type]))

    def _crawl(self, p: Params) -> None:
        NotImplementedError("必须实现_crawl方法")

    def _clean(self) -> None:
        NotImplementedError("必须实现_clean方法")

    def _save(self, p: Params, file_name: str = None) -> None:
        NotImplementedError("必须实现_clean方法")

    def run(self, p: Params) -> None:
        self._crawl(p)
        self._clean()
        self._save(p)


class Campany(JZSC):
    """
      建筑建设工程企业处理类
    """

    def __init__(self, js_path: str = None) -> None:
        super().__init__(js_path)
        self._ROOT_PATH = self._ROOT_PATH / '建设工程企业'
        self._ROOT_PATH.mkdir(exist_ok=True)

    def _crawl_detail(self, detail_ids: List[str]) -> None:
        """爬取详细信息"""
        # { code: 408, message: 'token失效', success: false }

        pass

    def _crawl(self, p: Params):
        page_limit = 30
        params = {"pg": "0", "pgsz": "15", "total": "450"}
        if p.province:
            params.__setitem__("qy_region", self._get_qy_region_by_province(p.province))
        if not p.province and p.city:
            raise ValueError("必须输入province参数后再输入city参数")
        if p.city:
            params.__setitem__("qy_region",
                               self._get_city_qy_regions_by_province(p.province).get(p.city, self.ERROR_REGION_ID))
        if p.qualification_type:
            qualification_types = [self._get_qy_type_by_qualification_type(p.qualification_type)]
        else:
            qualification_types = [value for name, value in self._qualification_to_type.items() if
                                   name in ("勘察企业", "设计企业", "建筑业企业", "监理企业")]
        type_to_qualification = {value: name for name, value in self._qualification_to_type.items()}
        apt_codes = self._get_apt_codes(p)
        for qualification_type in qualification_types:
            params.__setitem__("qy_type", qualification_type)
            for apt_code in apt_codes:
                time_print(f"开始爬取{apt_code}代码的数据")
                params.__setitem__("apt_code", apt_code)
                page = 0
                while True:
                    if page >= page_limit:
                        time_print(f"只爬取了{apt_code}代码的前450条数据")
                        break
                    params.__setitem__('pg', str(page))
                    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list"
                    response = requests.get(url, headers=self._headers, params=params)
                    time.sleep(secrets.choice(list(range(2, 3))))
                    try:
                        json_data = self._js.call('extract', response.text)
                    except Exception as _:
                        # 此时爬虫被封需要等待一段时间继续爬
                        time_print("爬虫被封，休息片刻...")
                        time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                        continue
                    df_cur = pd.DataFrame(json_data.get('data', dict()).get('list', list()))
                    df_cur['QUALIFICATION_TYPE'] = type_to_qualification.get(qualification_type)
                    if df_cur.empty:
                        break
                    self._df_results = pd.concat([self._df_results, df_cur])
                    page += 1
                time_print(f"成功爬取{apt_code}代码的数据")

    def _clean(self) -> None:
        self._df_results['COLLECT_TIME'] = self._df_results['COLLECT_TIME'].apply(
            lambda x: datetime.fromtimestamp(x / 1000).strftime(TIME_FORMAT))
        keys = ['RN', 'QY_ID', 'QY_ORG_CODE', 'QY_NAME', 'QY_FR_NAME', 'QY_REGION', 'QY_REGION_NAME', 'OLD_CODE',
                'COLLECT_TIME', 'QY_SRC_TYPE', 'QUALIFICATION_TYPE']
        values = ['序号', '查询ID', '统一社会信用代码', '企业名称', '企业法定代表人', '区域代码', '企业注册属地', '原始代码',
                  '注册时间', '数据类型', '资质类别']
        columns_map = dict(zip(keys, values))
        self._df_results.drop(columns=['RN'], inplace=True)
        self._df_results.rename(columns=columns_map, inplace=True)
        self._df_results.drop_duplicates(inplace=True)
        self._df_results = self._df_results[values[1:]]

    def _save(self, p: Params, file_name: str = None) -> None:
        dir_path = self._ROOT_PATH / p.province
        dir_path.mkdir(exist_ok=True)
        if not file_name:
            file_name = f"{p.city}.xlsx"
        self._df_results.to_excel(str((dir_path / file_name).absolute()), index=False)


if __name__ == '__main__':
    chat = Wechat()
    company = Campany()
    x = company.decrypt(
        "95780ba0943730051dccb5fe3918f9fe0b265875366ec51d2bbc4ecc85d8dc5a51890bb92ed7e87c2f1058839c9031ce82e2953071eef9336e5311c9470ee19f28191d49fa180a52c2f725536bc769427f2ddca3157d0559a947b42f661af659206102689ec47f28ba74b6209a9f2e2f")
    print(x)
    # provinces = ['湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '新疆生产建设兵团']
    # for province in provinces:
    #     city_region_map = company._get_city_qy_regions_by_province(province)
    #     for city, region_id in city_region_map.items():
    #         start_msg = f"开始爬取“{province}-{city}”的企业数据"
    #         time_print(start_msg)
    #         chat.send_msg("文件传输助手", start_msg)
    #         # chat.send_msg("程文梁", start_msg)
    #         p_ = Params(province=province, city=city)
    #         company.run(p_)
    #         end_msg = f"成功爬取“{province}-{city}”的企业数据"
    #         time_print(end_msg)
    #         chat.send_msg("文件传输助手", end_msg)
    # chat.send_msg("程文梁", end_msg)
    # df = pd.read_excel('./data/湖北-黄冈.xlsx').drop(columns=['序号']).drop_duplicates().sort_values(by='注册时间', ascending=False)
    # df.to_excel('湖北-黄冈.xlsx')
