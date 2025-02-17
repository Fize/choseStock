"""
A股数据流 MCP 服务
提供符合 Model Context Protocol 标准的 A股市场数据服务
"""

__version__ = "0.1.0"

from .server.mcp_server import AShareMCPServer, main

__all__ = [
    "AShareMCPServer",
    "main",
]
