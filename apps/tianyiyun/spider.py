from pprint import pprint
from urllib.parse import quote

import execjs
import requests


class TianYiYun:
    _headers = {
        'authority': 'www.ctyun.cn',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': 'ct_tgc=2971417f-9cc5-4b4a-9426-833c668899ae; ct_m_track=source_baidubrand-medium_cpt-content_se899252; ct_m_sid1=1701441048697-BfADoRAZ7h; ct_m_sid2=1701441048697-BfADoRAZ7h; vid=LHpyRlbsuSo0wfRohavqc09VDWnxwcJns06Qx6ptCLVNm8SU7qMGq8gn4ZGaNjZf; Hm_lvt_4b4ce93f1c92033213556e55cb65769f=1701441049; Hm_lpvt_4b4ce93f1c92033213556e55cb65769f=1701441052; ct_m_cat2_id=10000.0.3; ct_m_cat2_time=1701441103273; ct_m_label_id=4; ct_m_pvid=6; JSESSIONID=goeh00kkucii1pjjly726clg5',
        'origin': 'https://www.ctyun.cn',
        'referer': 'https://www.ctyun.cn/h5/auth/login',
        'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'x-ctyun-accesstoken': 'null',
        'x-riskdevicesign': 'b15dc300a7c4f8950c94fe8811a947cf',
    }

    def __init__(self):
        self._session = requests.session()

    def _encrypt_pwd(self, user: str, pwd: str) -> str:
        user += '0' * (24 - len(user))
        with open('./js/decrypt.js', 'r') as f:
            js = execjs.compile(f.read())
        return js.call('Ke', user, pwd, 1, 0, 0, 1)

    def login(self, user: str, pwd: str) -> None:
        data = {
            'id': user,
            'loginFree': 'false',
            'loginType': 'password',
            'newMode': 'true',
            'other': quote(user),
            # 'password': 'NTMek6oprfM=',
            'password': self._encrypt_pwd(quote(user), pwd),
        }
        print(data['password'])
        response = self._session.post('https://www.ctyun.cn/gw/auth/Login', headers=self._headers, data=data)
        pprint(response.json())

    def crawl(self):
        pass


if __name__ == '__main__':
    tyy = TianYiYun()
    tyy.login('lllj_sf', 'llj*963.')
    # tyy.login('234555551@qq.com', 'fffffffffff....666')
