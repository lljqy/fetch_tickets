#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
彩票分析与推荐系统主程序
支持大乐透和双色球两种彩票类型
"""

import argparse
import os
import json
from datetime import datetime
from typing import List, Dict, Any

from analysis.dlt_analyzer import DLTCrawler, DLTAnalyzer
from analysis.ssq_analyzer import SSQCrawler, SSQAnalyzer
from visualization.dlt_visualizer import DLTVisualizer
from visualization.ssq_visualizer import SSQVisualizer
from core.rules import ExcludeNumbersRule, IncludeNumbersRule


class LotterySystem:
    """彩票系统主类"""

    def __init__(self, lottery_type: str = "ssq"):
        """
        初始化彩票系统
        :param lottery_type: 彩票类型，"ssq"为双色球，"dlt"为大乐透
        """
        self.lottery_type = lottery_type.lower()

        if self.lottery_type == "ssq":
            self.crawler_class = SSQCrawler
            self.analyzer_class = SSQAnalyzer
            self.visualizer_class = SSQVisualizer
            self.lottery_name = "双色球"
            self.prefix = "ssq"
        elif self.lottery_type == "dlt":
            self.crawler_class = DLTCrawler
            self.analyzer_class = DLTAnalyzer
            self.visualizer_class = DLTVisualizer
            self.lottery_name = "大乐透"
            self.prefix = "dlt"
        else:
            raise ValueError(f"不支持的彩票类型: {lottery_type}")

    def _create_output_directory(self) -> str:
        """
        创建输出目录
        :return: 输出目录路径
        """
        # 创建data目录
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # 创建子目录：彩票类型+时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub_dir = f"{self.prefix}_{timestamp}"
        output_dir = os.path.join(data_dir, sub_dir)
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        return output_dir

    def _save_recommendations(self, recommendations: List[Dict[str, List[int]]], output_dir: str):
        """
        保存推荐号码到文件
        :param recommendations: 推荐号码列表
        :param output_dir: 输出目录
        """
        # 保存为JSON格式
        json_file = os.path.join(output_dir, f"{self.prefix}_recommendations.json")
        recommendations_data = {
            "lottery_type": self.lottery_type,
            "lottery_name": self.lottery_name,
            "timestamp": datetime.now().isoformat(),
            "recommendations": recommendations
        }
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(recommendations_data, f, ensure_ascii=False, indent=2)
        
        print(f"推荐号码已保存为 {json_file}")
        
        # 保存为文本格式
        txt_file = os.path.join(output_dir, f"{self.prefix}_recommendations.txt")
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(f"{self.lottery_name}推荐号码\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for idx, rec in enumerate(recommendations, 1):
                f.write(f"第{idx}注：前区: {rec['front']}  后区: {rec['back']}\n")
        
        print(f"推荐号码已保存为 {txt_file}")

    def _save_analysis_summary(self, draws: List[Dict[str, Any]], recommendations: List[Dict[str, List[int]]], 
                              rule_analysis: List[Dict[str, Any]], output_dir: str):
        """
        保存分析摘要
        :param draws: 历史开奖数据
        :param recommendations: 推荐号码
        :param rule_analysis: 规则分析结果
        :param output_dir: 输出目录
        """
        summary_file = os.path.join(output_dir, f"{self.prefix}_analysis_summary.txt")
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"{self.lottery_name}分析摘要\n")
            f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # 历史数据摘要
            f.write("历史开奖数据:\n")
            f.write("-" * 30 + "\n")
            for d in draws:
                f.write(f"期号: {d['issue']}  前区: {d['front']}  后区: {d['back']}\n")
            f.write("\n")
            
            # 推荐号码
            f.write("推荐号码:\n")
            f.write("-" * 30 + "\n")
            for idx, rec in enumerate(recommendations, 1):
                f.write(f"第{idx}注：前区: {rec['front']}  后区: {rec['back']}\n")
            f.write("\n")
            
            # 规则符合性分析
            if rule_analysis:
                f.write("规则符合性分析:\n")
                f.write("-" * 30 + "\n")
                for analysis in rule_analysis:
                    f.write(f"\n第{analysis['注数']}注: 前区{analysis['前区']} + 后区{analysis['后区']}\n")
                    f.write(f"符合率: {analysis['符合率']:.1f}%\n")
                    if analysis['符合的规则']:
                        f.write(f"符合的规则: {', '.join(analysis['符合的规则'])}\n")
                    if analysis['不符合的规则']:
                        f.write(f"不符合的规则: {', '.join(analysis['不符合的规则'])}\n")
        
        print(f"分析摘要已保存为 {summary_file}")

    def run_analysis(self, periods: int = 10, bet_count: int = 5,
                     exclude_front: List[int] = None, exclude_back: List[int] = None,
                     include_front: List[int] = None, include_back: List[int] = None,
                     save_plots: bool = True) -> Dict[str, Any]:
        """
        运行完整的彩票分析流程
        :param periods: 分析期数
        :param bet_count: 推荐注数
        :param exclude_front: 排除的前区号码
        :param exclude_back: 排除的后区号码
        :param include_front: 必须包含的前区号码
        :param include_back: 必须包含的后区号码
        :param save_plots: 是否保存图表
        :return: 分析结果
        """
        print(f"=== {self.lottery_name}分析与推荐系统 ===")

        # 创建输出目录
        output_dir = self._create_output_directory()
        print(f"输出目录: {output_dir}")

        # 1. 爬取历史数据
        print(f"\n正在爬取最近{periods}期{self.lottery_name}开奖号码...")
        crawler = self.crawler_class()
        draws = crawler.fetch_latest_draws(periods)

        # 显示历史数据
        for d in draws:
            print(f"期号: {d['issue']}  前区: {d['front']}  后区: {d['back']}")

        # 2. 创建分析器
        analyzer = self.analyzer_class(draws)

        # 3. 添加自定义规则
        if exclude_front or exclude_back:
            analyzer.add_custom_rule(ExcludeNumbersRule(exclude_front, exclude_back))
            print(f"已添加排除规则: 前区{exclude_front or []}, 后区{exclude_back or []}")

        if include_front or include_back:
            analyzer.add_custom_rule(IncludeNumbersRule(include_front, include_back))
            print(f"已添加包含规则: 前区{include_front or []}, 后区{include_back or []}")

        # 4. 生成推荐号码
        print(f"\n根据历史数据和经验推荐的{bet_count}注号码:")
        recommendations = analyzer.recommend_multi(bet_count)

        for idx, rec in enumerate(recommendations, 1):
            print(f"第{idx}注：前区: {rec['front']}  后区: {rec['back']}")

        # 5. 保存推荐号码
        self._save_recommendations(recommendations, output_dir)

        # 6. 可视化分析
        rule_analysis = None
        if save_plots:
            print("\n正在生成可视化分析...")
            visualizer = self.visualizer_class(draws)

            # 号码频率图
            fig1 = visualizer.plot_number_frequency()
            fig1.savefig(os.path.join(output_dir, f'{self.prefix}_number_frequency.png'), dpi=300, bbox_inches='tight')
            print(f"号码频率图已保存为 {self.prefix}_number_frequency.png")

            # 和值趋势图
            fig2 = visualizer.plot_sum_trend()
            fig2.savefig(os.path.join(output_dir, f'{self.prefix}_sum_trend.png'), dpi=300, bbox_inches='tight')
            print(f"和值趋势图已保存为 {self.prefix}_sum_trend.png")

            # 推荐号码分析
            fig3 = visualizer.plot_recommendation_analysis(recommendations)
            fig3.savefig(os.path.join(output_dir, f'{self.prefix}_recommendation_analysis.png'), dpi=300, bbox_inches='tight')
            print(f"推荐号码分析图已保存为 {self.prefix}_recommendation_analysis.png")

            # 规则符合性分析
            print("正在分析规则符合性...")
            rule_analysis = visualizer.analyze_rule_compliance(recommendations, analyzer.rule_engine)

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
            fig4.savefig(os.path.join(output_dir, f'{self.prefix}_rule_compliance.png'), dpi=300, bbox_inches='tight')
            print(f"规则符合性分析图已保存为 {self.prefix}_rule_compliance.png")

        # 7. 保存分析摘要
        self._save_analysis_summary(draws, recommendations, rule_analysis or [], output_dir)

        return {
            'lottery_type': self.lottery_type,
            'lottery_name': self.lottery_name,
            'draws': draws,
            'recommendations': recommendations,
            'analyzer': analyzer,
            'output_dir': output_dir
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='彩票分析与推荐系统')
    parser.add_argument('--type', choices=['ssq', 'dlt'], default='ssq',
                        help='彩票类型: ssq(双色球) 或 dlt(大乐透)')
    parser.add_argument('--periods', type=int, default=10,
                        help='分析期数 (默认: 10)')
    parser.add_argument('--bets', type=int, default=5,
                        help='推荐注数 (默认: 5)')
    parser.add_argument('--exclude-front', type=int, nargs='+',
                        help='排除的前区号码')
    parser.add_argument('--exclude-back', type=int, nargs='+',
                        help='排除的后区号码')
    parser.add_argument('--include-front', type=int, nargs='+',
                        help='必须包含的前区号码')
    parser.add_argument('--include-back', type=int, nargs='+',
                        help='必须包含的后区号码')
    parser.add_argument('--no-plots', action='store_true',
                        help='不生成图表')

    args = parser.parse_args()

    try:
        # 创建彩票系统
        system = LotterySystem(args.type)
        print(args.exclude_front)

        # 运行分析
        result = system.run_analysis(
            periods=args.periods,
            bet_count=args.bets,
            exclude_front=args.exclude_front,
            exclude_back=args.exclude_back,
            include_front=args.include_front,
            include_back=args.include_back,
            save_plots=not args.no_plots
        )

        print(f"\n=== {system.lottery_name}分析完成 ===")
        print(f"所有文件已保存到: {result['output_dir']}")

    except Exception as e:
        print(f"运行出错: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
