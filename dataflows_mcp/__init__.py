"""
A股数据流 MCP 服务
提供符合 Model Context Protocol 标准的 A股市场数据服务
支持 stdio、sse、streamable-http 三种 transport
"""

__version__ = "0.1.0"

from .server.mcp_server import main

__all__ = [
    "main",
]
