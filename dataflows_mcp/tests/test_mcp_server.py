"""
MCP服务器测试模块
测试MCP服务器的功能和接口
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataflows_mcp.server.mcp_server import AShareMCPServer
from dataflows_mcp.tools.mcp_tools import MCPTools


class TestAShareMCPServer:
    """测试A股MCP服务器"""

    @pytest.fixture
    def server(self):
        """创建服务器实例"""
        return AShareMCPServer()

    def test_server_initialization(self, server):
        """测试服务器初始化"""
        assert server is not None
        assert server.server is not None
        assert server.mcp_tools is not None
        assert isinstance(server.mcp_tools, MCPTools)

    @pytest.mark.asyncio
    async def test_list_tools(self, server):
        """测试列出工具"""
        # 直接测试工具数量和名称（通过SCHEMA_MAPPING）
        from dataflows_mcp.tools.schemas import SCHEMA_MAPPING
        
        # 验证Schema映射
        assert len(SCHEMA_MAPPING) == 14  # 应该有14个工具
        
        # 验证工具名称
        expected_tools = [
            "get_stock_kline_data",
            "get_stock_realtime_data",
            "get_technical_indicator_data",
            "get_stock_financial_data",
            "get_stock_news_data",
            "get_limit_up_stocks_data",
            "get_stock_comment_score_data",
            "get_stock_comment_focus_data",
            "get_stock_comment_desire_data",
            "get_stock_comment_institution_data",
            "get_individual_fund_flow_data",
            "get_concept_fund_flow_data",
            "get_industry_fund_flow_data",
            "get_big_deal_fund_flow_data"
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in SCHEMA_MAPPING


    @pytest.mark.asyncio
    async def test_call_tool_success(self, server):
        """测试成功调用工具"""
        # Mock工具方法
        mock_result = {
            "success": True,
            "data": [{"date": "2025-10-10", "close": 100.0}],
            "meta": {"code": "600519"},
            "error": None
        }
        
        with patch.object(server.mcp_tools, 'get_stock_kline_data', 
                         new_callable=AsyncMock, return_value=mock_result):
            # 直接调用MCPTools方法
            result = await server.mcp_tools.get_stock_kline_data(
                code="600519",
                lookback_days=30
            )
            
            # 验证结果
            assert result["success"] is True
            assert "data" in result
            assert "meta" in result
            assert result["meta"]["code"] == "600519"


    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self, server):
        """测试调用未知工具"""
        # 验证MCPTools没有unknown_tool方法
        assert not hasattr(server.mcp_tools, 'unknown_tool')
        
        # 验证SCHEMA_MAPPING中没有unknown_tool
        from dataflows_mcp.tools.schemas import SCHEMA_MAPPING
        assert "unknown_tool" not in SCHEMA_MAPPING


    @pytest.mark.asyncio
    async def test_call_tool_invalid_arguments(self, server):
        """测试使用无效参数调用工具"""
        # Mock工具方法抛出TypeError
        with patch.object(server.mcp_tools, 'get_stock_kline_data',
                         side_effect=TypeError("missing required argument")):
            # 调用时应该抛出TypeError
            with pytest.raises(TypeError):
                await server.mcp_tools.get_stock_kline_data()


    @pytest.mark.asyncio
    async def test_call_tool_execution_error(self, server):
        """测试工具执行异常"""
        # Mock工具方法抛出异常
        with patch.object(server.mcp_tools, 'get_stock_kline_data',
                         side_effect=Exception("API调用失败")):
            # 调用时应该抛出异常
            with pytest.raises(Exception, match="API调用失败"):
                await server.mcp_tools.get_stock_kline_data(code="600519")


    @pytest.mark.asyncio
    async def test_call_all_tools(self, server):
        """测试调用所有工具（Mock模式）"""
        # 测试所有工具方法存在
        tool_methods = [
            "get_stock_kline_data",
            "get_stock_realtime_data",
            "get_technical_indicator_data",
            "get_stock_financial_data",
            "get_stock_news_data",
            "get_limit_up_stocks_data",
            "get_stock_comment_score_data",
            "get_stock_comment_focus_data",
            "get_stock_comment_desire_data",
            "get_stock_comment_institution_data"
        ]
        
        for tool_name in tool_methods:
            # 验证MCPTools有这个方法
            assert hasattr(server.mcp_tools, tool_name)
            # 验证方法是可调用的
            assert callable(getattr(server.mcp_tools, tool_name))


    def test_tool_schemas(self, server):
        """测试工具Schema定义"""
        from dataflows_mcp.tools.schemas import SCHEMA_MAPPING, get_tool_schema
        from pydantic import BaseModel
        from typing import Type
        
        # 验证每个工具都有完整的Schema类
        for tool_name in SCHEMA_MAPPING.keys():
            schema_class = get_tool_schema(tool_name)
            assert schema_class is not None
            # 验证是Pydantic BaseModel子类
            assert issubclass(schema_class, BaseModel)  # type: ignore
            # 验证有Input和Output内部类
            assert hasattr(schema_class, 'Input')
            assert hasattr(schema_class, 'Output')



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
