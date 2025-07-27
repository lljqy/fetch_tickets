from typing import List
from collections import Counter
from abc import ABC, abstractmethod


class Rule(ABC):
    """规则基类"""

    @abstractmethod
    def check(self, front: List[int], back: List[int]) -> bool:
        """检查号码是否满足规则"""
        pass


class OddEvenRule(Rule):
    """奇偶均衡规则"""

    def __init__(self, front_odd_range: tuple = (2, 3), back_odd_count: int = 1):
        self.front_odd_range = front_odd_range
        self.back_odd_count = back_odd_count

    def check(self, front: List[int], back: List[int]) -> bool:
        front_odd = sum(1 for x in front if x % 2 == 1)
        back_odd = sum(1 for x in back if x % 2 == 1)
        return (self.front_odd_range[0] <= front_odd <= self.front_odd_range[1] and
                back_odd == self.back_odd_count)


class IntervalRule(Rule):
    """区间分布规则"""

    def __init__(self, intervals: List[tuple] = None):
        # 默认三段：1-12, 13-24, 25-35
        self.intervals = intervals or [(1, 12), (13, 24), (25, 35)]

    def check(self, front: List[int], back: List[int]) -> bool:
        counts = [0] * len(self.intervals)
        for x in front:
            for i, (start, end) in enumerate(self.intervals):
                if start <= x <= end:
                    counts[i] += 1
                    break
        return min(counts) > 0


class ConsecutiveRule(Rule):
    """连号限制规则"""

    def __init__(self, max_consecutive: int = 2):
        self.max_consecutive = max_consecutive

    def check(self, front: List[int], back: List[int]) -> bool:
        front_sorted = sorted(front)
        max_consecutive = 1
        cur = 1
        for i in range(1, len(front_sorted)):
            if front_sorted[i] == front_sorted[i - 1] + 1:
                cur += 1
                max_consecutive = max(max_consecutive, cur)
            else:
                cur = 1
        return max_consecutive <= self.max_consecutive


class SumRangeRule(Rule):
    """和值范围规则"""

    def __init__(self, front_sum_range: tuple = (70, 150), back_sum_range: tuple = (8, 18)):
        self.front_sum_range = front_sum_range
        self.back_sum_range = back_sum_range

    def check(self, front: List[int], back: List[int]) -> bool:
        front_sum = sum(front)
        back_sum = sum(back)
        return (self.front_sum_range[0] <= front_sum <= self.front_sum_range[1] and
                self.back_sum_range[0] <= back_sum <= self.back_sum_range[1])


class HotColdRule(Rule):
    """冷热搭配规则"""

    def __init__(self, front_counter: Counter, back_counter: Counter):
        self.front_counter = front_counter
        self.back_counter = back_counter

    def check(self, front: List[int], back: List[int]) -> bool:
        # 前区：至少包含1个热号和1个冷号
        hot_front = [num for num, _ in self.front_counter.most_common(10)]
        cold_front = [num for num, _ in self.front_counter.most_common()[-10:]]
        has_hot = any(x in hot_front for x in front)
        has_cold = any(x in cold_front for x in front)

        # 后区：1热1冷
        hot_back = [num for num, _ in self.back_counter.most_common(6)]
        cold_back = [num for num, _ in self.back_counter.most_common()[-6:]]
        back_hot = any(x in hot_back for x in back)
        back_cold = any(x in cold_back for x in back)

        return has_hot and has_cold and back_hot and back_cold


class RuleEngine:
    """规则引擎"""

    def __init__(self):
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        """添加规则"""
        self.rules.append(rule)

    def check_all(self, front: List[int], back: List[int]) -> bool:
        """检查所有规则"""
        return all(rule.check(front, back) for rule in self.rules)


# 示例自定义规则
class ExcludeNumbersRule(Rule):
    """排除指定号码规则"""

    def __init__(self, exclude_front: List[int] = None, exclude_back: List[int] = None):
        self.exclude_front = set(exclude_front or [])
        self.exclude_back = set(exclude_back or [])

    def check(self, front: List[int], back: List[int]) -> bool:
        return not any(x in self.exclude_front for x in front) and not any(x in self.exclude_back for x in back)


class IncludeNumbersRule(Rule):
    """必须包含指定号码规则"""

    def __init__(self, include_front: List[int] = None, include_back: List[int] = None):
        self.include_front = set(include_front or [])
        self.include_back = set(include_back or [])

    def check(self, front: List[int], back: List[int]) -> bool:
        front_has = all(x in front for x in self.include_front)
        back_has = all(x in back for x in self.include_back)
        return front_has and back_has


# 双色球特有规则
class RedBlueBalanceRule(Rule):
    """红蓝球平衡规则"""

    def __init__(self, red_high_prob: float = 0.7):
        # 红球高概率出现，蓝球相对随机
        self.red_high_prob = red_high_prob

    def check(self, front: List[int], back: List[int]) -> bool:
        # 检查前区是否有高概率号码（1-16区间）
        high_prob_count = sum(1 for x in front if 1 <= x <= 16)
        # 双色球前区6个，建议2-4个在1-16区间
        return 2 <= high_prob_count <= 4


class GapRule(Rule):
    """号码间隔规则"""

    def __init__(self, min_gap: int = 2, max_gap: int = 8):
        self.min_gap = min_gap
        self.max_gap = max_gap

    def check(self, front: List[int], back: List[int]) -> bool:
        front_sorted = sorted(front)
        for i in range(1, len(front_sorted)):
            gap = front_sorted[i] - front_sorted[i - 1]
            if gap < self.min_gap or gap > self.max_gap:
                return False
        return True


# 规则工厂类
class RuleFactory:
    """规则工厂，用于创建不同彩票类型的规则"""
    
    @staticmethod
    def create_dlt_rules():
        """创建大乐透规则"""
        return [
            OddEvenRule(front_odd_range=(2, 3), back_odd_count=1),
            IntervalRule(intervals=[(1, 12), (13, 24), (25, 35)]),
            ConsecutiveRule(max_consecutive=2),
            SumRangeRule(front_sum_range=(70, 150), back_sum_range=(8, 18))
        ]
    
    @staticmethod
    def create_ssq_rules():
        """创建双色球规则"""
        return [
            OddEvenRule(front_odd_range=(2, 4), back_odd_count=1),
            IntervalRule(intervals=[(1, 8), (9, 16), (17, 24), (25, 33)]),
            ConsecutiveRule(max_consecutive=3),
            SumRangeRule(front_sum_range=(90, 180), back_sum_range=(1, 16)),
            RedBlueBalanceRule(),
            GapRule(min_gap=2, max_gap=8)
        ] 