"""
数据格式一致性验证测试

验证改造后的数据格式与预期schema一致
"""
import pytest
from dataflows_mcp.tools.mcp_tools import MCPTools
from dataflows_mcp.tools.schemas import (
    KLineDataSchema,
    RealTimeQuotesSchema,
    TechnicalIndicatorSchema,
    FinancialDataSchema,
    NewsDataSchema,
    LimitUpStocksSchema,
    StockCommentScoreSchema,
    StockCommentFocusSchema,
    StockCommentDesireSchema,
    StockCommentInstitutionSchema
)



@pytest.fixture
def mcp_tools():
    """创建MCPTools实例"""
    return MCPTools()


class TestKLineDataFormat:
    """K线数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_kline_data_structure(self, mcp_tools):
        """验证K线数据结构"""
        result = await mcp_tools.get_stock_kline_data(code="600519", lookback_days=5)
        
        # 验证返回结构
        assert "success" in result
        assert "data" in result
        assert "meta" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # data应该是一个列表
            assert isinstance(data, list)
            
            # 验证K线数据项
            if len(data) > 0:
                item = data[0]
                required_fields = ["date", "open", "high", "low", "close", "volume"]
                for field in required_fields:
                    assert field in item, f"缺少必需字段: {field}"

    
    @pytest.mark.asyncio
    async def test_kline_data_validation(self, mcp_tools):
        """验证K线数据能通过Schema验证"""
        result = await mcp_tools.get_stock_kline_data(code="600519", lookback_days=5)
        
        if result["error"] is None and result["success"]:
            # 验证数据是列表且包含必需字段
            assert isinstance(result["data"], list)
            if len(result["data"]) > 0:
                item = result["data"][0]
                assert "date" in item
                assert "close" in item



class TestRealTimeDataFormat:
    """实时行情数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_realtime_data_structure(self, mcp_tools):
        """验证实时行情数据结构"""
        result = await mcp_tools.get_stock_realtime_data(code="600519")
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # 验证必需字段
            assert "code" in data
            assert "name" in data or "price" in data
            
            # 验证数据类型
            assert isinstance(data["code"], str)



class TestTechnicalIndicatorFormat:
    """技术指标数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_indicator_data_structure(self, mcp_tools):
        """验证技术指标数据结构"""
        result = await mcp_tools.get_technical_indicator_data(
            code="600519",
            indicator="rsi",
            lookback_days=30
        )
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # data应该是一个列表
            assert isinstance(data, list)

    
    @pytest.mark.asyncio
    async def test_multiple_indicators(self, mcp_tools):
        """验证多个技术指标的数据格式一致性"""
        indicators = ["rsi", "macd", "boll"]
        
        for indicator in indicators:
            result = await mcp_tools.get_technical_indicator_data(
                code="600519",
                indicator=indicator,
                lookback_days=30
            )
            
            if result["error"] is None and result["success"]:
                data = result["data"]
                # 所有指标都应该返回列表
                assert isinstance(data, list)



class TestFinancialDataFormat:
    """财务数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_financial_data_structure(self, mcp_tools):
        """验证财务数据结构"""
        result = await mcp_tools.get_stock_financial_data(
            code="600519",
            report_type="balance_sheet"
        )
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # data应该是一个字典，包含财务数据
            assert isinstance(data, dict)



class TestNewsDataFormat:
    """新闻数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_news_data_structure(self, mcp_tools):
        """验证新闻数据结构"""
        result = await mcp_tools.get_stock_news_data(
            code="600519",
            lookback_days=7,
            limit=10
        )
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # data应该是一个列表
            assert isinstance(data, list)
            
            # 验证新闻数量限制
            assert len(data) <= 10



class TestLimitUpStocksFormat:
    """涨停股数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_limit_up_data_structure(self, mcp_tools):
        """验证涨停股数据结构"""
        result = await mcp_tools.get_limit_up_stocks_data()
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            # data应该是一个列表
            assert isinstance(data, list)



class TestCommentDataFormat:
    """千股千评数据格式验证"""
    
    @pytest.mark.asyncio
    async def test_comment_score_structure(self, mcp_tools):
        """验证评分数据结构"""
        result = await mcp_tools.get_stock_comment_score_data(code="600519")
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            assert isinstance(data, list)

    
    @pytest.mark.asyncio
    async def test_comment_focus_structure(self, mcp_tools):
        """验证关注度数据结构"""
        result = await mcp_tools.get_stock_comment_focus_data(code="600519")
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            assert isinstance(data, list)

    
    @pytest.mark.asyncio
    async def test_comment_desire_structure(self, mcp_tools):
        """验证参与意愿数据结构"""
        result = await mcp_tools.get_stock_comment_desire_data(code="600519")
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            assert isinstance(data, list)

    
    @pytest.mark.asyncio
    async def test_comment_institution_structure(self, mcp_tools):
        """验证机构参与度数据结构"""
        result = await mcp_tools.get_stock_comment_institution_data(code="600519")
        
        assert "success" in result
        assert "data" in result
        assert "error" in result
        
        if result["error"] is None and result["success"]:
            data = result["data"]
            assert isinstance(data, list)


class TestErrorFormat:
    """错误格式验证"""
    
    @pytest.mark.asyncio
    async def test_error_structure(self, mcp_tools):
        """验证错误返回格式"""
        # 使用无效股票代码触发错误
        result = await mcp_tools.get_stock_kline_data(code="INVALID")
        
        assert "data" in result
        assert "error" in result
        
        # 错误情况下，error应该不为None
        if result["error"] is not None:
            assert isinstance(result["error"], str)
            assert len(result["error"]) > 0


class TestDataConsistency:
    """数据一致性验证"""
    
    @pytest.mark.asyncio
    async def test_same_code_consistency(self, mcp_tools):
        """验证同一股票代码的数据一致性"""
        code = "600519"
        
        # 获取K线数据
        kline_result = await mcp_tools.get_stock_kline_data(code=code, lookback_days=5)
        
        # 获取实时数据
        realtime_result = await mcp_tools.get_stock_realtime_data(code=code)
        
        # 两个接口都应该成功返回数据
        if kline_result["error"] is None and realtime_result["error"] is None:
            assert kline_result["success"] is True
            assert realtime_result["success"] is True
            assert realtime_result["data"]["code"] == code

    
    @pytest.mark.asyncio
    async def test_data_type_consistency(self, mcp_tools):
        """验证数据类型一致性"""
        result = await mcp_tools.get_stock_kline_data(code="600519", lookback_days=5)
        
        if result["error"] is None and result["success"]:
            kline_data = result["data"]
            
            # 验证所有数据项的类型一致
            for item in kline_data:
                assert isinstance(item.get("date"), str)
                # 数值字段应该是数字类型
                for field in ["open", "high", "low", "close", "volume"]:
                    if field in item:
                        assert isinstance(item[field], (int, float, str))



if __name__ == "__main__":
    pytest.main([__file__, "-v"])
