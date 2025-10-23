"""
重构的工具函数模块
提供基础的日期处理、数据保存、代码格式化等功能
使用标准日志系统，符合MCP服务规范
"""

from datetime import date, datetime
from typing import Any, Dict
import pandas as pd
import numpy as np
from .logging import logger
from .exceptions import ValidationError, DataFlowError


def safe_serialize_value(value: Any) -> Any:
    """
    安全地将值转换为可JSON序列化的类型
    
    Args:
        value: 需要转换的值
        
    Returns:
        可序列化的Python原生类型
    """
    # 处理None
    if value is None or (hasattr(value, '__len__') and len(value) == 0):
        return None
    
    # 处理pandas的NA值
    if pd.isna(value):
        return None
    
    # 处理numpy和pandas的数值类型
    if isinstance(value, (np.integer, np.int64, np.int32)):
        return int(value)
    if isinstance(value, (np.floating, np.float64, np.float32)):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    
    # 处理Timestamp
    if isinstance(value, pd.Timestamp):
        return value.strftime('%Y-%m-%d %H:%M:%S')
    if hasattr(value, 'strftime'):  # datetime对象
        return value.strftime('%Y-%m-%d %H:%M:%S')
    
    # 处理字符串
    if isinstance(value, (str, int, float, bool)):
        return value
    
    # 其他情况尝试转为字符串
    return str(value)


def dataframe_to_dict(df: pd.DataFrame, orient: str = 'records') -> Any:
    """
    安全地将DataFrame转换为字典，确保所有值都可JSON序列化
    
    Args:
        df: pandas DataFrame
        orient: 转换方向 'records'(行列表) / 'dict'(列字典) / 'list'(列列表)
        
    Returns:
        可JSON序列化的字典或列表
    """
    if df is None or df.empty:
        return [] if orient == 'records' else {}
    
    # 先转为dict
    data = df.to_dict(orient=orient)
    
    # 递归清理所有值
    if orient == 'records':
        # 列表形式: [{col1: val1, col2: val2}, ...]
        return [{k: safe_serialize_value(v) for k, v in row.items()} for row in data]
    elif orient == 'dict':
        # 字典形式: {col1: {row1: val1, ...}, ...}
        return {col: {k: safe_serialize_value(v) for k, v in vals.items()} 
                for col, vals in data.items()}
    elif orient == 'list':
        # 列表形式: {col1: [val1, val2, ...], ...}
        return {col: [safe_serialize_value(v) for v in vals] 
                for col, vals in data.items()}
    else:
        return data


def series_to_dict(series: pd.Series) -> Dict[str, Any]:
    """
    安全地将Series转换为字典，确保所有键值都可JSON序列化
    
    Args:
        series: pandas Series
        
    Returns:
        可JSON序列化的字典
    """
    if series is None or series.empty:
        return {}
    
    result = {}
    for idx, val in series.items():
        # 转换键
        if isinstance(idx, pd.Timestamp):
            key = idx.strftime('%Y-%m-%d')
        elif hasattr(idx, 'strftime'):
            key = idx.strftime('%Y-%m-%d')
        else:
            key = str(idx)
        
        # 转换值
        result[key] = safe_serialize_value(val)
    
    return result


def get_current_date() -> str:
    """
    获取当前日期字符串
    
    Returns:
        格式为YYYY-MM-DD的日期字符串
    """
    return date.today().strftime("%Y-%m-%d")


def format_stock_code(code: str, target_format: str = "plain") -> str:
    """
    格式化股票代码为不同数据源所需的格式
    
    Args:
        code: 原始股票代码，如"000001"或"000001.SZ"
        target_format: 目标格式 "plain"(纯数字) / "akshare" / "sina" / "xueqiu"
        verbose: 是否显示详细信息
        quiet: 是否静默模式
        
    Returns:
        格式化后的股票代码
        
    Raises:
        UtilsError: 代码格式错误时抛出
    """
    try:
        # 参数验证
        if not code or not isinstance(code, str):
            raise ValueError("股票代码不能为空")
        
        valid_formats = ["plain", "akshare", "sina", "xueqiu"]
        if target_format not in valid_formats:
            raise ValueError(f"目标格式必须是: {', '.join(valid_formats)}")
        
        # 清理代码，移除可能的后缀和空格
        clean_code = code.split('.')[0].strip()
        
        # 验证代码格式
        if len(clean_code) != 6 or not clean_code.isdigit():
            error_msg = f"无效的股票代码格式: {code}"
            logger.error(error_msg)
            raise ValidationError(error_msg, field="code", value=code)

        # 获取交易所代码
        exchange_code = get_exchange_code(clean_code)
        
        if target_format == "plain":
            # 纯数字格式
            return clean_code
        
        elif target_format == "akshare":
            # AkShare某些接口需要带后缀
            return f"{clean_code}.{exchange_code}"
        
        elif target_format == "sina":
            # 新浪接口格式: sh600036 (小写前缀)
            return f"{exchange_code.lower()}{clean_code}"
        
        elif target_format == "xueqiu":
            # 雪球接口格式: SH600036 (大写前缀)
            return f"{exchange_code}{clean_code}"
        
        else:
            return clean_code

    except ValidationError:
        raise  # 重新抛出已处理的异常
    except ValueError as e:
        error_msg = f"参数错误: {str(e)}"
        logger.error(error_msg)
        raise ValidationError(error_msg, field="code", value=code, original_error=e)
    except Exception as e:
        error_msg = f"格式化股票代码失败: {str(e)}"
        logger.error(error_msg)
        raise DataFlowError(error_msg, original_error=e)

def get_exchange_code(code: str) -> str:
    """
    根据股票代码获取交易所代码
    
    Args:
        code: 股票代码
        verbose: 是否显示详细信息
        quiet: 是否静默模式
        
    Returns:
        交易所代码: "SH"(上海) / "SZ"(深圳) / "BJ"(北京)
        
    Raises:
        UtilsError: 代码格式错误时抛出
    """
    try:
        # 参数验证
        if not code or not isinstance(code, str):
            raise ValueError("股票代码不能为空")
        
        clean_code = code.split('.')[0].strip()
        
        if clean_code.startswith(('60', '68', '51')):
            return "SH"  # 上海证券交易所
        elif clean_code.startswith(('00', '30')):
            return "SZ"  # 深圳证券交易所
        elif clean_code.startswith(('8', '4')):
            return "BJ"  # 北京证券交易所
        else:
            error_msg = f"无法识别股票代码的交易所: {code}"
            logger.error(error_msg)
            raise ValidationError(error_msg, field="code", value=code)

    except ValidationError:
        raise  # 重新抛出已处理的异常
    except ValueError as e:
        error_msg = f"参数错误: {str(e)}"
        logger.error(error_msg)
        raise ValidationError(error_msg, field="code", value=code, original_error=e)
    except Exception as e:
        error_msg = f"获取交易所代码失败: {str(e)}"
        logger.error(error_msg)
        raise DataFlowError(error_msg, original_error=e)

