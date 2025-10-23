# A股数据流MCP服务

> 提供符合MCP（Model Context Protocol）标准的A股数据获取和技术分析服务

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0.0-green)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 📖 简介

本项目将A股数据流功能改造为符合MCP协议的标准服务，使其能够被各种AI工具和客户端调用。通过MCP协议，AI助手可以轻松获取A股市场数据、技术指标、财务信息等，为投资分析提供数据支持。

### 核心特性

- 🎯 **MCP协议标准**: 完全符合MCP 1.0.0协议规范
- 🔄 **异步支持**: 所有工具方法支持异步调用
- 📦 **模块化设计**: 清晰的架构，易于扩展和维护
- 🛡️ **错误处理**: 完善的异常处理和日志系统
- ✅ **测试覆盖**: 100%测试覆盖率，确保代码质量
- 🚀 **高性能**: 内置缓存机制，优化数据获取性能

## 功能特性

- 📊 **K线数据**: 获取股票日线、周线、月线数据
- 💹 **实时行情**: 获取股票实时价格和涨跌幅
- 📈 **技术指标**: 支持RSI、MACD、BOLL、均线等20+种技术指标
- 💰 **财务数据**: 获取资产负债表、利润表、现金流量表
- 📰 **新闻数据**: 获取股票相关新闻资讯
- 🔥 **涨停股**: 获取今日涨停股票列表
- 📝 **千股千评**: 获取评分、关注度、参与意愿等数据
- 💸 **资金流向**: 个股资金流、概念资金流、行业资金流、大单追踪


## 📦 安装

### 前置要求

