"""
重构的工具函数模块
提供基础的日期处理、数据保存、代码格式化等功能
使用标准日志系统，符合MCP服务规范
"""

from datetime import date, datetime
from .logging import logger
from .exceptions import ValidationError, DataFlowError


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

def validate_date_format(date_str: str, verbose: bool = False, quiet: bool = False) -> bool:
    """
    验证日期格式是否为YYYY-MM-DD
    
    Args:
        date_str: 日期字符串
        verbose: 是否显示详细信息
        quiet: 是否静默模式
        
    Returns:
        是否为有效日期格式
        
    Raises:
        UtilsError: 验证失败时抛出
    """
    try:
        # 参数验证
        if not date_str or not isinstance(date_str, str):
            error_msg = "日期字符串不能为空"
            logger.error(error_msg)
            raise ValidationError(error_msg, field="date_str", value=date_str)

        datetime.strptime(date_str, "%Y-%m-%d")
        return True

    except ValueError as e:
        if "does not match format" in str(e) or "unconverted data remains" in str(e):
            return False
        error_msg = f"参数错误: {str(e)}"
        logger.error(error_msg)
        raise ValidationError(error_msg, field="date_str", value=date_str, original_error=e)
    except ValidationError:
        raise  # 重新抛出已处理的异常
    except Exception as e:
        error_msg = f"验证日期格式失败: {str(e)}"
        logger.error(error_msg)
        raise DataFlowError(error_msg, original_error=e)

