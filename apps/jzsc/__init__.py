import requests

cookies = {
    'Hm_lvt_b1b4b9ea61b6f1627192160766a9c55c': '1699107222,1699279591,1699487520,1699539078',
    'Hm_lpvt_b1b4b9ea61b6f1627192160766a9c55c': '1699543268',
}

headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Connection': 'keep-alive',
    # 'Cookie': 'Hm_lvt_b1b4b9ea61b6f1627192160766a9c55c=1699107222,1699279591,1699487520,1699539078; Hm_lpvt_b1b4b9ea61b6f1627192160766a9c55c=1699543268',
    'Referer': 'https://jzsc.mohurd.gov.cn/data/company/detail?id=002105291239452167',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'accessToken': 'jkFXxgu9TcpocIyCKmJ+tfpxe/45B9dbWMUXhdY7vLV0kkqvDiGSAa9LMcpJ5iYrhpUUKvcMtoMqfGfwdLCb8g==',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'timeout': '30000',
    'v': '231012',
}

params = {
    'compId': '002105291239452167',
}

response = requests.get(
    'https://jzsc.mohurd.gov.cn/APi/webApi/dataservice/query/comp/compDetail',
    params=params,
    cookies=cookies,
    headers=headers,
)
print(response.text)