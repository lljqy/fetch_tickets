# 彩票分析与推荐系统 (重构版)

这是一个基于Python的彩票分析与推荐系统，支持大乐透和双色球两种彩票类型。经过重构后，代码结构更加清晰，可维护性更强。

## 🏗️ 项目架构

### 目录结构
```
lotery/
├── core/                          # 核心模块
│   ├── __init__.py
│   ├── base.py                    # 基础类和配置
│   └── rules.py                   # 规则引擎
├── analysis/                      # 分析层
│   ├── __init__.py
│   ├── dlt_analyzer.py            # 大乐透分析器
│   └── ssq_analyzer.py            # 双色球分析器
├── visualization/                 # 可视层
│   ├── __init__.py
│   ├── base_visualizer.py         # 可视化基类
│   ├── dlt_visualizer.py          # 大乐透可视化
│   └── ssq_visualizer.py          # 双色球可视化
├── main.py                        # 主程序
├── README_NEW.md                  # 项目说明
└── requirements.txt               # 依赖包
```

### 设计模式

#### 1. 分层架构
- **核心层 (Core)**: 提供基础类、配置和规则引擎
- **分析层 (Analysis)**: 负责数据爬取和号码分析
- **可视层 (Visualization)**: 负责数据可视化
- **主程序层**: 整合所有功能，提供统一接口

#### 2. 抽象基类设计
- `BaseCrawler`: 爬虫基类，封装公共爬取逻辑
- `BaseAnalyzer`: 分析基类，封装公共分析逻辑
- `BaseVisualizer`: 可视化基类，封装公共可视化逻辑

#### 3. 工厂模式
- `RuleFactory`: 规则工厂，根据彩票类型创建相应规则
- `LotterySystem`: 彩票系统工厂，根据类型创建相应组件

#### 4. 配置驱动
- `LotteryConfig`: 集中管理彩票配置参数
- 支持多种彩票类型的配置

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install requests matplotlib numpy
```

### 2. 基本使用

#### 双色球分析
```bash
# 默认分析双色球，最近10期，推荐5注
python main.py

# 指定分析期数和推荐注数
python main.py --periods 20 --bets 10

# 排除特定号码
python main.py --exclude-front 1 2 3 --exclude-back 16

# 必须包含特定号码
python main.py --include-front 8 --include-back 5
```

#### 大乐透分析
```bash
# 分析大乐透
python main.py --type dlt

# 大乐透自定义参数
python main.py --type dlt --periods 15 --bets 8
```

### 3. 高级功能

#### 不生成图表
```bash
python main.py --no-plots
```

#### 查看帮助
```bash
python main.py --help
```

## 📊 功能特性

### 1. 数据爬取
- ✅ 自动爬取最新开奖数据
- ✅ 支持自定义爬取期数
- ✅ 数据验证和清洗
- ✅ 错误处理和重试机制

### 2. 智能推荐
- ✅ 基于历史数据的统计分析
- ✅ 多规则引擎验证
- ✅ 冷热号码搭配策略
- ✅ 随机性与规律性平衡
- ✅ 自定义规则支持

### 3. 可视化分析
- ✅ 号码出现频率图
- ✅ 和值趋势分析
- ✅ 推荐号码分布对比
- ✅ 规则符合性分析
- ✅ 统计摘要报告

### 4. 规则引擎
- ✅ 可扩展的规则系统
- ✅ 支持自定义规则
- ✅ 规则符合性统计
- ✅ 规则权重调整

## 🔧 技术特点

### 1. 高度模块化
- 每个模块职责单一，易于维护
- 模块间依赖关系清晰
- 支持独立测试和开发

### 2. 可扩展性强
- 抽象基类设计，易于添加新彩票类型
- 规则引擎支持自定义规则
- 可视化组件可独立扩展

### 3. 配置驱动
- 彩票参数集中配置
- 支持运行时参数调整
- 配置与代码分离

### 4. 错误处理
- 完善的异常处理机制
- 友好的错误提示
- 程序稳定性保障

## 🎯 彩票类型对比

| 特性 | 大乐透 | 双色球 |
|------|--------|--------|
| 前区号码范围 | 1-35 | 1-33 |
| 前区选号数量 | 5个 | 6个 |
| 后区号码范围 | 1-12 | 1-16 |
| 后区选号数量 | 2个 | 1个 |
| 前区颜色 | 天蓝色 | 红色 |
| 后区颜色 | 浅珊瑚色 | 蓝色 |
| 特有规则 | 基础规则 | 红蓝平衡、间隔规则 |

## 📈 输出文件

运行程序后会生成以下文件：

### 图表文件
- `{prefix}_number_frequency.png`: 号码频率图
- `{prefix}_sum_trend.png`: 和值趋势图
- `{prefix}_recommendation_analysis.png`: 推荐号码分析图
- `{prefix}_rule_compliance.png`: 规则符合性分析图

### 控制台输出
- 历史开奖数据
- 推荐号码列表
- 规则符合性分析
- 统计摘要信息

## 🔍 规则说明

### 基础规则
1. **奇偶均衡规则**: 控制奇偶号码比例
2. **区间分布规则**: 确保号码分布均匀
3. **连号限制规则**: 限制连续号码数量
4. **和值范围规则**: 控制号码和值范围
5. **冷热搭配规则**: 平衡冷热号码选择

### 自定义规则
1. **排除规则**: 排除指定号码
2. **包含规则**: 必须包含指定号码

### 双色球特有规则
1. **红蓝平衡规则**: 控制1-16区间号码数量
2. **间隔规则**: 控制相邻号码间隔

## 🛠️ 开发指南

### 1. 添加新彩票类型

1. 在 `core/base.py` 中添加新配置：
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

2. 在 `analysis/` 目录下创建新分析器：
```python
class NewLotteryCrawler(BaseCrawler):
    def _parse_draw_result(self, part):
        # 实现解析逻辑
        pass
    
    def _validate_draw(self, front, back):
        # 实现验证逻辑
        pass

