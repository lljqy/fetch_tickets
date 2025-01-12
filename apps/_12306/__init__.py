import requests

x = {'Accept': '*/*',
 'Accept-Encoding': 'gzip, deflate',
 'BIGipServerotn': '1389953290.64545.0000',
 'BIGipServerpassport': '988283146.50215.0000',
 'Connection': 'keep-alive',
 'JSESSIONID': 'F403D88AB0705C27FBBF9EFB1C4A48A9',
 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
               '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
 '_jc_save_fromDate': '2025-01-10',
 '_jc_save_fromStation': '%u5317%u4eac%2CNone',
 '_jc_save_showIns': 'true',
 '_jc_save_toDate': '2025-01-01',
 '_jc_save_toStation': '%u5e7f%u5dde%2CNone',
 '_jc_save_wfdc_flag': 'dc',
 '_passport_session': 'ce6f1af7f5cb46a0a445c83b6e85422d2983',
 '_uab_collina': '173177021080196427966096',
 'cursorStatus': 'off',
 'guidesStatus': 'off',
 'highContrastMode': 'defaltMode',
 'route': 'c5c62a339e7744272a54643b3be5bf64',
 'tk': '4--H-yEnx8cse3KCeGIk6ExJurubCbBQCx7FGgbcl1l0',
 'uKey': 'a7220698c260fb6318587862e87494cee4a880f4ed1a9354f2280da75a6db02d',
 'uamtk': 'TQIYTSNjiQzuji1POCe3CRpTAMrZ7q9BkZ5oMw64l1l0'}

cookies = {
    '_uab_collina': '173177021080196427966096',
    'JSESSIONID': 'D1DC87B0408D7895990FDDC8083C91F0',
    'tk': '612SlI7fkRDOoH-c4thB9Ekf-YleC-fGmbYIeQubl1l0',
    '_jc_save_wfdc_flag': 'dc',
    'guidesStatus': 'off',
    'highContrastMode': 'defaltMode',
    'cursorStatus': 'off',
    '_jc_save_fromDate': '2025-01-10',
    '_jc_save_showIns': 'true',
    '_jc_save_toDate': '2025-01-01',
    'BIGipServerotn': '1557725450.24610.0000',
    'BIGipServerpassport': '988283146.50215.0000',
    'route': '495c805987d0f5c8c84b14f60212447d',
    'uKey': 'd7af4812b1e59e4f4d5e538fa43d6f51d040f42c3f8b4b46b2600fedce614fa8',
    '_jc_save_fromStation': '%u5317%u4EAC%2CBXP',
    '_jc_save_toStation': '%u5E7F%u5DDE%2CIZQ',
}

headers = {
    'Host': 'kyfw.12306.cn',
    'Cache-Control': 'max-age=0',
    'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'https://kyfw.12306.cn',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-User': '?1',
    'Sec-Fetch-Dest': 'document',
    'Referer': 'https://kyfw.12306.cn/otn/leftTicket/init?random=1735720732850',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    # 'Cookie': '_uab_collina=173177021080196427966096; JSESSIONID=D1DC87B0408D7895990FDDC8083C91F0; tk=612SlI7fkRDOoH-c4thB9Ekf-YleC-fGmbYIeQubl1l0; _jc_save_wfdc_flag=dc; guidesStatus=off; highContrastMode=defaltMode; cursorStatus=off; _jc_save_fromDate=2025-01-10; _jc_save_showIns=true; _jc_save_toDate=2025-01-01; BIGipServerotn=1557725450.24610.0000; BIGipServerpassport=988283146.50215.0000; route=495c805987d0f5c8c84b14f60212447d; uKey=d7af4812b1e59e4f4d5e538fa43d6f51d040f42c3f8b4b46b2600fedce614fa8; _jc_save_fromStation=%u5317%u4EAC%2CBXP; _jc_save_toStation=%u5E7F%u5DDE%2CIZQ',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    '_json_att': '',
}

# response = requests.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc', cookies=cookies, headers=headers, data=data, verify=False)
# html = response.text
# print(html)
