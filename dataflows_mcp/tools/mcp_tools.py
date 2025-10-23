"""
MCP工具封装模块 - 支持 Progress Notifications
提供所有A股数据获取和技术分析功能的MCP工具接口
所有工具都支持进度报告功能
遵循MCP标准：成功时直接返回数据，失败时抛出异常
"""

import asyncio
from typing import Any, Dict, List, Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from mcp.server.fastmcp import Context
    from mcp.server.session import ServerSession

from ..core import (
    get_stock_kline,
    get_stock_realtime_eastmoney,
    get_stock_realtime_sina,
    get_stock_realtime_xueqiu,
    get_stock_financials,
    get_stock_news,
    get_stock_comment_score,
    get_stock_comment_focus,
    get_stock_comment_desire_daily,
    get_stock_comment_institution,
    get_limit_up_stocks,
    get_technical_indicator,
    get_individual_fund_flow,
    get_concept_fund_flow,
    get_industry_fund_flow,
    get_big_deal_fund_flow,
    get_stock_cyq,
    format_stock_code,
    get_current_date,
    get_exchange_code
)
from ..core.logging import logger
from ..core.exceptions import (
    DataFlowError,
    AkshareAPIError,
    TechnicalAnalysisError,
    ValidationError
)


class MCPTools:
    """
    MCP工具封装类
    封装所有A股数据获取和技术分析功能，提供统一的MCP工具接口
    所有工具都支持 Context 和 Progress Notifications
    遵循MCP协议标准：成功返回数据，失败抛出异常
    """

    def __init__(self):
        """初始化MCP工具类"""
        logger.info("MCP工具类已初始化")

    async def get_stock_kline_data(
        self,
        code: str,
        lookback_days: int = 60,
        period: str = "daily",
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票K线数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}K线数据，回溯{lookback_days}天，周期{period}")

        # 开始进度报告
        if ctx:
            await ctx.info(f"开始获取股票 {code} 的K线数据...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        # 获取数据
        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.2, 1.0, f"正在从数据源拉取{lookback_days}天的{period}数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_kline,
            code, lookback_days, period
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "数据获取完成，正在处理...")

        # 处理数据
        data = result.get("data", [])
        meta = result.get("meta", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共获取 {len(data)} 条K线数据")
            await ctx.info(f"成功获取股票 {code} 的 {len(data)} 条K线数据")

        logger.info(f"成功获取股票{code}的{len(data)}条K线数据")
        return {
            "data": data,
            "meta": meta
        }

    async def get_stock_realtime_eastmoney_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票实时行情（东方财富数据源，支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}实时行情（东方财富）")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 实时行情（东方财富）...")
            await ctx.report_progress(0.0, 1.0, "连接东方财富数据源...")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.5, 1.0, "正在获取实时行情数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_realtime_eastmoney,
            code
        )

        realtime_data = result.get("data", {})
        
        if ctx:
            price = realtime_data.get('price', 'N/A')
            await ctx.report_progress(1.0, 1.0, f"完成！当前价格: {price}")
            await ctx.info(f"成功获取股票 {code} 实时行情: {price}")

        logger.info(f"成功获取股票{code}实时行情（东方财富）: {realtime_data.get('price', 'N/A')}")
        return realtime_data

    async def get_stock_realtime_sina_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票实时行情（新浪数据源，支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}实时行情（新浪）")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 实时行情（新浪）...")
            await ctx.report_progress(0.0, 1.0, "连接新浪数据源...")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.5, 1.0, "正在获取实时行情数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_realtime_sina,
            code
        )

        realtime_data = result.get("data", {})
        
        if ctx:
            price = realtime_data.get('price', 'N/A')
            await ctx.report_progress(1.0, 1.0, f"完成！当前价格: {price}")
            await ctx.info(f"成功获取股票 {code} 实时行情: {price}")

        logger.info(f"成功获取股票{code}实时行情（新浪）: {realtime_data.get('price', 'N/A')}")
        return realtime_data

    async def get_stock_realtime_xueqiu_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票实时行情（雪球数据源，支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}实时行情（雪球）")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 实时行情（雪球）...")
            await ctx.report_progress(0.0, 1.0, "连接雪球数据源...")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.5, 1.0, "正在获取实时行情数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_realtime_xueqiu,
            code
        )

        realtime_data = result.get("data", {})
        
        if ctx:
            price = realtime_data.get('price', 'N/A')
            await ctx.report_progress(1.0, 1.0, f"完成！当前价格: {price}")
            await ctx.info(f"成功获取股票 {code} 实时行情: {price}")

        logger.info(f"成功获取股票{code}实时行情（雪球）: {realtime_data.get('price', 'N/A')}")
        return realtime_data

    async def get_stock_financial_data(
        self,
        code: str,
        report_type: str = "balance_sheet",
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票财务数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}{report_type}财务数据")

        if ctx:
            report_type_cn = {
                "balance_sheet": "资产负债表",
                "income": "利润表",
                "cashflow": "现金流量表"
            }.get(report_type, report_type)
            await ctx.info(f"开始获取股票 {code} 的{report_type_cn}...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在从数据源获取财务报表...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_financials,
            code, report_type
        )

        if ctx:
            await ctx.report_progress(0.8, 1.0, "正在处理财务数据...")

        financial_data = result.get("data", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, "完成！财务数据获取成功")
            await ctx.info(f"成功获取股票 {code} 的财务数据")

        logger.info(f"成功获取股票{code}财务数据，来源: {financial_data.get('_source', 'unknown')}")
        return financial_data

    async def get_stock_news_data(
        self,
        code: str,
        lookback_days: int = 7,
        limit: int = 100,
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取股票新闻数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}新闻数据，回溯{lookback_days}天，限制{limit}条")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的新闻数据...")
            await ctx.report_progress(0.0, 1.0, "初始化新闻获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.2, 1.0, f"正在搜索最近{lookback_days}天的新闻...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_news,
            code, lookback_days, limit
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在过滤和整理新闻...")

        news_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共获取 {len(news_data)} 条新闻")
            await ctx.info(f"成功获取股票 {code} 的 {len(news_data)} 条新闻")

        logger.info(f"成功获取股票{code}的{len(news_data)}条新闻")
        return news_data

    async def get_technical_indicator_data(
        self,
        code: str,
        indicator: str,
        lookback_days: int = 100,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取技术指标数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 计算股票{code}的{indicator}指标")

        if ctx:
            await ctx.info(f"开始计算股票 {code} 的 {indicator} 指标...")
            await ctx.report_progress(0.0, 1.0, "初始化技术指标计算")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, f"正在获取{lookback_days}天的K线数据...")
        
        if ctx:
            await ctx.report_progress(0.6, 1.0, f"正在计算 {indicator} 指标...")
        
        result = await loop.run_in_executor(
            None,
            get_technical_indicator,
            code, indicator, lookback_days
        )

        indicator_data = result.get("data", {})
        
        if ctx:
            latest_value = indicator_data.get('latest_value', 'N/A')
            await ctx.report_progress(1.0, 1.0, f"完成！{indicator} 最新值: {latest_value}")
            await ctx.info(f"成功计算股票 {code} 的 {indicator} 指标")

        logger.info(f"成功计算股票{code}的{indicator}指标: {indicator_data.get('latest_value', 'N/A')}")
        return indicator_data

    async def get_limit_up_stocks_data(
        self,
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取今日涨停股数据（支持进度报告）"""
        logger.info("MCP工具调用: 获取今日涨停股数据")

        if ctx:
            await ctx.info("开始获取今日涨停股票列表...")
            await ctx.report_progress(0.0, 1.0, "连接数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取涨停股票数据...")
        
        result = await loop.run_in_executor(
            None,
            get_limit_up_stocks
        )

        if ctx:
            await ctx.report_progress(0.8, 1.0, "正在过滤和整理数据...")

        limit_up_stocks = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！今日共 {len(limit_up_stocks)} 只涨停股")
            await ctx.info(f"成功获取 {len(limit_up_stocks)} 只涨停股数据")

        logger.info(f"成功获取{len(limit_up_stocks)}只涨停股数据")
        return limit_up_stocks

    async def get_stock_comment_score_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取千股千评评分数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}评分数据")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的千股千评数据...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取评分数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_comment_score,
            code
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在计算统计数据...")

        score_data = result.get("data", [])
        score_stats = result.get("stats", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(score_data)} 条评分记录")
            await ctx.info(f"成功获取股票 {code} 的 {len(score_data)} 条评分数据")

        logger.info(f"成功获取股票{code}的{len(score_data)}条评分数据")
        return {
            "data": score_data,
            "stats": score_stats
        }

    async def get_stock_comment_focus_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取用户关注指数数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}关注指数数据")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的关注指数...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取关注指数数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_comment_focus,
            code
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在计算统计数据...")

        focus_data = result.get("data", [])
        focus_stats = result.get("stats", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(focus_data)} 条关注记录")
            await ctx.info(f"成功获取股票 {code} 的 {len(focus_data)} 条关注指数")

        logger.info(f"成功获取股票{code}的{len(focus_data)}条关注指数数据")
        return {
            "data": focus_data,
            "stats": focus_stats
        }

    async def get_stock_comment_desire_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取市场参与意愿数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}参与意愿数据")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的参与意愿数据...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取参与意愿数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_comment_desire_daily,
            code
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在计算统计数据...")

        desire_data = result.get("data", [])
        desire_stats = result.get("stats", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(desire_data)} 条参与意愿记录")
            await ctx.info(f"成功获取股票 {code} 的 {len(desire_data)} 条参与意愿数据")

        logger.info(f"成功获取股票{code}的{len(desire_data)}条参与意愿数据")
        return {
            "data": desire_data,
            "stats": desire_stats
        }

    async def get_stock_comment_institution_data(
        self, 
        code: str,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取机构参与度数据（支持进度报告）"""
        logger.info(f"MCP工具调用: 获取股票{code}机构参与度数据")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的机构参与度...")
            await ctx.report_progress(0.0, 1.0, "初始化数据获取")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取机构参与度数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_comment_institution,
            code
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在计算统计数据...")

        institution_data = result.get("data", [])
        institution_stats = result.get("stats", {})
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(institution_data)} 条机构参与记录")
            await ctx.info(f"成功获取股票 {code} 的 {len(institution_data)} 条机构参与度数据")

        logger.info(f"成功获取股票{code}的{len(institution_data)}条机构参与度数据")
        return {
            "data": institution_data,
            "stats": institution_stats
        }

    async def get_individual_fund_flow_data(
        self,
        code: str,
        market: str = "sh",
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取个股资金流向数据（支持进度报告）"""
        logger.info(f"获取股票{code}的资金流向数据，市场: {market}")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的资金流向数据...")
            await ctx.report_progress(0.0, 1.0, "连接东方财富数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取资金流数据...")
        
        result = await loop.run_in_executor(
            None,
            get_individual_fund_flow,
            code,
            market
        )

        if ctx:
            await ctx.report_progress(0.8, 1.0, "正在整理资金流向数据...")

        fund_flow_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(fund_flow_data)} 条资金流数据")
            await ctx.info(f"成功获取股票 {code} 的 {len(fund_flow_data)} 条资金流数据")

        logger.info(f"成功获取股票{code}的{len(fund_flow_data)}条资金流数据")
        return fund_flow_data

    async def get_concept_fund_flow_data(
        self,
        symbol: str = "即时",
        indicator: str = "即时",
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取概念板块资金流向数据（支持进度报告）"""
        logger.info(f"获取概念资金流数据，周期: {symbol}")

        if ctx:
            await ctx.info(f"开始获取概念板块资金流数据（{symbol}）...")
            await ctx.report_progress(0.0, 1.0, "连接同花顺数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取概念板块数据...")
        
        result = await loop.run_in_executor(
            None,
            get_concept_fund_flow,
            symbol,
            indicator
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在排序和整理数据...")

        concept_flow_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(concept_flow_data)} 个概念板块")
            await ctx.info(f"成功获取 {len(concept_flow_data)} 个概念板块的资金流数据")

        logger.info(f"成功获取{len(concept_flow_data)}条概念资金流数据")
        return concept_flow_data

    async def get_industry_fund_flow_data(
        self,
        symbol: str = "即时",
        indicator: str = "即时",
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取行业板块资金流向数据（支持进度报告）"""
        logger.info(f"获取行业资金流数据，周期: {symbol}")

        if ctx:
            await ctx.info(f"开始获取行业板块资金流数据（{symbol}）...")
            await ctx.report_progress(0.0, 1.0, "连接同花顺数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取行业板块数据...")
        
        result = await loop.run_in_executor(
            None,
            get_industry_fund_flow,
            symbol,
            indicator
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在排序和整理数据...")

        industry_flow_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(industry_flow_data)} 个行业板块")
            await ctx.info(f"成功获取 {len(industry_flow_data)} 个行业板块的资金流数据")

        logger.info(f"成功获取{len(industry_flow_data)}条行业资金流数据")
        return industry_flow_data

    async def get_big_deal_fund_flow_data(
        self,
        ctx: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """获取大单追踪数据（支持进度报告）"""
        logger.info("获取大单追踪数据")

        if ctx:
            await ctx.info("开始获取大单追踪数据...")
            await ctx.report_progress(0.0, 1.0, "连接数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取大单交易数据...")
        
        result = await loop.run_in_executor(
            None,
            get_big_deal_fund_flow
        )

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在过滤和整理大单数据...")

        big_deal_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(big_deal_data)} 条大单记录")
            await ctx.info(f"成功获取 {len(big_deal_data)} 条大单追踪数据")

        logger.info(f"成功获取{len(big_deal_data)}条大单追踪数据")
        return big_deal_data

    async def get_stock_cyq_data(
        self,
        code: str,
        date: Optional[str] = None,
        ctx: Optional[Any] = None
    ) -> Dict[str, Any]:
        """获取股票筹码分布数据（支持进度报告）"""
        adjust = date if date else ""
        logger.info(f"获取股票筹码分布数据: {code}, date={date}")

        if ctx:
            await ctx.info(f"开始获取股票 {code} 的筹码分布数据...")
            await ctx.report_progress(0.0, 1.0, "连接东方财富数据源")

        loop = asyncio.get_event_loop()
        
        if ctx:
            await ctx.report_progress(0.3, 1.0, "正在获取筹码分布数据...")
        
        result = await loop.run_in_executor(
            None,
            get_stock_cyq,
            code,
            adjust
        )

        # 检查是否有错误
        error = result.get("error")
        if error:
            logger.error(f"获取筹码分布失败: {error}")
            if ctx:
                await ctx.error(f"获取筹码分布失败: {error}")
            raise DataFlowError(f"获取筹码分布失败: {error}")

        if ctx:
            await ctx.report_progress(0.7, 1.0, "正在分析筹码分布...")

        cyq_data = result.get("data", [])
        
        if ctx:
            await ctx.report_progress(1.0, 1.0, f"完成！共 {len(cyq_data)} 条筹码分布数据")
            await ctx.info(f"成功获取股票 {code} 的 {len(cyq_data)} 条筹码分布数据")

        logger.info(f"成功获取{len(cyq_data)}条筹码分布数据")
        return {
            "data": cyq_data,
            "meta": {
                "code": code,
                "date": date or "latest",
                "total_records": len(cyq_data)
            }
        }


# 创建全局MCP工具实例
_mcp_tools_instance: Optional[MCPTools] = None


def get_mcp_tools() -> MCPTools:
    """
    获取MCP工具实例

    Returns:
        MCPTools实例
    """
    global _mcp_tools_instance
    if _mcp_tools_instance is None:
        _mcp_tools_instance = MCPTools()
        logger.info("创建MCP工具实例")
    return _mcp_tools_instance
