import secrets
from collections import Counter
from typing import List, Dict, Any

import requests
from dlt_rules import Rule, RuleEngine, OddEvenRule, IntervalRule, ConsecutiveRule, SumRangeRule, HotColdRule
from dlt_visualizer import DLTVisualizer

DLT_URL: str = "https://webapi.sporttery.cn/gateway/lottery/getHistoryPageListV1.qry"
FRONT_RANGE: range = range(1, 36)
BACK_RANGE: range = range(1, 13)


class DLTCrawler:
    """
    大乐透历史数据爬虫
    """

    def __init__(self, url: str = DLT_URL):
        self.url = url
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
        self.params: Dict[str, str] = {
            'gameNo': '85',
            'provinceId': '0',
            'pageSize': '30',
            'isVerify': '1',
            'pageNo': '1',
        }

    def fetch_latest_draws(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        获取最近n期大乐透开奖号码
        :param n: 期数，最大30
        :return: [{'issue': 期号, 'front': [5个前区], 'back': [2个后区]}, ...]
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
            front_part, back_part = part[:5], part[5:]
            front: List[int] = list(map(lambda x: int(x), front_part))
            back: List[int] = list(map(lambda x: int(x), back_part))
            if len(front) == 5 and len(back) == 2:
                draws.append({'issue': issue, 'front': front, 'back': back})
            if len(draws) >= n:
                break
        return draws


class DLTAnalyzer:
    """
    大乐透号码分析与推荐
    """

    def __init__(self, draws: List[Dict[str, Any]]):
        self.draws = draws
        self.rule_engine = RuleEngine()
        self._setup_default_rules()

    def _setup_default_rules(self):
        """设置默认规则"""
        front_counter: Counter = Counter()
        back_counter: Counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        # 添加默认规则
        self.rule_engine.add_rule(OddEvenRule())
        self.rule_engine.add_rule(IntervalRule())
        self.rule_engine.add_rule(ConsecutiveRule())
        self.rule_engine.add_rule(SumRangeRule())
        self.rule_engine.add_rule(HotColdRule(front_counter, back_counter))

    def add_custom_rule(self, rule: Rule):
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

    def recommend(self) -> Dict[str, List[int]]:
        """
        根据历史数据和规则生成推荐号码
        :return: {'front': [5个前区], 'back': [2个后区]}
        """
        front_counter: Counter = Counter()
        back_counter: Counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        hot_front: List[int] = [num for num, _ in front_counter.most_common(10)]
        cold_front: List[int] = [num for num, _ in front_counter.most_common()[-10:]]
        all_front: set = set(FRONT_RANGE)
        warm_front: List[int] = list(all_front - set(hot_front) - set(cold_front))
        all_back: set = set(BACK_RANGE)
        hot_back: List[int] = [num for num, _ in back_counter.most_common(6)]
        cold_back: List[int] = [num for num, _ in back_counter.most_common()[-6:]]
        warm_back: List[int] = list(all_back - set(hot_back) - set(cold_back))

        for _ in range(100):  # 最多尝试100次
            # 前区选号
            front: List[int] = []
            if len(hot_front) >= 2:
                front += self._secrets_sample(hot_front, 2)
            if len(warm_front) >= 2:
                front += self._secrets_sample(warm_front, 2)
            if len(cold_front) >= 1:
                front += self._secrets_sample(cold_front, 1)
            while len(front) < 5:
                rest: List[int] = list(all_front - set(front))
                front.append(self._secrets_choice(rest))
            front.sort()

            # 后区选号
            back: List[int] = []
            if len(hot_back) > 0 and len(cold_back) > 0:
                b1 = self._secrets_sample(hot_back, 1)[0]
                b2 = self._secrets_sample([x for x in cold_back if x != b1], 1)[0] if len(
                    cold_back) > 1 or b1 not in cold_back else self._secrets_sample(warm_back, 1)[0]
                back = [b1, b2]
            else:
                back = self._secrets_sample(list(all_back), 2)
            back = list(set(back))  # 防止万一重复
            while len(back) < 2:
                rest = list(all_back - set(back))
                back.append(self._secrets_choice(rest))
            back.sort()

            # 检查所有规则
            if self.rule_engine.check_all(front, back):
                return {"front": front, "back": back}

        # 如果100次都不满足，返回最后一次
        return {"front": front, "back": back}

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


def main() -> None:
    n_ = 7
    multi_count = 5  # 生成5注
    show_visualization = True  # 是否显示可视化

    crawler = DLTCrawler()
    draws: List[Dict[str, Any]] = crawler.fetch_latest_draws(n_)
    print(f"正在爬取最近{n_}期大乐透开奖号码...")
    for d in draws:
        print(f"期号: {d['issue']}  前区: {d['front']}  后区: {d['back']}")
    print(f"\n根据历史数据和经验推荐的{multi_count}注号码:")
    analyzer = DLTAnalyzer(draws)

    # 示例：添加自定义规则
    # from dlt_rules import ExcludeNumbersRule, IncludeNumbersRule
    # analyzer.add_custom_rule(ExcludeNumbersRule(exclude_front=[1,2,3], exclude_back=[12]))
    # analyzer.add_custom_rule(IncludeNumbersRule(include_front=[8], include_back=[5]))

    recs: List[Dict[str, List[int]]] = analyzer.recommend_multi(multi_count)
    for idx, rec in enumerate(recs, 1):
        print(f"第{idx}注：前区: {rec['front']}  后区: {rec['back']}")

    # 可视化分析
    if show_visualization:
        print("\n正在生成可视化分析...")
        visualizer = DLTVisualizer(draws)

        # 号码频率图
        fig1 = visualizer.plot_number_frequency()
        fig1.savefig('number_frequency.png', dpi=300, bbox_inches='tight')
        print("号码频率图已保存为 number_frequency.png")

        # 和值趋势图
        fig2 = visualizer.plot_sum_trend()
        fig2.savefig('sum_trend.png', dpi=300, bbox_inches='tight')
        print("和值趋势图已保存为 sum_trend.png")

        # 推荐号码分析
        fig3 = visualizer.plot_recommendation_analysis(recs)
        fig3.savefig('recommendation_analysis.png', dpi=300, bbox_inches='tight')
        print("推荐号码分析图已保存为 recommendation_analysis.png")

        # 规则符合性分析
        print("正在分析规则符合性...")
        rule_analysis = visualizer.analyze_rule_compliance(recs, analyzer.rule_engine)

        # 打印规则符合性分析结果
        print("\n=== 规则符合性分析 ===")
        for analysis in rule_analysis:
            print(f"\n第{analysis['注数']}注: 前区{analysis['前区']} + 后区{analysis['后区']}")
            print(f"符合率: {analysis['符合率']:.1f}%")
            if analysis['符合的规则']:
                print(f"符合的规则: {', '.join(analysis['符合的规则'])}")
            if analysis['不符合的规则']:
                print(f"不符合的规则: {', '.join(analysis['不符合的规则'])}")

        # 生成规则符合性分析图
        fig4 = visualizer.plot_rule_compliance(rule_analysis)
        fig4.savefig('rule_compliance.png', dpi=300, bbox_inches='tight')
        print("规则符合性分析图已保存为 rule_compliance.png")

        # 显示图表
        # plt.show() # This line was commented out as per the new_code, as plt is not imported.


if __name__ == "__main__":
    main()
