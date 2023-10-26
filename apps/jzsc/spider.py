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
    _DATA_LIMIT = 450
    _ROOT_PATH = Path(sys.argv[0]).parent / 'data'
    _ROOT_PATH.mkdir(exist_ok=True)
    _SEP = "@@"
    # 获取省市code的接口地址
    _region_code_url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/region/index"
    # 获取资质名称编码的地址
    _apt_code_url = "https://jzsc.mohurd.gov.cn/APi/webApi/asite/qualapt/aptData"

    def __init__(self, js_path: str = None) -> None:
        super().__init__(js_path)
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
        response = requests.get(self._region_code_url, headers=self._headers, params=params)
        json_data = self.decrypt(response.text)
        result = {item['region_name']: item['region_id'] for item in json_data['data']}
        self._region_map.__setitem__(province, result)
        return result

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
        response = requests.get(self._apt_code_url, headers=self._headers, params=params)
        json_data = self.decrypt(response.text)
        return {item['APT_CASENAME'].strip(): item['APT_CODE'].strip() + self._SEP + item['APT_TYPE'] for item in
                json_data['data']['pageList']}

    def _get_apt_codes(self, p: Params) -> List[str]:
        apt_type = self._get_qy_type_by_qualification_type(p.qualification_type)
        if not self._apt_code_map:
            self._apt_code_map = self._get_apt_codes_map(p)
        if apt_type == self.ERROR_QY_TYPE:
            return sorted(set(
                apt_code_and_apt_type.split(self._SEP)[0]
                for apt_name, apt_code_and_apt_type in self._apt_code_map.items()))
        return sorted(
            set([apt_code_and_apt_type.split(self._SEP)[0]
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

    def __init__(self, js_path: str = None) -> None:
        super().__init__(js_path)
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

        pass

    def _get_total(self, p: Params) -> int:
        params = self._parse_params(p)
        response = requests.get(self._table_url, headers=self._headers, params=params)
        json_data = self.decrypt(response.text)
        return int(json_data.get('data', dict()).get('total', '0'))

    def _crawl2(self, p: Params) -> pd.DataFrame:
        params = self._parse_params(p)
        page = 0
        type_to_qualification = {value: name for name, value in self._qualification_to_type.items()}
        df_results = pd.DataFrame()
        while True:
            params.__setitem__('pg', str(page))
            response = requests.get(self._table_url, headers=self._headers, params=params)
            time.sleep(secrets.choice(list(range(2, 3))))
            try:
                json_data = self.decrypt(response.text)
            except Exception as _:
                # 此时爬虫被封需要等待一段时间继续爬
                time_print("爬虫被封，休息片刻...")
                time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                continue
            df_cur = pd.DataFrame(json_data.get('data', dict()).get('list', list()))
            if p.qualification_type:
                df_cur['QUALIFICATION_TYPE'] = type_to_qualification.get(p.qualification_type)
            if df_cur.empty:
                break
            df_results = pd.concat([df_results, df_cur])
            page += 1
        return df_results

    def _opt_crawl(self, p: Params) -> pd.DataFrame:
        qualification_types = ("勘察企业", "设计企业", "建筑业企业", "监理企业")
        for qualification_type in qualification_types:
            p.qualification_type = qualification_type
            total = self._get_total(p)

    def _crawl(self, p: Params):
        page_limit = 30
        params = {"pg": "0", "pgsz": "15", "total": "0"}
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
            # 先判断不选择“资质名称”的时候，数据流是否操作
            total = self._get_total(params)
            for apt_code in apt_codes:
                time_print(f"开始爬取{apt_code}代码的数据")
                params.__setitem__("apt_code", apt_code)
                page = 0
                while True:
                    if page >= page_limit:
                        time_print(f"只爬取了{apt_code}代码的前{self._DATA_LIMIT}条数据")
                        break
                    params.__setitem__('pg', str(page))
                    url = "https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/list"
                    response = requests.get(url, headers=self._headers, params=params)
                    time.sleep(secrets.choice(list(range(2, 3))))
                    try:
                        json_data = self.decrypt(response.text)
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
    # chat = Wechat()
    company = Campany()
    # x = company._get_apt_codes_map()
    # print(x)
    data = "5588a9e126c91a28cc2f6813e3793369c25469a35a79a5541917e64a1f6f6af3f55e740c95225fbef531f1f6866162beeebd6a236c0d68b85945a270cd51b0ed887007c82ea15bf8c9effa785b7db82c7b76fc2db59ca0db60d7a831d476b5c2324108ad3d284cabd10c7f829cdcc0c6e71b0f66cbab555a74dd5ac8ca81bdc39955fd8455e3e8adcfd56ab76ab3dedff1383814b223c28b444d5118688a716b3f3a55a32d0dc98d707d4e260240e1dfbeb575a4bb7cd6f9bd69190276fdbd70c265a56262e580c0d1831500bb9c5433562951a5385a8c57f091e2542006ec0133a0e7827ff269d53e7f3ca7689077de3d01bcd89f82c8155fb7237ac658024c3321ffce498deaabf394ae72c4f75c84eab665e38ff90cd6be2c668369d702217853e2ce74c3ca7189a9209d59edeb77729cf146368d060ad7b8b7c0d70cfcacc3d2ecb1cae7b8502b02f4542c7581cf94c204e06dd901678f71e7945bcd64722538edcde3bfac5ac97829fc54e85dcdbd1065122a85eddef15678d99691c4f1e41fd8977905ac4d0171c21936d09f2ff7bae3eb773e4b1e89c7cd319d6062048d013aacd57ec41423bd82eb4c0cac5c5ebb196ce9b6b33578593743438a413102c2661a22f7f895c0ee46afab5179b57cb47abb6adfa7f80538b8fa3aea6424ca929c05bdf976debe12461395371cb1953df7790a51c8d2f5c3f3f6cfcb09654ecc2cad9802cc7d9def63b86c11c78d6a38283b3422e82c817cf8adbb7f541368612155ac8c0f8428a0cffebbd45a2728541acf6e57e15c5e49e44fa836a2176de075e8b48d1a403e744ebcb6579f91da83ae2ea30f0bc9b2a4294fd561176bde806ff23b54f85e06c6adcf1ac07fe73345065dbca78fb853ceea38a0889b3a21d3ee6a4f557e6189c2b6c8b42701400cdfae257d5d89a6438d9bd068e348add6d40e5702b631d50496ea0d2f1fbb5c15961aa93c21c7aeaa5e063bf8aeeafdb20767447826431094db573da94a5664ec706bc665d3ccd7ba3577d8bc918f528681b1edc76632631f3d88ce95e0e9cdf0cd2df4cad3f6570e5a7b78c6e92236a6cd48629665b8c01069ffb59b4e9f5a3c876ed9b73f6ce8e3af961d82b725cb01b03c57747d973228ff51fe6fda9ea51f3d9bb027ef881aa0e707d3db8d28b03b9e9102075db51afc482b14a4420bd18c9093ebc0fa4ae01cb302629117c7e2a72cbb2117e744e62bc1c2403c0110155f9c8bd63399ec82006c1708e7fae640a463a3bf533ceb9a5f6652173878186a4f79ded62d852786d1e7d56a29250b81ce96ccc3c8049c08347081253d51a1a3ba993ca20e4cd354cd99a46616ccdf9206d4b0ecc3b355692a48c20a292e7334787f7d4f87bac898bb167030175194065311f1e605e6ad7e84b8b7e84766848a30ba99ca73d2a20e99fe8868789ee3229888fdf5b17d4c062255e4b2e5ea750de110efc4b668764625acc848f23752669a04e0527c7cb65311507d4b817c5fd2f22966b8dc19a3f2a8530680134388dc34ca0bdbf016159cf67ccfe2fadcda93448cf6de8e3ecb65a5db6533aa864540272eab0920701a8aa8e2e3517bdb16f77a19cfbd930601a4491d88f8bbb84ff6c98e9d032948192b7fa55e201d19de0c71d1ed8ee737aa7067b806770ab54df3f8687aabd2676970dbc93a3eb18cd144f4dd5b9c66e6099718213a4aeb49dcba3b3efc731d04fc56acd1dff78e33a2fa4d7c8f194d77feb457a5b407dcda0c6e1164c01fe093b107824953a42a7f7e46806a96c6237a42210f3640dd78536b2c481bf89e239c129124bf23eef8302916c1e87d1221c13abdf95135404bca48f161ff427c92f1c0ed8a8a4fe9644a460b4316ecbc39d821d1548e797ab76bb010836ca373070b95e123d6ae015a65ff9b20f0c17d2a8ed9a8149a0909bad627efcd48988dbb48f04f89fd980b7e1f2bf7949acf91ed9624100d2e0894c16bfe17bdb9baa1f5b7b3132489f81c05420ecf38d08fb201046a4707bf6e87471a78ab8d0c189241c3b5fac24bef7a9d5a94011f01ca9b8944d811c28b00883fe3c023ea2e296d3fcdc171c88496a7c5f6377ab22c91fc0206fa0c70d4dc0b2c9a587c986aca7e5206f4957168b76fc409c197fb14e4a10f933e10b9a54a8920b8955b737115d2450d5adca8271ac68a438892e4798519920283f2ac2545bc892605b8ce1dad43bd39462d2a4d5adba53f16f4b4e00d2c836cdc7e75945005c11e39849afe20d1f17c94cb9f01b47de0c1eeb82d2a32a0c99dfb5716e684fc7b36ac4b587b6484e11ad53766b1b5f1ba74ebb7e687acb4560890f8526ff941bdd5bd1a47260bddce364e771725ffddbe15e94abae83a4fd3806e6eec446931daecbc09db896eecfd3869764b21110f8596c1c745299b74f0210d23d00fb0017e6058fcc2a9fc334fc74e2929a913690ae133fa618fc6474c11cae09784ba8bdc01759aeb4740927d64b78e337881d78f6d61427ad37b644942db136a5e11918ff468fde775b89e63f66e7b6dae4ba38aa5babd6e68413585087b13e913b4c01d46860efc0bfe5c4a6242937e5ac0745d6b788a5f16edc6e9375df8c2c64d541c8831aa11cf753147654a82d2906a39160a7689569ebe39d2cdf6d5504ac87e4b6060e97a84795ba0805f023f09a21d8707b948f14c28d3d0106e23554ab4f7067a70a68e84c4b69aceb52e18bc3b5a3137c47e2d1c16063e280e0e8964189253ca7deed984ac7235ae2327bf940a49db13e658ac090c8458d947ded35462347a63f4d81067cb272da7367c7c7428bdd52bd408fb28b97f26d79e2f879dfeb2fd00180abbc9bc9db16ea543a1faa621e8d5df7ae43ac3a81d46d7bf7e5b30cfb7e5d011d865f41e048814a4ce21f9db2c71b0f9a791f7f1c15294fb9db3f9c4664d7474169fc2a5e7fe67802693dce6bc1949e66e02ba062bf25b37b6116275c504f53f59ad7ea8663b1ca44b5b1297af05f1ffa0ff9ced88c9a4efec70c85e8e65b03fd50e9039aa5e03d45ccd09b37aebc3ab557abbc0ad6c5351f70b6b7b22f5c6d64ea79be9ffb1395d9e86b88498c57db3304770d1abc55b726e9a01c73543d4f0a74393f6df23c57298a7a4dd81b289fd604a15732384822db15c802d6f4af9206b81111e53e8a3cc9563a8d26d55f1ba86b243c75ee2192943ec21a7bb70d55a43ff4bd9c46316fb77548c0980edd70a98fbb3bdc9f3091b9ef65da1d82b7bdefb29e220567ec67f12ca7442b403490f54e1c2c41807fc6447c4f085b8f3c4ab3a95bb13e24fb8cccacce7970644bc391d16d6576e6f904dc765b871f36d568afc57dca2a5085079a7f59ef9a6a9711b8e87a9a7c5dcf150c9d2369aa52a809430866391d63c51a075369cec9f1fef5252c944f62dd02d1ad5d616e33bc8cef2a133bbdae590ac967eb23b32f4a7eeb8674bb96a653f0f81ba35e15778a5e0a428302252fdc3017ecd53c3fe1150a939c5885810046337258f51037c9f515e37d27dbca3baeef8109334502fc273dac8ea0ddf9990500b3c75bdf60ec3088f6d041a42cea94ee23ba45cf9a6533ad98de9cc470450e2c7427c4b31c417631c18801ca7671248f7ff4ff439c61c24243a0dc7c0a14aaa613ec9cb949f3e5bbe7e0b4386b180832668dcfcb0d3b1a3b362a2f0015b466a647aed5c8e03f0c28bf0c162396355383f1c723d6708cd9606dfca30e939244d64418938affe8cf25a26cbf654c9eb58cba36749380e730b70656dc576939d14445844bfc9fbbb887dfa194bafaea315b838fd8b64e4b1229b33c018bfd98fab6234280fff8fccd1dd71d8585fa6669f8cd8fcb6758daa55a18de9809b8d5799f281d9398e0528c93b0f35c581ebcce74d49805303459e59caefe83968cad92b368daacb77bcf69807ea28b1a5a9e746b48a007aee1d846cd62fea2abcf80166c2215f3542dc275b76a359bdebc1f23783fb315af16f24ecfed3f375255c4d142f75d94adc6ba42db08f02a9989e6487f81eadc3ec464e9cbab02c58db626b13d440f2fe4227f7036246696f34a5cbfd4ad1a976feb4af4a47e28a9182907ccd830493669917fc6cb76683a31d28369f93a7565572db27c8e5699b19982d8d225e7fd2b067b558764603333af1cedc614ab663def511777052fb95a7e043c294969475bf363b3e65b1ac4257a1000d419dcfdfd4c0d36efbca61e1c434844464b3bb50fb1991e60e247dfa2a95b97c17abdd0bb482e53fcea4c503e6158836ae52d8c5efc0dc147e7a45e5363afc8fb87028863f9480d8374e4ebc7f338910ed0d289016d1aa63285924bda4fcc0b051abbc384a36cd8beabb9d78d0d43a577f6ce2f259ead19d7c51ab124b3a2ee863b0f1118a0d6f5a93a2918aca49ec1a7229c730ca11cdf2f0d0402e155c3767781404edd6210d65f0dd447027f8d79bbaee58a4a177f9c3e9df7b93138ecef7abd83394c717e8fbd09c27b1145ffd5d146409eaf91a55c2f50c3d83a0269ea4270b1e40ad52fa59557122abf541278fbf188044126ec9dbbb1580bd80f518ab218f4e02a8d206eb3e2ffd247b80f9a85b371302272f5feb73f71da645e4290ec941d9d3c866c2efcce7daf61456ca6579b75c99b077b48116b4084bd99ad615159cd48d359e808085578d19264899e688a303abbf05d1a798f6bd6e961beaf363f45044d6b5e876f2a7c79deb4da0a73a0bf4b1553325779ea10dc35222a196c8b4cd54b89ff041633d9d89c6168ccc43c93493504604c58221745659dec12499099e73562bedb801c8e353140ba1e893a901d34133ffbab1e185ef400119e5f216669e6c3f42d78034f24be19b75bf8bcedb04d0d0daa5b664135d25a43f6f64a55fadd9927538cf7b2deb99832bcee9f9d991ea0ec44e0ec1591c3e454832827504767361cfc0048c197e3b049ba2a78e8afda3bc93465741efac81f8d3f016d78b037bce8e16a60aeb149f15f9a57c8a54da90fc84e58c175130434c9538b2a109fbf930a2251f092097351b1d745df6922e15675ac4b40a9aa15a243b79030e2d7caceee6860bd51575b36b5d6e25fcfa19e1d335a64372b9590446068778300cd571c8156f731a1bbe381acf89ad25ce0368231ee8ba79b391c405a1821cf01990c3fa6b0981c27eb3521f24d5fa8de589028ec00c4cbbf7f52372b8a52d52c136ea7ae669794c9fce3935e824f116573376089ba07f67dc09ece1ec8179169c886f64355381e02b72ea58153e5f9930549d5647396217bcd19ddb96c6e5b70977e16edff3e096ec1f861abc48b9514aea8755de99dc213618064fc31126a6b3799a35cb0c54f32d66992ac87d1c935374cfe49eb2979229a8dd07885cd28ec4f40a6a9963390e225c6421efac9137bd2fe63478921ecb2f884160903c18045f646503e0316b41c13b4d576a54a15888d208f8cd6ed432417a4036204bf70a9f512bdcd0db8bcc84a8916ee044b5703768830c354640a05f4b8dab0ebcaff1a8a9078ec70d3ce8ea716072919885e58d29540a4e40ea9e29020fa74da7ad0964fec41c4f2d1bad9ae6a8a3032a9c193c846cf50ffbac9d6bfe0888bd8f0e2e69763213204180cde3d5eaf2669ada4ffa450c2f7750362a990b8a5075c87256bf136f6e6a1dd45619587c6c42385fc7f1764018986a2d18240923844d911a890b7c1d6dd766d4acaec5ad002b69bf61d04a041d2d28877e938811080e6a9f77893c9d8289b89ce52a782d9266fe3c5aa9fbe303962457c4c3c44d24d4b1213f603f07656e0d74c39809624a4965b2ad94d56133c5cafb721b96b936cd6e237f6e46de1171555c1d5c164e2941e84e8e96eab8c4e7debf1610714126eb72c5147e262bd08c838d224fa3bca14686198747eb0c1c370782289655505df6d7d76a34cce172a1e41a5e46cbe1903554b162bcece32805a385e116428e5a5766d82f4c152c8b8782bec4ff33272af7f222b4d56353cd6f205da0ea22f97e0acd39418dfd383f0577318439e9203ab700ae17ea180df7394ea2d1f90f827d49b54f1e3ab3d7b305a4d218850022e30a4cc1d2c02eafd2329e5ce7d8ce189470960c7129c5185ed793fc6359f81d3c0cb5f70121fd07e9d3184bc8f270335f1da2057f68bc59109e9735d016"
    x = company.decrypt(data)
    print(x)
    # # x = company.decrypt(
    # #     "fa8f1891eb026fa5ffabbd521d5acd4dace8066fd57432ad7076b9deb603f489044174507a759401992bf55af2efcc1b9e1b44064bf6f48c0c0f2ddc1b46182781316172ed220ffeb865e7f403df3aaa30bea3262ce33e4d91bd70d6038095a45dd3eaa4fe334c52b3ca62d3b36dcc0ad0d85c69805d65096fe27f794d9397af9214020b47f79c2d611d17627e569e2f386f507ff9c3107ad38b2eb01322c7bf4be6d986f80602f088dc2a16fbc909412da1971d7c6e8d2e1600334b7629bbe75fc663695d7d20598c1a4213f4afc75b3e1e163a730a4b3ad02736c9261ff2e1")
    # # print(x)
    # provinces = ['湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '新疆生产建设兵团']
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
