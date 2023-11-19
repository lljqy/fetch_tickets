import json
from typing import Iterable

from proxypool.schemas.proxy import Proxy

from proxypool.crawlers.base import BaseCrawler

BASE_URL = 'http://proxylist.fatezero.org/proxy.list'


class FateZeroCrawler(BaseCrawler):
    """
    FateZero crawler,http://proxylist.fatezero.org
    """
    urls = [BASE_URL]

    def parse(self, html: str, *args, **kwargs) -> Iterable:
        """
        parse html file to get proxies
        :return:
        """

        hosts_ports = html.split('\n')
        for addr in hosts_ports:
            if (addr):
                ip_address = json.loads(addr)
                host = ip_address['host']
                port = ip_address['port']
                yield Proxy(host=host, port=port)


if __name__ == '__main__':
    crawler = FateZeroCrawler()
    for proxy in crawler.crawl():
        print(proxy)
