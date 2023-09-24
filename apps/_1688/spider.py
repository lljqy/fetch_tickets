# import requests
#
# cookies = {
#     'lid': 'kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF',
#     'ali_ab': '124.240.90.185.1694183494693.3',
#     'taklid': 'c6c99afae212415fbf83d7c968a98a26',
#     'cna': 'WKCNHR3+yy4CAXzwT92rAd41',
#     'ali_apache_track': 'c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1',
#     '__mwb_logon_id__': 'kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF',
#     'mwb': 'tm',
#     'xlly_s': '1',
#     '_m_h5_tk': '6879c772bb560f0a477beba6c95dcd8b_1695567145418',
#     '_m_h5_tk_enc': '5d0cabdd0d682fbaca023b8aca57a373',
#     '_csrf_token': '1695557512177',
#     'tfstk': 'dZbM4Bi-QG-15XM6mlL_S4twwMrpRATXdt3vHEp4YpJCkGpYfrVDKImq3q52ntXpddIYG5tVKQAw3qJwQBze1QnZ7s7vgZXB7ns9HdpDos6u98U8y116ley8ez3UuTTtCWCqyjuc1ET4eX342zf1en-20Gen8XSYEZVM-LcxBvxIU7lpt1Jnr6_H_X98PpgquwAGtLWwpDorDe0XTSQEcmtwOBvJjWn7R',
#     'l': 'fBaxAt_4Nq7n6qmQBO5Churza77tfIObzsPzaNbMiIEGa66v9FtvUNCtH2ScWdtjgTfcyetyCykutd3vyXaLRjDDBeYB9__gzxv9-bpU-L5..',
#     'isg': 'BPDwORcaYeOIIjwMqnlrMLfYwb5COdSDUrosq-p0As85pYRPnk0kEc_T_e1gNYxb',
# }
#
# headers = {
#     'authority': 'data.p4psearch.1688.com',
#     'accept': '*/*',
#     'accept-language': 'zh-CN,zh;q=0.9',
#     'cache-control': 'no-cache',
#     # 'cookie': 'lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF; ali_ab=124.240.90.185.1694183494693.3; taklid=c6c99afae212415fbf83d7c968a98a26; cna=WKCNHR3+yy4CAXzwT92rAd41; ali_apache_track=c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1; __mwb_logon_id__=kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF; mwb=tm; xlly_s=1; _m_h5_tk=6879c772bb560f0a477beba6c95dcd8b_1695567145418; _m_h5_tk_enc=5d0cabdd0d682fbaca023b8aca57a373; _csrf_token=1695557512177; tfstk=dZbM4Bi-QG-15XM6mlL_S4twwMrpRATXdt3vHEp4YpJCkGpYfrVDKImq3q52ntXpddIYG5tVKQAw3qJwQBze1QnZ7s7vgZXB7ns9HdpDos6u98U8y116ley8ez3UuTTtCWCqyjuc1ET4eX342zf1en-20Gen8XSYEZVM-LcxBvxIU7lpt1Jnr6_H_X98PpgquwAGtLWwpDorDe0XTSQEcmtwOBvJjWn7R; l=fBaxAt_4Nq7n6qmQBO5Churza77tfIObzsPzaNbMiIEGa66v9FtvUNCtH2ScWdtjgTfcyetyCykutd3vyXaLRjDDBeYB9__gzxv9-bpU-L5..; isg=BPDwORcaYeOIIjwMqnlrMLfYwb5COdSDUrosq-p0As85pYRPnk0kEc_T_e1gNYxb',
#     'pragma': 'no-cache',
#     'referer': 'https://p4psearch.1688.com/',
#     'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
#     'sec-ch-ua-mobile': '?0',
#     'sec-ch-ua-platform': '"Windows"',
#     'sec-fetch-dest': 'script',
#     'sec-fetch-mode': 'no-cors',
#     'sec-fetch-site': 'same-site',
#     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
# }
#
# params = {
#     'beginpage': '3',
#     'asyncreq': '1',
#     'keywords': '鞋包',
#     'sortType': '',
#     'descendOrder': '',
#     'province': '',
#     'city': '',
#     'priceStart': '',
#     'priceEnd': '',
#     'dis': '',
#     'ptid': 'hr8e0d635449befc',
#     'spm': 'a2638t.b_78128457.szyxdivert.7.3836436c8o3NM7',
#     'hpageId': 'old-sem-pc-list',
#     'cosite': 'baidujj_pz',
#     'trackid': '885662561117990122602',
#     'location': 're',
#     'exp': 'pcListImgSearch:A;zgc_tab:C',
#     'pageid': '2a626372LkZz0U',
#     'p4pid': 'a6646f1071537',
#     'salt': '16955592154975',
#     'sign': 'edad13791c061507edc0ad242949afd9',
#     'callback': 'jsonp_1695559215498_84894',
#     '_': '1695559215498',
# }
#
# response = requests.get(
#     'https://data.p4psearch.1688.com/data/ajax/get_premium_offer_list.json',
#     params=params,
#     cookies=cookies,
#     headers=headers,
# )


