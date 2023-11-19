import time
import uuid
import urllib3
import threading

import requests
from geolite2 import geolite2
from fake_headers import Headers


# 爬数据的线程类
class CrawlThread(threading.Thread):
    def __init__(
            self,
            proxy_ip: str,
            target_url: str = "https://bb.cf08tp.cn/Home/index.php?m=Index&a=vote&vid=335688&id=2676&tp="
    ) -> None:
        super(CrawlThread, self).__init__()
        self.proxy_ip = proxy_ip
        self._target_url = target_url

    @staticmethod
    def get_china_ip(ip: str = '127.0.0.1') -> bool:
        reader = geolite2.reader()
        ip_info = reader.get(ip)
        geolite2.close()
        if not ip_info:
            return False
        return True if ip_info['country']['iso_code'] == 'CN' else False

    def run(self):
        # 开始计时
        pure_ip_address = self.proxy_ip.split(':')[0]
        # 验证IP归属
        if not self.get_china_ip(pure_ip_address):
            # pass
            raise ValueError('不是有效IP')
        start = time.perf_counter()
        # 消除关闭证书验证的警告
        urllib3.disable_warnings()
        headers = Headers(headers=True).generate()
        headers['Referer'] = 'https://bb.cf08tp.cn/Home/index.php?m=Index&a=index&id=2676'
        headers['Pragma'] = 'no-cache'
        headers['Host'] = 'bb.cf08tp.cn'
        headers['x-forward-for'] = pure_ip_address
        headers['Cookie'] = 'PHPSESSID={}'.format(
            ''.join(str(uuid.uuid1()).split('-')))
        html = requests.get(
            headers=headers,
            url=self._target_url,
            proxies={
                "http": 'http://' + self.proxy_ip,
                "https": 'https://' + self.proxy_ip
            },
            verify=False,
            timeout=2
        ).content.decode()
        # 结束计时
        end = time.perf_counter()
        # 输出内容
        print(threading.current_thread().name + "使用代理IP, 耗时 " + str(
            end - start) + "毫秒 " + self.proxy_ip + " 获取到如下HTML内容：\n" + html + "\n*************")


# 获取代理IP的线程类
class GetIpThread(threading.Thread):
    def __init__(self, fetch_second: int, api_url: str = "http://127.0.0.1:5555/random") -> None:
        super(GetIpThread, self).__init__()
        self._api_url = api_url
        self.fetch_second = fetch_second

    def run(self) -> None:
        while True:
            # 获取IP列表
            res = requests.get(self._api_url).content.decode()
            # 按照\n分割获取到的IP
            ips = res.split('\n')
            # 利用每一个IP
            for proxy_ip in ips:
                if not proxy_ip.strip():
                    continue
                # 开启一个线程
                try:
                    CrawlThread(proxy_ip).run()
                    time.sleep(1.5)
                except Exception as e:
                    print(e)
            # 休眠
            time.sleep(len(ips) / self.fetch_second)


if __name__ == '__main__':
    # 获取IP的API接口
    api_url = "http://127.0.0.1:5555/random"
    # 要抓取的目标网站地址
    fetch_second = 5
    # 开始自动获取IP
    GetIpThread(fetch_second, api_url).start()
