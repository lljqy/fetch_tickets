import re
import json
from urllib.parse import urljoin
from typing import Tuple, Dict, List

import requests
from fake_useragent import UserAgent

from apps.jzsc.spider import JZSC


class Geetest:
    _ua = UserAgent()
    _callback = "geetest_1700407154197"

    @property
    def _headers(self) -> Dict[str, str]:
        return {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Referer': 'https://jzsc.mohurd.gov.cn/data/company/detail?id=002105291239451309',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': self._ua.chrome,
            'accessToken': 'jkFXxgu9TcpocIyCKmJ+tfpxe/45B9dbWMUXhdY7vLUVKSRbJWdFdJDUz0rGGcpRhpUUKvcMtoMqfGfwdLCb8g==',
            'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'timeout': '30000',
            'v': '231012',
        }

    def _get_gt_and_challenge_and_random_id(self) -> Tuple[str, str, str]:
        response = requests.get('https://jzsc.mohurd.gov.cn/APi/webApi/geetest/startCaptcha', headers=self._headers)
        data = JZSC.decrypt(response.text).get('data', dict())
        return data.get('gt', ''), data.get('challenge', ''), data.get('randomId', '')

    def _pre_request(self, gt: str, challenge: str) -> None:
        #  2-1. 访问gettype.php接口
        params_2_1 = {
            'gt': gt,
            'callback': self._callback,
        }
        requests.get('https://api.geetest.com/gettype.php', params=params_2_1, headers=self._headers)
        #  2-2. 访问get.php接口
        params_2_2 = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            "w": "",
            "callback": self._callback
        }
        requests.get("https://api.geetest.com/get.php", params=params_2_2, headers=self._headers)
        #  2-3. 访问ajax.php接口
        params_2_3 = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            "callback": self._callback,
            "w": "",
        }
        requests.get("https://api.geevisit.com/ajax.php", params=params_2_3, headers=self._headers)

    def _get_pic_and_text(self, gt: str, challenge: str) -> Tuple[str, List[int], str]:
        params = {
            "is_next": "true",
            "type": "click",
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "https": "false",
            "protocol": "https://",
            "offline": "false",
            "product": "embed",
            "api_server": "api.geevisit.com",
            "isPC": "true",
            "autoReset": "true",
            "width": "100%",
            "callback": self._callback
        }
        response = requests.get("https://api.geevisit.com/get.php", params=params, headers=self._headers)
        data = json.loads(re.search(r"geetest_\d+\((.*?)\)", response.text).groups()[0]).get('data', dict())
        return data.get('pic'), data.get('c'), data.get('s')

    def _generate_positions(self, pic: str) -> str:
        pic = urljoin('https://static.geetest.com', pic)
        # todo 生成坐标位置
        return ''

    def _generate_w(self, pic: str, gt: str, challenge: str, c: List[int], s: str) -> str:
        positions = self._generate_positions(pic)
        # todo 逆向生成w参数的过程
        return ''

    def _get_validate_code(self, pic: str, gt: str, challenge: str, c: List[int], s: str) -> str:
        w = self._generate_w(pic, gt, challenge, c, s)
        params = {
            "gt": gt,
            "challenge": challenge,
            "lang": "zh-cn",
            "pt": "0",
            "client_type": "web",
            "w": w,
            "callback": self._callback
        }
        response = requests.get("https://api.geevisit.com/ajax.php", headers=self._headers, params=params)
        return response.json().get('validate')

    def _get_access_token(self, challenge: str, validate_code: str, random_id: str) -> str:
        # 1. 访问/geetest/verifyLoginCode
        params = {'geetest_challenge': challenge, 'geetest_validate': validate_code,
                  'geetest_seccode': "%s|jordan" % validate_code, 'randomId': random_id, 'session_key': None}
        response = requests.get(
            'https://jzsc.mohurd.gov.cn/APi/webApi/geetest/verifyLoginCode',
            params=params,
            headers=self._headers,
        )
        data = JZSC.decrypt(response.text).get('data')
        return data.get('accessToken')

    def process(self):
        # 1. 请求https://jzsc.mohurd.gov.cn/APi/webApi/geetest/startCaptcha获取gt和challenge
        gt, challenge, random_id = self._get_gt_and_challenge_and_random_id()
        # 2. 初始化请求
        self._pre_request(gt, challenge)
        # 3. 访问get.php获取图片和文字信息，获取pic, c, s这三个参数
        pic, c, s = self._get_pic_and_text(gt, challenge)
        # 4. 用第3步中的pic, c, s三个参数生成w参数，然后配合gt和challenge参数请求ajax.php获取validate参数
        validate_code = self._get_validate_code(pic, gt, challenge, c, s)
        # 5. 拿着validate参数生成accessToken参数
        access_token = self._get_access_token(challenge, validate_code, random_id)


if __name__ == '__main__':
    geetest = Geetest()
    print(geetest.process())
