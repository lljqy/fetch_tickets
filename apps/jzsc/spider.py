import sys
import json
import time
import secrets
import binascii
import warnings
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

warnings.filterwarnings('ignore')


@dataclass
class Params:
    province: str = None
    city: str = None
    qualification_type: str = None
    qualification_name: str = None


class JZSC():
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
    WAIT_TIME_WHEN_BE_BLOCKED = 20
    ERROR_REGION_ID = "-100"
    ERROR_QY_TYPE = "-101"
    ERROR_APT_CODE = "XXX"
    _DATA_LIMIT = 450
    _ROOT_PATH = Path(sys.argv[0]).parent / 'data'
    _ROOT_PATH.mkdir(exist_ok=True)
    _SEP = "@@"
    # 获取省市code的接口地址
    _region_code_url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/region/index"
    # 获取资质名称编码的地址
    _apt_code_url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/qualapt/aptData"
    _proxies = {
        "http": "http://127.0.0.1:33210",
        "https": "http://127.0.0.1:33210",
    }

    def __init__(self) -> None:
        self._df_results = pd.DataFrame()
        self._df_detail_results = pd.DataFrame()
        self._cookie = None
        self._region_map = dict()
        self._apt_code_map = self._get_apt_codes_map()
        # self._ips = ProxyHandler().get_latest_kdl_free_ips()
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
    def decrypt(data: str, encoding: str = 'utf-8') -> Dict[str, Dict]:
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
        if self._region_map.get(province):
            return self._region_map.get(province)
        params = {"region_id": self._get_qy_region_by_province(province)}
        while True:
            try:
                response = requests.get(self._region_code_url, headers=self._headers, params=params,
                                        proxies=self._proxies,
                                        verify=False)
                json_data = self.decrypt(response.text)
                result = {item['region_name']: item['region_id'] for item in json_data['data']}
                self._region_map.__setitem__(province, result)
                return result
            except (Exception, requests.exceptions.ConnectionError) as _:
                continue

    def _get_qy_type_by_qualification_type(self, qualification_type: str) -> str:
        return self._qualification_to_type.get(qualification_type, self.ERROR_QY_TYPE)

    def _get_apt_codes_map(self, p: Params = None) -> Dict[str, str]:
        """
        :param p:
        :return: {资质名称: 资质名称编码 + @@ + 资质类型编码, ....}
        """
        params = dict()
        if p and p.qualification_name:
            params.__setitem__("apt_root", self._qualification_to_name.get(p.qualification_name, self.ERROR_APT_CODE))
        while True:
            try:
                response = requests.get(self._apt_code_url, headers=self._headers, params=params, proxies=self._proxies,
                                        verify=False)
                json_data = self.decrypt(response.text)
                return {item['APT_CASENAME'].strip(): item['APT_CODE'].strip() + self._SEP + item['APT_TYPE'] for item
                        in
                        json_data['data']['pageList']}
            except (Exception, requests.exceptions.ConnectionError) as _:
                continue

    def _get_apt_names(self, p: Params) -> List[str]:
        apt_type = self._get_qy_type_by_qualification_type(p.qualification_type)
        if not self._apt_code_map:
            self._apt_code_map = self._get_apt_codes_map(p)
        if apt_type == self.ERROR_QY_TYPE:
            return sorted(self._apt_code_map.keys())
        return sorted(
            set([apt_name for apt_name, apt_code_and_apt_type in self._apt_code_map.items() if
                 apt_code_and_apt_type.split(self._SEP)[1] == apt_type]))

    def _get_apt_cods(self, p: Params) -> List[str]:
        apt_type = self._get_qy_type_by_qualification_type(p.qualification_type)
        if not self._apt_code_map:
            self._apt_code_map = self._get_apt_codes_map(p)
        if apt_type == self.ERROR_QY_TYPE:
            return sorted(set(
                apt_code_and_apt_type.split(self._SEP)[1]
                for apt_name, apt_code_and_apt_type in self._apt_code_map.items()))
        return sorted(
            set([apt_code_and_apt_type.split(self._SEP)[1]
                 for apt_name, apt_code_and_apt_type in self._apt_code_map.items()
                 if apt_code_and_apt_type.split(self._SEP)[1] == apt_type]))

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

    _table_url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list"

    def __init__(self) -> None:
        super().__init__()
        self._ROOT_PATH = self._ROOT_PATH / '建设工程企业'
        self._ROOT_PATH.mkdir(exist_ok=True)

    def _parse_params(self, p: Params) -> Dict[str, str]:
        params = {"pg": "0", "pgsz": "15", "total": "0"}
        if not p.province and p.city:
            raise ValueError("必须输入province参数后再输入city参数")
        if p.city:
            params.__setitem__("qy_region",
                               self._get_city_qy_regions_by_province(p.province).get(p.city, self.ERROR_REGION_ID))
        if p.qualification_type:
            params.__setitem__("qy_type", self._get_qy_type_by_qualification_type(p.qualification_type))
        if p.qualification_name:
            params.__setitem__(
                "apt_code", self._apt_code_map.get(p.qualification_name, self.ERROR_APT_CODE).split(self._SEP)[0])
        return params

    def _crawl_detail(self, detail_ids: List[str]) -> None:
        """爬取详细信息"""
        # { code: 408, message: 'token失效', success: false }
        # 企业详情
        query_id = "002105291239451309"
        com_detail_url = f"https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/compDetail"
        response = requests.get(
            com_detail_url, headers=self._headers, params={'compId': query_id}, proxies=self._proxies)
        time.sleep(secrets.choice([interval // 100 for interval in range(10)]))
        json_data = self.decrypt(response.text)

    def _get_total(self, p: Params) -> int:
        params = self._parse_params(p)
        while True:
            try:
                response = requests.get(self._table_url, headers=self._headers, params=params, proxies=self._proxies,
                                        verify=False)
                json_data = self.decrypt(response.text)
                return int(json_data.get('data', dict()).get('total', '0'))
            except (Exception, requests.exceptions.ConnectionError) as _:
                time_print("爬虫被封, 请稍等...")
                time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                continue
        return 0

    def _crawl_single(self, p: Params) -> pd.DataFrame:
        params = self._parse_params(p)
        page = 0
        df_results = pd.DataFrame()
        while True:
            if page > self._DATA_LIMIT // int(params.get('pgsz')):
                time_print(f"{p}条件下的总数超过了{self._DATA_LIMIT}条")
                break
            params.__setitem__('pg', str(page))
            try:
                response = requests.get(self._table_url, headers=self._headers, params=params, proxies=self._proxies,
                                        verify=False)
                time.sleep(secrets.choice([interval // 100 for interval in range(10)]))
                json_data = self.decrypt(response.text)
            except (Exception, requests.exceptions.ConnectionError) as _:
                # 此时爬虫被封需要等待一段时间继续爬
                time_print("爬虫被封，休息片刻...")
                time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                continue
            df_cur = pd.DataFrame(json_data.get('data', dict()).get('list', list()))
            if p.qualification_type:
                df_cur['QUALIFICATION_TYPE'] = p.qualification_type
            if df_cur.empty:
                break
            df_results = pd.concat([df_results, df_cur])
            page += 1
        return df_results

    def _opt_crawl(self, p: Params) -> pd.DataFrame:
        qualification_types = ("勘察企业", "设计企业", "建筑业企业", "监理企业")
        df_results = pd.DataFrame()
        for qualification_type in qualification_types:
            p.qualification_type = qualification_type
            total = self._get_total(p)
            if total <= self._DATA_LIMIT:
                time_print(f"无须爬取资质名称：开始爬取{p.province}-{p.city}-{p.qualification_type}的数据")
                df_cur = self._crawl_single(p)
                time_print(f"无须爬取资质名称：成功爬取{p.province}-{p.city}-{p.qualification_type}的数据")
            else:
                df_cur = pd.DataFrame()
                apt_names = self._get_apt_names(p)
                for apt_name in apt_names:
                    time_print(f"开始爬取{p.province}-{p.city}-{p.qualification_type}-{apt_name}的数据")
                    p.__setattr__("qualification_name", apt_name)
                    df_cur = pd.concat([df_cur, self._crawl_single(p)])
                    p.__setattr__("qualification_name", None)
                    time_print(f"成功爬取{p.province}-{p.city}-{p.qualification_type}-{apt_name}的数据")
            df_results = pd.concat([df_results, df_cur])
        return df_results

    def _crawl(self, p: Params) -> None:
        df_results = self._opt_crawl(p)
        self._df_results = df_results

    def _clean(self) -> None:
        keys = ['RN', 'QY_ID', 'QY_ORG_CODE', 'QY_NAME', 'QY_FR_NAME', 'QY_REGION', 'QY_REGION_NAME', 'OLD_CODE',
                'COLLECT_TIME', 'QY_SRC_TYPE', 'QUALIFICATION_TYPE']
        values = ['序号', '查询ID', '统一社会信用代码', '企业名称', '企业法定代表人', '区域代码', '企业注册属地', '原始代码',
                  '注册时间', '数据类型', '资质类别']
        if self._df_results.empty:
            self._df_results = pd.DataFrame(columns=keys)
        self._df_results['COLLECT_TIME'] = self._df_results['COLLECT_TIME'].apply(
            lambda x: datetime.fromtimestamp(x / 1000).strftime(TIME_FORMAT))
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
    exists = list()


    def find(path: Path):
        for file_or_dir_name in path.iterdir():
            if file_or_dir_name.is_dir():
                find(file_or_dir_name)
            else:
                province = file_or_dir_name.parent.name
                city = file_or_dir_name.name.split('.')[0]
                exists.append(f"{province}-{city}")


    # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包三级')条件下的总数超过了450条
    # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包二级')条件下的总数超过了450条
    # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包三级')条件下的总数超过了450条
    # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包二级')条件下的总数超过了450条
    # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑装修装饰工程专业承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包三级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包三级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑幕墙工程专业承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑装修装饰工程专业承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='消防设施工程专业承包二级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='特种工程(结构补强)专业承包不分等级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='环保工程专业承包三级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='钢结构工程专业承包三级')条件下的总数超过了450条
    # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='防水防腐保温工程专业承包二级')条件下的总数超过了450条

    # 已经爬完的 ['内蒙古', '辽宁', '吉林', '黑龙江', '北京', '天津', '河北', '山西','上海', '江苏', '浙江', '安徽', '福建', '江西', '山东',]

    # 木可 ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南']
    # 弟弟 ['湖南', '湖北', '广东', '广西', '海南', '重庆', '四川']
    # 吴炀 ['贵州', '云南', '西藏', '陕西', '甘肃']
    # 吴炀 ['青海', '宁夏', '新疆', '新疆生产建设兵团']

    provinces = [
        '河南',
        '湖南', '湖北', '广东', '广西', '海南', '重庆', '四川',
        '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '新疆生产建设兵团']
    company = Campany()
    find(company._ROOT_PATH)
    for province in provinces:
        city_region_map = company._get_city_qy_regions_by_province(province)
        for city, region_id in city_region_map.items():
            if f"{province}-{city}" in exists:
                time_print(f"{province}-{city}已经爬取过了")
                continue
            start_msg = f"开始爬取“{province}-{city}”的企业数据"
            time_print(start_msg)
            p_ = Params(province=province, city=city)
            company.run(p_)
            end_msg = f"成功爬取“{province}-{city}”的企业数据"
            time_print(end_msg)
