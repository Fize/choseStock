"""
重构的A股技术分析模块
提供完整的技术指标计算和分析功能，适配A股市场数据
使用标准日志系统，符合MCP服务规范
"""

import pandas as pd
from stockstats import wrap
from typing import Any
from .utils import format_stock_code, get_current_date
from .session_cache import session_cache
from .akshare_client import AkshareClient
from .logging import logger
from .exceptions import TechnicalAnalysisError, DataFlowError


class AShareTechnical:
    """重构的A股技术分析类"""
    
    def __init__(self):
        """
        初始化技术分析模块
        
        Args:
            verbose: 是否显示详细信息
            quiet: 是否静默模式
        """
        self.client = AkshareClient()
        
        # 支持的技术指标及其说明
        self.indicators_info = {
            # 移动平均线
            "close_5_sma": "5日简单移动平均: 短期趋势指标，用于判断短期支撑阻力",
            "close_10_sma": "10日简单移动平均: 短期趋势指标，常用于短线交易",
            "close_20_sma": "20日简单移动平均: 中短期趋势指标，常用技术分析基准",
            "close_30_sma": "30日简单移动平均: 月线均线，中期趋势判断",
            "close_60_sma": "60日简单移动平均: 季线均线，中长期趋势判断",
            "close_120_sma": "120日简单移动平均: 半年线，长期趋势判断",
            "close_250_sma": "250日简单移动平均: 年线，长期投资参考",
            
            # 指数移动平均线
            "close_5_ema": "5日指数移动平均: 对价格变化更敏感的短期均线",
            "close_10_ema": "10日指数移动平均: 短期动量指标",
            "close_20_ema": "20日指数移动平均: 中短期趋势指标",
            
            # MACD指标
            "macd": "MACD差离值: 趋势跟踪动量指标，判断买卖时机",
            "macds": "MACD信号线: MACD的9日EMA，用于产生交易信号",
            "macdh": "MACD柱状图: MACD与信号线差值，显示动量强弱",
            
            # 相对强弱指标
            "rsi": "RSI相对强弱指标: 超买超卖指标，14日RSI为标准",
            "rsi_6": "6日RSI: 短期超买超卖指标",
            "rsi_12": "12日RSI: 中期相对强弱指标",
            "rsi_24": "24日RSI: 长期相对强弱指标",
            
            # 布林带指标
            "boll": "布林中轨: 20日移动平均线，价格重心",
            "boll_ub": "布林上轨: 上阻力线，超买区域",
            "boll_lb": "布林下轨: 下支撑线，超卖区域",
            
            # 波动率指标
            "atr": "ATR平均真实波动: 衡量价格波动程度",
            "atr_14": "14日ATR: 标准波动率指标",
            
            # 动量指标
            "cci": "CCI商品通道指数: 超买超卖及趋势指标",
            "cci_14": "14日CCI: 标准商品通道指数",
            
            # 成交量指标
            "vwma": "成交量加权移动平均: 结合成交量的价格平均",
            "mfi": "资金流量指标: 结合价格和成交量的动量指标",
            
            # KDJ指标
            "kdjk": "KDJ指标K值: 随机指标K值",
            "kdjd": "KDJ指标D值: 随机指标D值",
            "kdjj": "KDJ指标J值: 随机指标J值",
            
            # 威廉指标
            "wr": "威廉指标: 反向超买超卖指标",
            "wr_14": "14日威廉指标: 标准威廉指标",
        }
    
    @session_cache()
    def get_technical_indicator(
        self, 
        code: str, 
        indicator: str, 
        lookback_days: int = 60
    ) -> dict[str, Any]:
        """
        计算单个技术指标
        
        Args:
            code: 股票代码
            indicator: 技术指标名称
            lookback_days: 计算所需的历史数据天数
            
        Returns:
            技术指标数据字典
            
        Raises:
            TechnicalAnalysisError: 技术分析失败时抛出
        """
        try:
            # 参数验证
            if not code or not isinstance(code, str):
                raise ValueError("股票代码不能为空")
            
            if not indicator or not isinstance(indicator, str):
                raise ValueError("技术指标名称不能为空")
            
            if lookback_days <= 0 or lookback_days > 1000:
                raise ValueError("回溯天数必须在1-1000之间")
            
            # 验证指标支持
            if indicator not in self.indicators_info:
                supported = ', '.join(list(self.indicators_info.keys())[:10])
                error_msg = f'不支持的指标: {indicator}。支持的指标包括: {supported}...'
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg, indicator=indicator)

            formatted_code = format_stock_code(code)
            logger.info(f"计算 {formatted_code} 的 {indicator} 指标")
    
            # 获取K线数据
            kline_result = self.client.get_stock_kline(
                code=formatted_code, 
                lookback_days=lookback_days
            )
            
            if kline_result.get('error'):
                error_msg = f'获取K线数据失败: {kline_result["error"]}'
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg, indicator=indicator)

            kline_data = kline_result['data']
            if not kline_data:
                error_msg = '无K线数据'
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg, indicator=indicator)

            # 转换为DataFrame并计算指标
            df = self._prepare_dataframe(kline_data)
            wrapped_df = wrap(df)
            
            # 计算指标
            if hasattr(wrapped_df, indicator) or indicator in wrapped_df.columns:
                # 触发指标计算
                indicator_values = wrapped_df[indicator]
                
                # 获取最近的有效值
                latest_value = self._get_latest_valid_value(indicator_values)
                
                result = {
                    'data': {
                        'indicator': indicator,
                        'latest_value': latest_value,
                        'values': indicator_values.dropna().tail(20).to_dict(),  # 最近20个有效值
                        'description': self.indicators_info.get(indicator, ''),
                        'calculation_date': get_current_date()
                    },
                    'error': None
                }
                logger.info(f"成功计算 {indicator}: {latest_value}")
                return result
            else:
                error_msg = f'指标计算失败: {indicator}'
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg, indicator=indicator)
        except TechnicalAnalysisError:
            raise  # 重新抛出已处理的异常
        except Exception as e:
            error_msg = f"计算技术指标失败: {str(e)}"
            logger.error(error_msg)
            raise TechnicalAnalysisError(error_msg, indicator=indicator, original_error=e)
    
    def get_technical_indicators_window(
        self, 
        code: str, 
        indicator: str, 
        lookback_days: int = 30,
        window_days: int = 60
    ) -> dict[str, Any]:
        """
        获取指定时间窗口内的技术指标数据，仅返回原始数据
        """
        try:
            if not code or not isinstance(code, str):
                raise ValueError("股票代码不能为空")
            if not indicator or not isinstance(indicator, str):
                raise ValueError("技术指标名称不能为空")
            if lookback_days <= 0 or lookback_days > 100:
                raise ValueError("显示天数必须在1-100之间")
            if window_days <= 0 or window_days > 1000:
                raise ValueError("计算天数必须在1-1000之间")
            result = self.get_technical_indicator(code, indicator, window_days)
            if result.get('error'):
                error_msg = f"获取技术指标失败: {result['error']}"
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg, indicator=indicator)
            indicator_data = result['data']
            values = indicator_data['values']
            # 仅返回最近lookback_days天的原始数据
            recent_values = dict(list(values.items())[-lookback_days:])
            return {
                'indicator': indicator,
                'latest_value': indicator_data['latest_value'],
                'values': recent_values,
                'description': indicator_data['description'],
                'calculation_date': indicator_data['calculation_date'],
                'error': None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_stock_technical_summary(
        self, 
        code: str, 
        lookback_days: int = 100
    ) -> dict[str, Any]:
        """
        获取多个核心技术指标的原始数据
        """
        try:
            if not code or not isinstance(code, str):
                raise ValueError("股票代码不能为空")
            if lookback_days <= 0 or lookback_days > 1000:
                raise ValueError("分析天数必须在1-1000之间")
            core_indicators = [
                'close_20_sma', 'close_60_sma', 'rsi', 'macd', 'macds', 
                'boll', 'boll_ub', 'boll_lb', 'kdjk', 'kdjd'
            ]
            indicators_data = {}
            issues = []
            for indicator in core_indicators:
                try:
                    result = self.get_technical_indicator(code, indicator, lookback_days)
                    if not result.get('error'):
                        indicators_data[indicator] = result['data']
                except Exception as e:
                    issues.append(f"获取技术指标失败: {indicator} - {str(e)}")
            if issues:
                logger.warning("以下技术指标获取失败:")
                for issue in issues:
                    logger.warning(f" - {issue}")
            return indicators_data
        except Exception as e:
            return {'error': str(e)}
    
    def _prepare_dataframe(self, kline_data: list[dict]) -> pd.DataFrame:
        """
        将K线数据转换为适合技术分析的DataFrame格式
        
        Args:
            kline_data: K线数据列表
            
        Returns:
            格式化的DataFrame
            
        Raises:
            TechnicalAnalysisError: 数据转换失败时抛出
        """
        try:
            if not kline_data:
                error_msg = "K线数据为空"
                logger.error(error_msg)
                raise TechnicalAnalysisError(error_msg)

            df = pd.DataFrame(kline_data)
            
            # 重命名列以匹配stockstats要求
            column_mapping = {
                'date': 'date',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'volume': 'volume'
            }
            
            # 检查必需的列
            required_columns = ['close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    error_msg = f"缺少必需的列: {col}"
                    logger.error(error_msg)
                    raise TechnicalAnalysisError(error_msg)
            
            df = df.rename(columns=column_mapping)
            
            # 确保数据类型正确
            numeric_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # 设置日期索引
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
            
            # 按日期排序
            df.sort_index(inplace=True)
            
            # 移除无效数据
            df = df.dropna(subset=['close'])

            if df.empty:
                logger.warning("数据清理后为空")

            return df

        except TechnicalAnalysisError:
            raise  # 重新抛出已处理的异常
        except Exception as e:
            error_msg = f"数据转换失败: {str(e)}"
            logger.error(error_msg)
            raise TechnicalAnalysisError(error_msg, original_error=e)
    
    def _get_latest_valid_value(self, series) -> Any:
        """
        获取序列中最新的有效值
        
        Args:
            series: pandas序列
            
        Returns:
            最新有效值
        """
        try:
            valid_values = series.dropna()
            if len(valid_values) > 0:
                latest = valid_values.iloc[-1]
                if pd.isna(latest):
                    return "N/A"
                return round(float(latest), 4) if isinstance(latest, (int, float)) else latest
            return "N/A"
        except Exception:
            return "N/A"
    


# 提供便捷的函数接口 - 使用工厂模式
# 注意：这些函数现在通过工厂创建新实例，不再使用单例模式

def get_technical_analyzer_instance() -> "AShareTechnical":
    """获取技术分析实例（使用工厂模式）。

    返回一个新的 AShareTechnical 实例，使用工厂模式确保更好的并发安全性。

    Returns:
        AShareTechnical: 技术分析器实例。

    示例:
        >>> from dataflows_mcp.core.a_share_technical import get_technical_analyzer_instance
        >>> analyzer = get_technical_analyzer_instance()
    """
    from .factories import get_factory
    return get_factory().create_technical_analyzer()


def get_technical_indicator(code: str, indicator: str, lookback_days: int = 100) -> dict[str, Any]:
    """便捷：获取技术指标数据（封装缓存）。

    参数:
        code: 股票代码
        indicator: 技术指标名称
        lookback_days: 回溯天数，默认 100

    返回:
        dict: 包含 'data' 和 'error' 字段的字典。

    示例:
        >>> from dataflows_mcp.core.a_share_technical import get_technical_indicator
        >>> res = get_technical_indicator('600519', 'rsi', 30)
        >>> print(res['data']['latest_value'])
    """
    return get_technical_analyzer_instance().get_technical_indicator(code, indicator, lookback_days)


def get_supported_indicators() -> list[str]:
    """获取支持的技术指标列表"""
    return list(AShareTechnical().indicators_info.keys())