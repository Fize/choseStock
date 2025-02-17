"""
MCP服务自定义异常模块
定义数据流相关的异常类，用于替换原来的直接退出机制
"""


class DataFlowError(Exception):
    """数据流基础异常类"""

    def __init__(self, message: str, original_error: Exception = None):
        """
        初始化数据流异常

        Args:
            message: 异常消息
            original_error: 原始异常（如果有）
        """
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self) -> str:
        """格式化异常信息"""
        if self.original_error:
            return f"{self.message} (原始错误: {str(self.original_error)})"
        return self.message


class AkshareAPIError(DataFlowError):
    """AkShare API调用异常"""

    def __init__(self, message: str, code: str = None, original_error: Exception = None):
        """
        初始化AkShare API异常

        Args:
            message: 异常消息
            code: 股票代码（如果有）
            original_error: 原始异常
        """
        self.code = code
        if code:
            message = f"股票{code}: {message}"
        super().__init__(message, original_error)


class TechnicalAnalysisError(DataFlowError):
    """技术分析异常"""

    def __init__(self, message: str, indicator: str = None, original_error: Exception = None):
        """
        初始化技术分析异常

        Args:
            message: 异常消息
            indicator: 技术指标名称（如果有）
            original_error: 原始异常
        """
        self.indicator = indicator
        if indicator:
            message = f"技术指标{indicator}: {message}"
        super().__init__(message, original_error)


class CacheError(DataFlowError):
    """缓存异常"""

    def __init__(self, message: str, cache_key: str = None, original_error: Exception = None):
        """
        初始化缓存异常

        Args:
            message: 异常消息
            cache_key: 缓存键（如果有）
            original_error: 原始异常
        """
        self.cache_key = cache_key
        if cache_key:
            message = f"缓存操作失败[{cache_key}]: {message}"
        super().__init__(message, original_error)


class ValidationError(DataFlowError):
    """数据验证异常"""

    def __init__(self, message: str, field: str = None, value: str = None, original_error: Exception = None):
        """
        初始化验证异常

        Args:
            message: 异常消息
            field: 验证字段（如果有）
            value: 验证值（如果有）
            original_error: 原始异常
        """
        self.field = field
        self.value = value

        if field and value:
            message = f"字段'{field}'的值'{value}'验证失败: {message}"
        elif field:
            message = f"字段'{field}'验证失败: {message}"

        super().__init__(message, original_error)


class NetworkError(DataFlowError):
    """网络连接异常"""

    def __init__(self, message: str, url: str = None, original_error: Exception = None):
        """
        初始化网络异常

        Args:
            message: 异常消息
            url: 请求URL（如果有）
            original_error: 原始异常
        """
        self.url = url
        if url:
            message = f"网络请求失败[{url}]: {message}"
        super().__init__(message, original_error)


class ConfigurationError(DataFlowError):
    """配置异常"""

    def __init__(self, message: str, config_key: str = None, original_error: Exception = None):
        """
        初始化配置异常

        Args:
            message: 异常消息
            config_key: 配置键（如果有）
            original_error: 原始异常
        """
        self.config_key = config_key
        if config_key:
            message = f"配置错误[{config_key}]: {message}"
        super().__init__(message, original_error)


# 异常工具函数
def wrap_exception(original_error: Exception, exception_class: type, message: str = None) -> DataFlowError:
    """
    包装原始异常为自定义异常

    Args:
        original_error: 原始异常
        exception_class: 目标异常类
        message: 自定义消息（可选）

    Returns:
        包装后的异常实例
    """
    if message is None:
        message = str(original_error)

    return exception_class(message, original_error=original_error)