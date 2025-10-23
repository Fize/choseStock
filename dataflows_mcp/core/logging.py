"""
MCP服务日志系统模块
替换原有的CLI输出系统，提供标准化的日志功能
支持将日志输出到文件和终端
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional
from logging.handlers import RotatingFileHandler


class MCPLogger:
    """MCP服务专用日志器"""

    def __init__(self, name: str = "dataflows_mcp"):
        self.logger = logging.getLogger(name)
        self._handlers_configured = False

    def setup(
        self, 
        level: int = logging.INFO, 
        format_string: Optional[str] = None,
        log_to_file: bool = True,
        log_file_path: Optional[str] = None
    ) -> None:
        """
        设置日志配置

        Args:
            level: 日志级别，默认为INFO
            format_string: 自定义日志格式字符串
            log_to_file: 是否输出到文件，默认为True
            log_file_path: 日志文件路径，如果为None则从环境变量STOCK_LOG_FILE读取，
                          环境变量未设置则使用默认路径 ~/.stock.log
        """
        if format_string is None:
            format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        # 避免重复配置
        if self._handlers_configured:
            return

        # 设置日志级别
        self.logger.setLevel(level)
        
        # 创建格式化器
        formatter = logging.Formatter(format_string)
        
        # 清除现有的handlers
        self.logger.handlers.clear()
        
        # 添加控制台handler（输出到stderr）
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 添加文件handler
        if log_to_file:
            # 确定日志文件路径
            if log_file_path is None:
                log_file_path = os.environ.get('STOCK_LOG_FILE')
            
            if log_file_path is None:
                # 使用默认路径：用户家目录下的.stock.log
                log_file_path = str(Path.home() / '.stock.log')
            
            # 确保日志文件目录存在
            log_file = Path(log_file_path)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 创建RotatingFileHandler（支持日志轮转，避免文件过大）
            # 最大10MB，保留5个备份文件
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.logger.info(f"日志文件已配置: {log_file_path}")
        
        self._handlers_configured = True

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


def setup_logging(
    level: int = logging.INFO,
    log_to_file: bool = True,
    log_file_path: Optional[str] = None
) -> MCPLogger:
    """
    快速设置日志配置并返回日志器

    Args:
        level: 日志级别
        log_to_file: 是否输出到文件，默认为True
        log_file_path: 日志文件路径，如果为None则从环境变量STOCK_LOG_FILE读取

    Returns:
        MCPLogger实例
    """
    logger.setup(level, log_to_file=log_to_file, log_file_path=log_file_path)
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