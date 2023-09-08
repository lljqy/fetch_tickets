import time
from typing import List

import requests
from lxml import etree
from fake_useragent import UserAgent


class ProxyHandler:

    def __init__(self):
        self._wait_time = 1
        self._ua = UserAgent()
        self._headers = dict()

    def get_latest_kdl_free_ips(self, limit: int = 30, browser: str = 'chrome') -> List[str]:
        """
        获取快代理上面的免费的代理ip
        :param limit:
        :param browser:
        :return:
        """
        page = 1
        results = set()
        while len(results) < limit:
            self._headers.__setitem__("User-Agent", getattr(self._ua, browser))
            response = requests.get(
                url=f"https://www.kuaidaili.com/free/inha/{page}",
                headers=self._headers,
                verify=False
            )
            html = etree.HTML(response.text)
            table_datas = html.xpath("//td[@data-title='IP' or @data-title='PORT']")
            n = len(table_datas)
            for index in range(0, n, 2):
                url = f"http://{table_datas[index].text}:{table_datas[index + 1].text}"
                results.add(url)
            time.sleep(self._wait_time)
            page += 1
        return list(results)