- Python 3.10 或更高版本
- [uv](https://docs.astral.sh/uv/) 包管理器

安装 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 方式一：直接从 GitHub 运行（推荐）

无需克隆代码，一条命令即可使用：

```bash
# 临时运行（每次拉取最新代码）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 或全局安装
uv tool install git+https://github.com/Fize/choseStock.git
a-share-mcp
```

### 方式二：本地开发

适用于需要修改代码或参与开发：

```bash
# 克隆项目
git clone https://github.com/Fize/choseStock.git
cd choseStock

# 使用 uv 安装依赖
uv sync

# 运行服务器
uv run a-share-mcp
```

## 🚀 快速开始

### 一键运行（无需克隆代码）

```bash
# 直接从 GitHub 运行
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp
```

### 配置 MCP 客户端

MCP 服务器通过标准输入输出（stdio）与客户端通信。在 MCP 客户端配置文件中添加：

**方式一：直接从 GitHub 运行（推荐）**

无需克隆代码，自动使用最新版本：

```json
{
  "mcpServers": {
    "a-share-dataflows": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Fize/choseStock.git",
        "a-share-mcp"
      ]
    }
  }
}
```

**方式二：使用全局安装**

先安装：`uv tool install git+https://github.com/Fize/choseStock.git`

```json
{
  "mcpServers": {
    "a-share-dataflows": {
      "command": "a-share-mcp"
    }
  }
}
```

**方式三：使用本地项目**

适用于开发或需要修改代码：

```json
{
  "mcpServers": {
    "a-share-dataflows": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/choseStock",
        "run",
        "a-share-mcp"
      ]
    }
  }
}
```

### 测试连接

使用 MCP Inspector 测试服务器：

```bash
# 直接从 GitHub 测试
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp
```

## ⚙️ 配置选项

### 环境变量

服务器支持以下环境变量配置：

#### 日志配置

- **STOCK_LOG_FILE**: 自定义日志文件路径
  - 默认值: `~/.stock.log`
  - 示例: `export STOCK_LOG_FILE=/var/log/stock.log`

- **DEBUG**: 启用调试模式
  - 默认值: 未设置（INFO级别）
  - 设置任意值启用: `export DEBUG=1`

#### 使用示例

```bash
# 使用默认配置（日志保存到 ~/.stock.log）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 自定义日志文件位置
STOCK_LOG_FILE=/tmp/stock.log uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 启用调试模式
DEBUG=1 uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 组合使用
DEBUG=1 STOCK_LOG_FILE=/tmp/stock_debug.log uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp
```

#### 在MCP客户端配置中使用

```json
{
  "mcpServers": {
    "a-share-dataflows": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Fize/choseStock.git",
        "a-share-mcp"
      ],
      "env": {
        "STOCK_LOG_FILE": "/path/to/your/stock.log",
        "DEBUG": "1"
      }
    }
  }
}
```

### 日志功能

- **双重输出**: 日志同时输出到终端和文件
- **自动轮转**: 单个文件最大10MB，保留5个备份
- **UTF-8编码**: 支持中文日志
- **详细信息**: 包含时间戳、模块名、日志级别和消息

查看日志：
```bash
# 实时查看日志
tail -f ~/.stock.log

# 查看最后100行
tail -100 ~/.stock.log

# 搜索错误信息
grep "ERROR" ~/.stock.log
```

详细的日志使用说明请参考 [LOG_USAGE.md](./LOG_USAGE.md)

## 💻 开发指南

### 常用命令

```bash
# 直接运行（无需克隆，自动获取最新版本）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 全局安装
uv tool install git+https://github.com/Fize/choseStock.git

# 更新到最新版本
uv tool install --reinstall git+https://github.com/Fize/choseStock.git

# 卸载
uv tool uninstall chosestock-cli

# 查看已安装的工具
uv tool list
```

### 开发命令（需要克隆代码）

```bash
# 克隆仓库
git clone https://github.com/Fize/choseStock.git
cd choseStock

# 同步依赖
uv sync

# 运行服务器
uv run a-share-mcp

# 运行测试
uv run pytest

# 查看测试覆盖率
uv run pytest --cov=dataflows_mcp --cov-report=html

# 代码格式化
uv run black dataflows_mcp/
uv run isort dataflows_mcp/

# 类型检查
uv run mypy dataflows_mcp/

# 添加新依赖
uv add <package-name>
```

### 添加新工具

1. 在 `dataflows_mcp/core/` 中实现核心功能
2. 在 `dataflows_mcp/tools/schemas.py` 中定义 Schema
3. 在 `dataflows_mcp/tools/mcp_tools.py` 中添加工具方法
4. 在 `dataflows_mcp/server/mcp_server.py` 中注册工具
5. 在 `dataflows_mcp/tests/` 中添加测试用例

### 故障排除

#### uvx 命令未找到

如果提示 `uvx: command not found`：

```bash
# 安装或更新 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.zshrc  # 或 source ~/.bashrc
```

#### 首次运行较慢

`uvx` 首次运行时需要下载并缓存依赖，这是正常的：

```bash
# 首次运行可能需要几分钟
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 后续运行会使用缓存，速度很快
```

#### 清除缓存

如果遇到奇怪的问题，可以清除缓存：

```bash
# 清除 uv 缓存
uv cache clean

# 重新运行
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp
```

#### MCP 连接失败

1. 确保命令能正常运行：`uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp`
2. 检查客户端配置文件中的命令格式是否正确
3. 查看客户端日志排查问题

### 诊断工具

如果需要详细诊断，可以克隆代码运行诊断脚本：

```bash
git clone https://github.com/Fize/choseStock.git
cd choseStock
uv run python dataflows_mcp/scripts/diagnose.py
```


## 🔧 可用工具

### 数据获取工具

#### 1. get_stock_kline_data
获取股票K线数据（OHLCV）

**参数**:
- `code` (string, 必需): 股票代码，如"600519"
- `lookback_days` (integer, 可选): 回溯天数，默认60
- `period` (string, 可选): 周期类型，可选值：daily/weekly/monthly，默认daily

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-10-10",
      "open": 1800.0,
      "high": 1850.0,
      "low": 1790.0,
      "close": 1820.0,
      "volume": 1000000
    }
  ],
  "meta": {
    "code": "600519",
    "period": "daily",
    "count": 30
  },
  "error": null
}
```

#### 2. get_stock_realtime_data
获取股票实时行情数据

**参数**:
- `code` (string, 必需): 股票代码

**返回**: 包含最新价、涨跌幅、成交量等实时数据

#### 3. get_technical_indicator_data
计算技术指标

**参数**:
- `code` (string, 必需): 股票代码
- `indicator` (string, 必需): 指标名称，如"rsi"、"macd"、"boll"
- `lookback_days` (integer, 可选): 回溯天数，默认100

**支持的指标**: rsi, macd, kdj, boll, ma, ema, wr, cci, dmi, obv, atr, roc 等20+种

#### 4. get_stock_financial_data
获取财务报表数据

**参数**:
- `code` (string, 必需): 股票代码
- `report_type` (string, 可选): 报表类型
  - `balance_sheet`: 资产负债表（默认）
  - `income_statement`: 利润表
  - `cash_flow`: 现金流量表

#### 5. get_stock_news_data
获取股票相关新闻

**参数**:
- `code` (string, 必需): 股票代码
- `lookback_days` (integer, 可选): 回溯天数，默认7
- `limit` (integer, 可选): 新闻数量限制，默认100

#### 6. get_limit_up_stocks_data
获取今日涨停股票列表

**参数**: 无

**返回**: 包含涨停股票代码、名称、涨停时间等信息

### 千股千评工具

#### 7. get_stock_comment_score_data
获取股票综合评分数据

**参数**:
- `code` (string, 必需): 股票代码

#### 8. get_stock_comment_focus_data
获取股票关注指数

**参数**:
- `code` (string, 必需): 股票代码

#### 9. get_stock_comment_desire_data
获取股票参与意愿指数

**参数**:
- `code` (string, 必需): 股票代码

#### 10. get_stock_comment_institution_data
获取机构参与度数据

**参数**:
- `code` (string, 必需): 股票代码

### 资金流向工具

#### 11. get_individual_fund_flow_data
获取个股资金流向数据（东方财富）

**参数**:
- `code` (string, 必需): 股票代码，如"600519"
- `market` (string, 可选): 市场类型，可选值：sh/sz/bj，默认sh

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2025-01-15",
      "close_price": 1820.0,
      "change_percent": 2.5,
      "main_net_inflow": 150000000.0,
      "main_net_inflow_rate": 5.2,
      "super_large_net_inflow": 80000000.0,
      "super_large_net_inflow_rate": 2.8,
      "large_net_inflow": 70000000.0,
      "large_net_inflow_rate": 2.4,
      "medium_net_inflow": -50000000.0,
      "medium_net_inflow_rate": -1.7,
      "small_net_inflow": -100000000.0,
      "small_net_inflow_rate": -3.5
    }
  ],
  "error": null
}
```

