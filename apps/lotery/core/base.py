import secrets
from collections import Counter
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    """彩票爬虫基类"""

    def __init__(self, url: str, params: Dict[str, str] = None):
        self.url = url
        self.params = params or {}
        self.headers: Dict[str, str] = {
            'authority': 'webapi.sporttery.cn',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'zh-CN,zh;q=0.9',
            'origin': 'https://static.sporttery.cn',
            'referer': 'https://static.sporttery.cn/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }

    @abstractmethod
    def _parse_draw_result(self, part: List[str]) -> tuple[List[int], List[int]]:
        """解析开奖结果，子类必须实现"""
        pass

    @abstractmethod
    def _validate_draw(self, front: List[int], back: List[int]) -> bool:
        """验证开奖结果，子类必须实现"""
        pass


class BaseAnalyzer(ABC):
    """彩票分析基类"""

    def __init__(self, draws: List[Dict[str, Any]], rule_engine_class, rule_classes: List):
        self.draws = draws
        self.rule_engine = rule_engine_class()
        self.rule_classes = rule_classes
        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认规则"""
        front_counter: Counter = Counter()
        back_counter: Counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        # 添加默认规则
        for rule_class in self.rule_classes:
            if rule_class.__name__ == 'HotColdRule':
                self.rule_engine.add_rule(rule_class(front_counter, back_counter))
            else:
                self.rule_engine.add_rule(rule_class())

    def add_custom_rule(self, rule):
        """添加自定义规则"""
        self.rule_engine.add_rule(rule)

    def _secrets_sample(self, population: List[int], k: int) -> List[int]:
        """安全采样k个不重复元素"""
        population = list(population)
        if k > len(population):
            raise ValueError("Sample larger than population")
        result = []
        pool = population[:]
        for _ in range(k):
            idx = secrets.randbelow(len(pool))
            result.append(pool.pop(idx))
        return result

    def _secrets_choice(self, population: List[int]) -> int:
        """安全随机选一个元素"""
        return population[secrets.randbelow(len(population))]

    @abstractmethod
    def recommend(self) -> Dict[str, List[int]]:
        """根据历史数据和规则生成推荐号码，子类必须实现"""
        pass

    def recommend_multi(self, count: int) -> List[Dict[str, List[int]]]:
        """
        一次生成多注推荐号码
        :param count: 生成注数
        :return: List[{'front': [...], 'back': [...]}]
        """
        results = []
        for _ in range(count):
            results.append(self.recommend())
        return results

    def get_hot_cold_numbers(self) -> Dict[str, Any]:
        """获取冷热号码统计"""
        front_counter: Counter = Counter()
        back_counter: Counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        return {
            'front_counter': front_counter,
            'back_counter': back_counter,
            'hot_front': [num for num, _ in front_counter.most_common(self.get_hot_front_count())],
            'cold_front': [num for num, _ in front_counter.most_common()[-self.get_cold_front_count():]],
            'hot_back': [num for num, _ in back_counter.most_common(self.get_hot_back_count())],
            'cold_back': [num for num, _ in back_counter.most_common()[-self.get_cold_back_count():]]
        }

    @abstractmethod
    def get_hot_front_count(self) -> int:
        """获取前区热号数量，子类必须实现"""
        pass

    @abstractmethod
    def get_cold_front_count(self) -> int:
        """获取前区冷号数量，子类必须实现"""
        pass

    @abstractmethod
    def get_hot_back_count(self) -> int:
        """获取后区热号数量，子类必须实现"""
        pass

    @abstractmethod
    def get_cold_back_count(self) -> int:
        """获取后区冷号数量，子类必须实现"""
        pass

    @abstractmethod
    def get_front_range(self) -> range:
        """获取前区号码范围，子类必须实现"""
        pass

    @abstractmethod
    def get_back_range(self) -> range:
        """获取后区号码范围，子类必须实现"""
        pass

    @abstractmethod
    def get_front_count(self) -> int:
        """获取前区号码数量，子类必须实现"""
        pass

    @abstractmethod
    def get_back_count(self) -> int:
        """获取后区号码数量，子类必须实现"""
        pass


class LotteryConfig:
    """彩票配置类"""

    def __init__(self,
                 name: str,
                 url: str,
                 params: Dict[str, str],
                 front_range: range,
                 back_range: range,
                 front_count: int,
                 back_count: int,
                 front_color: str,
                 back_color: str,
                 front_name: str,
                 back_name: str):
        self.name = name
        self.url = url
        self.params = params
        self.front_range = front_range
        self.back_range = back_range
        self.front_count = front_count
        self.back_count = back_count
        self.front_color = front_color
        self.back_color = back_color
        self.front_name = front_name
        self.back_name = back_name


# 预定义配置
DLT_CONFIG = LotteryConfig(
    name="大乐透",
    url="https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry",
    params={
        'gameNo': '85',
        'provinceId': '0',
        'pageSize': '30',
        'isVerify': '1',
        'pageNo': '1',
    },
    front_range=range(1, 36),
    back_range=range(1, 13),
    front_count=5,
    back_count=2,
    front_color="skyblue",
    back_color="lightcoral",
    front_name="红球",
    back_name="蓝球"
)

SSQ_CONFIG = LotteryConfig(
    name="双色球",
    url="https://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice",
    params={
        'name': 'ssq',
        'issueCount': '',
        'issueStart': '',
        'issueEnd': '',
        'dayStart': '',
        'dayEnd': '',
        'pageNo': '1',
        'pageSize': '30',
        'week': '',
        'systemType': 'PC',
    },
    front_range=range(1, 34),
    back_range=range(1, 17),
    front_count=6,
    back_count=1,
    front_color="red",
    back_color="blue",
    front_name="红球",
    back_name="蓝球"
)
