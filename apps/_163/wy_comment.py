import json
from typing import Dict, List
from datetime import datetime

import execjs
import requests
import pandas as pd

from utils.common import _time_print


class WYComment:
    cookies = {
        '__bid_n': '1838e6beb899881c564207',
        'FPTOKEN': 'hs+MOkdXwJzNFRH8z7k5zGBKGp7lG46J8GyM9oEztAe0pEe19J0v1EA74rR+oIN2pscTRWl/cCrHWI6F4+Q510EH1FrnE6ldnOjJ3SNZCC3hri/klD4SVS6DykxHoc6GVyZaUQzzbjG0ew7EvwTK0y23l4fk93UyGPPrNeOOLLPkK0G1tFsRQeISOyZ94VP3HTg3x5QzQk8lII7UiYIq3zGzE/dUFhh+JdZZdp11aaEVzjnv+l75ooXk3Se+PgKZ4xGGqum6uBPFySvjybQjglEqhMoEkPTSsW8JvLPw2fzJlDksNUZwobEstC7rMyQ7ke5BczW3TDyJLkALp44fnZJXM0p+/HuIL16CN8vJvUXDrwWwsX8+uW17JQp+b7+C48f5IJ7BzFVMogvamggzfA==|HuW4diam2WRui/pbbBdZGG8b/d147Ky8/wqpqi7NLQc=|10|8889f14ad98c29a8a3bd0b88b51a2798',
        'NMTID': '00OifJDAzeB11WwgEIpl07TCm4rBFkAAAGKxZuqxA',
        'JSESSIONID-WYYY': 'rMF9VT7%2Fno8RtJGbzHudrqX0x9MCD%2BQyfC9%5C1nsWB%5Cu2HJob2Hwu9vRes5kIzuVI3VN6MqU%2Fp0U%5CgbnNzwaZqA84ShKhwQRevxbzpkkW6v45Aobha6SkxqQF7Rrds%2FAJwg8DKS0B3xkVGJiZgSXj0dgANHTaE39vC4EPuY0w%2B7XWUl5E%3A1695534233493',
        '_iuqxldmzr_': '32',
        '_ntes_nnid': 'a5dc27faf4ff63bc8ec1de282d597fef,1695532433531',
        '_ntes_nuid': 'a5dc27faf4ff63bc8ec1de282d597fef',
        'WEVNSM': '1.0.0',
        'WNMCID': 'acdbzl.1695532433768.01.0',
        'WM_NI': 'uns83JIFTusV1r4koH83clYu%2FQ6M39xoYk2XWzrbNbQjQnL%2FviFPgwHEbIHZVLT3dZHlvYGXJ6ztdh09yma1i2QU6w97bA%2BJaWuw4QMdh7oT9dFoawyDoOJAHPS0bt2BZFg%3D',
        'WM_NIKE': '9ca17ae2e6ffcda170e2e6eeadbc53abaabfaeb365a2b48ab2d84f839b8b86d162909ffd99f73daca6af85cb2af0fea7c3b92ab7b2bdd9b2428b9a9c96f25ef3aefc8cee44fcedad8ddc7fed8ffaaeb233bcb1978cb15495a6be83cd6a93b69f8fcf25b6b78ab1e67d8c9baeaacb5296949cd4e7528cb4babac6548aeab695e764f4e7b78ee43babee9fb6b57dfbe9aea2aa42a389bb98b75b8fbca8d8ee60fbbc8a90e47dbb9ca1b0c94b8c909dd1e180f29e96a7e637e2a3',
        'WM_TID': 'ZJOHSNdF7EhEVUVUUVfUifBi1ouxyaZH',
        'sDeviceId': 'YD-Vel1t79k3LNEEkVQVEOAmKAih4%2F45sWx',
    }

    headers = {
        'authority': 'music.163.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': '__bid_n=1838e6beb899881c564207; FPTOKEN=hs+MOkdXwJzNFRH8z7k5zGBKGp7lG46J8GyM9oEztAe0pEe19J0v1EA74rR+oIN2pscTRWl/cCrHWI6F4+Q510EH1FrnE6ldnOjJ3SNZCC3hri/klD4SVS6DykxHoc6GVyZaUQzzbjG0ew7EvwTK0y23l4fk93UyGPPrNeOOLLPkK0G1tFsRQeISOyZ94VP3HTg3x5QzQk8lII7UiYIq3zGzE/dUFhh+JdZZdp11aaEVzjnv+l75ooXk3Se+PgKZ4xGGqum6uBPFySvjybQjglEqhMoEkPTSsW8JvLPw2fzJlDksNUZwobEstC7rMyQ7ke5BczW3TDyJLkALp44fnZJXM0p+/HuIL16CN8vJvUXDrwWwsX8+uW17JQp+b7+C48f5IJ7BzFVMogvamggzfA==|HuW4diam2WRui/pbbBdZGG8b/d147Ky8/wqpqi7NLQc=|10|8889f14ad98c29a8a3bd0b88b51a2798; NMTID=00OifJDAzeB11WwgEIpl07TCm4rBFkAAAGKxZuqxA; JSESSIONID-WYYY=rMF9VT7%2Fno8RtJGbzHudrqX0x9MCD%2BQyfC9%5C1nsWB%5Cu2HJob2Hwu9vRes5kIzuVI3VN6MqU%2Fp0U%5CgbnNzwaZqA84ShKhwQRevxbzpkkW6v45Aobha6SkxqQF7Rrds%2FAJwg8DKS0B3xkVGJiZgSXj0dgANHTaE39vC4EPuY0w%2B7XWUl5E%3A1695534233493; _iuqxldmzr_=32; _ntes_nnid=a5dc27faf4ff63bc8ec1de282d597fef,1695532433531; _ntes_nuid=a5dc27faf4ff63bc8ec1de282d597fef; WEVNSM=1.0.0; WNMCID=acdbzl.1695532433768.01.0; WM_NI=uns83JIFTusV1r4koH83clYu%2FQ6M39xoYk2XWzrbNbQjQnL%2FviFPgwHEbIHZVLT3dZHlvYGXJ6ztdh09yma1i2QU6w97bA%2BJaWuw4QMdh7oT9dFoawyDoOJAHPS0bt2BZFg%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6eeadbc53abaabfaeb365a2b48ab2d84f839b8b86d162909ffd99f73daca6af85cb2af0fea7c3b92ab7b2bdd9b2428b9a9c96f25ef3aefc8cee44fcedad8ddc7fed8ffaaeb233bcb1978cb15495a6be83cd6a93b69f8fcf25b6b78ab1e67d8c9baeaacb5296949cd4e7528cb4babac6548aeab695e764f4e7b78ee43babee9fb6b57dfbe9aea2aa42a389bb98b75b8fbca8d8ee60fbbc8a90e47dbb9ca1b0c94b8c909dd1e180f29e96a7e637e2a3; WM_TID=ZJOHSNdF7EhEVUVUUVfUifBi1ouxyaZH; sDeviceId=YD-Vel1t79k3LNEEkVQVEOAmKAih4%2F45sWx',
        'nm-gcore-status': '1',
        'origin': 'https://music.163.com',
        'pragma': 'no-cache',
        'referer': 'https://music.163.com/playlist?id=11860849',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    }

    params = {
        'csrf_token': '',
    }
    EMPTY = ''

    def __init__(self, js_path: str) -> None:
        self._js = self._get_js(js_path)

    def _get_js(self, js_path: str) -> execjs.ExternalRuntime.Context:
        with open(js_path, mode='r') as f:
            js_code = execjs.compile(f.read())
        return js_code

    def _encrypt(self, params: Dict[str, str]) -> Dict[str, str]:
        p1 = json.dumps(params, ensure_ascii=False)
        p2 = '010001'
        p3 = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        p4 = '0CoJUm6Qyw8W8jud'
        data = self._js.call('d', p1, p2, p3, p4)
        return {
            'params': data['encText'],
            'encSecKey': data['encSecKey']
        }

    def _deep_get(self, name: str, d: Dict) -> str:
        ans = self.EMPTY
        for k in name.split('.'):
            d = d.get(k, dict())
            if isinstance(d, dict) and not d:
                return self.EMPTY
            ans = d
        return ans

    def _parse(self, comments: List[Dict]) -> pd.DataFrame:
        columns = ['ip_location', 'nick_name', 'content', 'user_avatar_url', 'time']
        raws = ['ipLocation.location', 'user.nickname', 'content', 'user.avatarUrl', 'time']
        ans = list()
        for comment in comments:
            cur = dict()
            for index, column in enumerate(columns):
                cur[column] = self._deep_get(raws[index], comment)
            ans.append(cur)
        df_results = pd.DataFrame(ans, columns=columns)
        df_results.loc[:, 'time'] = df_results['time'].apply(lambda x: datetime.fromtimestamp(x / 1000))
        return df_results

    def parse_to_file(self) -> None:
        _time_print("开始爬取")
        data = {"rid": "A_PL_0_11860849", "threadId": "A_PL_0_11860849", "pageNo": 1, "pageSize": 20,
                "cursor": "-1", "offset": 0, "orderType": 1, "csrf_token": self.EMPTY}
        cursor = -1
        start = 1
        limit = 20
        df_result = pd.DataFrame()
        total = None
        while True:
            data.update({
                'pageNo': start,
                'pageSize': limit,
                'cursor': str(cursor),
            })
            response = requests.post(
                'https://music.163.com/weapi/comment/resource/comments/get',
                params=self.params,
                cookies=self.cookies,
                headers=self.headers,
                data=self._encrypt(data),
            )
            result = json.loads(response.text)
            d = result.get('data', dict())
            if total is None:
                total = d.get('totalCount', -1)
            comments = d.get('comments', list())
            counts = df_result.shape[0]
            if not comments and total > 0 and counts >= total:
                _time_print(f"第{start}页有重复的, {counts}行")
                break
            df_comments = self._parse(comments)
            df_result = pd.concat([df_result, df_comments]).drop_duplicates()
            cursor = d.get('cursor', comments[-1].get('time', '-1'))
            start += 1
        _time_print("结束爬取")
        df_result.drop_duplicates().to_excel('./data/周杰伦-网易评论.xlsx', index=False)


if __name__ == '__main__':
    wy = WYComment("./js/decrypt.js")
    wy.parse_to_file()