**说明**:
- `main_net_inflow`: 主力净流入金额（元）
- `super_large_net_inflow`: 超大单净流入金额
- `large_net_inflow`: 大单净流入金额
- `medium_net_inflow`: 中单净流入金额
- `small_net_inflow`: 小单净流入金额
- `*_rate`: 对应的净流入率（%）

#### 12. get_concept_fund_flow_data
获取概念板块资金流向数据（同花顺）

**参数**:
- `symbol` (string, 可选): 板块类型，可选值：即时/3日排行/5日排行/10日排行/20日排行，默认"即时"
- `indicator` (string, 可选): 指标类型，可选值同上，默认"即时"

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "序号": 1,
      "板块": "人工智能",
      "最新价": 1520.5,
      "涨跌幅": 3.2,
      "流入资金": 500000000.0,
      "流出资金": 350000000.0,
      "净额": 150000000.0,
      "公司家数": 85,
      "领涨股": "科大讯飞",
      "领涨股涨跌幅": 5.8
    }
  ],
  "error": null
}
```

**说明**:
- 支持即时数据和多日排行榜查询
- 返回字段根据查询类型略有差异
- 可用于分析热门概念板块资金动向

#### 13. get_industry_fund_flow_data
获取行业板块资金流向数据（同花顺）

**参数**:
- `symbol` (string, 可选): 板块类型，可选值：即时/3日排行/5日排行/10日排行/20日排行，默认"即时"
- `indicator` (string, 可选): 指标类型，可选值同上，默认"即时"

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "序号": 1,
      "板块": "电子",
      "最新价": 2300.8,
      "涨跌幅": 2.1,
      "流入资金": 800000000.0,
      "流出资金": 600000000.0,
      "净额": 200000000.0,
      "公司家数": 120,
      "领涨股": "立讯精密",
      "领涨股涨跌幅": 4.5
    }
  ],
  "error": null
}
```

**说明**:
- 与概念板块数据结构类似
- 按照申万行业分类统计
- 可用于分析行业轮动和资金偏好

#### 14. get_big_deal_fund_flow_data
获取大单追踪数据（同花顺）

**参数**: 无

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "trade_time": "14:35:20",
      "code": "600519",
      "name": "贵州茅台",
      "trade_price": 1820.0,
      "trade_volume": 5000,
      "trade_amount": 9100000.0,
      "deal_type": "买盘",
      "change_percent": 2.5,
      "turnover_rate": 0.15
    }
  ],
  "error": null
}
```

**说明**:
- `trade_time`: 成交时间
- `deal_type`: 成交类型（买盘/卖盘/中性盘）
- `trade_amount`: 成交金额（元）
- 实时追踪大额交易，捕捉主力资金动向

#### 15. get_stock_cyq_data
获取股票筹码分布数据（东方财富）

**参数**:
- `code` (string, 必需): 股票代码
- `adjust` (string, 可选): 复权类型，默认为 ""
  - `""`: 不复权
  - `"qfq"`: 前复权
  - `"hfq"`: 后复权

**返回格式**:
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-01-15",
      "profit_ratio": 85.5,
      "average_cost": 1650.0,
      "90_cost_low": 1500.0,
      "90_cost_high": 1800.0,
      "90_concentration": 15.2,
      "70_cost_low": 1550.0,
      "70_cost_high": 1750.0,
      "70_concentration": 10.8
    }
  ],
  "error": null
}
```

