"""
A股数据流模块
专注A股市场数据获取和技术分析

主要功能:
- A股行情数据获取 (实时价格、K线数据)
- A股财务数据获取 (资产负债表、利润表、现金流)
- A股新闻资讯获取
- A股技术分析指标计算
- 市场指数数据获取
- 线程安全的会话缓存
- 统一的错误处理机制

特性:
- 支持verbose和quiet参数控制输出
- 线程安全的缓存机制
- 多数据源回退机制
- 统一的异常处理
- 简洁高效的接口设计
"""

# 导出实际存在的 A 股数据与分析接口
from .akshare_client import (
    AkshareClient,
    get_akshare_client_instance,
    get_limit_up_stocks,
    get_stock_kline,
    get_stock_realtime,
    get_stock_financials,
    get_stock_news,
    get_stock_comment_score,
    get_stock_comment_focus,
    get_stock_comment_desire_daily,
    get_stock_comment_institution,
    get_individual_fund_flow,
    get_concept_fund_flow,
    get_industry_fund_flow,
    get_big_deal_fund_flow,
    get_stock_cyq,
)

# A股技术分析接口
from .a_share_technical import (
    AShareTechnical,
    get_technical_analyzer_instance,
    get_technical_indicator,
    get_supported_indicators,
)

# 基础工具函数（当前模块中存在的）
from .utils import (
    format_stock_code,
    get_current_date,
    validate_date_format,
    get_exchange_code,
)

# 缓存相关函数
from .session_cache import (
    clear_session_cache,
    get_cache_stats,
)

# 工厂模式相关
from .factories import (
    DataFlowFactory,
    get_factory,
    set_factory,
    reset_factory,
    get_akshare_client,
    get_technical_analyzer,
)

# 异常处理
from .exceptions import (
    DataFlowError,
    AkshareAPIError,
    TechnicalAnalysisError,
    CacheError,
    ValidationError,
    NetworkError,
    ConfigurationError,
    wrap_exception,
)

# 日志系统
from .logging import (
    MCPLogger,
    logger,
    setup_logging,
    get_logger,
)


__all__ = [
    # akshare client
    "AkshareClient",
    "get_akshare_client_instance",
    "get_limit_up_stocks",
    "get_stock_kline",
    "get_stock_realtime",
    "get_stock_financials",
    "get_stock_news",
    "get_stock_comment_score",
    "get_stock_comment_focus",
    "get_stock_comment_desire_daily",
    "get_stock_comment_institution",
    "get_individual_fund_flow",
    "get_concept_fund_flow",
    "get_industry_fund_flow",
    "get_big_deal_fund_flow",
    "get_stock_cyq",

    # technical
    "AShareTechnical",
    "get_technical_analyzer_instance",
    "get_technical_indicator",
    "get_supported_indicators",

    # utils
    "format_stock_code",
    "get_current_date",
    "validate_date_format",
    "get_exchange_code",

    # cache
    "clear_session_cache",
    "get_cache_stats",

    # factory pattern
    "DataFlowFactory",
    "get_factory",
    "set_factory",
    "reset_factory",
    "get_akshare_client",
    "get_technical_analyzer",

    # exceptions
    "DataFlowError",
    "AkshareAPIError",
    "TechnicalAnalysisError",
    "CacheError",
    "ValidationError",
    "NetworkError",
    "ConfigurationError",
    "wrap_exception",

    # logging
    "MCPLogger",
    "logger",
    "setup_logging",
    "get_logger",
]
