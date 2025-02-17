"""
MCP服务器模块
提供A股数据流的MCP服务实现
"""

from .mcp_server import AShareMCPServer, main

__all__ = [
    "AShareMCPServer",
    "main"
]
