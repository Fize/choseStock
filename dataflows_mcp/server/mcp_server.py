"""
MCP服务器实现
提供符合MCP协议的A股数据服务
支持 stdio、sse、streamable-http 三种 transport
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from dataflows_mcp.core.logging import logger, setup_logging


# 解析命令行参数（在导入 FastMCP 之前）
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="A股数据流MCP服务器")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport类型: stdio(默认), sse, streamable-http"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP服务器端口（仅用于sse和streamable-http）"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="HTTP服务器主机地址（仅用于sse和streamable-http）"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试模式"
    )
    return parser.parse_args()


# 解析参数（仅在非测试环境下）
if "pytest" not in sys.modules:
    _args = parse_args()
else:
    # 测试环境下使用默认参数
    class MockArgs:
        transport = "sse"
        port = 8000
        host = "127.0.0.1"
        debug = False
    _args = MockArgs()

# 导入 FastMCP（在参数解析之后）
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from dataflows_mcp import __version__
from dataflows_mcp.tools.mcp_tools import get_mcp_tools

# 创建 FastMCP 服务器实例（传入 host 和 port）
mcp = FastMCP(
    "a-share-dataflows",
    host=_args.host,
    port=_args.port
)

# 获取工具实例
mcp_tools_instance = get_mcp_tools()


# =============================================================================
# 自定义路由 - 心跳端点
# =============================================================================

# CONSTITUTION_EXCEPTION: 简单健康检查端点，无业务逻辑，豁免完整TDD要求
# 理由：端点仅返回5个静态/环境字段，无分支逻辑，无数据处理，失败风险极低
# 保留测试：契约测试 + 集成测试（验证端点可访问性和响应时间）
# 批准：待PR审查（需2名审查者）
# 记录：docs/exceptions.md

@mcp.custom_route("/", methods=["GET"])
async def heartbeat(request: Request) -> Response:
    """
    心跳端点 - SSE/Streamable HTTP模式下的健康检查
    
    该端点用于客户端检测服务器连接状态，返回服务器健康信息。
    仅在SSE和Streamable HTTP传输模式下生效（stdio模式无HTTP服务器）。
    
    Args:
        request: Starlette Request对象
        
    Returns:
        Response: JSON响应，包含以下字段：
            - status (str): 服务健康状态，"healthy" | "unhealthy"
            - timestamp (str): ISO 8601格式的UTC时间戳
            - transport (str): 当前传输模式，"sse" | "streamable-http"
            - server (str): 服务器名称，"a-share-dataflows"
            - version (str): 服务器版本号，如"0.1.0"
            
    Example:
        >>> # 使用curl测试
        >>> curl http://localhost:8000/
        {
            "status": "healthy",
            "timestamp": "2025-11-12T10:30:00.123456+00:00",
            "transport": "sse",
            "server": "a-share-dataflows",
            "version": "0.1.0"
        }
        
    Notes:
        - 响应时间目标: <100ms (p95)
        - 并发能力: >1000 req/s
        - 无状态设计: 不依赖任何持久化数据或全局状态
        - 日志级别: DEBUG（避免生产环境日志噪音）
    """
    # 生成UTC时间戳
    timestamp = datetime.now(timezone.utc).isoformat()
    
    # 构建响应数据
    response_data = {
        "status": "healthy",
        "timestamp": timestamp,
        "transport": _args.transport,
        "server": "a-share-dataflows",
        "version": __version__
    }
    
    # DEBUG级别日志（避免生产环境噪音）
    if request.client:
        logger.debug(f"心跳请求 - 来源: {request.client.host}")
    else:
        logger.debug("心跳请求 - 来源: unknown")
    
    # 返回JSON响应，禁用缓存
    return JSONResponse(
        response_data,
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate"
        }
    )


# =============================================================================
# 工具定义 - 所有工具都支持 Context 和 Progress Notifications
# =============================================================================

@mcp.tool()
async def get_stock_kline_data(
    code: str,
    lookback_days: int = 60,
    period: str = "daily",
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票K线数据（OHLCV），支持日线、周线、月线等多种周期
    
    Args:
        code: 股票代码，支持格式：600519、600519.SH、000001.SZ等
        lookback_days: 回溯天数，范围1-1000天
        period: 周期类型：daily(日线)、weekly(周线)、monthly(月线)
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_kline_data(code, lookback_days, period, ctx)


@mcp.tool()
async def get_stock_realtime_eastmoney_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票实时行情数据（东方财富数据源），包含最新价格、涨跌幅、成交量等信息
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_realtime_eastmoney_data(code, ctx)


@mcp.tool()
async def get_stock_realtime_sina_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票实时行情数据（新浪数据源），包含最新价格、涨跌幅、成交量等信息
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_realtime_sina_data(code, ctx)


@mcp.tool()
async def get_stock_realtime_xueqiu_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票实时行情数据（雪球数据源），包含最新价格、涨跌幅、成交量等信息
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_realtime_xueqiu_data(code, ctx)


@mcp.tool()
async def get_technical_indicator_data(
    code: str,
    indicator: str,
    lookback_days: int = 100,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    计算股票技术指标，支持RSI、MACD、BOLL、均线等多种指标
    
    Args:
        code: 股票代码
        indicator: 技术指标名称，如rsi、macd、boll、close_20_sma等
        lookback_days: 回溯天数，范围1-1000天
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_technical_indicator_data(code, indicator, lookback_days, ctx)


@mcp.tool()
async def get_stock_financial_data(
    code: str,
    report_type: str = "balance_sheet",
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票财务数据，包含资产负债表、利润表、现金流量表
    
    Args:
        code: 股票代码
        report_type: 报表类型：balance_sheet(资产负债表)、income(利润表)、cashflow(现金流量表)
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_financial_data(code, report_type, ctx)


@mcp.tool()
async def get_stock_news_data(
    code: str,
    lookback_days: int = 7,
    limit: int = 100,
    ctx: Optional[Context[ServerSession, None]] = None
) -> List[Dict[str, Any]]:
    """
    获取股票相关新闻数据
    
    Args:
        code: 股票代码
        lookback_days: 回溯天数，范围1-30天
        limit: 新闻数量限制，范围1-500条
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_news_data(code, lookback_days, limit, ctx)


