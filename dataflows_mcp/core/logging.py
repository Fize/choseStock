"""
MCP服务日志系统模块
替换原有的CLI输出系统，提供标准化的日志功能
"""

import logging
import sys
from typing import Optional


class MCPLogger:
    """MCP服务专用日志器"""

    def __init__(self, name: str = "dataflows_mcp"):
        self.logger = logging.getLogger(name)

    def setup(self, level: int = logging.INFO, format_string: Optional[str] = None) -> None:
        """
        设置日志配置

        Args:
            level: 日志级别，默认为INFO
            format_string: 自定义日志格式字符串
        """
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # 配置基础日志
        logging.basicConfig(
            level=level,
            format=format_string,
            handlers=[
                logging.StreamHandler(sys.stderr)  # 输出到stderr，符合服务标准
            ]
        )

    def info(self, message: str, *args, **kwargs) -> None:
        """记录信息级别日志 - 替换原来的output.print()"""
        self.logger.info(message, *args, **kwargs)

    def debug(self, message: str, *args, **kwargs) -> None:
        """记录调试级别日志"""
        self.logger.debug(message, *args, **kwargs)

    def warning(self, message: str, *args, **kwargs) -> None:
        """记录警告级别日志"""
        self.logger.warning(message, *args, **kwargs)

    def error(self, message: str, *args, **kwargs) -> None:
        """记录错误级别日志 - 替换原来的output.fatal()的部分功能"""
        self.logger.error(message, *args, **kwargs)

    def critical(self, message: str, *args, **kwargs) -> None:
        """记录严重错误级别日志"""
        self.logger.critical(message, *args, **kwargs)


# 创建全局日志器实例
logger = MCPLogger("dataflows_mcp")


def setup_logging(level: int = logging.INFO) -> MCPLogger:
    """
    快速设置日志配置并返回日志器

    Args:
        level: 日志级别

    Returns:
        MCPLogger实例
    """
    logger.setup(level)
    return logger


def get_logger(name: str = "dataflows_mcp") -> MCPLogger:
    """
    获取指定名称的日志器

    Args:
        name: 日志器名称

    Returns:
        MCPLogger实例
    """
    return MCPLogger(name)