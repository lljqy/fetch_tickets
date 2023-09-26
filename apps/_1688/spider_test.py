import json
import time
from secrets import choice

import requests
import pandas as pd

from utils.common import time_print
from apps._1688.constants import districts


class T1688Processor:
    cookies = {
        'lid': 'kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF',
        'ali_ab': '124.240.90.185.1694183494693.3',
        'taklid': 'c6c99afae212415fbf83d7c968a98a26',
        'xlly_s': '1',
        'cookie2': '1e1cd518a7c41b5ab6226a678123c54a',
        't': '5226f62d630e6501e3161b6b19fa0458',
        '_tb_token_': 'e7356ef77e113',
        'cna': 'WKCNHR3+yy4CAXzwT92rAd41',
        'cookie1': 'UteENY5glSGJU436H5DaRbCCV9fB9F1hfA%2FBunTie9g%3D',
        'cookie17': 'UUpjNF2nKV83sQ%3D%3D',
        'sgcookie': 'E1002iTYwiNNxgRWZi1%2B6zW%2BCIrWUUJPGi68ZpXb4s0%2BqkaOmJ%2BhiAvy2Ab2yz8ejv5Dp7EGbS%2FLwx0%2B9%2BpRqSw0KSq61vrcLve52eD52qtIWOtnS2pV23mSFtrZLJgLTBZNItYZ38pbpLKtCP8pTIdnUg%3D%3D',
        'sg': '%E8%B7%AF1e',
        'csg': '0d07fe9c',
        'unb': '2222815911',
        'uc4': 'id4=0%40U2gp9GiXprAPmiX33S3Ip%2Fh8j7Rn&nk4=0%40Crm6yTdJOuTu2rmHtDrt%2FH3micnFmA%3D%3D',
        '__cn_logon__': 'true',
        '__cn_logon_id__': 'kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF',
        'ali_apache_track': 'c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1',
        'ali_apache_tracktmp': 'c_w_signed=Y',
        '_nk_': 'kkk%5Cu65B0%5Cu624B%5Cu4E0A%5Cu8DEF',
        'last_mid': 'b2b-2222815911',
        '_csrf_token': '1694937989013',
        '__mwb_logon_id__': 'kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF',
        'mwb': 'tm',
        '_m_h5_tk': '56f1c3acba5a1a184e6f84225b334afb_1694952302552',
        '_m_h5_tk_enc': '3a6be2d702535ac2995dae5ddf1c1209',
        'keywordsHistory': '%E5%A5%B3%E8%A3%85',
        'tfstk': 'duFp28gqoGjnC3BSWpBGUxKSks_ieWUU6kzXZ0mHFlETPc0BFQO7B0E_XDOh8ub82oE0K4cItLp8mzjetwWEF0EEjuAu-7ewwrzztwll8XzEabscmsq88ylrkHS_w_cF4mLGjifciyy1s8Ihmw7mv1I_Jn85fUAuZJ3CUsXEdPTrk2HK2Qm9wcVBivobRcd5czXaDSVxXsKmD4vCWNpyUvgNDD_rd',
        'l': 'fBaxAt_4Nq7n6g6FXO5Cnurza77O5QRbzsPzaNbMiIEGa1uAdQWZXNCta3IJfdtjgT5AKetyVhmX9dFvPuzLRx_7x_tLARjSHtJw8e99ki6A.',
        'isg': 'BFZW70TWLyf-ghp-wGd1In2-pwxY95oxdDXAPsC9rTmlg_QdKIPVQTw1Gx9vK5JJ',
    }

    headers = {
        'authority': 'search.1688.com',
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        # 'cookie': 'lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF; ali_ab=124.240.90.185.1694183494693.3; taklid=c6c99afae212415fbf83d7c968a98a26; xlly_s=1; cookie2=1e1cd518a7c41b5ab6226a678123c54a; t=5226f62d630e6501e3161b6b19fa0458; _tb_token_=e7356ef77e113; cna=WKCNHR3+yy4CAXzwT92rAd41; cookie1=UteENY5glSGJU436H5DaRbCCV9fB9F1hfA%2FBunTie9g%3D; cookie17=UUpjNF2nKV83sQ%3D%3D; sgcookie=E1002iTYwiNNxgRWZi1%2B6zW%2BCIrWUUJPGi68ZpXb4s0%2BqkaOmJ%2BhiAvy2Ab2yz8ejv5Dp7EGbS%2FLwx0%2B9%2BpRqSw0KSq61vrcLve52eD52qtIWOtnS2pV23mSFtrZLJgLTBZNItYZ38pbpLKtCP8pTIdnUg%3D%3D; sg=%E8%B7%AF1e; csg=0d07fe9c; unb=2222815911; uc4=id4=0%40U2gp9GiXprAPmiX33S3Ip%2Fh8j7Rn&nk4=0%40Crm6yTdJOuTu2rmHtDrt%2FH3micnFmA%3D%3D; __cn_logon__=true; __cn_logon_id__=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF; ali_apache_track=c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1; ali_apache_tracktmp=c_w_signed=Y; _nk_=kkk%5Cu65B0%5Cu624B%5Cu4E0A%5Cu8DEF; last_mid=b2b-2222815911; _csrf_token=1694937989013; __mwb_logon_id__=kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF; mwb=tm; _m_h5_tk=56f1c3acba5a1a184e6f84225b334afb_1694952302552; _m_h5_tk_enc=3a6be2d702535ac2995dae5ddf1c1209; keywordsHistory=%E5%A5%B3%E8%A3%85; tfstk=duFp28gqoGjnC3BSWpBGUxKSks_ieWUU6kzXZ0mHFlETPc0BFQO7B0E_XDOh8ub82oE0K4cItLp8mzjetwWEF0EEjuAu-7ewwrzztwll8XzEabscmsq88ylrkHS_w_cF4mLGjifciyy1s8Ihmw7mv1I_Jn85fUAuZJ3CUsXEdPTrk2HK2Qm9wcVBivobRcd5czXaDSVxXsKmD4vCWNpyUvgNDD_rd; l=fBaxAt_4Nq7n6g6FXO5Cnurza77O5QRbzsPzaNbMiIEGa1uAdQWZXNCta3IJfdtjgT5AKetyVhmX9dFvPuzLRx_7x_tLARjSHtJw8e99ki6A.; isg=BFZW70TWLyf-ghp-wGd1In2-pwxY95oxdDXAPsC9rTmlg_QdKIPVQTw1Gx9vK5JJ',
        'origin': 'https://s.1688.com',
        'pragma': 'no-cache',
        'referer': 'https://s.1688.com/',
        'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36',
    }

    def __init__(self):
        self.results = list()
        self.names = {'province': '生产省份', 'city': '生产城市', 'biz_type': '企业类型', 'send_province': '发货城市',
                      'send_city': '货品简介', 'factory': '工厂名称', 'factory_url': '工厂网址', 'simple_subject': '网店主题',
                      'brief': '物品简称', 'original_price': '成本价', 'consign_price': '市场价', 'per_month_quantity': '月销量',
                      'quantity': '总销量', 'sale_money': '销售总额'}

    def _fetch(self) -> None:
        params = {
            'keywords': 'Ůװ',
            'beginPage': '0',
            'async': 'true',
            'asyncCount': '20',
            'pageSize': '60',
            'startIndex': '0',
            'pageName': 'major',
            'offset': '8',
            'sessionId': '43c3aa3a7f414874846b0c24ff19c3d8',
        }

        for province, cities in districts.items():
            for city in cities:
                params.__setitem__('province', province)
                params.__setitem__('city', city)
                begin_page = 1
                while begin_page <= 5:
                    try:
                        params.__setitem__('beginPage', str(begin_page))
                        response = requests.get(
                            'https://search.1688.com/service/marketOfferResultViewService',
                            params=params,
                            cookies=self.cookies,
                            headers=self.headers,
                        )
                        data_list = json.loads(response.text).get('data').get('data').get('offerList')
                        for item_dict in data_list:
                            cur = dict()
                            try:
                                cur.__setitem__('province', item_dict.get('company').get('province'))
                                cur.__setitem__('city', item_dict.get('company').get('city'))
                                cur.__setitem__('biz_type', item_dict.get('company').get('bizTypeName'))
                                cur.__setitem__('send_province', item_dict.get('information').get('sendProvince'))
                                cur.__setitem__('send_city', item_dict.get('information').get('sendCity'))
                                cur.__setitem__('factory', item_dict.get('company').get('name'))
                                cur.__setitem__('factory_url', item_dict.get('company').get('url'))
                                cur.__setitem__('simple_subject', item_dict.get('information').get('simpleSubject'))
                                cur.__setitem__('brief', item_dict.get('information').get('brief'))
                                cur.__setitem__('original_price',
                                                item_dict.get('tradePrice').get('offerPrice').get('originalValue').get(
                                                    'integer'))
                                cur.__setitem__('consign_price',
                                                item_dict.get('tradePrice').get('offerPrice').get('priceInfo').get(
                                                    'consignPrice'))
                                cur.__setitem__('per_month_quantity',
                                                item_dict.get('tradeQuantity').get('quantitySumMonth'))
                                cur.__setitem__('quantity', item_dict.get('tradeQuantity').get('saleQuantity'))
                                if item_dict.get('tradeQuantity').get('gmvValue'):
                                    cur.__setitem__('sale_money',
                                                    item_dict.get('tradeQuantity').get('gmvValue').get('integer'))
                                else:
                                    cur.__setitem__('sale_money', 0)
                            except Exception as _:
                                print(_)
                            self.results.append(cur)
                        time_print(f"{province}-{city}:{begin_page}, 爬取完毕")
                        begin_page += 1
                        time.sleep(choice((1, 2)))
                    except Exception as _:
                        time_print(f'{province}-{city}:{begin_page}，爬取停止，{_}')
                        break

    def _clean(self) -> None:
        UNKNOWN_PRICE = '-1.00'
        # df_results = pd.read_excel("./data/results.xlsx")
        df_results = pd.DataFrame(self.results)
        df_results.rename(columns=self.names, inplace=True)
        # df_results['市场价'] = df_results['市场价'].astype(float)
        df_results.drop_duplicates(inplace=True)
        self.results = df_results.to_dict(orient='records')

    def _persistent(self, path: str) -> None:
        df_results = pd.DataFrame(self.results)
        df_results.to_excel(path, index=False)

    def run(self) -> None:
        self._fetch()
        self._clean()
        self._persistent('./data/女装.xlsx')


if __name__ == '__main__':
    t = T1688Processor()
    t.run()
