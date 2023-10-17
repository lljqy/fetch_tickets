import re
import json
from pathlib import Path
from typing import List, Dict
from secrets import SystemRandom

import requests
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Route

from core.base_processor import BaseCrawlPackageProcessor
from utils.common import time_print, TIME_FORMAT, BASE_DIR


class CTripProcessor(BaseCrawlPackageProcessor):
    _cookies = {
        'MKT_CKID': '1696934370793.ll2sh.a1ki',
        'GUID': '09031074214937747423',
        '_RSG': 'zvK0lH9vEtC0SULvRD.yd9',
        '_RDG': '28a28e51419bc4245809801861e0b22927',
        '_RGUID': 'cdcee494-6f01-4e7d-99fc-f8d6f955e700',
        'MKT_Pagesource': 'PC',
        '_bfaStatusPVSend': '1',
        'ibulanguage': 'CN',
        'ibulocale': 'zh_cn',
        'cookiePricesDisplayed': 'CNY',
        'UBT_VID': '1696934370623.34tyyy',
        'cticket': 'C0B130F150047D45E6C01CB548BA5A1F1817E3DE8CDC23B34D6E86134594ACA1',
        'login_type': '0',
        'login_uid': 'F6DF19CF6B184CB78864DAFAF5662F7D',
        'DUID': 'u=F6DF19CF6B184CB78864DAFAF5662F7D&v=0',
        'IsNonUser': 'F',
        'AHeadUserInfo': 'VipGrade=0&VipGradeName=%C6%D5%CD%A8%BB%E1%D4%B1&UserName=&NoReadMessageCount=0',
        'intl_ht1': 'h4=2_4037106,2_374461',
        '_RF1': '124.240.84.155',
        'Union': 'OUID=index&AllianceID=4897&SID=155952&SourceID=&createtime=1697033549&Expires=1697638349467',
        'MKT_OrderClick': 'ASID=4897155952&AID=4897&CSID=155952&OUID=index&CT=1697033549468&CURL=https%3A%2F%2Fwww.ctrip.com%2F%3Fsid%3D155952%26allianceid%3D4897%26ouid%3Dindex&VAL={}',
        'MKT_CKID_LMT': '1697033549803',
        '_ubtstatus': '%7B%22vid%22%3A%221696934370623.34tyyy%22%2C%22sid%22%3A3%2C%22pvid%22%3A2%2C%22pid%22%3A102001%7D',
        '_bfi': 'p1%3D102001%26p2%3D102001%26v1%3D2%26v2%3D1',
        '_bfaStatus': 'success',
        'librauuid': '',
        '_jzqco': '%7C%7C%7C%7C1697033550227%7C1.982593758.1696934370791.1697033559072.1697033580176.1697033559072.1697033580176.0.0.0.15.15',
        '_bfa': '1.1696934370623.34tyyy.1.1697033558959.1697033668129.3.3.102002',
    }
    _headers = {
        'authority': 'm.ctrip.com',
        'accept': 'application/json',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://hotels.ctrip.com',
        'p': '31925527702',
        'pragma': 'no-cache',
        'referer': 'https://hotels.ctrip.com/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    def __init__(self, js_path: str) -> None:
        self._random = SystemRandom()
        self.script = self._get_script()
        with open(js_path, 'w') as f:
            f.write(self.script)
        super().__init__(js_path)
        self._browser = None
        self._page = None

    @staticmethod
    def save_cookies(cookies: List[Dict], path: str) -> None:
        with open(path, 'w', encoding='utf-8-sig') as f:
            f.write(json.dumps(cookies, ensure_ascii=False))

    @staticmethod
    def load_cookies(path: str) -> List[Dict[str, str]]:
        with open(path, 'r', encoding='utf-8-sig') as f:
            cookies = json.load(f)
        return cookies

    def _get_callback(self) -> str:
        letters = "qwertyuiopasdfg$hjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"
        n = len(letters)
        callback = ""
        for i in range(10):
            callback += letters[int(self._random.random() * n)]
        return callback

    def _get_script(self):
        payload = {
            'callback': '',
            'a': 0,
            'b': '2023-10-11',
            'c': '2023-10-12',
            'd': 'zh-cn',
            'e': 2,
            'webpSupport': True,
            'platform': 'online',
            'pageID': '102002',
            'head': {
                'Version': '',
                'userRegion': 'CN',
                'Locale': 'zh-CN',
                'LocaleController': 'zh-CN',
                'TimeZone': '8',
                'Currency': 'CNY',
                'PageId': '102002',
                'webpSupport': True,
                'userIP': '',
                'P': '31925527702',
                'ticket': '',
                'clientID': '09031074214937747423',
                'group': 'ctrip',
                'Frontend': {
                    'vid': '1696934370623.34tyyy',
                    'sessionID': 3,
                    'pvid': 3,
                },
                'Union': {
                    'AllianceID': '',
                    'SID': '',
                    'Ouid': '',
                },
                'HotelExtension': {
                    'group': 'CTRIP',
                    'hasAidInUrl': False,
                    'Qid': '527976842620',
                    'WebpSupport': True,
                },
            },
        }
        payload.__setitem__('callback', self._get_callback())
        response = requests.post('https://m.ctrip.com/restapi/soa2/21881/getHotelScript',
                                 cookies=self._cookies,
                                 headers=self._headers,
                                 json=payload)
        return response.json().get('Response')

    def _get_test_ab(self) -> str:
        return self._page.evaluate("window.testab")

    def _get_hotel_uuid_key(self):
        return self._page.evaluate("window.Kar98k && window.Kar98k.hoteluuidkeys")

    def _hook(self):
        if self._browser is None:
            playwright = sync_playwright().start()
            browser_type = playwright.chromium
            self._browser = browser_type.launch(headless=False, args=["--disabled-blink-features=AutomationControlled"])
            context = self._browser.new_context()
            cookies_dir = Path(BASE_DIR) / 'apps' / 'xc' / 'preserve'
            cookies_dir.mkdir(exist_ok=True)
            cookies_file_path = cookies_dir / 'cookies.json'
            if cookies_file_path.exists():
                context.add_cookies(self.load_cookies(str(cookies_file_path)))

            self._page = context.new_page()

            def handle_js(route: Route):
                if re.search(r"smart.01ff5bbcb05a03e8f105.js", route.request.url):
                    response = route.fetch()
                    content = response.body().replace(
                        b'''n.realUrl && 0 < n.realUrl.indexOf("?") && (t = "&"),''',
                        b'''window.testab = e, n.realUrl && 0 < n.realUrl.indexOf("?") && (t = "&"),''')
                    route.fulfill(body=content)
                else:
                    route.continue_()

            self._page.set_default_timeout(0)
            self._page.route("**/*.js", handle_js)
            self._page.goto("https://hotels.ctrip.com/hotels/list?countryId=1&city=2&checkin=2023/10/13&checkout=2023/10/14&optionId=2&optionType=City&directSearch=0&display=%E4%B8%8A%E6%B5%B7&crn=1&adult=1&children=0&searchBoxArg=t&travelPurpose=0&ctm_ref=ix_sb_dl&domestic=1&")
            self._page.locator(
                selector="#ibu_hotel_container > div > div.list-search-container > ul > li.list-item.list-btn > button"
            ).click()
            # 保存cookies
            self.save_cookies(context.cookies(), str(cookies_file_path))

    def _crawl(self):
        # 先hook页面
        self._hook()
        test_ab = self._get_test_ab()
        hotel_uuid_key = self._get_hotel_uuid_key()
        # 再设置参数
        params = {
            'testab': test_ab,
        }
        json_data = {
            'meta': {
                'fgt': '',
                'hotelId': '',
                'priceToleranceData': '',
                'priceToleranceDataValidationCode': '',
                'mpRoom': [],
                'hotelUniqueKey': '',
                'shoppingid': '',
                'minPrice': '',
                'minCurr': '',
            },
            'seqid': '',
            'deduplication': [],
            'filterCondition': {
                'star': [],
                'rate': '',
                'rateCount': [],
                'priceRange': {
                    'lowPrice': 0,
                    'highPrice': -1,
                },
                'priceType': '',
                'breakfast': [
                    3,
                ],
                'payType': [],
                'bedType': [],
                'bookPolicy': [],
                'bookable': [],
                'discount': [],
                'hotPoi': [],
                'zone': [],
                'landmark': [],
                'metro': [],
                'airportTrainstation': [],
                'location': [],
                'cityId': [],
                'amenty': [],
                'promotion': [],
                'category': [],
                'feature': [],
                'brand': [],
                'popularFilters': [],
                'hotArea': [],
                'ctripService': [],
                'priceQuickFilters': [],
                'applicablePeople': [],
                'covid': [],
            },
            'searchCondition': {
                'sortType': '1',
                'adult': 1,
                'child': 0,
                'age': '',
                'pageNo': 1,
                'optionType': 'City',
                'optionId': '2',
                'lat': 0,
                'destination': '',
                'keyword': '',
                'cityName': '上海',
                'lng': 0,
                'cityId': 2,
                'checkIn': '2023-10-11',
                'checkOut': '2023-10-12',
                'roomNum': 1,
                'mapType': 'gd',
                'travelPurpose': 0,
                'countryId': 1,
                'url': 'https://hotels.ctrip.com/hotels/list?countryId=1&city=2&checkin=2023/10/11&checkout=2023/10/12&optionId=2&optionType=City&directSearch=0&display=%E4%B8%8A%E6%B5%B7&crn=1&adult=1&children=0&searchBoxArg=t&travelPurpose=0&ctm_ref=ix_sb_dl&domestic=1&&highPrice=-1&barCurr=CNY&breakfast=3&sort=1',
                'pageSize': 10,
                'timeOffset': 28800,
                'radius': 0,
                'directSearch': 0,
                'signInHotelId': 0,
                'signInType': 0,
                'hotelIdList': [],
            },
            'queryTag': 'NORMAL',
            'genk': True,
            'genKeyParam': {
                'a': 0,
                'b': '2023-10-11',
                'c': '2023-10-12',
                'd': 'zh-cn',
                'e': 2,
            },
            'pageTraceId': '2cacc0cb-a079-4a26-88fd-07e1312a2aea',
            'tsid': 'prd-2023_10_11_2-f6b1935b-9cab-47ec-ae0f-1b7a81c51fd6-hotel_online_list-3.6.2-DOM-online',
            'webpSupport': True,
            'platform': 'online',
            'pageID': '102002',
            'head': {
                'Version': '',
                'userRegion': 'CN',
                'Locale': 'zh-CN',
                'LocaleController': 'zh-CN',
                'TimeZone': '8',
                'Currency': 'CNY',
                'PageId': '102002',
                'webpSupport': True,
                'userIP': '',
                'P': '31925527702',
                'ticket': '',
                'clientID': '09031074214937747423',
                'group': 'ctrip',
                'Frontend': {
                    'vid': '1696934370623.34tyyy',
                    'sessionID': 3,
                    'pvid': 3,
                },
                'Union': {
                    'AllianceID': '',
                    'SID': '',
                    'Ouid': '',
                },
                'HotelExtension': {
                    'group': 'CTRIP',
                    'hasAidInUrl': False,
                    'Qid': '210439909457',
                    'WebpSupport': True,
                    'hotelUuidKey': hotel_uuid_key,
                },
            },
        }

        response = requests.post(
            'https://m.ctrip.com/restapi/soa2/21881/json/HotelSearch',
            params=params,
            cookies=self._cookies,
            headers=self._headers,
            json=json_data,
        )
        print(response.json())

    def _clean(self):
        pass

    def _save(self):
        pass

    def run(self):
        self._crawl()
        self._clean()
        self._save()


if __name__ == '__main__':
    trip = CTripProcessor('js/test_ab.js')
    trip.run()
