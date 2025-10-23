"""
MCP服务工厂类模块
使用工厂模式替换原有的单例模式，提供更好的并发安全性和测试支持
"""

from typing import Optional
from .logging import logger


class DataFlowFactory:
    """
    数据流服务工厂
    负责创建和管理各种数据流服务实例
    """

    def __init__(self):
        """初始化工厂"""
        logger.info("数据流服务工厂已初始化")

    def create_akshare_client(self) -> "AkshareClient":
        """
        创建Akshare客户端实例

        Returns:
            AkshareClient实例
        """
        try:
            # 延迟导入以避免循环依赖
            from .akshare_client import AkshareClient

            client = AkshareClient()
            logger.debug("创建新的Akshare客户端实例")
            return client

        except ImportError as e:
            logger.error(f"导入AkshareClient失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建Akshare客户端失败: {e}")
            raise

    def create_technical_analyzer(self) -> "AShareTechnical":
        """
        创建技术分析器实例

        Returns:
            AShareTechnical实例
        """
        try:
            # 延迟导入以避免循环依赖
            from .a_share_technical import AShareTechnical

            analyzer = AShareTechnical()
            logger.debug("创建新的技术分析器实例")
            return analyzer

        except ImportError as e:
            logger.error(f"导入AShareTechnical失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建技术分析器失败: {e}")
            raise

    def get_akshare_client(self) -> "AkshareClient":
        """
        获取Akshare客户端（便捷方法，保持向后兼容）

        Returns:
            AkshareClient实例
        """
        return self.create_akshare_client()

    def get_technical_analyzer(self) -> "AShareTechnical":
        """
        获取技术分析器（便捷方法，保持向后兼容）

        Returns:
            AShareTechnical实例
        """
        return self.create_technical_analyzer()


# 全局工厂实例（非单例，可随时替换）
_default_factory: Optional[DataFlowFactory] = None


def get_factory() -> DataFlowFactory:
    """
    获取默认工厂实例

    Returns:
        DataFlowFactory实例
    """
    global _default_factory
    if _default_factory is None:
        _default_factory = DataFlowFactory()
        logger.info("创建默认数据流服务工厂")
    return _default_factory


def set_factory(factory: DataFlowFactory) -> None:
    """
    设置工厂实例（主要用于测试）

    Args:
        factory: 新的工厂实例
    """
    global _default_factory
    _default_factory = factory
    logger.info("已设置新的数据流服务工厂")


def reset_factory() -> None:
    """重置工厂实例为默认值"""
    global _default_factory
    _default_factory = None
    logger.info("已重置数据流服务工厂")


# 便捷函数，保持与原有单例模式的兼容性
def get_akshare_client() -> "AkshareClient":
    """
    获取Akshare客户端（便捷函数）

    Returns:
        AkshareClient实例
    """
    return get_factory().create_akshare_client()


def get_technical_analyzer() -> "AShareTechnical":
    """
    获取技术分析器（便捷函数）

    Returns:
        AShareTechnical实例
    """
    return get_factory().create_technical_analyzer()