@mcp.tool()
async def get_limit_up_stocks_data(
    ctx: Optional[Context[ServerSession, None]] = None
) -> List[Dict[str, Any]]:
    """
    获取今日涨停股票列表
    
    Args:
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_limit_up_stocks_data(ctx)


@mcp.tool()
async def get_stock_comment_score_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取千股千评评分数据，包含综合评分和历史趋势
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_comment_score_data(code, ctx)


@mcp.tool()
async def get_stock_comment_focus_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取用户关注指数数据，反映市场关注度
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_comment_focus_data(code, ctx)


@mcp.tool()
async def get_stock_comment_desire_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取市场参与意愿数据，反映投资者参与热情
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_comment_desire_data(code, ctx)


@mcp.tool()
async def get_stock_comment_institution_data(
    code: str,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取机构参与度数据，反映机构投资者关注程度
    
    Args:
        code: 股票代码
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_comment_institution_data(code, ctx)


@mcp.tool()
async def get_individual_fund_flow_data(
    code: str,
    market: str = "sh",
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取个股资金流向数据（东方财富），包含主力净流入、超大单、大单、中单、小单等资金流向
    
    Args:
        code: 股票代码，如600519
        market: 市场标识，可选值: sh(上海)、sz(深圳)、bj(北京)，默认sh
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_individual_fund_flow_data(code, market, ctx)


@mcp.tool()
async def get_concept_fund_flow_data(
    symbol: str = "即时",
    indicator: str = "即时",
    ctx: Optional[Context[ServerSession, None]] = None
) -> List[Dict[str, Any]]:
    """
    获取概念板块资金流向数据（同花顺），包含概念板块的资金流入流出情况
    
    Args:
        symbol: 时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行
        indicator: 数据指标，与symbol保持一致
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_concept_fund_flow_data(symbol, indicator, ctx)


@mcp.tool()
async def get_industry_fund_flow_data(
    symbol: str = "即时",
    indicator: str = "即时",
    ctx: Optional[Context[ServerSession, None]] = None
) -> List[Dict[str, Any]]:
    """
    获取行业板块资金流向数据（同花顺），包含行业板块的资金流入流出情况
    
    Args:
        symbol: 时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行
        indicator: 数据指标，与symbol保持一致
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_industry_fund_flow_data(symbol, indicator, ctx)


@mcp.tool()
async def get_big_deal_fund_flow_data(
    ctx: Optional[Context[ServerSession, None]] = None
) -> List[Dict[str, Any]]:
    """
    获取大单追踪数据（东方财富），包含大单交易明细
    
    Args:
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_big_deal_fund_flow_data(ctx)


@mcp.tool()
async def get_stock_cyq_data(
    code: str,
    date: Optional[str] = None,
    ctx: Optional[Context[ServerSession, None]] = None
) -> Dict[str, Any]:
    """
    获取股票筹码分布数据，分析持仓成本分布
    
    Args:
        code: 股票代码
        date: 查询日期，格式YYYYMMDD，默认为最新交易日
        ctx: MCP Context，用于进度报告
    """
    return await mcp_tools_instance.get_stock_cyq_data(code, date, ctx)


# =============================================================================
# 主函数
# =============================================================================

def main():
    """主函数 - MCP服务器入口点"""
    global _args
    
    # 初始化日志系统
    log_level = logging.DEBUG if _args.debug or os.environ.get('DEBUG') else logging.INFO
    setup_logging(level=log_level, log_to_file=True)
    
    # 记录启动信息
    logger.info("=" * 60)
    logger.info("A股数据流MCP服务器启动")
    logger.info("=" * 60)
    logger.info(f"Python版本: {sys.version.split()[0]}")
    logger.info(f"Transport: {_args.transport}")
    if _args.transport in ["sse", "streamable-http"]:
        logger.info(f"监听地址: {_args.host}:{_args.port}")
    logger.info(f"日志级别: {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")
    
    # 记录环境变量配置
    log_file = os.environ.get('STOCK_LOG_FILE', str(Path.home() / '.stock.log'))
    logger.info(f"日志文件: {log_file}")
    
    if _args.debug:
        logger.info("调试模式: 已启用")
    
    logger.info("-" * 60)
    
    try:
        # 根据 transport 类型启动服务器
        if _args.transport == "stdio":
            logger.info("使用 stdio transport，等待客户端连接...")
            mcp.run(transport="stdio")
        elif _args.transport == "sse":
            logger.info(f"使用 SSE transport，服务器启动在 http://{_args.host}:{_args.port}")
            mcp.run(transport="sse")
        elif _args.transport == "streamable-http":
            logger.info(f"使用 Streamable HTTP transport，服务器启动在 http://{_args.host}:{_args.port}")
            mcp.run(transport="streamable-http")
            
    except KeyboardInterrupt:
        logger.info("-" * 60)
        logger.info("收到中断信号，正在关闭服务器...")
        logger.info("服务器已安全关闭")
    except Exception as e:
        logger.error("-" * 60)
        logger.error(f"服务器运行异常: {str(e)}")
        logger.error("服务器异常退出")
        import traceback
        logger.error(f"错误堆栈:\n{traceback.format_exc()}")
        sys.exit(1)


if __name__ == "__main__":
    main()
