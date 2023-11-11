import sys
import json
import time
import secrets
import binascii
import warnings
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, wait, Future

import requests
import pandas as pd
from Crypto.Cipher import AES
from selenium import webdriver
from Crypto.Util import Padding

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


class JZSC:
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
    proxy_ip = '127.0.0.1'
    proxy_port = 33210
    _proxies = {
        "http": f"http://{proxy_ip}:{proxy_port}",
        "https": f"http://{proxy_ip}:{proxy_port}",
    }

    def __init__(self) -> None:
        self._df_results = pd.DataFrame()
        self._df_detail_results = pd.DataFrame()
        self._cookie = None
        self._region_map = dict()
        self._apt_code_map = self._get_apt_codes_map()
        # self._ips = ProxyHandler().get_latest_kdl_free_ips()

    def _get_selenium_config(self) -> webdriver.ChromeOptions:
        # 浏览器适配对象
        options = webdriver.ChromeOptions()
        # 设置无头
        # options.add_argument("--headless")
        if self._proxies:
            options.add_argument('--proxy-server={}:{}'.format(self.proxy_ip, self.proxy_port))
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
        for key in keys:
            try:
                aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
                return json.loads(Padding.unpad(aes.decrypt(binascii.a2b_base64(n)), AES.block_size).decode(encoding))
            except Exception as _:
                continue

    def _refresh_cookie(self, query_id: str) -> None:
        self._cookie = None
        options = self._get_selenium_config()
        driver = webdriver.Chrome(options)
        while True:
            try:
                driver.get(f"https://jzsc.mohurd.gov.cn/data/company/detail?id={query_id}")
                break
            except Exception as _:
                time_print("爬虫被封，请稍等...")
                time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                continue

        while not driver.execute_script("return window.localStorage.getItem(arguments[0]);", "accessToken"):
            continue
        self._cookie = driver.get_cookies()
        self._access_token = driver.execute_script(
            "return window.localStorage.getItem(arguments[0]);", "accessToken")
        with open(self._ROOT_PATH.parent.parent / 'token.txt', 'w') as f:
            f.write(self._access_token)

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

    def _clean(self, *args, **kwargs) -> None:
        NotImplementedError("必须实现_clean方法")

    def _save(self, p: Params, file_name: str = None, *args, **kwargs) -> None:
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
        with open(self._ROOT_PATH.parent / 'token.txt') as f:
            self._access_token = f.readline().strip()
        self._ROOT_PATH = self._ROOT_PATH / '建设工程企业'
        self._ROOT_PATH.mkdir(exist_ok=True)

    @staticmethod
    def _clean(df_results: pd.DataFrame) -> pd.DataFrame:
        keys = ['RN', 'QY_ID', 'QY_ORG_CODE', 'QY_NAME', 'QY_FR_NAME', 'QY_REGION', 'QY_REGION_NAME', 'OLD_CODE',
                'COLLECT_TIME', 'QY_SRC_TYPE', 'QUALIFICATION_TYPE']
        values = ['序号', '查询ID', '统一社会信用代码', '企业名称', '企业法定代表人', '区域代码', '企业注册属地', '原始代码',
                  '注册时间', '数据类型', '资质类别']
        if df_results.empty:
            df_results = pd.DataFrame(columns=keys)
        df_results['COLLECT_TIME'] = df_results['COLLECT_TIME'].apply(
            lambda x: datetime.fromtimestamp(x / 1000).strftime(TIME_FORMAT))
        columns_map = dict(zip(keys, values))
        df_results.drop(columns=['RN'], inplace=True)
        df_results.rename(columns=columns_map, inplace=True)
        df_results.drop_duplicates(inplace=True)
        return df_results[values[1:]]

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

    def _crawl(self, p: Params):
        df_results = self._opt_crawl(p)
        self._df_results = df_results

    def _save(self, p: Params, file_name: str = None, **kwargs) -> None:
        """
        保存表格数据
        :param p:
        :param file_name:
        :param kwargs:
        :return:
        """
        dir_path = self._ROOT_PATH / p.province
        dir_path.mkdir(exist_ok=True)
        if not file_name:
            file_name = f"{p.city}.xlsx"
        df_results = kwargs.pop("df_results", pd.DataFrame())
        df_results.to_excel(str((dir_path / file_name).absolute()), index=False)

    def find(self, path: Path, exists: List[str]) -> List[str]:
        for file_or_dir_name in path.iterdir():
            if file_or_dir_name.is_dir():
                self.find(file_or_dir_name, exists)
            else:
                province = file_or_dir_name.parent.name
                city = file_or_dir_name.name.split('.')[0]
                exists.append(f"{province}-{city}")
        return exists

    def get_detail(self, qy_id: str) -> Dict[str, pd.DataFrame]:
        def refresh_headers(query_id: str) -> None:
            self._refresh_cookie(query_id)
            headers.__setitem__('accessToken', self._access_token)

        def _crawl_company_detail(query_id: str) -> pd.DataFrame:
            com_detail_url = f"https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/compDetail"
            while True:
                try:
                    response = requests.get(
                        com_detail_url,
                        headers=headers,
                        params={'compId': query_id},
                        proxies=self._proxies,
                        cookies=getattr(self, 'cookies', cookies))
                    time.sleep(secrets.choice([interval // 100 for interval in range(10)]))
                    json_data = self.decrypt(response.text)
                    if json_data.get('code') == requests.codes.request_timeout and json_data.get(
                            'message') == 'token失效':
                        refresh_headers(query_id)
                        continue
                    df_cur_company = pd.DataFrame([json_data.get('data', dict()).get('compMap')])
                    df_cur_company['QY_ID'] = query_id
                    return df_cur_company
                except Exception as _:
                    time_print("爬虫被封，请稍等...")
                    time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                    continue

        def _crawl_cert_detail(query_id: str, apt_cert_nos: List[str]) -> pd.DataFrame:
            cert_url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/caCertDetail"
            params = {'qyId': query_id}
            df_cert_nos = pd.DataFrame()
            for cert_no in apt_cert_nos:
                params.__setitem__('certno', cert_no)
                while True:
                    try:
                        response = requests.get(
                            cert_url,
                            headers=headers,
                            params=params,
                            proxies=self._proxies,
                            cookies=getattr(self, 'cookies', cookies))
                        time.sleep(secrets.choice([interval // 100 for interval in range(10)]))
                        json_data = self.decrypt(response.text)
                    except Exception as _:
                        time_print("爬虫被封，请稍等...")
                        time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                        continue
                    if json_data.get('code') == requests.codes.request_timeout and json_data.get(
                            'message') == 'token失效':
                        refresh_headers(query_id)
                        continue
                    df_single_cert_no = pd.DataFrame([json_data.get('data', dict()).get('rawCaDetail', dict())])
                    df_cert_nos = pd.concat([df_cert_nos, df_single_cert_no])
                    break
            return df_cert_nos

        def _crawl_qualification(query_id: str) -> pd.DataFrame:
            page = 0
            params = {'qyId': query_id, "pg": str(page), "pgsz": "15"}
            qualification_list_url = f"https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/caDetailList"

            df_cur_company = pd.DataFrame()
            while True:
                if page > self._DATA_LIMIT // int(params.get('pgsz')):
                    time_print(f"{query_id}条件下资质的总数超过了{self._DATA_LIMIT}条")
                    break
                params.__setitem__('pg', str(page))
                try:
                    # 查询证书列表
                    response = requests.get(
                        qualification_list_url,
                        headers=headers,
                        params=params,
                        proxies=self._proxies,
                        cookies=getattr(self, 'cookies', cookies))
                    time.sleep(secrets.choice([interval // 100 for interval in range(10)]))
                    json_data = self.decrypt(response.text)
                except Exception as _:
                    time_print("爬虫被封，请稍等...")
                    time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                    continue
                if json_data.get('code') == requests.codes.request_timeout and json_data.get('message') == 'token失效':
                    refresh_headers(query_id)
                    continue
                page += 1
                df_cur_page_company = pd.DataFrame(json_data.get('data', dict()).get('pageList').get('list'))
                if df_cur_page_company.empty:
                    break
                # 查询证书详情
                apt_cert_nos = df_cur_page_company['APT_CERTNO'].unique().tolist()
                df_cert_nos = _crawl_cert_detail(query_id, apt_cert_nos)
                df_cur_page_company['QY_ID'] = query_id
                common_columns = set(df_cur_page_company.columns).intersection(df_cert_nos.columns)
                on = 'APT_CERTNO'
                df_cur_page_company = pd.merge(
                    df_cur_page_company,
                    df_cert_nos.drop(columns=common_columns.difference([on])),
                    on=on,
                    how='left'
                )
                df_cur_company = pd.concat([df_cur_company, df_cur_page_company])
            return df_cur_company

        headers = {**self._headers, 'accessToken': self._access_token, 'v': '231012'}
        cookies = {
            'Hm_lvt_b1b4b9ea61b6f1627192160766a9c55c': '1698365699,1698506447,1699107222,1699279591',
            'Hm_lpvt_b1b4b9ea61b6f1627192160766a9c55c': '1699399352',
        }
        return {
            'company_detail': _crawl_company_detail(qy_id),
            'qualification': _crawl_qualification(qy_id)
        }

    def run_detail(self, p: Params) -> None:
        """爬取详细信息"""
        file_path = self._ROOT_PATH / p.province / F"{p.city}.xlsx"
        df_raw = pd.read_excel(file_path, dtype=str)
        detail_ids = df_raw['查询ID'].unique().tolist()
        df_company = pd.DataFrame()
        df_qualification = pd.DataFrame()
        for detail_id in detail_ids:
            time_print(f"开始爬{p.province}-{p.city}-{detail_id}数据")
            detail_result = self.get_detail(query_id=detail_id)
            # 企业详情
            df_cur_company = detail_result.get('company_detail')
            df_company = pd.concat([df_cur_company, df_company])
            # 企业资质和证书详情
            df_cur_qualification = detail_result.get('qualification')
            df_qualification = pd.concat([df_cur_qualification, df_qualification])
            time_print(f"成功爬{p.province}-{p.city}-{detail_id}数据")
        with pd.ExcelWriter(file_path) as writer:
            df_raw.to_excel(writer, sheet_name="企业数据", index=False)
            df_company.to_excel(writer, sheet_name='公司详情', index=False)
            df_qualification.to_excel(writer, sheet_name='企业资质资格', index=False)

    def count(self, dir_path: Path) -> int:
        ans = 0
        for file_or_dir in dir_path.iterdir():
            if file_or_dir.is_dir():
                ans += self.count(file_or_dir)
            else:
                ans += pd.read_excel(str(file_or_dir)).shape[0]
        return ans

    def run(self, p: Params) -> None:
        time_print(f"开始爬取“{p.province}-{p.city}”的企业数据")
        df_results = self._opt_crawl(p)
        df_results = self._clean(df_results=df_results)
        self._save(p, df_results=df_results)
        time_print(f"成功爬取“{p.province}-{p.city}”的企业数据")

    def concurrent_run(self, max_workers: int = 5) -> None:

        def handle_exception(worker: Future) -> None:
            try:
                worker.result()
            except Exception as e:
                time_print(str(e))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            tasks = list()
            for province, _ in self._province_to_region_id.items():
                city_region_map = company._get_city_qy_regions_by_province(province)
                for city, region_id in city_region_map.items():
                    task = executor.submit(self.run, Params(province=province, city=city))
                    tasks.append(task)
                    task.add_done_callback(handle_exception)
            wait(tasks)

    def search(self, social_credit_code_or_company: str) -> Dict[str, pd.DataFrame]:
        params = {
            'complexname': social_credit_code_or_company,
            'pg': '0',
            'pgsz': '15',
            'total': '0',
        }
        while True:
            try:
                response = requests.get(
                    'https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list',
                    params=params,
                    headers=self._headers,
                )
                json_data = self.decrypt(response.text)
                df_enterprise_data = pd.DataFrame(json_data.get('data', dict()).get('list', list()))
                if df_enterprise_data.empty:
                    return {
                        "enterprise": df_enterprise_data,
                        "company_detail": pd.DataFrame(),
                        "qualification": pd.DataFrame()
                    }
                query_id = df_enterprise_data['QY_ID'].astype(str).unique().tolist()[0]
                df_enterprise_data['QUALIFICATION_TYPE'] = ''
                df_enterprise_data = self._clean(df_enterprise_data)
                detail = self.get_detail(query_id)
                return {"enterprise": df_enterprise_data, **detail}
            except Exception as _:
                time_print("爬虫被封, 请稍等")
                time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                continue


if __name__ == '__main__':
    company = Campany()
    print(company.search("91130300401815606Y"))
    company.concurrent_run()
