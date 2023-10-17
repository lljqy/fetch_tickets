import time
import secrets
from typing import Dict, List
from datetime import datetime
from dataclasses import dataclass

import requests
import pandas as pd

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

    def __init__(self, js_path: str) -> None:
        super().__init__(js_path)
        self._df_results = pd.DataFrame()

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
            params.__setitem__("qy_type", self._get_qy_type_by_qualification_type(p.qualification_type))
        apt_codes = self._get_apt_codes(p)
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
                time.sleep(secrets.choice(list(range(2, 4))))
                try:
                    json_data = self._js.call('extract', response.text)
                except Exception as _:
                    # 此时爬虫被封需要等待一段时间继续爬
                    time_print("爬虫被封，休息片刻...")
                    time.sleep(self.WAIT_TIME_WHEN_BE_BLOCKED)
                    continue
                df_cur = pd.DataFrame(json_data.get('data', dict()).get('list', list()))
                if df_cur.empty:
                    break
                self._df_results = pd.concat([self._df_results, df_cur])
                page += 1
            time_print(f"成功爬取{apt_code}代码的数据")

    def _clean(self) -> None:
        self._df_results['COLLECT_TIME'] = self._df_results['COLLECT_TIME'].apply(
            lambda x: datetime.fromtimestamp(x / 1000).strftime(TIME_FORMAT))
        columns_map = {
            "RN": "序号",
            "QY_ID": "查询ID",
            "QY_ORG_CODE": "统一社会信用代码",
            "QY_NAME": "企业名称",
            "QY_FR_NAME": "企业法定代表人",
            "QY_REGION": "区域代码",
            "QY_REGION_NAME": "企业注册属地",
            "OLD_CODE": "原始代码",
            "COLLECT_TIME": "注册时间",
            "QY_SRC_TYPE": "数据类型",
        }
        self._df_results.drop(columns=['RN'], inplace=True)
        self._df_results.rename(columns=columns_map, inplace=True)
        self._df_results.drop_duplicates()

    def _save(self, p: Params, file_name: str = None) -> None:
        if not file_name:
            file_name = '-'.join((p.province, p.city))
        self._df_results.to_excel(f'./data/{file_name}".xlsx"', index=False)

    def run(self, p: Params) -> None:
        self._crawl(p)
        self._clean()
        self._save(p)


if __name__ == '__main__':
    # j = JZSC(js_path="./js/decrypt.js")
    # p_ = Params(province='湖北', city='黄冈')
    # j.run(p_)
    df = pd.read_excel('./data/湖北-黄冈.xlsx').drop(columns=['序号']).drop_duplicates().sort_values(by='注册时间', ascending=False)
    df.to_excel('湖北-黄冈.xlsx')
