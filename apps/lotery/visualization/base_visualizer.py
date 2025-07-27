from collections import Counter
from typing import List, Dict, Any
from abc import ABC, abstractmethod

import matplotlib.pyplot as plt
import numpy as np

from core.rules import RuleEngine

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False


class BaseVisualizer(ABC):
    """彩票可视化基类"""

    def __init__(self, draws: List[Dict[str, Any]], front_range: range, back_range: range):
        self.draws = draws
        self.front_range = front_range
        self.back_range = back_range

    def plot_number_frequency(self, figsize=(15, 10)):
        """绘制号码出现频率图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # 统计频率
        front_counter = Counter()
        back_counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        # 前区频率图
        front_nums = list(self.front_range)
        front_freqs = [front_counter.get(num, 0) for num in front_nums]

        ax1.bar(front_nums, front_freqs, color=self.get_front_color(), alpha=0.7)
        ax1.set_title(f'前区{self.get_front_name()}出现频率', fontsize=14, fontweight='bold')
        ax1.set_xlabel('号码')
        ax1.set_ylabel('出现次数')
        ax1.grid(True, alpha=0.3)

        # 后区频率图
        back_nums = list(self.back_range)
        back_freqs = [back_counter.get(num, 0) for num in back_nums]

        ax2.bar(back_nums, back_freqs, color=self.get_back_color(), alpha=0.7)
        ax2.set_title(f'后区{self.get_back_name()}出现频率', fontsize=14, fontweight='bold')
        ax2.set_xlabel('号码')
        ax2.set_ylabel('出现次数')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_sum_trend(self, figsize=(12, 8)):
        """绘制和值趋势图"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)

        # 计算和值
        front_sums = [sum(d["front"]) for d in self.draws]
        back_sums = [sum(d["back"]) for d in self.draws]
        issues = [d["issue"] for d in self.draws]

        # 前区和值趋势
        ax1.plot(issues, front_sums, 'o-', color=self.get_front_color(), linewidth=2, markersize=6)
        ax1.set_title(f'前区{self.get_front_name()}和值趋势', fontsize=14, fontweight='bold')
        ax1.set_xlabel('期号')
        ax1.set_ylabel('和值')
        ax1.grid(True, alpha=0.3)

        # 后区和值趋势
        ax2.plot(issues, back_sums, 'o-', color=self.get_back_color(), linewidth=2, markersize=6)
        ax2.set_title(f'后区{self.get_back_name()}和值趋势', fontsize=14, fontweight='bold')
        ax2.set_xlabel('期号')
        ax2.set_ylabel('和值')
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def analyze_rule_compliance(self, recommendations: List[Dict[str, List[int]]], rule_engine: RuleEngine) -> List[Dict[str, Any]]:
        """
        分析推荐号码的规则符合性
        :param recommendations: 推荐号码列表
        :param rule_engine: 规则引擎
        :return: 每注号码的规则符合性分析结果
        """
        results = []

        for i, rec in enumerate(recommendations, 1):
            front = rec["front"]
            back = rec["back"]

            rule_analysis = {
                "注数": i,
                "前区": front,
                "后区": back,
                "符合的规则": [],
                "不符合的规则": [],
                "符合率": 0.0
            }

            # 检查每个规则
            for rule in rule_engine.rules:
                rule_name = rule.__class__.__name__
                if rule.check(front, back):
                    rule_analysis["符合的规则"].append(rule_name)
                else:
                    rule_analysis["不符合的规则"].append(rule_name)

            # 计算符合率
            total_rules = len(rule_engine.rules)
            if total_rules > 0:
                rule_analysis["符合率"] = len(rule_analysis["符合的规则"]) / total_rules * 100

            results.append(rule_analysis)

        return results

    def plot_rule_compliance(self, rule_analysis: List[Dict[str, Any]], figsize=(15, 12)):
        """绘制规则符合性分析图"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # 1. 符合率柱状图
        compliance_rates = [analysis["符合率"] for analysis in rule_analysis]
        bet_numbers = [f"第{analysis['注数']}注" for analysis in rule_analysis]

        bars = ax1.bar(bet_numbers, compliance_rates,
                       color=['green' if rate >= 80 else 'orange' if rate >= 60 else 'red' for rate in
                              compliance_rates])
        ax1.set_title('各注号码规则符合率', fontweight='bold')
        ax1.set_ylabel('符合率 (%)')
        ax1.set_ylim(0, 100)
        ax1.grid(True, alpha=0.3)

        # 添加数值标签
        for bar, rate in zip(bars, compliance_rates):
            ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                     f'{rate:.1f}%', ha='center', va='bottom')

        # 2. 规则符合情况热力图
        rule_names = set()
        for analysis in rule_analysis:
            rule_names.update(analysis["符合的规则"])
            rule_names.update(analysis["不符合的规则"])
        rule_names = sorted(list(rule_names))

        compliance_matrix = []
        for analysis in rule_analysis:
            row = []
            for rule_name in rule_names:
                if rule_name in analysis["符合的规则"]:
                    row.append(1)  # 符合
                else:
                    row.append(0)  # 不符合
            compliance_matrix.append(row)

        im = ax2.imshow(compliance_matrix, cmap='RdYlGn', aspect='auto')
        ax2.set_title('规则符合情况热力图', fontweight='bold')
        ax2.set_xlabel('规则')
        ax2.set_ylabel('注数')
        ax2.set_xticks(range(len(rule_names)))
        ax2.set_xticklabels(rule_names, rotation=45, ha='right')
        ax2.set_yticks(range(len(bet_numbers)))
        ax2.set_yticklabels(bet_numbers)

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax2)
        cbar.set_ticks([0, 1])
        cbar.set_ticklabels(['不符合', '符合'])

        # 3. 详细规则分析
        ax3.text(0.05, 0.95, "详细规则分析:", transform=ax3.transAxes, fontsize=12, fontweight='bold')
        y_pos = 0.85

        for analysis in rule_analysis:
            text = f"第{analysis['注数']}注: 前区{analysis['前区']} + 后区{analysis['后区']}"
            ax3.text(0.05, y_pos, text, transform=ax3.transAxes, fontsize=10, fontweight='bold')
            y_pos -= 0.04

            if analysis["符合的规则"]:
                text = f"  符合: {', '.join(analysis['符合的规则'])}"
                ax3.text(0.05, y_pos, text, transform=ax3.transAxes, fontsize=9, color='green')
                y_pos -= 0.03

            if analysis["不符合的规则"]:
                text = f"  不符合: {', '.join(analysis['不符合的规则'])}"
                ax3.text(0.05, y_pos, text, transform=ax3.transAxes, fontsize=9, color='red')
                y_pos -= 0.03

            text = f"  符合率: {analysis['符合率']:.1f}%"
            ax3.text(0.05, y_pos, text, transform=ax3.transAxes, fontsize=9)
            y_pos -= 0.04

        ax3.set_title('规则符合性详情', fontweight='bold')
        ax3.axis('off')

        # 4. 统计摘要
        total_bets = len(rule_analysis)
        avg_compliance = np.mean(compliance_rates)
        max_compliance = max(compliance_rates)
        min_compliance = min(compliance_rates)

        # 统计各规则的符合情况
        rule_stats = {}
        for rule_name in rule_names:
            rule_stats[rule_name] = sum(1 for analysis in rule_analysis if rule_name in analysis["符合的规则"])

        stats_text = f"""
