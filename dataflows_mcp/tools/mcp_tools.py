"""
MCP工具封装模块
提供所有A股数据获取和技术分析功能的MCP工具接口
支持异步调用，符合MCP服务规范
"""

import asyncio
from typing import Any, Dict, List, Optional
from datetime import datetime
from ..core import (
    get_stock_kline,
    get_stock_realtime,
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
    validate_date_format,
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
    """

    def __init__(self):
        """初始化MCP工具类"""
        logger.info("MCP工具类已初始化")

    async def get_stock_kline_data(
        self,
        code: str,
        lookback_days: int = 60,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        获取股票K线数据 - MCP工具

        Args:
            code: 股票代码
            lookback_days: 回溯天数，默认60天
            period: 周期类型，默认daily

        Returns:
            K线数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}K线数据")

            # 在线程池中执行同步操作
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_kline,
                code, lookback_days, period
            )

            logger.info(f"成功获取股票{code}的{len(result.get('data', []))}条K线数据")
            return {
                "success": True,
                "data": result.get("data", []),
                "meta": result.get("meta", {}),
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "meta": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取K线数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "meta": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_realtime_data(self, code: str) -> Dict[str, Any]:
        """
        获取股票实时行情 - MCP工具

        Args:
            code: 股票代码

        Returns:
            实时行情数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}实时行情")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_realtime,
                code
            )

            realtime_data = result.get("data", {})
            logger.info(f"成功获取股票{code}实时行情: {realtime_data.get('price', 'N/A')}")

            return {
                "success": True,
                "data": realtime_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取实时行情失败: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取实时行情异常: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_financial_data(
        self,
        code: str,
        report_type: str = "balance_sheet"
    ) -> Dict[str, Any]:
        """
        获取股票财务数据 - MCP工具

        Args:
            code: 股票代码
            report_type: 报表类型 balance_sheet/income/cashflow

        Returns:
            财务数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}{report_type}财务数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_financials,
                code, report_type
            )

            financial_data = result.get("data", {})
            logger.info(f"成功获取股票{code}财务数据，来源: {financial_data.get('_source', 'unknown')}")

            return {
                "success": True,
                "data": financial_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取财务数据失败: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取财务数据异常: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_news_data(
        self,
        code: str,
        lookback_days: int = 7,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        获取股票新闻数据 - MCP工具

        Args:
            code: 股票代码
            lookback_days: 回溯天数
            limit: 新闻数量限制

        Returns:
            新闻数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}新闻数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_news,
                code, lookback_days, limit
            )

            news_data = result.get("data", [])
            logger.info(f"成功获取股票{code}的{len(news_data)}条新闻")

            return {
                "success": True,
                "data": news_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取新闻数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取新闻数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_technical_indicator_data(
        self,
        code: str,
        indicator: str,
        lookback_days: int = 100
    ) -> Dict[str, Any]:
        """
        获取技术指标数据 - MCP工具

        Args:
            code: 股票代码
            indicator: 技术指标名称
            lookback_days: 回溯天数

        Returns:
            技术指标数据字典
        """
        try:
            logger.info(f"MCP工具调用: 计算股票{code}的{indicator}指标")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_technical_indicator,
                code, indicator, lookback_days
            )

            indicator_data = result.get("data", {})
            logger.info(f"成功计算股票{code}的{indicator}指标: {indicator_data.get('latest_value', 'N/A')}")

            return {
                "success": True,
                "data": indicator_data,
                "error": None
            }

        except (TechnicalAnalysisError, ValidationError) as e:
            logger.error(f"计算技术指标失败: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"计算技术指标异常: {str(e)}")
            return {
                "success": False,
                "data": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_limit_up_stocks_data(self) -> Dict[str, Any]:
        """
        获取今日涨停股数据 - MCP工具

        Returns:
            涨停股数据字典
        """
        try:
            logger.info("MCP工具调用: 获取今日涨停股数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_limit_up_stocks
            )

            limit_up_stocks = result.get("data", [])
            logger.info(f"成功获取{len(limit_up_stocks)}只涨停股数据")

            return {
                "success": True,
                "data": limit_up_stocks,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取涨停股数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取涨停股数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_comment_score_data(self, code: str) -> Dict[str, Any]:
        """
        获取千股千评评分数据 - MCP工具

        Args:
            code: 股票代码

        Returns:
            评分数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}评分数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_comment_score,
                code
            )

            score_data = result.get("data", [])
            score_stats = result.get("stats", {})
            logger.info(f"成功获取股票{code}的{len(score_data)}条评分数据")

            return {
                "success": True,
                "data": score_data,
                "stats": score_stats,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取评分数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取评分数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_comment_focus_data(self, code: str) -> Dict[str, Any]:
        """
        获取用户关注指数数据 - MCP工具

        Args:
            code: 股票代码

        Returns:
            关注指数数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}关注指数数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_comment_focus,
                code
            )

            focus_data = result.get("data", [])
            focus_stats = result.get("stats", {})
            logger.info(f"成功获取股票{code}的{len(focus_data)}条关注指数数据")

            return {
                "success": True,
                "data": focus_data,
                "stats": focus_stats,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取关注指数数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取关注指数数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_comment_desire_data(self, code: str) -> Dict[str, Any]:
        """
        获取市场参与意愿数据 - MCP工具

        Args:
            code: 股票代码

        Returns:
            参与意愿数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}参与意愿数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_comment_desire_daily,
                code
            )

            desire_data = result.get("data", [])
            desire_stats = result.get("stats", {})
            logger.info(f"成功获取股票{code}的{len(desire_data)}条参与意愿数据")

            return {
                "success": True,
                "data": desire_data,
                "stats": desire_stats,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取参与意愿数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取参与意愿数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_comment_institution_data(self, code: str) -> Dict[str, Any]:
        """
        获取机构参与度数据 - MCP工具

        Args:
            code: 股票代码

        Returns:
            机构参与度数据字典
        """
        try:
            logger.info(f"MCP工具调用: 获取股票{code}机构参与度数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_comment_institution,
                code
            )

            institution_data = result.get("data", [])
            institution_stats = result.get("stats", {})
            logger.info(f"成功获取股票{code}的{len(institution_data)}条机构参与度数据")

            return {
                "success": True,
                "data": institution_data,
                "stats": institution_stats,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取机构参与度数据失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取机构参与度数据异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "stats": {},
                "error": f"系统错误: {str(e)}"
            }

    async def get_individual_fund_flow_data(
        self,
        code: str,
        market: str = "sh"
    ) -> Dict[str, Any]:
        """获取个股资金流向数据（东方财富）

        Args:
            code: 股票代码
            market: 市场标识，可选值: sh(上海)、sz(深圳)、bj(北京)

        Returns:
            包含资金流数据的字典
        """
        try:
            logger.info(f"获取股票{code}的资金流向数据，市场: {market}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_individual_fund_flow,
                code,
                market
            )

            fund_flow_data = result.get("data", [])
            logger.info(f"成功获取股票{code}的{len(fund_flow_data)}条资金流数据")

            return {
                "success": True,
                "data": fund_flow_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取个股资金流向失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取个股资金流向异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_concept_fund_flow_data(
        self,
        symbol: str = "即时",
        indicator: str = "即时"
    ) -> Dict[str, Any]:
        """获取概念板块资金流向数据（同花顺）

        Args:
            symbol: 时间周期，可选值: "即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
            indicator: 数据指标，与symbol保持一致

        Returns:
            包含概念资金流数据的字典
        """
        try:
            logger.info(f"获取概念资金流数据，周期: {symbol}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_concept_fund_flow,
                symbol,
                indicator
            )

            concept_flow_data = result.get("data", [])
            logger.info(f"成功获取{len(concept_flow_data)}条概念资金流数据")

            return {
                "success": True,
                "data": concept_flow_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取概念资金流向失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取概念资金流向异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_industry_fund_flow_data(
        self,
        symbol: str = "即时",
        indicator: str = "即时"
    ) -> Dict[str, Any]:
        """获取行业板块资金流向数据（同花顺）

        Args:
            symbol: 时间周期，可选值: "即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
            indicator: 数据指标，与symbol保持一致

        Returns:
            包含行业资金流数据的字典
        """
        try:
            logger.info(f"获取行业资金流数据，周期: {symbol}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_industry_fund_flow,
                symbol,
                indicator
            )

            industry_flow_data = result.get("data", [])
            logger.info(f"成功获取{len(industry_flow_data)}条行业资金流数据")

            return {
                "success": True,
                "data": industry_flow_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取行业资金流向失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取行业资金流向异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_big_deal_fund_flow_data(self) -> Dict[str, Any]:
        """获取大单追踪数据（同花顺）

        Returns:
            包含大单交易数据的字典
        """
        try:
            logger.info("获取大单追踪数据")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_big_deal_fund_flow
            )

            big_deal_data = result.get("data", [])
            logger.info(f"成功获取{len(big_deal_data)}条大单追踪数据")

            return {
                "success": True,
                "data": big_deal_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取大单追踪失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取大单追踪异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
            }

    async def get_stock_cyq_data(
        self,
        code: str,
        adjust: str = ""
    ) -> Dict[str, Any]:
        """获取股票筹码分布数据（东方财富）

        Args:
            code: 股票代码
            adjust: 复权类型，""=不复权，"qfq"=前复权，"hfq"=后复权

        Returns:
            包含筹码分布数据的字典（近90个交易日）
        """
        try:
            logger.info(f"获取股票筹码分布数据: {code}, adjust={adjust}")

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                get_stock_cyq,
                code,
                adjust
            )

            cyq_data = result.get("data", [])
            error = result.get("error")

            if error:
                logger.error(f"获取筹码分布失败: {error}")
                return {
                    "success": False,
                    "data": [],
                    "error": error
                }

            logger.info(f"成功获取{len(cyq_data)}条筹码分布数据")

            return {
                "success": True,
                "data": cyq_data,
                "error": None
            }

        except (AkshareAPIError, ValidationError) as e:
            logger.error(f"获取筹码分布失败: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"获取筹码分布异常: {str(e)}")
            return {
                "success": False,
                "data": [],
                "error": f"系统错误: {str(e)}"
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