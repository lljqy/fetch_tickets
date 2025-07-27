import secrets
from typing import List, Dict, Any

import requests

from core.base import BaseCrawler, BaseAnalyzer, DLT_CONFIG
from core.rules import RuleEngine, HotColdRule, RuleFactory


class DLTCrawler(BaseCrawler):
    """大乐透历史数据爬虫"""

    def __init__(self, url: str = DLT_CONFIG.url):
        super().__init__(url, DLT_CONFIG.params)

    def fetch_latest_draws(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近n期开奖号码
        :param n: 期数，最大30
        :return: [{'issue': 期号, 'front': [前区号码], 'back': [后区号码]}, ...]
        """
        resp: requests.Response = requests.get(self.url, params=self.params, headers=self.headers, timeout=10)
        resp.raise_for_status()
        data: Dict[str, Any] = resp.json()
        draws: List[Dict[str, Any]] = []
        result_list = data.get('value', {}).get('list', [])

        for item in result_list[:n]:
            issue: str = item.get('lotteryDrawNum', '')
            front_str: str = item.get('lotteryDrawResult', '')
            part = front_str.split(' ')

            # 子类实现具体的解析逻辑
            front, back = self._parse_draw_result(part)

            if self._validate_draw(front, back):
                draws.append({'issue': issue, 'front': front, 'back': back})
            if len(draws) >= n:
                break
        return draws

    def _parse_draw_result(self, part: List[str]) -> tuple[List[int], List[int]]:
        """解析大乐透开奖结果"""
        front_part, back_part = part[:5], part[5:]  # 大乐透：前区5个，后区2个
        front: List[int] = list(map(lambda x: int(x), front_part))
        back: List[int] = list(map(lambda x: int(x), back_part))
        return front, back

    def _validate_draw(self, front: List[int], back: List[int]) -> bool:
        """验证大乐透开奖结果"""
        return len(front) == 5 and len(back) == 2  # 大乐透：前区5个，后区2个


class DLTAnalyzer(BaseAnalyzer):
    """大乐透号码分析与推荐"""

    def __init__(self, draws: List[Dict[str, Any]]):
        # 使用规则工厂创建大乐透规则
        rule_classes = [HotColdRule]  # HotColdRule需要特殊处理
        super().__init__(draws, RuleEngine, rule_classes)
        
        # 添加大乐透特有规则
        for rule in RuleFactory.create_dlt_rules():
            self.rule_engine.add_rule(rule)

    def _get_excluded_numbers(self) -> tuple[set[int], set[int]]:
        """获取被排除的号码"""
        exclude_front = set()
        exclude_back = set()
        
        for rule in self.rule_engine.rules:
            if hasattr(rule, 'exclude_front'):
                exclude_front.update(rule.exclude_front)
            if hasattr(rule, 'exclude_back'):
                exclude_back.update(rule.exclude_back)
        
        return exclude_front, exclude_back

    def recommend(self) -> Dict[str, List[int]]:
        """
        根据历史数据和规则生成推荐号码
        :return: {'front': [5个前区], 'back': [2个后区]}
        """
        hot_cold_data = self.get_hot_cold_numbers()
        hot_front = hot_cold_data['hot_front']
        cold_front = hot_cold_data['cold_front']
        hot_back = hot_cold_data['hot_back']
        cold_back = hot_cold_data['cold_back']
        
        # 获取被排除的号码
        exclude_front, exclude_back = self._get_excluded_numbers()
        
        # 从可用号码中排除被排除的号码
        all_front: set = set(self.get_front_range()) - exclude_front
        all_back: set = set(self.get_back_range()) - exclude_back
        
        # 更新热冷号码，排除被排除的号码
        hot_front = [x for x in hot_front if x not in exclude_front]
        cold_front = [x for x in cold_front if x not in exclude_front]
        warm_front: List[int] = list(all_front - set(hot_front) - set(cold_front))
        
        hot_back = [x for x in hot_back if x not in exclude_back]
        cold_back = [x for x in cold_back if x not in exclude_back]
        warm_back: List[int] = list(all_back - set(hot_back) - set(cold_back))

        for _ in range(100):  # 最多尝试100次
            # 前区选号（大乐透需要5个）
            front: List[int] = []
            if len(hot_front) >= 2:
                front += self._secrets_sample(hot_front, 2)
            if len(warm_front) >= 2:
                front += self._secrets_sample(warm_front, 2)
            if len(cold_front) >= 1:
                front += self._secrets_sample(cold_front, 1)
            while len(front) < 5:  # 大乐透前区需要5个
                rest: List[int] = list(all_front - set(front))
                if not rest:  # 如果没有可用号码了，跳出循环
                    break
                front.append(self._secrets_choice(rest))
            front.sort()

            # 后区选号（大乐透需要2个）
            back: List[int] = []
            if len(hot_back) > 0 and len(cold_back) > 0:
                b1 = self._secrets_sample(hot_back, 1)[0]
                b2 = self._secrets_sample([x for x in cold_back if x != b1], 1)[0] if len(
                    cold_back) > 1 or b1 not in cold_back else self._secrets_sample(warm_back, 1)[0]
                back = [b1, b2]
            else:
                available_back = list(all_back)
                if len(available_back) >= 2:
                    back = self._secrets_sample(available_back, 2)
            back = list(set(back))  # 防止万一重复
            while len(back) < 2:
                rest = list(all_back - set(back))
                if not rest:  # 如果没有可用号码了，跳出循环
                    break
                back.append(self._secrets_choice(rest))
            back.sort()

            # 检查所有规则
            if self.rule_engine.check_all(front, back):
                return {"front": front, "back": back}

        # 如果100次都不满足，返回最后一次（但确保不包含被排除的号码）
        if not front or not back:
            # 如果生成失败，返回最简单的组合
            available_front = list(all_front)[:5]
            available_back = list(all_back)[:2]
            return {"front": sorted(available_front), "back": sorted(available_back)}
        
        return {"front": front, "back": back}

    def get_hot_front_count(self) -> int:
        return 10

    def get_cold_front_count(self) -> int:
        return 10

    def get_hot_back_count(self) -> int:
        return 6

    def get_cold_back_count(self) -> int:
        return 6

    def get_front_range(self) -> range:
        return DLT_CONFIG.front_range

    def get_back_range(self) -> range:
        return DLT_CONFIG.back_range

    def get_front_count(self) -> int:
        return DLT_CONFIG.front_count

    def get_back_count(self) -> int:
        return DLT_CONFIG.back_count 