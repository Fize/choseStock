"""
MCP工具Schema定义模块
定义所有MCP工具的输入输出Schema，符合MCP规范
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class KLineDataSchema(BaseModel):
    """K线数据工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码，支持格式：600519、600519.SH、000001.SZ等",
            examples=["600519", "000001.SZ", "300750"]
        )
        lookback_days: int = Field(
            default=60,
            ge=1,
            le=1000,
            description="回溯天数，范围1-1000天",
            examples=[30, 60, 90]
        )
        period: str = Field(
            default="daily",
            description="周期类型：daily(日线)、weekly(周线)、monthly(月线)",
            examples=["daily", "weekly", "monthly"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="K线数据列表，包含date, open, high, low, close, volume, change等字段"
        )
        meta: Dict[str, Any] = Field(
            default={},
            description="元数据，包含code, period, count, start_date, end_date等信息"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class RealTimeQuotesSchema(BaseModel):
    """实时行情工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: Dict[str, Any] = Field(
            default={},
            description="实时行情数据，包含price, change, change_percent, volume, amount等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class TechnicalIndicatorSchema(BaseModel):
    """技术指标工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )
        indicator: str = Field(
            ...,
            description="技术指标名称",
            examples=["rsi", "macd", "boll", "close_20_sma"]
        )
        lookback_days: int = Field(
            default=100,
            ge=1,
            le=1000,
            description="回溯天数，范围1-1000天",
            examples=[30, 60, 100]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: Dict[str, Any] = Field(
            default={},
            description="技术指标数据，包含indicator, latest_value, values, description等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class FinancialDataSchema(BaseModel):
    """财务数据工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )
        report_type: str = Field(
            default="balance_sheet",
            description="报表类型：balance_sheet(资产负债表)、income(利润表)、cashflow(现金流量表)",
            examples=["balance_sheet", "income", "cashflow"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: Dict[str, Any] = Field(
            default={},
            description="财务数据，包含各项财务指标和_source字段标注数据来源"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class NewsDataSchema(BaseModel):
    """新闻数据工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )
        lookback_days: int = Field(
            default=7,
            ge=1,
            le=30,
            description="回溯天数，范围1-30天",
            examples=[7, 14, 30]
        )
        limit: int = Field(
            default=100,
            ge=1,
            le=500,
            description="新闻数量限制，范围1-500条",
            examples=[10, 50, 100]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="新闻数据列表，包含title, content, publish_time, source, url等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class LimitUpStocksSchema(BaseModel):
    """涨停股数据工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        # 无输入参数，直接获取今日涨停股
        pass

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="涨停股数据列表，包含code, name, current_value, change_percent等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class StockCommentScoreSchema(BaseModel):
    """千股千评评分数据工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="评分历史数据，包含date, score等字段"
        )
        stats: Dict[str, Any] = Field(
            default={},
            description="统计信息，包含latest_score, average_score, score_trend等"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class StockCommentFocusSchema(BaseModel):
    """用户关注指数工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="关注指数历史数据，包含date, focus_index等字段"
        )
        stats: Dict[str, Any] = Field(
            default={},
            description="统计信息，包含latest_focus, average_focus, focus_level等"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class StockCommentDesireSchema(BaseModel):
    """市场参与意愿工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="参与意愿历史数据，包含date, daily_desire_change, five_day_avg_change等字段"
        )
        stats: Dict[str, Any] = Field(
            default={},
            description="统计信息，包含latest_desire_change, average_desire_change, desire_strength等"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class StockCommentInstitutionSchema(BaseModel):
    """机构参与度工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="机构参与度历史数据，包含date, institution_participation等字段"
        )
        stats: Dict[str, Any] = Field(
            default={},
            description="统计信息，包含latest_institution_participation, average_institution_participation等"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class IndividualFundFlowSchema(BaseModel):
    """个股资金流向工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码，如600519",
            examples=["600519", "000001", "300750"]
        )
        market: str = Field(
            default="sh",
            description="市场标识，可选值: sh(上海)、sz(深圳)、bj(北京)",
            examples=["sh", "sz", "bj"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="个股资金流数据，包含date, main_net_inflow, super_large_net_inflow等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class ConceptFundFlowSchema(BaseModel):
    """概念资金流向工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        symbol: str = Field(
            default="即时",
            description="时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行",
            examples=["即时", "3日排行", "5日排行"]
        )
        indicator: str = Field(
            default="即时",
            description="数据指标，与symbol保持一致",
            examples=["即时", "3日排行", "5日排行"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="概念资金流数据，包含concept, inflow, outflow, net_amount等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class IndustryFundFlowSchema(BaseModel):
    """行业资金流向工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        symbol: str = Field(
            default="即时",
            description="时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行",
            examples=["即时", "3日排行", "5日排行"]
        )
        indicator: str = Field(
            default="即时",
            description="数据指标，与symbol保持一致",
            examples=["即时", "3日排行", "5日排行"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="行业资金流数据，包含industry, inflow, outflow, net_amount等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class BigDealFundFlowSchema(BaseModel):
    """大单追踪工具Schema"""

    class Input(BaseModel):
        """输入参数Schema（无需参数）"""
        pass

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="大单交易数据，包含code, name, trade_price, trade_volume, deal_type等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


class StockCyqSchema(BaseModel):
    """筹码分布工具Schema"""

    class Input(BaseModel):
        """输入参数Schema"""
        code: str = Field(
            ...,
            description="股票代码",
            examples=["600519", "000001", "300750"]
        )
        adjust: str = Field(
            default="",
            description="复权类型：\"\"(不复权)、\"qfq\"(前复权)、\"hfq\"(后复权)",
            examples=["", "qfq", "hfq"]
        )

    class Output(BaseModel):
        """输出数据Schema"""
        success: bool = Field(..., description="请求是否成功")
        data: List[Dict[str, Any]] = Field(
            default=[],
            description="筹码分布数据（近90个交易日），包含date, profit_ratio, average_cost, 90_cost_low, 90_cost_high, 90_concentration, 70_cost_low, 70_cost_high, 70_concentration等字段"
        )
        error: Optional[str] = Field(
            default=None,
            description="错误信息，成功时为None"
        )


# Schema映射字典，用于工具注册
SCHEMA_MAPPING = {
    "get_stock_kline_data": KLineDataSchema,
    "get_stock_realtime_data": RealTimeQuotesSchema,
    "get_technical_indicator_data": TechnicalIndicatorSchema,
    "get_stock_financial_data": FinancialDataSchema,
    "get_stock_news_data": NewsDataSchema,
    "get_limit_up_stocks_data": LimitUpStocksSchema,
    "get_stock_comment_score_data": StockCommentScoreSchema,
    "get_stock_comment_focus_data": StockCommentFocusSchema,
    "get_stock_comment_desire_data": StockCommentDesireSchema,
    "get_stock_comment_institution_data": StockCommentInstitutionSchema,
    "get_individual_fund_flow_data": IndividualFundFlowSchema,
    "get_concept_fund_flow_data": ConceptFundFlowSchema,
    "get_industry_fund_flow_data": IndustryFundFlowSchema,
    "get_big_deal_fund_flow_data": BigDealFundFlowSchema,
    "get_stock_cyq_data": StockCyqSchema,
}


def get_tool_schema(tool_name: str) -> Optional[BaseModel]:
    """
    根据工具名称获取对应的Schema类

    Args:
        tool_name: 工具名称

    Returns:
        Schema类或None
    """
    return SCHEMA_MAPPING.get(tool_name)


def get_all_tool_names() -> List[str]:
    """
    获取所有支持的工具名称

    Returns:
        工具名称列表
    """
    """
    return list(SCHEMA_MAPPING.keys())

    """
    return list(SCHEMA_MAPPING.keys())