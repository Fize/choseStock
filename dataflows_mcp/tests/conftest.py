"""
MCP服务测试配置
提供测试所需的fixtures和配置
"""

import pytest
import asyncio
from typing import Generator


@pytest.fixture
def event_loop() -> Generator:
    """为异步测试提供事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mcp_tools():
    """提供MCPTools实例"""
    from dataflows_mcp.tools.mcp_tools import MCPTools
    return MCPTools()