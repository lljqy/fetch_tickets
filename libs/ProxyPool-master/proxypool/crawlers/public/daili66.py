from typing import Iterable

from pyquery import PyQuery as pq

from proxypool.schemas.proxy import Proxy
from proxypool.crawlers.base import BaseCrawler

MAX_PAGE = 3
BASE_URL = 'http://www.66ip.cn/{page}.html'


class DaiLi66Crawler(BaseCrawler):
    """
    http://www.66ip.cn/1.html
    """
    urls = [BASE_URL.format(page=page) for page in range(1, MAX_PAGE + 1)]

    @staticmethod
    def parse(html: str, *args, **kwargs) -> Iterable:
        """
        parse html file to get proxies
        :return:
        """
        doc = pq(html)
        trs = doc('.containerbox table tr:gt(0)').items()
        for tr in trs:
            host = tr.find('td:nth-child(1)').text()
            port = int(tr.find('td:nth-child(2)').text())
            yield Proxy(host=host, port=port)


if __name__ == '__main__':
    crawler = DaiLi66Crawler()
    for proxy in crawler.crawl():
        print(proxy)