**说明**:
- `profit_ratio`: 获利比例（%），当前价格下的盈利筹码占比
- `average_cost`: 平均成本（元），所有筹码的加权平均价格
- `90_cost_low/high`: 90%成本区间（元），90%筹码分布的价格范围
- `90_concentration`: 90%集中度（%），90%筹码价格分布的紧密程度
- `70_cost_low/high`: 70%成本区间（元），70%筹码分布的价格范围
- `70_concentration`: 70%集中度（%），70%筹码价格分布的紧密程度
- 数据涵盖近90个交易日
- 筹码分布分析主力持仓成本和散户套牢区域


## 🏗️ 架构设计

### 项目结构

```
choseStock/
├── dataflows_mcp/           # MCP 数据流服务
│   ├── core/                    # 核心功能层
│   │   ├── akshare_client.py       # AkShare数据源客户端
│   │   ├── a_share_technical.py    # 技术分析引擎
│   │   ├── session_cache.py        # 会话缓存管理
│   │   ├── exceptions.py           # 自定义异常
│   │   ├── factories.py            # 工厂模式
│   │   ├── logging.py              # 日志系统
│   │   └── utils.py                # 工具函数
│   ├── tools/                   # MCP 工具层
│   │   ├── mcp_tools.py            # 工具实现
│   │   └── schemas.py              # Pydantic Schema
│   ├── server/                  # MCP 服务层
│   │   └── mcp_server.py           # MCP 服务器
│   ├── scripts/                 # 实用脚本
│   │   └── diagnose.py             # 诊断工具
│   └── tests/                   # 测试套件
│       ├── test_mcp_tools.py
│       ├── test_mcp_server.py
│       ├── test_schemas.py
│       └── test_data_format.py
├── pyproject.toml           # 项目配置
├── uv.lock                  # 依赖锁文件
└── README.md                # 项目文档
```

### 设计原则

1. **分层架构**: 
   - Core 层：业务逻辑和数据获取
   - Tools 层：MCP 工具封装
   - Server 层：MCP 协议实现

2. **依赖注入**: 使用工厂模式创建实例，便于测试和扩展

3. **异步优先**: 所有工具方法支持异步调用，提升并发性能

4. **错误处理**: 统一的异常体系，完善的错误传播机制

5. **日志系统**: 标准化日志输出，便于监控和调试

6. **测试覆盖**: 完整的测试套件，确保代码质量

## 📊 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 协议 | MCP 1.0.0 | Model Context Protocol |
| 数据源 | AkShare 1.17+ | A股数据获取 |
| 数据处理 | Pandas 2.2+ | 数据分析和处理 |
| 技术分析 | pandas-ta | 技术指标计算 |
| 数据验证 | Pydantic 2.0+ | Schema 定义和验证 |
| 异步 | asyncio | 异步 IO 支持 |
| 测试 | pytest | 单元测试和集成测试 |
| 包管理 | uv | 快速的 Python 包管理器 |

## 📝 更新日志

### v0.1.0 (2025-10-21)

**MCP 服务器标准化改造**：
- ✅ 使用 `pyproject.toml` 配置标准入口点
- ✅ 采用 uv 作为包管理器
- ✅ 支持 `uvx` 从 GitHub 直接运行，无需克隆代码
- ✅ 简化启动方式为 `uvx --from git+...` 或 `a-share-mcp`
- ✅ 移除手动路径管理脚本
- ✅ 完善包结构（添加 `__init__.py`）
- ✅ 完善文档和开发指南

**核心功能**：
- 15+ 数据工具涵盖行情、技术指标、财务、资金流向等
- 完整的测试套件确保代码质量
- 异步支持提升并发性能
- 内置缓存优化数据获取

## 🚀 部署

**快速部署（推荐）**：

```bash
# 无需克隆代码，直接运行
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp
```

详细部署指南请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [AkShare](https://github.com/akfamily/akshare) - 提供A股数据源
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
