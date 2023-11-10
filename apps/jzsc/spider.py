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
        # self._apt_code_map = self._get_apt_codes_map()
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
        result = dict()
        for key in keys:
            try:
                aes = AES.new(key=key, mode=AES.MODE_CBC, iv=iv)
                result = json.loads(Padding.unpad(aes.decrypt(binascii.a2b_base64(n)), AES.block_size).decode(encoding))
            except Exception as _:
                continue
        return result

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
        with open(self._ROOT_PATH.parent / 'token.txt') as f:
            self._access_token = f.readline().strip()
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

    def run_detail(self, p: Params) -> None:
        """爬取详细信息"""

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
                    time_print(f"{p}条件下的总数超过了{self._DATA_LIMIT}条")
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
        file_path = self._ROOT_PATH / p.province / F"{p.city}.xlsx"
        df_raw = pd.read_excel(file_path, dtype=str)
        detail_ids = df_raw['查询ID'].unique().tolist()
        df_company = pd.DataFrame()
        df_qualification = pd.DataFrame()
        for detail_id in detail_ids:
            time_print(f"开始爬{p.province}-{p.city}-{detail_id}数据")
            # 企业详情
            df_cur_company = _crawl_company_detail(detail_id)
            df_company = pd.concat([df_cur_company, df_company])
            # 企业资质和证书详情
            df_cur_qualification = _crawl_qualification(detail_id)
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