import requests

cookies = {
    'lid': 'kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF',
    'ali_ab': '124.240.90.185.1694183494693.3',
    'taklid': 'c6c99afae212415fbf83d7c968a98a26',
    'cna': 'WKCNHR3+yy4CAXzwT92rAd41',
    'ali_apache_track': 'c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1',
    '__mwb_logon_id__': 'kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF',
    'mwb': 'tm',
    'xlly_s': '1',
    '_m_h5_tk': '6879c772bb560f0a477beba6c95dcd8b_1695567145418',
    '_m_h5_tk_enc': '5d0cabdd0d682fbaca023b8aca57a373',
    '_csrf_token': '1695557512177',
    'tfstk': 'dZbM4Bi-QG-15XM6mlL_S4twwMrpRATXdt3vHEp4YpJCkGpYfrVDKImq3q52ntXpddIYG5tVKQAw3qJwQBze1QnZ7s7vgZXB7ns9HdpDos6u98U8y116ley8ez3UuTTtCWCqyjuc1ET4eX342zf1en-20Gen8XSYEZVM-LcxBvxIU7lpt1Jnr6_H_X98PpgquwAGtLWwpDorDe0XTSQEcmtwOBvJjWn7R',
    'l': 'fBaxAt_4Nq7n6qmQBO5Churza77tfIObzsPzaNbMiIEGa66v9FtvUNCtH2ScWdtjgTfcyetyCykutd3vyXaLRjDDBeYB9__gzxv9-bpU-L5..',
    'isg': 'BENDoTjbIrovSO8lVRiIWXAp0gftuNf6tesfAnUWxaYmNHdW8YznSKjiroTflC_y',
}

headers = {
    'authority': 'data.p4psearch.1688.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    # 'cookie': 'lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF; ali_ab=124.240.90.185.1694183494693.3; taklid=c6c99afae212415fbf83d7c968a98a26; cna=WKCNHR3+yy4CAXzwT92rAd41; ali_apache_track=c_mid=b2b-2222815911|c_lid=kkk%E6%96%B0%E6%89%8B%E4%B8%8A%E8%B7%AF|c_ms=1; __mwb_logon_id__=kkk%25E6%2596%25B0%25E6%2589%258B%25E4%25B8%258A%25E8%25B7%25AF; mwb=tm; xlly_s=1; _m_h5_tk=6879c772bb560f0a477beba6c95dcd8b_1695567145418; _m_h5_tk_enc=5d0cabdd0d682fbaca023b8aca57a373; _csrf_token=1695557512177; tfstk=dZbM4Bi-QG-15XM6mlL_S4twwMrpRATXdt3vHEp4YpJCkGpYfrVDKImq3q52ntXpddIYG5tVKQAw3qJwQBze1QnZ7s7vgZXB7ns9HdpDos6u98U8y116ley8ez3UuTTtCWCqyjuc1ET4eX342zf1en-20Gen8XSYEZVM-LcxBvxIU7lpt1Jnr6_H_X98PpgquwAGtLWwpDorDe0XTSQEcmtwOBvJjWn7R; l=fBaxAt_4Nq7n6qmQBO5Churza77tfIObzsPzaNbMiIEGa66v9FtvUNCtH2ScWdtjgTfcyetyCykutd3vyXaLRjDDBeYB9__gzxv9-bpU-L5..; isg=BENDoTjbIrovSO8lVRiIWXAp0gftuNf6tesfAnUWxaYmNHdW8YznSKjiroTflC_y',
    'pragma': 'no-cache',
    'referer': 'https://p4psearch.1688.com/',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'script',
    'sec-fetch-mode': 'no-cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
}

params = {
    'beginpage': '3',
    'asyncreq': '1',
    'keywords': '鞋包',
    'sortType': '',
    'descendOrder': '',
    'province': '',
    'city': '',
    'priceStart': '',
    'priceEnd': '',
    'dis': '',
    'ptid': 'hr8e0d635449befc',
    'spm': 'a2638t.b_78128457.szyxdivert.7.3836436c8o3NM7',
    'hpageId': 'old-sem-pc-list',
    'cosite': 'baidujj_pz',
    'trackid': '885662561117990122602',
    'location': 're',
    'exp': 'pcListImgSearch:A;zgc_tab:C',
    'pageid': '2a626372LkZz0U',
    'p4pid': 'a6646f1071537',
    'salt': '16955592206160',
    'sign': 'bd29fc8c94c255bbd70f6a75a3255a66',
    'callback': 'jsonp_1695559220617_15628',
    '_': '1695559220617',
}

# response = requests.get(
#     'https://data.p4psearch.1688.com/data/ajax/get_premium_offer_list.json',
#     params=params,
#     cookies=cookies,
#     headers=headers,
# )
response = requests.get(
    'https://detail.1688.com/offer/731224119433.html',
    # params=params,
    cookies=cookies,
    headers=headers,
)
text = response.text
print(text)