统计摘要:
- 总注数: {total_bets}注
- 平均符合率: {avg_compliance:.1f}%
- 最高符合率: {max_compliance:.1f}%
- 最低符合率: {min_compliance:.1f}%

各规则符合情况:
"""
        for rule_name, count in rule_stats.items():
            percentage = count / total_bets * 100
            stats_text += f"- {rule_name}: {count}/{total_bets} ({percentage:.1f}%)\n"

        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=9,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax4.set_title('规则符合性统计', fontweight='bold')
        ax4.axis('off')

        plt.tight_layout()
        return fig

    def plot_recommendation_analysis(self, recommendations: List[Dict[str, List[int]]], figsize=(15, 10)):
        """分析推荐号码在趋势中的位置"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        # 历史数据统计
        front_sums = [sum(d["front"]) for d in self.draws]
        back_sums = [sum(d["back"]) for d in self.draws]

        # 推荐号码统计
        rec_front_sums = [sum(rec["front"]) for rec in recommendations]
        rec_back_sums = [sum(rec["back"]) for rec in recommendations]

        # 前区和值分布对比
        ax1.hist(front_sums, bins=15, alpha=0.6, color='lightcoral', label='历史数据', density=True)
        ax1.hist(rec_front_sums, bins=5, alpha=0.8, color=self.get_front_color(), label='推荐号码', density=True)
        ax1.set_title(f'前区{self.get_front_name()}和值分布对比', fontweight='bold')
        ax1.set_xlabel('和值')
        ax1.set_ylabel('密度')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # 后区和值分布对比
        ax2.hist(back_sums, bins=10, alpha=0.6, color='lightblue', label='历史数据', density=True)
        ax2.hist(rec_back_sums, bins=3, alpha=0.8, color=self.get_back_color(), label='推荐号码', density=True)
        ax2.set_title(f'后区{self.get_back_name()}和值分布对比', fontweight='bold')
        ax2.set_xlabel('和值')
        ax2.set_ylabel('密度')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # 推荐号码详情
        ax3.text(0.05, 0.95, "推荐号码详情:", transform=ax3.transAxes, fontsize=12, fontweight='bold')
        y_pos = 0.85
        for i, rec in enumerate(recommendations, 1):
            front_sum = sum(rec["front"])
            back_sum = sum(rec["back"])
            text = f"第{i}注: 前区{rec['front']}(和值:{front_sum}) + 后区{rec['back']}(和值:{back_sum})"
            ax3.text(0.05, y_pos, text, transform=ax3.transAxes, fontsize=10)
            y_pos -= 0.08
        ax3.set_title('推荐号码统计', fontweight='bold')
        ax3.axis('off')

        # 统计摘要
        stats_text = f"""
统计摘要:
- 分析期数: {len(self.draws)}期
- 推荐注数: {len(recommendations)}注
- 历史前区和值范围: {min(front_sums)}-{max(front_sums)}
- 推荐前区和值范围: {min(rec_front_sums)}-{max(rec_front_sums)}
- 历史后区和值范围: {min(back_sums)}-{max(back_sums)}
- 推荐后区和值范围: {min(rec_back_sums)}-{max(rec_back_sums)}
        """
        ax4.text(0.05, 0.95, stats_text, transform=ax4.transAxes, fontsize=10,
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        ax4.set_title('统计摘要', fontweight='bold')
        ax4.axis('off')

        plt.tight_layout()
        return fig

    def plot_number_distribution(self, figsize=(15, 8)):
        """绘制号码分布图"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

        # 统计每个号码的出现次数
        front_counter = Counter()
        back_counter = Counter()
        for d in self.draws:
            front_counter.update(d["front"])
            back_counter.update(d["back"])

        # 前区号码分布
        front_nums = list(self.front_range)
        front_freqs = [front_counter.get(num, 0) for num in front_nums]
        
        # 按频率排序
        sorted_front = sorted(zip(front_nums, front_freqs), key=lambda x: x[1], reverse=True)
        top_front_nums, top_front_freqs = zip(*sorted_front[:10])
        
        ax1.bar(range(len(top_front_nums)), top_front_freqs, color=self.get_front_color(), alpha=0.7)
        ax1.set_title(f'前区{self.get_front_name()}出现频率TOP10', fontweight='bold')
        ax1.set_xlabel('号码')
        ax1.set_ylabel('出现次数')
        ax1.set_xticks(range(len(top_front_nums)))
        ax1.set_xticklabels(top_front_nums)
        ax1.grid(True, alpha=0.3)

        # 后区号码分布
        back_nums = list(self.back_range)
        back_freqs = [back_counter.get(num, 0) for num in back_nums]
        
        # 按频率排序
        sorted_back = sorted(zip(back_nums, back_freqs), key=lambda x: x[1], reverse=True)
        top_back_nums, top_back_freqs = zip(*sorted_back[:8])
        
        ax2.bar(range(len(top_back_nums)), top_back_freqs, color=self.get_back_color(), alpha=0.7)
        ax2.set_title(f'后区{self.get_back_name()}出现频率TOP8', fontweight='bold')
        ax2.set_xlabel('号码')
        ax2.set_ylabel('出现次数')
        ax2.set_xticks(range(len(top_back_nums)))
        ax2.set_xticklabels(top_back_nums)
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    @abstractmethod
    def get_front_color(self) -> str:
        """获取前区颜色，子类必须实现"""
        pass

    @abstractmethod
    def get_back_color(self) -> str:
        """获取后区颜色，子类必须实现"""
        pass

    @abstractmethod
    def get_front_name(self) -> str:
        """获取前区名称，子类必须实现"""
        pass

    @abstractmethod
    def get_back_name(self) -> str:
        """获取后区名称，子类必须实现"""
        pass 