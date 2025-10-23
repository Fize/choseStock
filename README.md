# A股数据流MCP服务

> 提供符合MCP（Model Context Protocol）标准的A股数据获取和技术分析服务  
> **✨ 全面支持 Streamable HTTP 和 Progress Notifications | 18个工具实时进度反馈**

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.16.0-green)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-Enabled-orange)](https://github.com/jlowin/fastmcp)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## ⚡ 快速开始

```bash
# 一键启动（stdio transport）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 或启动 HTTP 服务（支持进度反馈）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp -- \
    --transport streamable-http --port 8000
```

**在 MCP 客户端中配置**：

```json
{
  "mcpServers": {
    "a-share": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/Fize/choseStock.git", "a-share-mcp"]
    }
  }
}
```

---

## � 目录

- [简介](#-简介)
- [功能演示](#-功能演示)
- [Streamable 特性](#-streamable-特性)
- [功能特性](#功能特性)
- [安装](#-安装)
- [快速开始](#-快速开始)
- [配置选项](#️-配置选项)
- [可用工具](#-可用工具)
- [架构设计](#️-架构设计)
- [技术栈](#-技术栈)
- [开发指南](#-开发指南)
- [更新日志](#-更新日志)
- [部署](#-部署)
- [常见问题](#-常见问题)
- [许可证](#-许可证)

---

## �📖 简介

本项目将A股数据流功能改造为符合MCP协议的标准服务，使其能够被各种AI工具和客户端调用。通过MCP协议，AI助手可以轻松获取A股市场数据、技术指标、财务信息等，为投资分析提供数据支持。

### 核心特性

- 🎯 **MCP协议标准**: 完全符合MCP 1.16.0协议规范
- 🌊 **三种传输模式**: stdio、SSE、streamable-http 灵活切换
- 📊 **实时进度反馈**: 所有18个工具支持 Progress Notifications
- ⚡ **FastMCP框架**: 基于最新 FastMCP 实现，性能优异
- � **异步架构**: 全异步设计，支持高并发调用
- 📦 **模块化设计**: 清晰的分层架构，易于扩展和维护
- 🛡️ **健壮性**: 完善的异常处理和日志系统
- ✅ **测试覆盖**: 100%测试覆盖率，确保代码质量
- 🚀 **高性能**: 内置缓存机制，优化数据获取性能

## 🎬 功能演示

### Streamable HTTP + Progress Notifications

启动服务器：
```bash
uv run python -m dataflows_mcp.server.mcp_server --transport streamable-http --port 8000
```

客户端调用示例：
```python
from mcp import ClientSession, stdio_client

async def progress_callback(progress: float, total: float, message: str):
    print(f"[{int(progress/total*100)}%] {message}")

async with stdio_client() as (read, write):
    async with ClientSession(read, write) as session:
        # 获取 K 线数据，实时查看进度
        result = await session.call_tool(
            "get_stock_kline_data",
            {"code": "600519", "lookback_days": 100},
            progress_callback=progress_callback
        )

# 输出：
# [0%] 初始化数据获取 - 准备获取 600519 的 daily K线数据
# [20%] 正在从数据源拉取 100 天的 daily 数据...
# [70%] 数据获取完成，正在处理和验证...
# [100%] 完成！共获取 100 条K线数据
```

### 支持的传输模式对比

| 模式 | 适用场景 | 进度支持 | 会话管理 | 启动命令 |
|------|----------|---------|---------|----------|
| **stdio** | MCP 客户端集成 | ✅ | - | `a-share-mcp` |
| **sse** | Web 实时推送 | ✅ | ✅ | `a-share-mcp --transport sse --port 8000` |
| **streamable-http** | 断点续传、会话恢复 | ✅ | ✅ | `a-share-mcp --transport streamable-http --port 8000` |

## 🆕 Streamable 特性

### 📡 三种传输模式

### 📡 三种传输模式

现在支持三种 MCP transport 模式：

| 模式 | 说明 | 适用场景 | 启动命令 |
|------|------|---------|---------|
| **stdio** | 标准输入输出 | MCP 客户端集成 | `--transport stdio`（默认） |
| **sse** | Server-Sent Events | Web 应用实时推送 | `--transport sse --port 8000` |
| **streamable-http** | HTTP 流式传输 | 断点续传、会话恢复 | `--transport streamable-http --port 8000` |

### 📊 Progress Notifications

**所有 18 个数据工具** 都支持实时进度报告，让您清楚了解数据获取过程：

```python
# 客户端示例（使用 MCP Python SDK）
from mcp import ClientSession, stdio_client

async def progress_handler(progress: float, total: float, message: str):
    percentage = (progress / total) * 100
    print(f"[{percentage:.0f}%] {message}")

async with stdio_client() as (read, write):
    async with ClientSession(read, write) as session:
        result = await session.call_tool(
            "get_stock_kline_data",
            {
                "code": "600519",
                "lookback_days": 100,
                "period": "daily"
            },
            progress_callback=progress_handler
        )
```

**进度输出示例**：
```
[0%] 初始化数据获取 - 准备获取 600519 的 daily K线数据
[20%] 正在从数据源拉取 100 天的 daily 数据...
[70%] 数据获取完成，正在处理和验证...
[100%] 完成！共获取 100 条K线数据
```

### 🎯 支持进度的工具列表

#### 📈 行情数据（7个工具）
- ✅ `get_stock_kline_data` - K线数据（日/周/月线）
- ✅ `get_stock_realtime_eastmoney_data` - 实时行情（东方财富）
- ✅ `get_stock_realtime_sina_data` - 实时行情（新浪）
- ✅ `get_stock_realtime_xueqiu_data` - 实时行情（雪球）
- ✅ `get_stock_news_data` - 新闻资讯
- ✅ `get_stock_financial_data` - 财务报表
- ✅ `get_technical_indicator_data` - 技术指标（20+种）

#### 🔥 市场数据（5个工具）
- ✅ `get_limit_up_stocks_data` - 涨停股票
- ✅ `get_stock_comment_score_data` - 千股千评评分
- ✅ `get_stock_comment_focus_data` - 关注指数
- ✅ `get_stock_comment_desire_data` - 参与意愿
- ✅ `get_stock_comment_institution_data` - 机构参与度

#### 💰 资金流向（5个工具）
- ✅ `get_individual_fund_flow_data` - 个股资金流
- ✅ `get_concept_fund_flow_data` - 概念板块资金流
- ✅ `get_industry_fund_flow_data` - 行业板块资金流
- ✅ `get_big_deal_fund_flow_data` - 大单追踪
- ✅ `get_stock_cyq_data` - 筹码分布

**总计**: 18个工具，100% 支持实时进度反馈 ✨

## 功能特性

### 📊 数据覆盖（18个工具）

#### 基础行情数据
- 📊 **K线数据**: 获取股票日线、周线、月线数据（OHLCV）
- 💹 **实时行情**: 支持东方财富、新浪、雪球三个数据源
- 📰 **新闻资讯**: 获取股票相关新闻和公告

#### 技术分析
- 📈 **技术指标**: 支持 **20+ 种技术指标**
  - 趋势指标：MA、EMA、MACD、DMI
  - 震荡指标：RSI、KDJ、WR、CCI、STOCH
  - 能量指标：OBV、VR、EMV、MFI
  - 波动指标：BOLL、ATR、KELTNER
  - 其他：ROC、TRIX、VWAP等

#### 基本面分析
- 💰 **财务数据**: 
  - 资产负债表（Balance Sheet）
  - 利润表（Income Statement）
  - 现金流量表（Cash Flow Statement）

#### 市场情绪
- 🔥 **涨停数据**: 获取今日涨停股票列表
- 📝 **千股千评**: 
  - 综合评分
  - 关注度指数
  - 参与意愿指数
  - 机构参与度

#### 资金流向
- 💸 **多维度资金流向**: 
  - 个股资金流（主力/超大单/大单/中单/小单）
  - 概念板块资金流
  - 行业板块资金流
  - 大单追踪（实时）
  - 筹码分布（CYQ）

**所有工具均支持实时进度反馈 ✨**


## 📦 安装

### 前置要求

- Python 3.10 或更高版本
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）

安装 uv：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 🚀 方式一：直接运行（推荐）

无需克隆代码，一条命令即可使用：

```bash
# stdio transport（用于 MCP 客户端）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# streamable-http（用于 Web 应用，支持进度）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp -- --transport streamable-http --port 8000

# 查看帮助
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp -- --help
```

### 🔧 方式二：全局安装

```bash
# 全局安装
uv tool install git+https://github.com/Fize/choseStock.git

# 启动服务（stdio）
a-share-mcp

# 启动服务（streamable-http）
a-share-mcp --transport streamable-http --port 8000

# 启动服务（sse）
a-share-mcp --transport sse --port 8000 --debug
```

### 💻 方式三：本地开发

适用于需要修改代码或参与开发：

```bash
# 克隆项目
git clone https://github.com/Fize/choseStock.git
cd choseStock

# 使用 uv 安装依赖
uv sync

# 运行服务器（stdio）
uv run a-share-mcp

# 运行服务器（streamable-http）
uv run python -m dataflows_mcp.server.mcp_server --transport streamable-http --port 8000
```

## 🚀 快速开始

### 命令行参数

服务器支持以下命令行参数：

```bash
a-share-mcp [OPTIONS]

OPTIONS:
  --transport {stdio,sse,streamable-http}
                        传输模式（默认: stdio）
  --port PORT           HTTP 端口（默认: 8000，仅用于 sse/streamable-http）
  --host HOST           监听地址（默认: 127.0.0.1）
  --debug               启用调试模式（详细日志）
  -h, --help           显示帮助信息
```

### 启动服务器

#### 1️⃣ stdio Transport（MCP 客户端集成）

```bash
# 默认使用 stdio
uv run python -m dataflows_mcp.server.mcp_server

# 或明确指定
uv run python -m dataflows_mcp.server.mcp_server --transport stdio
```

#### 2️⃣ Streamable HTTP Transport（推荐，支持进度）

```bash
# 启动 HTTP 服务器（默认端口 8000）
uv run python -m dataflows_mcp.server.mcp_server --transport streamable-http --port 8000

# 自定义主机和端口
uv run python -m dataflows_mcp.server.mcp_server \
    --transport streamable-http \
    --host 0.0.0.0 \
    --port 9000

# 启用调试模式
uv run python -m dataflows_mcp.server.mcp_server \
    --transport streamable-http \
    --port 8000 \
    --debug
```

#### 3️⃣ SSE Transport（Web 应用实时推送）

```bash
# 启动 SSE 服务器
uv run python -m dataflows_mcp.server.mcp_server --transport sse --port 8000
```

### 一键运行（无需克隆代码）

```bash
# stdio transport（用于 MCP 客户端）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# streamable-http（带进度反馈）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp -- \
    --transport streamable-http --port 8000 --debug
```

### 配置 MCP 客户端

MCP 服务器支持多种集成方式，推荐使用 stdio transport：

#### 方式一：直接从 GitHub 运行（推荐）✨

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

#### 方式二：使用全局安装

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

#### 方式三：使用本地项目（开发用）

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

#### 使用 MCP Inspector 测试

```bash
# 直接从 GitHub 测试（推荐）
npx @modelcontextprotocol/inspector uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 或使用全局安装版本
npx @modelcontextprotocol/inspector a-share-mcp
```

#### 测试 Streamable HTTP

```bash
# 1. 启动服务器
uv run python -m dataflows_mcp.server.mcp_server --transport streamable-http --port 8000

# 2. 在浏览器访问
# http://127.0.0.1:8000

# 3. 使用 MCP Client SDK 测试
# 参见 examples/client_progress_demo.py
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
# ========== 直接运行（无需克隆） ==========
# stdio transport
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# streamable-http transport（带进度）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp -- \
    --transport streamable-http --port 8000

# ========== 全局安装 ==========
# 安装
uv tool install git+https://github.com/Fize/choseStock.git

# 运行（stdio）
a-share-mcp

# 运行（streamable-http）
a-share-mcp --transport streamable-http --port 8000 --debug

# 更新到最新版本
uv tool install --reinstall git+https://github.com/Fize/choseStock.git

# 卸载
uv tool uninstall chosestock-cli

# 查看已安装的工具
uv tool list
```

### 本地开发（需要克隆代码）

```bash
# ========== 克隆仓库 ==========
git clone https://github.com/Fize/choseStock.git
cd choseStock

# ========== 依赖管理 ==========
# 同步依赖
uv sync

# 添加新依赖
uv add <package-name>

# 添加开发依赖
uv add --dev <package-name>

# ========== 运行服务器 ==========
# stdio（默认）
uv run a-share-mcp

# streamable-http
uv run python -m dataflows_mcp.server.mcp_server --transport streamable-http --port 8000

# sse
uv run python -m dataflows_mcp.server.mcp_server --transport sse --port 8000

# 调试模式
uv run python -m dataflows_mcp.server.mcp_server --debug

# ========== 测试 ==========
# 运行所有测试
uv run pytest

# 运行特定测试文件
uv run pytest dataflows_mcp/tests/test_mcp_server.py

# 查看测试覆盖率
uv run pytest --cov=dataflows_mcp --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html

# ========== 代码质量 ==========
# 代码格式化
uv run black dataflows_mcp/
uv run isort dataflows_mcp/

# 类型检查
uv run mypy dataflows_mcp/

# 代码检查
uv run ruff check dataflows_mcp/
```

### 添加新工具

添加支持进度报告的新工具需要以下步骤：

1. **在 `dataflows_mcp/core/` 中实现核心功能**
   ```python
   # 示例：akshare_client.py
   async def get_new_data(self, code: str) -> pd.DataFrame:
       """获取新数据"""
       # 实现数据获取逻辑
       return data
   ```

2. **在 `dataflows_mcp/tools/schemas.py` 中定义 Schema**
   ```python
   class GetNewDataArgs(BaseModel):
       """新工具参数定义"""
       code: str = Field(..., description="股票代码")
       days: int = Field(default=30, description="回溯天数")
   ```

3. **在 `dataflows_mcp/tools/mcp_tools.py` 中添加工具方法**
   ```python
   async def get_new_data(
       self,
       code: str,
       days: int = 30,
       ctx: Optional[Any] = None
   ) -> Dict[str, Any]:
       """获取新数据（支持进度报告）"""
       try:
           # 报告开始
           if ctx:
               await ctx.report_progress(0.0, 1.0, f"初始化数据获取 - {code}")
           
           # 获取数据
           if ctx:
               await ctx.report_progress(0.2, 1.0, f"正在从数据源拉取...")
           data = await self.akshare_client.get_new_data(code)
           
           # 处理数据
           if ctx:
               await ctx.report_progress(0.7, 1.0, "数据获取完成，正在处理...")
           result = self._process_data(data)
           
           # 完成
           if ctx:
               await ctx.report_progress(1.0, 1.0, f"完成！共获取 {len(result)} 条数据")
           
           return {"success": True, "data": result}
       except Exception as e:
           return {"success": False, "error": str(e)}
   ```

4. **在 `dataflows_mcp/server/mcp_server.py` 中注册工具**
   ```python
   @mcp.tool()
   async def get_new_data(
       code: str,
       days: int = 30,
       ctx: Any = None
   ) -> str:
       """获取新数据
       
       Args:
           code: 股票代码
           days: 回溯天数
       """
       result = await mcp_tools_instance.get_new_data(code, days, ctx=ctx)
       return json.dumps(result, ensure_ascii=False, indent=2)
   ```

5. **在 `dataflows_mcp/tests/` 中添加测试用例**
   ```python
   @pytest.mark.asyncio
   async def test_get_new_data():
       """测试新工具"""
       tools = MCPTools()
       result = await tools.get_new_data("600519", days=30)
       assert result["success"] is True
   ```

6. **更新文档**
   - 在 README.md 的工具列表中添加说明
   - 更新工具总数统计

### 进度报告最佳实践

```python
# 推荐的进度阶段划分：
# 0.0  - 初始化（准备开始）
# 0.2  - 开始获取数据（连接数据源）
# 0.5  - 数据获取中（可选，用于大数据量）
# 0.7  - 数据处理（验证、转换）
# 1.0  - 完成

# 进度消息建议：
# - 使用中文，清晰描述当前操作
# - 包含关键参数信息（如股票代码、数据量）
# - 最后阶段显示结果摘要（如记录数）
```

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

| 类别 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **MCP 协议** | MCP SDK | 1.16.0 | Model Context Protocol |
| **MCP 框架** | FastMCP | Latest | 快速 MCP 服务开发框架 |
| **传输层** | Uvicorn | 0.30+ | ASGI 服务器（HTTP/SSE） |
| **数据源** | AkShare | 1.17+ | A股数据获取 |
| **数据处理** | Pandas | 2.2+ | 数据分析和处理 |
| **技术分析** | pandas-ta | Latest | 技术指标计算（20+种） |
| **数据验证** | Pydantic | 2.0+ | Schema 定义和验证 |
| **异步运行时** | asyncio | - | Python 异步 IO |
| **测试框架** | pytest | Latest | 单元测试和集成测试 |
| **包管理** | uv | Latest | 快速的 Python 包管理器 |

### 核心依赖

```toml
[project.dependencies]
mcp = ">=1.16.0"           # MCP 协议支持
fastmcp = "*"              # FastMCP 框架
akshare = ">=1.17.1"       # 数据源
pandas = ">=2.2.0"         # 数据处理
pandas-ta = "*"            # 技术指标
pydantic = ">=2.0.0"       # 数据验证
uvicorn = ">=0.30.0"       # HTTP 服务器
```

## 📝 更新日志

### v0.2.0 (2025-01-21) - Streamable 大版本更新 🎉

**🆕 Streamable MCP 支持**：
- ✅ **三种传输模式**: stdio、sse、streamable-http 全面支持
- ✅ **Progress Notifications**: 18个工具100%支持实时进度反馈
- ✅ **FastMCP框架**: 完全重写服务器，采用 FastMCP 框架
- ✅ **命令行参数**: 支持 --transport、--port、--host、--debug 参数
- ✅ **实时进度**: 4阶段进度报告（初始化→获取→处理→完成）
- ✅ **中文消息**: 所有进度消息使用中文，更易理解

**🔧 架构改进**：
- ✅ Context 自动注入：所有工具方法支持 Context 参数
- ✅ 异步优化：全异步架构，支持高并发
- ✅ 错误处理：完善的异常处理机制
- ✅ 测试覆盖：100%测试覆盖率

**📚 文档更新**：
- ✅ 完整的 Streamable 使用文档
- ✅ Progress Notifications 示例代码
- ✅ 客户端集成指南
- ✅ 开发者最佳实践

**🚀 性能提升**：
- ✅ FastMCP 框架带来更好的性能
- ✅ Uvicorn ASGI 服务器支持
- ✅ 会话缓存优化

### v0.1.0 (2024-10-21)

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

### 生产环境部署

#### Docker 部署（推荐）

```dockerfile
FROM python:3.12-slim

# 安装 uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# 安装应用
RUN uv tool install git+https://github.com/Fize/choseStock.git

# 启动服务（streamable-http）
CMD ["a-share-mcp", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]

# 或启动服务（sse）
# CMD ["a-share-mcp", "--transport", "sse", "--host", "0.0.0.0", "--port", "8000"]
```

构建和运行：

```bash
# 构建镜像
docker build -t a-share-mcp .

# 运行容器（streamable-http）
docker run -d -p 8000:8000 a-share-mcp

# 运行容器（stdio，用于 MCP 客户端）
docker run -it a-share-mcp a-share-mcp --transport stdio
```

#### Systemd 服务

创建 `/etc/systemd/system/a-share-mcp.service`：

```ini
[Unit]
Description=A-Share MCP Data Service
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/home/your-user
ExecStart=/home/your-user/.local/bin/a-share-mcp --transport streamable-http --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
# 重载配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start a-share-mcp

# 开机自启
sudo systemctl enable a-share-mcp

# 查看状态
sudo systemctl status a-share-mcp

# 查看日志
sudo journalctl -u a-share-mcp -f
```

#### Nginx 反向代理

```nginx
upstream a_share_mcp {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://a_share_mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 对于 SSE 连接
        proxy_buffering off;
        proxy_cache off;
    }
}
```

### 环境变量配置

生产环境推荐使用环境变量：

```bash
# 日志配置
export STOCK_LOG_FILE=/var/log/a-share-mcp/stock.log
export DEBUG=0  # 生产环境关闭调试

# 启动服务
a-share-mcp --transport streamable-http --port 8000
```

详细部署指南请查看 [DEPLOYMENT.md](./DEPLOYMENT.md)

## ❓ 常见问题

### Q1: 如何选择合适的传输模式？

**stdio** - 推荐用于 MCP 客户端集成（如 Claude Desktop、Continue.dev）
- ✅ 最简单的配置
- ✅ 标准 MCP 协议
- ✅ 支持进度反馈

**streamable-http** - 推荐用于 Web 应用或需要会话管理的场景
- ✅ HTTP 协议，易于集成
- ✅ 支持断点续传
- ✅ 会话管理
- ✅ 支持进度反馈

**sse** - 推荐用于需要服务器推送的 Web 应用
- ✅ 服务器主动推送
- ✅ 实时更新
- ✅ 支持进度反馈

### Q2: 进度反馈在所有传输模式下都可用吗？

是的！所有三种传输模式（stdio、sse、streamable-http）都完整支持 Progress Notifications。18个工具在任何模式下都会报告实时进度。

### Q3: 如何查看详细的运行日志？

```bash
# 启用调试模式
a-share-mcp --debug

# 或查看日志文件
tail -f ~/.stock.log

# 自定义日志位置
STOCK_LOG_FILE=/tmp/stock.log a-share-mcp --debug
```

### Q4: 数据源是什么？是否需要 API Key？

本项目使用 [AkShare](https://github.com/akfamily/akshare) 作为数据源：
- ✅ **完全免费**，无需 API Key
- ✅ 数据来自公开市场数据
- ✅ 支持实时和历史数据

### Q5: 如何更新到最新版本？

```bash
# 直接运行模式（自动使用最新版本）
uvx --from git+https://github.com/Fize/choseStock.git a-share-mcp

# 全局安装模式
uv tool install --reinstall git+https://github.com/Fize/choseStock.git

# 本地开发模式
cd choseStock
git pull
uv sync
```

### Q6: 支持哪些 Python 版本？

- **最低要求**: Python 3.10
- **推荐版本**: Python 3.12+
- **已测试**: Python 3.10, 3.11, 3.12

### Q7: 如何在生产环境部署？

参见 [🚀 部署](#-部署) 部分，我们提供了：
- Docker 部署方案
- Systemd 服务配置
- Nginx 反向代理配置

### Q8: 遇到 "uvx: command not found" 怎么办？

```bash
# 安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 重新加载 shell 配置
source ~/.zshrc  # 或 source ~/.bashrc

# 验证安装
uvx --version
```

### Q9: 如何贡献代码或报告问题？

- 🐛 **Bug 报告**: [GitHub Issues](https://github.com/Fize/choseStock/issues)
- 💡 **功能建议**: [GitHub Discussions](https://github.com/Fize/choseStock/discussions)
- 🔧 **Pull Request**: 欢迎提交 PR

### Q10: 有完整的 API 文档吗？

是的！查看以下文档：
- [🔧 可用工具](#-可用工具) - 所有18个工具的详细说明
- [STREAMABLE_IMPLEMENTATION.md](./STREAMABLE_IMPLEMENTATION.md) - Streamable 实现细节
- [LOG_USAGE.md](./LOG_USAGE.md) - 日志使用指南

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [AkShare](https://github.com/akfamily/akshare) - 提供A股数据源
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