class NewLotteryAnalyzer(BaseAnalyzer):
    def recommend(self):
        # 实现推荐逻辑
        pass
```

3. 在 `visualization/` 目录下创建新可视化器：
```python
class NewLotteryVisualizer(BaseVisualizer):
    def get_front_color(self):
        return "颜色"
    
    def get_back_color(self):
        return "颜色"
```

4. 在 `main.py` 中注册新彩票类型：
```python
elif self.lottery_type == "new":
    self.crawler_class = NewLotteryCrawler
    self.analyzer_class = NewLotteryAnalyzer
    self.visualizer_class = NewLotteryVisualizer
```

### 2. 添加新规则

1. 在 `core/rules.py` 中添加新规则：
```python
class NewRule(Rule):
    def __init__(self, param1, param2):
        self.param1 = param1
        self.param2 = param2
    
    def check(self, front, back):
        # 实现规则检查逻辑
        return True
```

2. 在 `RuleFactory` 中注册新规则：
```python
@staticmethod
def create_new_lottery_rules():
    return [
        # 添加新规则
        NewRule(param1, param2)
    ]
```

### 3. 自定义可视化

继承 `BaseVisualizer` 并重写相关方法：
```python
class CustomVisualizer(BaseVisualizer):
    def plot_custom_analysis(self):
        # 实现自定义分析图表
        pass
```

## 🧪 测试

### 运行测试
```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试
python -m pytest tests/test_ssq.py
```

### 测试覆盖
- 规则引擎测试
- 分析器功能测试
- 可视化组件测试
- 爬虫功能测试

## 📝 注意事项

1. **API限制**: 爬虫有请求频率限制，建议适当调整请求间隔
2. **数据准确性**: 请验证爬取的数据准确性
3. **规则调整**: 根据实际需求调整规则参数
4. **概率性**: 彩票具有随机性，推荐结果仅供参考
5. **法律合规**: 请遵守当地法律法规

## 🔮 未来规划

1. **数据库集成**: 添加数据库存储历史数据
2. **机器学习**: 集成机器学习算法提高预测准确性
3. **Web界面**: 开发Web界面方便用户使用
4. **多线程**: 优化爬虫性能
5. **API服务**: 提供RESTful API服务
6. **移动端**: 开发移动端应用

## 📄 许可证

本项目仅供学习和研究使用，请勿用于商业用途。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

---

**重构完成！** 🎉 新的代码结构更加清晰，可维护性更强，支持轻松扩展新的彩票类型和功能。 