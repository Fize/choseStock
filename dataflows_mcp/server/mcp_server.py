"""
MCP服务器实现
提供符合MCP协议的A股数据服务
使用 stdio transport（通过 supergateway 转换为 SSE/HTTP）
"""

import sys
import os
import logging
import argparse
from pathlib import Path
from typing import Any, Dict, List, Optional

from dataflows_mcp.core.logging import logger, setup_logging


# 解析命令行参数
def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="A股数据流MCP服务器")
    parser.add_argument(
        "--transport",
        type=str,
        choices=["stdio"],
        default="stdio",
        help="Transport类型: stdio（默认且唯一支持）"
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
        transport = "stdio"
        debug = False
    _args = MockArgs()

# 导入 FastMCP
from mcp.server.fastmcp import FastMCP, Context
from mcp.server.session import ServerSession

from dataflows_mcp import __version__
from dataflows_mcp.tools.mcp_tools import get_mcp_tools

# 创建 FastMCP 服务器实例（stdio transport）
mcp = FastMCP("a-share-dataflows")

# 获取工具实例
mcp_tools_instance = get_mcp_tools()


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
    logger.info(f"Transport: stdio")
    logger.info(f"日志级别: {'DEBUG' if log_level == logging.DEBUG else 'INFO'}")
    logger.info("提示: 使用 supergateway 可将此服务转换为 HTTP/SSE 端点")
    
    # 记录环境变量配置
    log_file = os.environ.get('STOCK_LOG_FILE', str(Path.home() / '.stock.log'))
    logger.info(f"日志文件: {log_file}")
    
    if _args.debug:
        logger.info("调试模式: 已启用")
    
    logger.info("-" * 60)
    
    try:
        # 使用 stdio transport 启动服务器
        logger.info("使用 stdio transport，等待客户端连接...")
        mcp.run(transport="stdio")
            
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