if __name__ == '__main__':
    # 企业详情
    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/compDetail?compId=002105291239451309"
    data = "5588a9e126c91a28cc2f6813e3793369f7b54741889253ad1b1e7bf1f1f612a588cf4d821ba934dabddf57ce95b64cfb3421b44bbf7d4be14ddfe50218e06903d70abd8d904377acfa80b6ed1e8a2b153f47c5c68c9b5b33c3ef3eac9379ca86d1b597d4325d8417df661468080148fdb1cfb9904401ae2ed47d5ecb081461ac57373efef3e95764b10db238c9fc5ea7a96836fe088ae2079521bb4b59a9da10ec2c89ac96bc150d09131cadae9779ac64f8b8c4cbc574e5f2642a1c7b320a2d76533a06feb2d121263a51d621e318a01b6b8428bbfe5f520d918b6e38ec0d39aedab85360fb5889744ad179ec48241d3199cff96c988e161beed4dfb4661679f6fb908ad15f4e925dfdfa9058c0f25016daa9a32f0f4e3bb5e4544bfe869ab17999bbe1da233e817ac169a3a5c049062bff352f9716f50d76e51bfa439b3b643a37d23fcf20d4c90531d3596ec5149d269fef8e958347e72c185096608173cb9b35689497fa3a221215c36ee4775127e1bc3f3506fb24e1ff06fa508707309cca8855afdc2809571d3e581b6708539bb04cc257ad5cd6cfd58cf42ae447b317237e116004df3d359126d98b575df087d416c138b7078cf82a17682dfa58a966beeaa5b0cd512980c6d585e27d311711d028f2158034d064151059828c806dd2bbd2156d8d7e1be9572a93b8993825fe8a6c56e630823aba29956c93dae200b935fec363df92e9afd8984bec9d3416ca2cf0bfac5b626a732cdf13aee94d7927028ffddf95f997258bfd5e1b3b9a524fe9584e1be6cb51fceb9184e2e5a8f6d671393a97643462c0794014d188fc6ded8cf1e576ab720e4de785a460efdd519a75d1fe08561e91b8596b48df4f9f311fc39239dfa6cf49f117348da821a313aac26b66389a9c10c266f67fe361e5f4f8945724345babd0456612d1f4d483621c91ed0608c68e1b5a1465f038a7fd4a7f6c79fec745ac0e08756360e3e91076fbfd63549f9cded939efdadec9584b75e22904950489631274da78bbeaf59eb7c4f59dcfd3af2ed0ed9c3f127eda255ddfa4fb94f3adcebe5c869cc6c0992f7533d9d28cb2d4b14f8601278e4e70e7ee6ffc9a7f371540ba13786dd1ec63dd55a8b5106ea644b462bf41a767b514c13fb1e1eaa037e21bbc102558810f508a69cad6fad9c172d8d19f68430eacad15ddb31615634a6ffb92bf9f6e99b609a06c4a398fdf9dfc1a9a83b08b16f8c0df041b871bd6a9fad340265b19753e85d99b8c62056deefe6faaac72484b56a43a31b6c3514661e444b7a40f749dfd0d72b7bd7bb9b2f707786035a9d215dce9330b94429bec140ec4d86b2e0e29dbd0c6c5be2037e3bf09fa17f18e3851bf26dff57ed004bd823dc25ac481fc62ae0ddfd70b814dd19787feadd2c0a3eadaaf25231760d43208cc4fd32e05903f89bcc58eb0b833e373d8395df36318f92a30545224ee7235c533e9a403127e847ef396c06e27d50cfa0d34e670ed6761c246453ba43147419bed5c697df36b47b27b386d8c67525e7234225014b48ff271a9952ce59ac6be7003fd8919a86fc5f8eb3aec2389f4ad3f0dba0768f34518ce5d203c576dd5e12eede883681c8d48d86ecc84710bc343d4d27ab60ff5d42b9179db00cbecc7ba2fa68ad1bbae7ec8905ffce5de6362de84df8f7bce3bdb30ae68e9a1578cb1bfed285e211b7944b5362a4cef5ad42957a0908cbbd3ea7a255dbc425947093fb61ee8355d4f4fd1825feaf645c728ca59296c9f2acb08c2248e017abb6179fb0f556e1608c164ebc52b73b8a5a5d63e26c18110f361b7177ce39a2d773c8543607692e95bd2b0a83c10190868b54d1b154f2d69b245a13f5c87009d2f1fdc233f924a9dee428d58a5c91b1e59df6b27283dd1209786e6efab6337f3f1535b9b44d6c4b834829880f548727389f258caccf386ae33f783eae4bd8da5dc7e"
    x = {'code': 200, 'data': {'mcList': [],
                               'compMap': {'QY_ID': '002105291239451309', 'QY_ORG_CODE': '91610800064834709T',
                                           'OLD_CODE': '064834709', 'QY_NAME': '榆林永邦建设工程有限公司', 'QY_OLD_NAME': None,
                                           'QY_REGION': '610800', 'QY_REGION_NAME': '陕西省-榆林市', 'QY_REG_ADDR': None,
                                           'QY_ADDR': '陕西省榆林市榆阳区金沙路汇金绿园2号写字楼701室', 'QY_ZIPCODE': '719000',
                                           'QY_PARENT_COMP': None, 'QY_LSGX': None, 'QY_LSGX_NAME': None,
                                           'QY_JJXZ': '有限责任公司（自然人独资）', 'QY_JJXZ_NAME': None,
                                           'QY_GSZCLX': 'QY_ZCLX_1592', 'QY_GSZCLX_NAME': '有限责任公司（自然人独资）',
                                           'QY_REG_MONEY': 6000, 'QY_REG_CURTYPE': 'B_BZLB_001',
                                           'QY_REG_CURTYPE_NAME': '人民币', 'QY_REG_DATE': None, 'QY_FR_NAME': '马拴柱',
                                           'QY_FR_CARDTYPE': None, 'QY_FR_CARDTYPE_NAME': None, 'QY_FR_CARDNO': None,
                                           'QY_OFFICE_TEL': '13892227728', 'QY_OFFICE_FAX': None, 'QY_LXR': None,
                                           'QY_LXR_TEL': '13892227728', 'QY_LXR_MOBILE': None, 'QY_LXR_EMAIL': None,
                                           'QY_BAK_LXR': None, 'QY_BAK_LXR_MOBLIE': None, 'QY_BAK_LXR_EMAIL': None,
                                           'QY_WEBSITE': None, 'QY_JY_STATUS': '1', 'QY_JY_STATUS_NAME': '正常',
                                           'QY_REMARK': None, 'QY_TYPE': 'QY_ZZ_ZZZD_001', 'QY_TYPE_NAME': '建筑业企业资质',
                                           'COLLECT_TIME': 1622263196000, 'COLLECT_SOURCE': 'ZS#680832',
                                           'QY_YYZZH': '91610800064834709T', 'QY_SRC_TYPE': '0', 'ZJ_GOVNUM': None,
                                           'ADMINAREANUM': '610802', 'REGION_FULLNAME_NEW': '陕西省-榆林市-榆阳区',
                                           'IS_FAKE': 0}}, 'message': '', 'success': True}

    # 证书信息 + 企业资质资格
    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/caDetailList?qyId=002105291241564845&pg=0&pgsz=15"
    w = {'code': 200, 'data': {'orderStr': 'apt_certno asc, apt_id', 'pageSize': 25,
                               'pageList': {'total': 10, 'pageSize': 15, 'list': [
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '市政公用工程施工总承包二级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1488470400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '陕西省住房和城乡建设厅',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203220822011', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D110B',
                                    'COLLECT_SOURCE': 'ZS##D261047095', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798740000, 'RN': 1, 'APT_CERTNO': 'D261047095'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '建筑工程施工总承包二级', 'QY_NAME': '榆林永邦建设工程有限公司', 'APT_GET_DATE': 1488470400000,
                                    'APT_GET_TYPE': 'QY_ZZ_QDFS_001', 'APT_TYPE_NAME': '建筑业企业资质',
                                    'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限', 'APT_STATUS_NAME': '有效',
                                    'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '陕西省住房和城乡建设厅', 'APT_LIMIT_CONTENT': None,
                                    'APT_EDATE': 1703952000000, 'APT_ID': '221223203220822012',
                                    'APT_TYPE': 'QY_ZZ_ZZZD_001', 'APT_GRANT_UNITID': None,
                                    'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D101B',
                                    'COLLECT_SOURCE': 'ZS##D261047095', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798740000, 'RN': 2, 'APT_CERTNO': 'D261047095'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '建筑装修装饰工程专业承包二级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1523462400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203344899636', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D211B',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 3, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '防水防腐保温工程专业承包二级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1523462400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203344899637', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D206B',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 4, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '环保工程专业承包三级', 'QY_NAME': '榆林永邦建设工程有限公司', 'APT_GET_DATE': 1523462400000,
                                    'APT_GET_TYPE': 'QY_ZZ_QDFS_001', 'APT_TYPE_NAME': '建筑业企业资质',
                                    'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限', 'APT_STATUS_NAME': '有效',
                                    'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局', 'APT_LIMIT_CONTENT': None,
                                    'APT_EDATE': 1703952000000, 'APT_ID': '221223203344899638',
                                    'APT_TYPE': 'QY_ZZ_ZZZD_001', 'APT_GRANT_UNITID': None,
                                    'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D235C',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 5, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '水利水电工程施工总承包三级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1523462400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203344899639', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D105C',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 6, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '古建筑工程专业承包三级', 'QY_NAME': '榆林永邦建设工程有限公司', 'APT_GET_DATE': 1523462400000,
                                    'APT_GET_TYPE': 'QY_ZZ_QDFS_001', 'APT_TYPE_NAME': '建筑业企业资质',
                                    'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限', 'APT_STATUS_NAME': '有效',
                                    'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局', 'APT_LIMIT_CONTENT': None,
                                    'APT_EDATE': 1703952000000, 'APT_ID': '221223203344899640',
                                    'APT_TYPE': 'QY_ZZ_ZZZD_001', 'APT_GRANT_UNITID': None,
                                    'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D214C',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 7, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '钢结构工程专业承包三级', 'QY_NAME': '榆林永邦建设工程有限公司', 'APT_GET_DATE': 1523462400000,
                                    'APT_GET_TYPE': 'QY_ZZ_QDFS_001', 'APT_TYPE_NAME': '建筑业企业资质',
                                    'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限', 'APT_STATUS_NAME': '有效',
                                    'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局', 'APT_LIMIT_CONTENT': None,
                                    'APT_EDATE': 1703952000000, 'APT_ID': '221223203344899641',
                                    'APT_TYPE': 'QY_ZZ_ZZZD_001', 'APT_GRANT_UNITID': None,
                                    'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D209C',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 8, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '城市及道路照明工程专业承包三级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1523462400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203344899642', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D215C',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 9, 'APT_CERTNO': 'D361094546'},
                                   {'QY_ID': '002105291239451309', 'QY_SRC_TYPE': '0', 'IS_LIMIT': '0',
                                    'APT_NAME': '建筑幕墙工程专业承包二级', 'QY_NAME': '榆林永邦建设工程有限公司',
                                    'APT_GET_DATE': 1523462400000, 'APT_GET_TYPE': 'QY_ZZ_QDFS_001',
                                    'APT_TYPE_NAME': '建筑业企业资质', 'APT_STATUS': 'B_ZGZT_001', 'IS_LIMIT_NAME': '不受限',
                                    'APT_STATUS_NAME': '有效', 'OLD_CODE': '064834709', 'APT_GRANT_UNIT': '榆林市城乡建设规划局',
                                    'APT_LIMIT_CONTENT': None, 'APT_EDATE': 1703952000000,
                                    'APT_ID': '221223203344899643', 'APT_TYPE': 'QY_ZZ_ZZZD_001',
                                    'APT_GRANT_UNITID': None, 'QY_ORG_CODE': '91610800064834709T', 'APT_CODE': 'D213B',
                                    'COLLECT_SOURCE': 'ZS##D361094546', 'APT_GET_TYPE_NAME': '申请',
                                    'COLLECT_TIME': 1671798824000, 'RN': 10, 'APT_CERTNO': 'D361094546'}],
                                            'pageNum': 0}}, 'message': '', 'success': True}
    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/caCertDetail?qyId=002105291239451309&certno=D261047095"
    data = "5588a9e126c91a28cc2f6813e37933695200acf48c974f58b6a551d08a5efbb212d9653f977f6d2b4ad915e7104d9f9aca86f905955999145581c45fefa6aa4f2993e0d4636243c14f784270d293019c9326ef89c7d18633451a8a403241f54fce33bf6b4581c3918f7e24706ad7fd98dd2ffcf3e264a3ea92d5f59eaa7c71cef24b190c3278873398002111b88a82f519c758307f1eff414eeb686f0386d8647eab0e4c08fab0ee9a9c52d162fce729e7fd614610f39f455d67659f0b39742ab911073ba0a748ce793ba3785d2019c8052945233278e2495eaf8b033ce7a70f8d5dd59bd0510ddd2cb49f4ff9e33c9432fa7ceb02077189b0e1136bbaeba9e4a67365a66a81fcd2efa9ec6c48a06e4d0641f37db8dbf45c3808ae802643e0381809655043072bc38bae30f54e6361131f9ba5ee91653134815f61ba534689e02b2f96227db635fd081af572a9dd4b898eb2e92bd8505796cc196a43cef8b5533c1d6ef6f24703280780ea97555e53e3f194c434756370eaf88dc24ffb9c5ef5478bd69986941dd6c020784b2e921b7c26fe6c0104266c3cef2acf74f3dc9c6a9773aa8c7064e1f741b70073ce6f8f6f428b900174d6ed4b19c2c4258d1c1a6c4fe36e6f963ecd690b40bcf37fa02ee35f1f461753287b094d72f71495d781411282738f8ece8c4a4ec928e77623791ff70524020a67da86a1698ea9052f372ba0939893f6f958b1018ad91692601d3ec3409cb3e6170b24ae6678dbb37d0a290fa0c3f6c71af979efd5a56b170328a4fde874b09eca8b282afe6dccea0b0e470d05c6dc5b91c83dbbeb45fc59c1bca7a3784c5165a7794a419995dee826a8d04821ad12ff3c32a2836aa0c7ca0a96fcf326cf45fb5112ae031e571e35a3c519d44d3feac018d17179070f9f4e423d9aae09de559cea7a138446c134d97530d693e4ceb29cd814e3e5b961a5f2d3291493cdf2895dca0d2efd22c93540272b521f67441c647b36965b8c187345c6b8194362d3deea1ef6e50b8b96b5ba789b42435cf75abcef88a467400228a972124e5c7bbf982dfe23245dd3e8797495b9858a5835e148baf85aaf7f535118564d36bb17010fe58534085237959bd1ed8c11cf9343c2189185721abee8040c7c428297d31e7fda1af807251b4cc8b3549aec5335ca1ebbf74d63aec07a9e2d7fd0c866305a480e5531d12e95acb91583c0150bee40bba62fb1f29a3b4260b06074beac0b36a80213686c0ec059aae76d0d361f25489039102d7c7f5b83768e3e1ec20237347d3e4215f57602293abc2e0eb76ef04215f70d5205c5c300b76ff9dea2f7d6d2987e9f5e15e828381cd21207864ff3303aa20cf7a36060638c5aff10dc60edc0e442cb905fe94e05b9d47dd4911d195a66947ff7d19b1ef01f69c73d9d8415af4143f3a95ef75739045861b6660682b5beca57ff75148a7d5db6f89b3ca86356c8a3a21a0a777c920bf1753c2ef1b8a2f71bef2ada18df546ffad6b062b9797a45b41af88dcda2ab7289d3f115b2b5746d326eb99f22ef21981a4fcd4024657313b52e2b4b772333c3a62e563fca93b8100caac8c168642b4f8e9ed04f120948fb9d6d66a1c42604d46af0b75a00388049ad6bf7d1ad987d3790904a0ba95937402be9672364000188086c012eee7d56ff22c30cc27c2f2d42f8c9c38f321f614f05f42af84afa4927afae96b8c118a67c159e8984be0584b9e3834f9c0aa6f3a2b5f42caf3a3c74f1bdc4f0b984729727b0ce6bd03bcea2ad0cc09103a0cd3dbd32028a2be19dce21eaad0036b92aacff6ac7abf7fa1b389b144d99950004d273152d75647fd71c60d48c0f132e22b30e73f51278c09a8fc4cbcb83cc5dec4ba23e23f98c723b56d0f702a90eed98db54becaa87185007c8e420bd6c1ddb8e4d2613714ce69d14142a595e83ebf4d85f3b35fe1fa3da0bdc7ac87a2f40c76dcd41e6a21b3bfd55e376f8b46c822771793991047a52b42320f1520393c9587bb092cec4fd160d902d1062d35764a476b2527c625b500edbf089569b1f3c7673703361aa02065564e50cd41a4f2a8a19cfbe955cb17e496e32778e872fbc0b10b356490f6a0378e89d308768887bec246232ff38769f5adf444b2af195b98e1ae8e2fe8f91ff0450a8447b067eeacbd8195456b53828d8cf4d70df12e4b41f1ccb1d30f82d093033f044a54ec2d199e590469a05723a18f628887687db3da06c98244784fa54d4b2d4c00830fcdb19698b44da00582bb66e83602d82c35ca7cc794cca29c868a703ccc59711b031096dc4029e5fef4525773168188c1d491f25e09bf93cdd79b6ababe87dc760298b9ed3b0c6dd3498b7e850a5d6180eeb157ffb4ec26f83dc4207fed2cdd4c391063f4f36079fdb0c72332224187a99dbc8b3c6c93b668456c771b5d673790f5cccf4d3df3bfb95d3bc936f4a26f2c398570818229f1be4293920da9b2647958e86234cf7a8873a76929ca41c5b5f9191b11263c219ddcc54ec9f99185fea086c13435c1ff430cad75e8a3f22dd47e7f62b77bb4f7758ef5b4a0297fe294049c05c3d184f1492c781fd8184f940865f246062d3446334504f68cea340fe9c41525449e1590db272223855fc441fb86227cf9c595655a919719984c2206be6d8250fa67fe2fb9649cc080c568efe0fed75f5356e652b257e7a5de55cba1837e810a06b452ef415f063ed614dbab0722e41f8094fe995c08dfca19aca6d8cfab424327f2240b82a40e2e26220aecb9ef19ed406c0272c37cdf9a13dbee53e99d36b2f8534749de1e77f44341c21bac85aab11e18d375969bd333f2a31a92e88439a25fdcca99be9b01d965f2d447adc580aa9c6f89987cedea7bd4881a21f710e64d30b72e97128e44bde546f7e37ed09ffb344ab47698293f6b87fd7526e6a15154b819f7d032e93be3cfa1be7f444de1cf0727ccab910bf5de6880aed48f5d396efc0008f43e5c6c1c202c7218a5db081874218ce5ea8ad788c6b17e830207ffda64ba30558104688c7cf7eb70e9be1dbd11e5b1ec6575a18788d045906cd57ea94f2f49665af90eed383544051b0d59b740366f344f159461e2aaa2e1190c26aa01f185a0dbcef5db8b9b3412f2e4d10455e8d0ac08075fd930518c2f07cc0ebe38c8eff79a3f7dbe4fb584588a50dead6a766d185f87ed2d139f545d4fdf0cdf74ba68408d3cfd1d152b8542e234f75b7d6af6b5f458bb7d3aaf33a3774d4af81e2f63454138509a649dad28abd0ceb5b8828cdf338d91b63ae154a5a60ac273946b62d378cb3e252330885c8269a321542ecda74ac00946fa9b33406ebd4de5f2b9330d4563b75c3fcac0b359c2f790d7d4e329be7f2b8b8feecd024dfb1fa691ee4a1e7f8acb59c356902ac81ef667d7e5cbb84739c31e8fffc3550a459f7c2aa26c29387d64091817edc59fd163236aeb796f9256cc5e34d3e1401f4ebdbc2662a8bef4ba265b50805f4f2822c4682c48640b2493c96efa85bc39b5f47129d17e01d67dae89a8ddf7c04befb25e42b8452425e4f064328e74e6f7581c4dfc594705ad1069b9faefc7c2c2bb4a95f01e9d6f2ed3f03a3352eea0fcaa1279ec4bc16dba7b509b0837ec6c3958893a789b23eeb57aba54262122f26f5a335737db02e19ee49904d4aece7370a3c1b58172b75f4663436000e3f26ac6831c0b0418e5a96a7c52ffa42fe9c0745cec2ac9ea98093cd43f61d787c00bd681814b49d346570500b1fefe5b3cd4be4b81fe1d69b85cfde77a8e2413c7dd0d1a91d8de5223e30c4822e5f49861cbf6e24874d593dad9fbc1d7617a168027d81d476739f8e107d88e978a39fc31e3917a8e1033008d11e47ca4fd6235ea1a6c57eed064193a3ed649045376aa2017a9a431452daf510a87fc38dbe50b5b43706b09cda270686cf4098c423d1657984ab561dbf2119c700243cbd719f78a35e81b785de54868353b3395aaefc958552bea66186164640d5443397757522e3fd2adae0b0119bf92d7c215e5cf00e6cb288046b35f40969e5ab51943843071c02ffb196d960aeacd3e2f21b25b3166a1034c8211efe910918ecc2d0a52ede42ed3353aab6df7c383e99e806a9b45cff41ad577e987358a45023771366b6d6062e40f2a1cff4d288692abc5a66defbab36d5dc5a41e915689adef3da5d3683157c5d758dfe4dbeb57b7d71ad8e30b066d7ff73e02d7d5b5cc6a5e77ee64dea7dacd1edf78aee596fe5f1fac9c29a060580c8ca9b7017ca50be325834c1b3bc100e483b92af94f239d7e900c776e62a5e4f18a0a41bafd84e95abb80dd8488a008fa4caec85fbfd43fd4cfeac4013f07e48079866e6977be7f57de98e47d326851a5cda498d918bd95e8ac4e854c068effd36faf62f8123ca17f6532d06b7ea1301e7287c3e7f4f367730425db49d62d2f7d8914f8d60c89fb2d19a5b04fc13758ccf4ef2c50b1f292e9f4ae6b1285493f403bd7ad28cfd9f76d79769420b05246c470e846ea373a916775793c8065819af49970fa42a72758ee279bc1b807c71f86d1c722f7ccd0fdc23c59dd2e80b40bb2eb674197827cc7f1461c19c2f7ab47bd9e61d40353f2a894d296a462d2c1016ff2812f3cb3bb8cca8468ae0eb3169765195cf0c328d802344a0aaf7a5f055ebf7471025a99b661bd68fba33714de0956d5a3db91b9679b305e44e0223ba9f1599c329aacdcf63d6929671348543693fed40634201ce047dfa1c839b80a55dacd0b296e9ee5a780b568cc3ad1bea3988eb65d0c999203dd3231d2314cc9b77c0986684d47a306e91ec4867f45808d6f3b0b6c19db369a20c7bff2ac8b043198dcaad7cc3c3b984a541e2527b9bdb5eb08819ee5bb21ac764b4ab18a6620936733f5e03334b7cab69642582815203d7918b5de72e717c17b47f4b5a324c78cc067381943f067eed01aae40446deae56796f160b46549f0c90b51814d95729075c9f09d7e6cfcd966ad55167248e27bccbc934a59979caa4ae5441aeb10681ce663d5850dcb52a75e3a1230497c587aeecec38891c4a572e4e601094f1239afe5e716ba8d6bae393f6e02be9a2333cef786d30ef66d5ee2b8b3abaefe3cf7b28ca6a5ef556db634fb44c60ee6bf3d37eb96f3e8baf60b84d17f892d51a5f24ca645d5c3e02e9fe4253c2437bbe684ed0755018d280316ece893da0092d054c9cda7108fd491bfed26805ef13cc8e71896fccd557322f0fd608f8728aa1c8786f3f1846cf93f98f33580bd37f69deb60b7e2b7d18b4b267e43a0f2d6bcb242b3b4786e2a50cded2348bd61e1f335d3cedf2ed4c2694c179dd947cc5aff8284917296a44d6f483c1711be0f09a79df8ce0697766ebc8e565553dd14e0933d84ff5f5c40170305370250f87961914a5bfade1f54626d2c61737566aacaab4bfd188fc5dbd4e7b83c7a7e86193141bc73e4f78a442da664a7a58c0d1a3cf1c47ecda8e126a803866ae990bcc21fe359ff4ce2f74fbec9c053379b60e78a9d375504c334183a5f4a4c27c39ebd0a3510703cc848aec261b757ef072aed07e0dff106370cc2d87691539f449d9c5882bd2c309a113fd5763aa2fd78d20eadd4a0c7decd3afe8013799aa583536b1c2545d56303ef24da59e0f31e5849b6cf85d453cbc5642b1cee1ca213071526864f3b9cb65f65b98937b4e7ef92f5f68d3228af9e3791143c354334002c98a5959f274e64a30b006b38fbf10326a0638399ddd59f5ba024b6a8d2eaa710bd977f840072269ec863467f3301cb0eaa8f4ecb13336517608e2b3cccce9b877982256b9e68c5f6984bb60834d46b1e88b7aeab68cedc19c5bc0a91507dc4381c53aee40bf59cfdefcc0b98ac40adb87036ced2f8076f4dd03d90c8e604b411619304b92dc4de095b560cce39587d9fcb109f3a1d84a65c88a17d5976621a1b6a1d572b1701e6659d14f53eae0ced86d4932d2d56eec90edd3c60e2bc3c99dda2d0d1c88e31fb52541a5830cf8350f63e2368cf18202337390ac4f32b5ba81c9ce5528266a8494aae71e3b6c76b2117afa86902a249baa0070d1105ad7b8da14fa0ac83043a73842408628969d9625c310e1d114b5eeece3fed89312fed01c5af37ff300be2a6b070c60add8f61a078a749a568f9f0717680a4f9494d8b7ed8716e988b0a3de8835c56f0817172231e786a94110664e73430dabef5c2aa946c71735aff888eda7dd3d898506fcffc3935d724eafed998d41e6e2d82b043908ade104cf4b117331b9e6f6124b1ede3e3923789bcef2b360428c08d2ac4a17bf2163e925e15f59e2037fc41fb45169004eee81b05d623224e1c11df5fbb980065071062be0be5e2078425aeeac23100504336dce981181a7daa43ab9e9848656133ce5cc7cde0befeab88ade6b432495dd3a544850d8ec3f7a71a92d5c9310f0d33a5ec9f72ef2efa21511d303444a3b79e5b2bbc35309652e21bb4ebb4c49e97a0e8c01f9b2001d4535f170a1bad9834c4bce399e857f6ad4d62bf6bbed2b40145efc3b9a36db494df6760ab1c69de9e21f36760e15229996de33b114b92e5303cd1e7e66209912ce9c61573144ff3dc4ba0b5aacbd8a1a789524c9736fdc5bf64c5f24030c5aafaf0937cd08af9aa53870465d9b8b9348449a9f2d68716cffab093c2737f0e192339e87c91505ec083838c5258e2792e1bc8193bd08280c28f3207a91d1e8539c76ca972f309343815bdbdbc191d31d9c029482a5fc230b79863e2cc459732c64aea70c8163505ced4e50fbcc3ab72ebbff0727eeebd6a390795d5170d54f2cc0e2ecd867fc41994dfda977dd78dc98bff4d33c20374c6b28317ba31f5853eebed9cfd8b141ec4be8b1c23619c91546b873ac22fc724165cda7ae0f7ffc89e48a71cec7c41c29b6937197cf192638962571f46c1853d790c6a4cb8425cd1f5b451304586f8f99c18bae5e6b5715cbb5b913c083ee770dc88abe30716baa1c32ac413b0a05a51a4ef8ab9474046d9be1df2a22124d2df632667fe3545715067587275bc4d600e353fa74dd14fb51d7f706526ea0f383a5c5498718a0f43bb7a4922878434bcc7fa8e7e7d21cb995733a634c041d86682c72571ccc505be77d732d661297268b904f5c7fb024948379d3e87e4c90037a3f9c4b76ca0e8401b1ecdf15c94f86852a43a348733f89c2a3a720c6a2b4b871abc3a1080a848555cebac129508778378ecc484a0ac7ae75a652549efd39b9263150592d170343bef62bef3703183a5dd0f0ef76f8e96eda770034fec8c80cbfa5773d42d16d94832296786d52341848c2374d5cd575d49a28724aa0b2535dc119860e385a79961c35ae7dc881a0e5a527b13bbaa6652e8c489f6a61e583ebdd7acfceb136ab0ad8effa862c8c4967d0fe9576d22fc5ee237a96ae6406af4730ceb6f4511d3f1044385256becdf321db393dbb5e719a08e8c0b58c1f450580826cd662851b32b2ed1d8eb6ea71aaedc167123873b27ac41c6713d68c5859969cdf7363327181ca936b3890564bdd74765a562602864a83538b5295aaf88aeb20333eb99bc945678fc5296ec2a0b68ca26dc6739fa1e4d07cf39d636a1a0decd2184d27552c3c507e8e579d769ee609dff5ef2bfe031818b8e33cfb6f56a9a9a48ac5bfb0b2cd3d905288c6f77148551f26d4faebdf3bc3e2dec521c3406c0e46afcd2c621d4c83c745e9bccf3a2afd3fd62e478525b9338f2dac5054b8687a2cbb07cb4429eaa0032ff83cf0d1767b01b12cfca9d5d0a35b0df86dc4e209021ef84625858e9ad3fb46b23f1fab4d0c6030386b5e528fad2a3bc59b9e15d5fe7200b1fb88c8dc4b593b74a20498fae242444e507dd673e34baff458a543dd087ef5317e1eb0328f1cb9c0942d7a11bac2cf14bec910bb6588874cc706796616a0aeff2e001eeaa2442f0498308f569267b8503e309b2ef964f36eb1983b057b930cb3026a61ca718c067192b998c829f538dd5c7b8a263d92c9d9b53b953cce3233060b2982d943f428510df7f84f290b225ab02aebc7301115432cab5a8ffbdd7cfb7d3dc069c25df53851fcd5401a763d82ec233f4690f152b8cc4b5a2819010bbff3faf21c3dd869d297e5297b13345c9771d40c100452767e42fe67f57667c65a34197688410e470cc8cb9676d5fe5ede9f41e757ce1bc86457606b7ad8ebe2dd1e2cce4123e21479da8a5c13b7af7d041a21678bdf69628dce876cb3220944704b59966446fd7dfcb95acef5ad12f7b87c262bef3b9fca7dc205e618806b4bdc9dd0bfd4452da0dfacdb7e19cbd4e993fa9acec86b46304635754089367dc00b8c983b29312d28113c4ce79681d95bf1887892321413583f9582c42279bc08f5eba35c4da3656e7707e10ccfdd195832bb5d83b6ef126832404402010865839dd2f6268d51754cfe854a56925860f9ef6f8a116b1ead14d4778485155e4070ba2dc71fae663132435d385a81010ac776828b7227d0b388ded48a659ae231b6455c9fb999f1981d236134ee2169d864624e8aaa6520315202f328e984cca8f05ba16940bbcd96758fe1718b70748ada79794c8828f9216d77c6cce049824292775a6697da2f2b8d33e334ce49ca6620e87b598fa9c87c04a86ea5a78d21f070742a22892983c65c85a295b32ad938ae9fd4ce2713db398dae20db54414af2a31e7858f0769a85944dd0d53cb7d44aef5c5c56ea6931e5e73fbe9369f60293c8ad2f7d134bf59e3d26393155669dd956ce3720a4e2fcbd26999ca0334c42a2c5f066da3429ffb984fcc8d12806fe805659255345fbdb17362d445f6760227496ab87eb1f9ee35932c7f0ca6fc59a5ff14693f296972e70b18eb0cd5d6dad3c9a0bdb0311b3bcdf93d40d7ab56ec71bab333bef627a5b58430673e65cf8638972f8e2d1c21d137080dc2044a975ad0bd8d772a527f6531600a11bb8402a6ee307ffb7ba95b285df54b6764f0fac1230dee51636f6f43827065f8b4824be3e44e189cb63c669896070a42329ac0348e0631f055b735265596332c6924552bf564ec12e7858b8451daf7c706c7eb61b80cd5bbc0a7ed9a4e47ab0622218c241270bbbb2f38e05e4f07b2cbccebca897c743897ff27b35bdf45815850c45474c1d44833f6fa2d98c9848573886eecb48e82d97adb8499f0fef082019a2a72991ee203c395adaa2588953886e04e77f537fe40441fe6d7c4bb43d8ef6c628835cfa276c48ee71d28a99db046d5c90c6bcb30d7cdae4dc827ed1822baff28bacf169b354c99a66274b721be14564e72aa0d688054af2f76b9bc488436532ed00bcb2f5c8eaafff4c80f6db5971052b01c9f1e7eb1efbfbc12a630756163c845a8f5d62ea581bb54b11bfae9e217d7b7cc3e748702ec8d705558863bdefeb9aef1c079f66a8cb2386780598decdd41a36a58554b9e813c6c7b7659cea702e0018dfc8f798d0c1a1e11e5dd92e9628d5d894cc5ad761ea8c6c4940cfaf74bae84f10c87c078d2ef9f26a9fad2b72e974aeaf79d943ef2f1446700631fbde5bb980de514760aed5bb4bbcb202fa25ace700ccf9785cb6bea37127e51135c941e16bbbafdeb3da5abe650ed3df4a747fc7f2739262e63aadc7a22a9cfcefb6ebd80f01ed1adcad7b835647ed499f115f1a73b928f79b9cb38022cc07757a7612dc7734c82a1cef464424f90fbc8e9283019718a53f9b4c36ec10a1e6b00ad6f3583fcf1458b298a77a3bebe6b3e83a8781792b8c0a6f61fa8a422389fd232fa7747b25f0e5db5ad11683c04350e020d7963474811ecd2f5c5a69ce846e1ab5eb09397c1ca529d9acbb7d982cd2a5200f636f49b817fbf1fc51a0a92def7a59ad2b12a9650f0c257d421498c24b9e96237e6a60cc080adb44ac6153d66328a6638c9a11a1ff515285aea2bb0c2f81e7b8286c6ba0993e0e52ec1f21d396ada97b94f992597526e54e1ca22dc503ef9217cfed18b68de2475f5634730497061bf8bf62896a72f8d22ae13535ecb05c3d2c09842e48bee3c6c74136386f7232df049cbb06670882b18e692ab5b8d88343d47f9ad41abe5b6555483fe3b33ff7fcedbb0c9b4fe10de4f1e6f63c8fc3cba60b5f887d45708def81328ccd8a69898a3f2d0ad0c08c3ae2a3ec4307f4665893dcbf9a8acc8f0ad81ddd3114862feb2c48919a429887ed072630f20b33bb7967afa7de75760fd650e2630f7be03067124103b7b41f2ba5858454a5e2a8fac12e78cbfe5adc2335d58bad2c408c77e393d2788cc9e93e244cb8da7c6b7b3e53c5faa009f1c93d939e911b247523e2affa9b68af1437ec306d29c56acd92336b6626c5571c923d288379b1132e04417c9ca115c4d01a688f4982649ccc5b0fe712a4727d1eda16242554e80484e44d62d934eeafeb7ef121a369ae8d34f0d8e66fc3ef4e20e8f8ca377744075679cbb6b967fd48d3c397cb5ea4f8c4158272575501501d0bce4331053832d2977a478890de36cec37d6eb9a0308c09138c068f598d88d0bb5b901d355280145d268c2c452eb12de404418ff7c1328c9dac27b5650ff4c615c"
    y = {'code': 200, 'data': {
        'rawCaDetail': {'APT_CERTNO': 'D261047095', 'APT_TYPE': 'QY_ZZ_ZZZD_001', 'APT_QYMC': '榆林永邦建设工程有限公司',
                        'APT_QY_ID': '002105291239451309', 'APT_GRANT_UNIT': '陕西省住房和城乡建设厅',
                        'APT_GRANT_DATE': 1488470400000, 'APT_EDATE': 1703952000000,
                        'APT_BOUND_PRINT': '市政公用工程施工总承包贰级,建筑工程施工总承包贰级', 'APT_MARK': '-', 'APT_CHILDMARK': None,
                        'FBPRINTNUMBER': '04709', 'QRCODE': '9EB94E5AD8824138A78412477B6EC170',
                        'FBQRCODE': '9EB94E5AD8824138A78412477B6EC170', 'APT_QY_GSZCLX': 'QY_ZCLX_1592',
                        'APT_QY_REG_MONEY': 6000, 'APT_QY_FR_NAME': '马拴柱',
                        'APT_QY_REG_ADDR': '陕西省榆林市榆阳区金沙路汇金绿园2号写字楼701室', 'APT_QY_REG_CURTYPE': None,
                        'APT_TYPE_NAME': '建筑业企业资质'}}, 'message': '', 'success': True}

    # 人员信息
    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/regStaffList?qyId=002105291239451309&pg=0&pgsz=15"
    data = "5588a9e126c91a28cc2f6813e3793369972d9835598457b59835c82a79d79a6ff42f3519edc90e53d800338fb19e508aa44796bbffec1a11e556647c17f703d0c665408dd2c00ac11e36010c30ee4f5564288b2f19eaa346c42012397b6f3d06b32c6c1ad3318215a142a84e8739c78b8955834824024bef7f8e9003eb9cc5de45e66d9a9735ced73e8143c99c723623356f1af45429882e4d9bee937c9ab7f1481b0523cd7007743e8d4dd52658053001f99b21e81fc831168fb2132bb2a6313e37cf284c837f63799367868bb5a1c03bd3a3e0a9a1b70fd60ac59765cd98c9a874c4e24178a7db4bd0560aa72561604b53f35d3ba3ab9d6f550dd2e890ebe237db14a0bb811589d7abdfac2988b31de27a0d3bca09a67f6e73c98c32dee9c0d6d91db3fd5aded57584f4dfdb1901af8ef65a762628af10b865372cafe885695e1253bf9837a954821f97de190c062537a494e04d151456bd3a299a563243ec92feb734a024e2608adb4a6ff9d0e2ea3d5608da5dea15078b06318802b9bca0ccb57055ab097bae339b3ac0097d1819f1d73b43315004ec9ba7fdf5f0979b6a07dfbb0d5b9dec1eeea771c2e3f6a00b875d33a0d304b02b42c66b96a22db1e6edb4ce986bd02242aafd22ee12c8e0136d4d7072a3cf01daaa2fcb68a4581eb1395dbc61ec269303de44ea49943937747d340c535cb77f7d6028236c4cf3bbb8d9ab2a0f8740dcab3368408b98cc30a83df5c185202f23d8236679c692239f02cd0376328ce5b566be34d7a0e67701b28d5ecf0eb5b8291e5e40f8e3add5d06c0b582c2985691bce50c59ada9aa605a7658e836baf559ecbb0e28be11e8761b4b0f066e1ad3dc769b856e84bb056f33d71958a265ab7a93b371581e2220123b6d94ae3fbf9ca5dbe5171348b4b904eee8d3cb562113ba0d12b253f8bf399572ed1297fadeec325e97b22204321ff43e080766d27bc910b3912113d4e62a4180328ba96716b8e9c5568946f9fcfd6b7eddecd32ba1bd20ccf4646ca4e719c4bb2f1aedc58f46f0508c576afb58384a2bef0458169ee18d7c07b1b0dd8f3d8258d730b5a95571ef4d1880be20acae589502c7bb904e5008645af564a1ba3988ce13f442ac541f3b261f5fb900f9fbd3cc90584c114de247ddfa9b063ab8420b593bce745f58bf8bc0000325997291e0183e273a00d0551f4bf1acf069db404b6d470780806752dacb2210fb489741d74d6bfafdb425309c56384277c4fa721788339d99ac46ffaa204d110dba831271be30daf2014d8d2fa1a8381193ace71bc52cf219696359c52775dbabd53c0bb0b46e9317f95c1fea52573501ffe21f6bdab8cb4adbd50d2238eded9ebac26c2e44f89a44e7828a44aeea3e75773d1414d2d650cb9123e4f17042d51b4ca902a51ba3fd151d4abe21798a7b94d31a691599c7529061112177a55e9a589c3a1c46bdec9ec76540fa387fe8c5fc8dcc54f0a34033ac3969d294bad7ed32ee37986c8ccec81cc23772cbbd468c8e5ee42ff227d95724724ce479a1d65c189c17739bb77cf7c2ff9f42045be08c9d14a3bff0f31eac128e74133d25f5f9db4fdc14fff11b144fc6ede09c19fc18812a995dd8b013172ae1491e876d3d4ceb0c44371f431313cc00f88c30e139df4d2398bf05264494e7345bc4a53a5fe4dafbf11753d800f4ebf78032ca179078c5c11b93ebbc14f4275205fd02e7b77a1abf67e92a2c777bae015940be4f865fe88c136d63ee33dcce7bdc7de5da51519dfff5d5e118d5031d101f977958ffced8bb2028d35eb90c989219256a62f5f1d07c562e71ff8fdb2c5bda8ad6fb1ae263f721e03bc0e3dae9e31d132d6a4adef8b47bf5d54fcdd5ca075f5c2840e9e4c47489d1fab17712dbaf891f48a1966b875b104de067e5124cbf3004656c2581e9b499d3b29dcd9298a5de05d7b8a94aefe06f24e724d82617fa3ac42ec11884aab4e7b8bfcd1a5a590d1f19b5fcc4fa67dbf449ab42173f5b7a680333b8165f1eb225b8cf361ba4f2d879620bb80ad1f0c8a3781a656cbdf367568ce6bf939fcfa1f173a25d5935855f16841f705355260eef925cc83e54d96bd4d6e759c18c4597f1c69742c1655d042431f65529cd09efdf5bc1bc84ac4d3e277668cd080787e5488a15480aa2dae5bf84ff5156c82d84c454d6b33e8a51cc659eb7df86f57721b37cc0d7c2a60c5db3c010e76a78efaf19c26044a507c81aad9d44de46f425ecda262359cd75a7b78638c782fb5d7c0df5f2fb61f03589de283473e3b13fcd0ee069c3eb4e82df3aec5183fdd200acb2a489620a6cd4c0a93bcf1bb4fa95316fe2ac7b09227984092a1f1b00ca129feb6ae29286c685c2eda54b2abc019df52cef34106ed123872a952b3c084612a73d642ea29b0090e7c94eaaef556c6435d579c39cd4d4b6909bcab89e1871f39c75ced910f4e36328bdf98125eb8c7c3ee2ae6743fa1205786ad03a517cf74c70ae80c7543947fd967177680d373a0d8b9d9bbe024bb292d18cee50f1c2d73b12f9f4aa7e4394c4deefff19d5ab7f6ff4c913210de6870006ecd948cf63e43d992d3c886281b07e9b235761959208679ed55b211d6a8"
    z = {'code': 200, 'data': {'qyIdSet': [], 'orderStr': 'reg_type desc,reg_certno,reg_seal_code,reg_prof_name',
                               'qyId': '002105291239451309', 'pageSize': 25, 'reg_type': '',
                               'pageList': {'total': 5, 'pageSize': 15, 'list': [
                                   {'REG_TYPE_NAME': '二级注册建造师', 'REG_SDATE': 1630598400000, 'REG_CERTNO': '30306120',
                                    'IDCARD': '612701198******13', 'REG_QYID': '002105291239451309', 'RY_CARDNO': None,
                                    'RN': 1, 'REG_SEAL_CODE': '陕261141556894', 'REG_TYPE': 'RY_ZCLB_072',
                                    'RY_ID': '002303160119888497', 'RY_NAME': '刘平', 'REG_PROF_NAME': '机电工程'},
                                   {'REG_TYPE_NAME': '二级注册建造师', 'REG_SDATE': 1630598400000, 'REG_CERTNO': '30306120',
                                    'IDCARD': '612701198******13', 'REG_QYID': '002105291239451309', 'RY_CARDNO': None,
                                    'RN': 2, 'REG_SEAL_CODE': '陕261141556894', 'REG_TYPE': 'RY_ZCLB_072',
                                    'RY_ID': '002303160119888497', 'RY_NAME': '刘平', 'REG_PROF_NAME': '建筑工程'},
                                   {'REG_TYPE_NAME': '二级注册建造师', 'REG_SDATE': 1630598400000, 'REG_CERTNO': '30306120',
                                    'IDCARD': '612701198******13', 'REG_QYID': '002105291239451309', 'RY_CARDNO': None,
                                    'RN': 3, 'REG_SEAL_CODE': '陕261141556894', 'REG_TYPE': 'RY_ZCLB_072',
                                    'RY_ID': '002303160119888497', 'RY_NAME': '刘平', 'REG_PROF_NAME': '市政公用工程'},
                                   {'REG_TYPE_NAME': '二级注册建造师', 'REG_SDATE': 1630598400000, 'REG_CERTNO': '30306120',
                                    'IDCARD': '612701198******13', 'REG_QYID': '002105291239451309', 'RY_CARDNO': None,
                                    'RN': 4, 'REG_SEAL_CODE': '陕261141556894', 'REG_TYPE': 'RY_ZCLB_072',
                                    'RY_ID': '002303160119888497', 'RY_NAME': '刘平', 'REG_PROF_NAME': '水利水电工程'},
                                   {'REG_TYPE_NAME': '二级注册建造师', 'REG_SDATE': 1638115200000,
                                    'REG_CERTNO': '陕261212144448', 'IDCARD': '612701198******11',
                                    'REG_QYID': '002105291239451309', 'RY_CARDNO': None, 'RN': 5,
                                    'REG_SEAL_CODE': '陕261212144448', 'REG_TYPE': 'RY_ZCLB_072',
                                    'RY_ID': '002303160119902865', 'RY_NAME': '白冬', 'REG_PROF_NAME': '水利水电工程'}],
                                            'pageNum': 0}}, 'message': '', 'success': True}

    company = Campany()
    # count = company.count(company._ROOT_PATH)
    # print(count)
    # data = "5588a9e126c91a28cc2f6813e3793369f7b54741889253ad1b1e7bf1f1f612a50f892a28d9cbb8e4ee40f4af5d9005c7b167d827fa9909c42d22f740e41a86d1ffddff057235a00688f0299c93167d006b4ef5f39595e70dd0b51216de353f98300d31ea16d8e989ee386171c6821bbd849b02cacc420504ee24b750577a6e8fc3a777de864cf85dceac0ec8c233976774996d9abea06f0eeb95be0ac2d1931cf3eca057ce8c53e2e075b567f96471ec522b035b83710c88756004c85c379c647e3b174d787041c6b4560e8f0f2d9e2923e043e3e1db1cd447303b68fe5a802cfebedbcb5fd71b749d465fc7cc1190c164d9b24db61578e53f346b2cbd6362b4a41f042962ebc17a99763bcf3dd9be6409c122918f6b45078c77b2465f7b852ab800bc5aec8a18303df1b1be053697bc226e5cdeb0b26053f3b1729a552d142dcc5f5fcd26745b8ac27a4ceea11b5443bea5d6b846e0b692044ff78d7fb1f9a5949ba2990670f3c2357a4e24c51a1e302e008852756c781b22d6ca0edea8ba92fb6ada74911eff624a52b4aa9a2bef56e835c74cccbcf973a2c289034788ebba530f1353c2130e7ffa688f7813680c2a0ea0c0ccbbc83d4683631f9fde215f0bd70f35c271b01b3d239faa4c087cd695db63ab0aa174d03b22f7e53d054ea1a2d7795d9fa3804d2ceb30785409c23ee37a9a2cb50911f797c2d8f9a24e0b59d612324bd9556589328aa229f8e9219439635b7e942559d40f3b75b797ca1d827fbeb47bf57560bcb389fcc4fa73e61ab8aae17dee673029741a1279764de400c9d416ec8034d3543673a8a612487ffc6c66c0a7ee2acb8d0dcefbfff9335fac8f64ce1f49c2b03c354cb23d82311b61d8baaf0bccc9af0312990087bde03e3564b9763a95b13064e5e7c2475a36fbcea51eabf8b93a49517ea47a22b566ba63159fd9a331abdc1983756589620b8189f2da77da8450c58c9ebec17e15e64648e4bb36e00e7b8d8e7516f8a259cb0a0f3d37ae1605803e1d26c40cf72e60fc4a5a3f0dcd5854f8ff0f45ed8a37947dd9e4dc4f1e390545100c3423b46fcfcf518689f5aea382500dc20bd1736d14a7cf68397481148876ea0bde565c88fd3733ea8975d622adb32d44865d24692d1dd6f4d4438c91418cb1d8033e7ffd098f93cc3222b174d4c64d6a5059146358341d09e4290b87d98ea71906a16f929792155ef65f3479da72b4ce4c3eab1d09d46583ca0cc05bc8809e66e02f60f40fd6d5e1c9801ec80f29269af4390d8dcba6e328b8e3378b1f00f217a846c463a13149b394cde2e2c6935c8e3a0a1f3165d0830e333942ff3f30bf6dd736648b0e49d875edf981b7bf1eacc36292ac7a530d45438440ddcd56e19ae6715ea0429a827d099b0e602be60b99fa222496c96ae8e743397c0dcbd7869f610b17c8e81d255ec12ad1c9baec0dd888940a8bc52588e1dda2a29ff15ef8efd1dd3d57229abab972c7b5e506a8d9c8cae585984584e47d2ad72da524493b42102c8b7f03062f5f1f248f7b9e874a1ed2370d64401e4292dc04548509d25aa9b4ebda62816c0af9185628da61093ea0b49d77e8e07efa8e9ed6d394d4f3fd8397c50a6090e82293ab49136f18ef0c36c742e10311c9c3d9dd43c2161f2694583ee13de33a95977393d8ee5103b043418114cd17a4cfe6738090cc7f83fac3a65fcc6008c2c9d9cc8aa1cbf609d1198a669ba2650106c35bec44dc1268f34bc9ec6386455a2e7a712ce22dcf73d72b553f942d3db0cb892775dbdaaf96e978c5a110b5e424fe0701de31d98cdfa9e6d316ea0e2d30c6141ae8a18e2d1cf37f3ff4e121f2425bd5cc19cc4aeb1b36d3c55fd0782117856e6901e0c48338acf053cb832b81498ff232b55ab7564b53c19fdc67defc3af4dac80e9120465a732eed47e3c4eea045916e15aeab59f029bffca43e513a37d95138615a6d36a2059c0a37a16ed43c3cf51336"
    # print(company.decrypt(data))
    print(company.run_detail(Params(province='云南', city='保山')))
    # exists = list()
    #
    #
    # def find(path: Path):
    #     for file_or_dir_name in path.iterdir():
    #         if file_or_dir_name.is_dir():
    #             find(file_or_dir_name)
    #         else:
    #             province = file_or_dir_name.parent.name
    #             city = file_or_dir_name.name.split('.')[0]
    #             exists.append(f"{province}-{city}")
    #
    #
    # # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包三级')条件下的总数超过了450条
    # # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包二级')条件下的总数超过了450条
    # # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包三级')条件下的总数超过了450条
    # # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包二级')条件下的总数超过了450条
    # # Params(province='吉林', city='长春', qualification_type='建筑业企业', qualification_name='建筑装修装饰工程专业承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包三级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='市政公用工程施工总承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包三级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑工程施工总承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑幕墙工程专业承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='建筑装修装饰工程专业承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='消防设施工程专业承包二级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='特种工程(结构补强)专业承包不分等级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='环保工程专业承包三级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='钢结构工程专业承包三级')条件下的总数超过了450条
    # # Params(province='黑龙江', city='哈尔滨', qualification_type='建筑业企业', qualification_name='防水防腐保温工程专业承包二级')条件下的总数超过了450条
    #
    # # 已经爬完的 ['内蒙古', '辽宁', '吉林', '黑龙江', '北京', '天津', '河北', '山西','上海', '江苏', '浙江', '安徽', '福建', '江西', '山东',]
    #
    # # 木可 ['上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南']
    # # 弟弟 ['湖南', '湖北', '广东', '广西', '海南', '重庆', '四川']
    # # 吴炀 ['贵州', '云南', '西藏', '陕西', '甘肃']
    # # 吴炀 ['青海', '宁夏', '新疆', '新疆生产建设兵团']
    #
    # provinces = [
    #     '河南',
    #     '湖南', '湖北', '广东', '广西', '海南', '重庆', '四川',
    #     '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '新疆生产建设兵团']
    # company = Campany()
    # find(company._ROOT_PATH)
    # for province in provinces:
    #     city_region_map = company._get_city_qy_regions_by_province(province)
    #     for city, region_id in city_region_map.items():
    #         if f"{province}-{city}" in exists:
    #             time_print(f"{province}-{city}已经爬取过了")
    #             continue
    #         start_msg = f"开始爬取“{province}-{city}”的企业数据"
    #         time_print(start_msg)
    #         p_ = Params(province=province, city=city)
    #         company.run(p_)
    #         end_msg = f"成功爬取“{province}-{city}”的企业数据"
    #         time_print(end_msg)
