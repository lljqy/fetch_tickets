# 彩票分析与推荐系统

这是一个基于Python的彩票分析与推荐系统，支持大乐透和双色球两种彩票类型。

## 项目结构

```
lotery/
├── base_lottery.py              # 基础类，封装公共代码
├── dlt_crawler_and_predict.py   # 大乐透爬虫和预测（原始版本）
├── dlt_rules.py                 # 大乐透规则引擎
├── dlt_visualizer.py            # 大乐透可视化
├── ssq_crawler_and_predict.py   # 双色球爬虫和预测（原始版本）
├── ssq_rules.py                 # 双色球规则引擎
├── ssq_visualizer.py            # 双色球可视化
├── ssq_refactored.py            # 双色球重构版本（使用基础类）
└── README.md                    # 项目说明文档
```

## 代码架构

### 1. 基础类设计 (`base_lottery.py`)

为了提高代码的可维护性，我们设计了以下基础类：

- **BaseLotteryCrawler**: 彩票爬虫基类
- **BaseLotteryAnalyzer**: 彩票分析基类  
- **BaseLotteryVisualizer**: 彩票可视化基类
- **LotteryConfig**: 彩票配置类

### 2. 规则引擎

每种彩票都有独立的规则引擎，包含以下规则：

- **OddEvenRule**: 奇偶均衡规则
- **IntervalRule**: 区间分布规则
- **ConsecutiveRule**: 连号限制规则
- **SumRangeRule**: 和值范围规则
- **HotColdRule**: 冷热搭配规则
- **ExcludeNumbersRule**: 排除指定号码规则
- **IncludeNumbersRule**: 必须包含指定号码规则

### 3. 彩票类型对比

| 特性 | 大乐透 | 双色球 |
|------|--------|--------|
| 前区号码范围 | 1-35 | 1-33 |
| 前区选号数量 | 5个 | 6个 |
| 后区号码范围 | 1-12 | 1-16 |
| 后区选号数量 | 2个 | 1个 |
| 前区颜色 | 天蓝色 | 红色 |
| 后区颜色 | 浅珊瑚色 | 蓝色 |

## 使用方法

### 1. 运行双色球分析

```python
# 使用重构版本（推荐）
python ssq_refactored.py

# 或使用原始版本
python ssq_crawler_and_predict.py
```

### 2. 运行大乐透分析

```python
python dlt_crawler_and_predict.py
```

### 3. 自定义规则

```python
from ssq_rules import ExcludeNumbersRule, IncludeNumbersRule

# 添加排除规则
analyzer.add_custom_rule(ExcludeNumbersRule(exclude_front=[1,2,3], exclude_back=[16]))

# 添加包含规则
analyzer.add_custom_rule(IncludeNumbersRule(include_front=[8], include_back=[5]))
```

## 功能特性

### 1. 数据爬取
- 自动爬取最新开奖数据
- 支持自定义爬取期数
- 数据验证和清洗

### 2. 智能推荐
- 基于历史数据的统计分析
- 多规则引擎验证
- 冷热号码搭配策略
- 随机性与规律性平衡

### 3. 可视化分析
- 号码出现频率图
- 和值趋势分析
- 推荐号码分布对比
- 规则符合性分析

### 4. 规则引擎
- 可扩展的规则系统
- 支持自定义规则
- 规则符合性统计
- 规则权重调整

## 维护指南

### 1. 添加新的彩票类型

1. 创建新的配置文件：
```python
NEW_LOTTERY_CONFIG = LotteryConfig(
    name="新彩票",
    url="API地址",
    game_no="游戏编号",
    front_range=range(1, 新前区范围),
    back_range=range(1, 新后区范围),
    front_count=前区选号数,
    back_count=后区选号数,
    front_color="前区颜色",
    back_color="后区颜色",
    front_name="前区名称",
    back_name="后区名称"
)
```

2. 继承基础类实现具体功能：
```python
class NewLotteryCrawler(BaseLotteryCrawler):
    def _parse_draw_result(self, part):
        # 实现解析逻辑
        pass
    
    def _validate_draw(self, front, back):
        # 实现验证逻辑
        pass

class NewLotteryAnalyzer(BaseLotteryAnalyzer):
    def recommend(self):
        # 实现推荐逻辑
        pass
```

### 2. 添加新规则

1. 在规则文件中添加新规则类：
```python
class NewRule(Rule):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def check(self, front, back):
        # 实现规则检查逻辑
        return True
```

2. 在分析器中注册新规则：
```python
rule_classes = [..., NewRule]
```

### 3. 修改推荐策略

在 `recommend()` 方法中调整：
- 冷热号码比例
- 随机选择概率
- 规则权重
- 尝试次数

### 4. 自定义可视化

继承 `BaseLotteryVisualizer` 并重写相关方法：
```python
class CustomVisualizer(BaseLotteryVisualizer):
    def plot_custom_analysis(self):
        # 实现自定义分析图表
        pass
```

## 依赖库

```bash
pip install requests matplotlib numpy
```

## 注意事项

1. **API限制**: 爬虫有请求频率限制，建议适当调整请求间隔
2. **数据准确性**: 请验证爬取的数据准确性
3. **规则调整**: 根据实际需求调整规则参数
4. **概率性**: 彩票具有随机性，推荐结果仅供参考

## 扩展建议

1. **数据库集成**: 添加数据库存储历史数据
2. **机器学习**: 集成机器学习算法提高预测准确性
3. **Web界面**: 开发Web界面方便用户使用
4. **多线程**: 优化爬虫性能
5. **API服务**: 提供RESTful API服务

## 许可证

本项目仅供学习和研究使用，请勿用于商业用途。 