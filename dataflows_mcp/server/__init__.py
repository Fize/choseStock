"""
MCP服务器模块
提供A股数据流的MCP服务实现
支持 stdio、sse、streamable-http 三种 transport
"""

from .mcp_server import main

__all__ = [
    "main"
]
