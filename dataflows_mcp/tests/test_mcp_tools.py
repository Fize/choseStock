"""
MCP工具测试模块
测试MCPTools类的所有功能，确保异步封装正确工作
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from dataflows_mcp.tools.mcp_tools import MCPTools, get_mcp_tools
from dataflows_mcp.core.exceptions import (
    AkshareAPIError,
    TechnicalAnalysisError,
    ValidationError
)


class TestMCPTools:
    """MCPTools测试类"""

    def setup_method(self):
        """测试方法初始化"""
        self.mcp_tools = MCPTools()

    def test_get_mcp_tools_singleton(self):
        """测试获取MCP工具实例的单例模式"""
        # 第一次获取
        tools1 = get_mcp_tools()
        assert tools1 is not None
        assert isinstance(tools1, MCPTools)

        # 第二次获取应该是同一个实例
        tools2 = get_mcp_tools()
        assert tools1 is tools2

    @pytest.mark.asyncio
    async def test_get_stock_kline_data_success(self):
        """测试成功获取K线数据"""
        mock_data = {
            "data": [
                {"date": "2025-10-01", "open": 100.0, "close": 105.0},
                {"date": "2025-10-02", "open": 105.0, "close": 110.0}
            ],
            "meta": {"code": "600519", "period": "daily", "count": 2}
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_kline", return_value=mock_data):
            result = await self.mcp_tools.get_stock_kline_data("600519", 60, "daily")

            assert result["success"] is True
            assert len(result["data"]) == 2
            assert result["data"][0]["date"] == "2025-10-01"
            assert result["meta"]["code"] == "600519"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_kline_data_error(self):
        """测试获取K线数据失败"""
        with patch("dataflows_mcp.tools.mcp_tools.get_stock_kline", side_effect=AkshareAPIError("API错误")):
            result = await self.mcp_tools.get_stock_kline_data("invalid_code", 60, "daily")

            assert result["success"] is False
            assert result["data"] == []
            assert result["meta"] == {}
            assert "API错误" in result["error"]

    @pytest.mark.asyncio
    async def test_get_stock_realtime_data_success(self):
        """测试成功获取实时行情数据"""
        mock_data = {
            "data": {
                "price": 150.5,
                "change": 2.5,
                "change_percent": 1.69,
                "volume": 1000000
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_realtime", return_value=mock_data):
            result = await self.mcp_tools.get_stock_realtime_data("600519")

            assert result["success"] is True
            assert result["data"]["price"] == 150.5
            assert result["data"]["change_percent"] == 1.69
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_financial_data_success(self):
        """测试成功获取财务数据"""
        mock_data = {
            "data": {
                "total_assets": 1000000000,
                "net_profit": 50000000,
                "_source": "akshare"
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_financials", return_value=mock_data):
            result = await self.mcp_tools.get_stock_financial_data("600519", "balance_sheet")

            assert result["success"] is True
            assert result["data"]["total_assets"] == 1000000000
            assert result["data"]["_source"] == "akshare"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_news_data_success(self):
        """测试成功获取新闻数据"""
        mock_data = {
            "data": [
                {
                    "title": "测试新闻标题",
                    "content": "测试新闻内容",
                    "publish_time": "2025-10-10 10:00:00",
                    "source": "新浪财经"
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_news", return_value=mock_data):
            result = await self.mcp_tools.get_stock_news_data("600519", 7, 10)

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["title"] == "测试新闻标题"
            assert result["data"][0]["source"] == "新浪财经"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_technical_indicator_data_success(self):
        """测试成功获取技术指标数据"""
        mock_data = {
            "data": {
                "indicator": "rsi",
                "latest_value": 65.5,
                "values": [60.0, 62.5, 65.5],
                "description": "相对强弱指标"
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_technical_indicator", return_value=mock_data):
            result = await self.mcp_tools.get_technical_indicator_data("600519", "rsi", 100)

            assert result["success"] is True
            assert result["data"]["indicator"] == "rsi"
            assert result["data"]["latest_value"] == 65.5
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_technical_indicator_data_error(self):
        """测试获取技术指标数据失败"""
        with patch("dataflows_mcp.tools.mcp_tools.get_technical_indicator",
                  side_effect=TechnicalAnalysisError("技术指标计算错误")):
            result = await self.mcp_tools.get_technical_indicator_data("600519", "invalid_indicator", 100)

            assert result["success"] is False
            assert result["data"] == {}
            assert "技术指标计算错误" in result["error"]

    @pytest.mark.asyncio
    async def test_get_limit_up_stocks_data_success(self):
        """测试成功获取涨停股数据"""
        mock_data = {
            "data": [
                {
                    "code": "600519",
                    "name": "贵州茅台",
                    "current_value": 1800.0,
                    "change_percent": 10.0
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_limit_up_stocks", return_value=mock_data):
            result = await self.mcp_tools.get_limit_up_stocks_data()

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["code"] == "600519"
            assert result["data"][0]["change_percent"] == 10.0
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_comment_score_data_success(self):
        """测试成功获取评分数据"""
        mock_data = {
            "data": [
                {"date": "2025-10-01", "score": 85},
                {"date": "2025-10-02", "score": 82}
            ],
            "stats": {
                "latest_score": 82,
                "average_score": 83.5,
                "score_trend": "stable"
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_comment_score", return_value=mock_data):
            result = await self.mcp_tools.get_stock_comment_score_data("600519")

            assert result["success"] is True
            assert len(result["data"]) == 2
            assert result["stats"]["latest_score"] == 82
            assert result["stats"]["average_score"] == 83.5
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_comment_focus_data_success(self):
        """测试成功获取关注指数数据"""
        mock_data = {
            "data": [
                {"date": "2025-10-01", "focus_index": 75},
                {"date": "2025-10-02", "focus_index": 80}
            ],
            "stats": {
                "latest_focus": 80,
                "average_focus": 77.5,
                "focus_level": "high"
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_comment_focus", return_value=mock_data):
            result = await self.mcp_tools.get_stock_comment_focus_data("600519")

            assert result["success"] is True
            assert len(result["data"]) == 2
            assert result["stats"]["latest_focus"] == 80
            assert result["stats"]["focus_level"] == "high"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_comment_desire_data_success(self):
        """测试成功获取参与意愿数据"""
        mock_data = {
            "data": [
                {
                    "date": "2025-10-01",
                    "daily_desire_change": 2.5,
                    "five_day_avg_change": 1.8
                }
            ],
            "stats": {
                "latest_desire_change": 2.5,
                "average_desire_change": 1.8,
                "desire_strength": "strong"
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_comment_desire_daily", return_value=mock_data):
            result = await self.mcp_tools.get_stock_comment_desire_data("600519")

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["daily_desire_change"] == 2.5
            assert result["stats"]["desire_strength"] == "strong"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_stock_comment_institution_data_success(self):
        """测试成功获取机构参与度数据"""
        mock_data = {
            "data": [
                {"date": "2025-10-01", "institution_participation": 65},
                {"date": "2025-10-02", "institution_participation": 70}
            ],
            "stats": {
                "latest_institution_participation": 70,
                "average_institution_participation": 67.5
            }
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_comment_institution", return_value=mock_data):
            result = await self.mcp_tools.get_stock_comment_institution_data("600519")

            assert result["success"] is True
            assert len(result["data"]) == 2
            assert result["stats"]["latest_institution_participation"] == 70
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_general_exception_handling(self):
        """测试通用异常处理"""
        with patch("dataflows_mcp.tools.mcp_tools.get_stock_kline",
                  side_effect=Exception("未知错误")):
            result = await self.mcp_tools.get_stock_kline_data("600519", 60, "daily")

            assert result["success"] is False
            assert result["data"] == []
            assert result["meta"] == {}
            assert "系统错误" in result["error"]

    @pytest.mark.asyncio
    async def test_get_individual_fund_flow_data_success(self):
        """测试成功获取个股资金流向数据"""
        mock_data = {
            "data": [
                {
                    "date": "2025-01-15",
                    "close_price": 1820.0,
                    "change_percent": 2.5,
                    "main_net_inflow": 150000000.0,
                    "main_net_inflow_rate": 5.2,
                    "super_large_net_inflow": 80000000.0,
                    "super_large_net_inflow_rate": 2.8,
                    "large_net_inflow": 70000000.0,
                    "large_net_inflow_rate": 2.4,
                    "medium_net_inflow": -50000000.0,
                    "medium_net_inflow_rate": -1.7,
                    "small_net_inflow": -100000000.0,
                    "small_net_inflow_rate": -3.5
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_individual_fund_flow", return_value=mock_data):
            result = await self.mcp_tools.get_individual_fund_flow_data("600519", "sh")

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["date"] == "2025-01-15"
            assert result["data"][0]["main_net_inflow"] == 150000000.0
            assert result["data"][0]["super_large_net_inflow"] == 80000000.0
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_individual_fund_flow_data_error(self):
        """测试获取个股资金流向数据失败"""
        with patch("dataflows_mcp.tools.mcp_tools.get_individual_fund_flow",
                  side_effect=AkshareAPIError("API错误")):
            result = await self.mcp_tools.get_individual_fund_flow_data("invalid_code", "sh")

            assert result["success"] is False
            assert result["data"] == []
            assert "API错误" in result["error"]

    @pytest.mark.asyncio
    async def test_get_concept_fund_flow_data_success(self):
        """测试成功获取概念板块资金流向数据"""
        mock_data = {
            "data": [
                {
                    "序号": 1,
                    "板块": "人工智能",
                    "最新价": 1520.5,
                    "涨跌幅": 3.2,
                    "流入资金": 500000000.0,
                    "流出资金": 350000000.0,
                    "净额": 150000000.0,
                    "公司家数": 85,
                    "领涨股": "科大讯飞",
                    "领涨股涨跌幅": 5.8
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_concept_fund_flow", return_value=mock_data):
            result = await self.mcp_tools.get_concept_fund_flow_data("即时", "即时")

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["板块"] == "人工智能"
            assert result["data"][0]["净额"] == 150000000.0
            assert result["data"][0]["领涨股"] == "科大讯飞"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_concept_fund_flow_data_multi_day(self):
        """测试获取概念板块多日排行数据"""
        mock_data = {
            "data": [
                {
                    "序号": 1,
                    "板块": "新能源车",
                    "涨跌幅": 5.5,
                    "主力净流入-净额": 300000000.0,
                    "主力净流入-净占比": 8.5,
                    "公司家数": 120
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_concept_fund_flow", return_value=mock_data):
            result = await self.mcp_tools.get_concept_fund_flow_data("3日排行", "3日排行")

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["板块"] == "新能源车"
            assert result["data"][0]["主力净流入-净额"] == 300000000.0
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_industry_fund_flow_data_success(self):
        """测试成功获取行业板块资金流向数据"""
        mock_data = {
            "data": [
                {
                    "序号": 1,
                    "板块": "电子",
                    "最新价": 2300.8,
                    "涨跌幅": 2.1,
                    "流入资金": 800000000.0,
                    "流出资金": 600000000.0,
                    "净额": 200000000.0,
                    "公司家数": 120,
                    "领涨股": "立讯精密",
                    "领涨股涨跌幅": 4.5
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_industry_fund_flow", return_value=mock_data):
            result = await self.mcp_tools.get_industry_fund_flow_data("即时", "即时")

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["板块"] == "电子"
            assert result["data"][0]["净额"] == 200000000.0
            assert result["data"][0]["领涨股"] == "立讯精密"
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_industry_fund_flow_data_error(self):
        """测试获取行业板块资金流向数据失败"""
        with patch("dataflows_mcp.tools.mcp_tools.get_industry_fund_flow",
                  side_effect=AkshareAPIError("数据获取失败")):
            result = await self.mcp_tools.get_industry_fund_flow_data("即时", "即时")

            assert result["success"] is False
            assert result["data"] == []
            assert "数据获取失败" in result["error"]

    @pytest.mark.asyncio
    async def test_get_big_deal_fund_flow_data_success(self):
        """测试成功获取大单追踪数据"""
        mock_data = {
            "data": [
                {
                    "trade_time": "14:35:20",
                    "code": "600519",
                    "name": "贵州茅台",
                    "trade_price": 1820.0,
                    "trade_volume": 5000,
                    "trade_amount": 9100000.0,
                    "deal_type": "买盘",
                    "change_percent": 2.5,
                    "turnover_rate": 0.15
                }
            ]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_big_deal_fund_flow", return_value=mock_data):
            result = await self.mcp_tools.get_big_deal_fund_flow_data()

            assert result["success"] is True
            assert len(result["data"]) == 1
            assert result["data"][0]["code"] == "600519"
            assert result["data"][0]["name"] == "贵州茅台"
            assert result["data"][0]["deal_type"] == "买盘"
            assert result["data"][0]["trade_amount"] == 9100000.0
            assert result["error"] is None

    @pytest.mark.asyncio
    async def test_get_big_deal_fund_flow_data_error(self):
        """测试获取大单追踪数据失败"""
        with patch("dataflows_mcp.tools.mcp_tools.get_big_deal_fund_flow",
                  side_effect=AkshareAPIError("大单数据获取失败")):
            result = await self.mcp_tools.get_big_deal_fund_flow_data()

            assert result["success"] is False
            assert result["data"] == []
            assert "大单数据获取失败" in result["error"]


class TestMCPToolsIntegration:
    """MCPTools集成测试类"""

    @pytest.mark.asyncio
    async def test_multiple_concurrent_calls(self):
        """测试多个并发调用"""
        mcp_tools = MCPTools()

        # 模拟多个并发调用
        mock_kline_data = {"data": [{"date": "2025-10-01", "close": 100.0}], "meta": {}}
        mock_realtime_data = {"data": {"price": 150.5, "change": 2.5}}

        with patch("dataflows_mcp.tools.mcp_tools.get_stock_kline", return_value=mock_kline_data), \
             patch("dataflows_mcp.tools.mcp_tools.get_stock_realtime", return_value=mock_realtime_data):

            # 并发调用多个方法
            tasks = [
                mcp_tools.get_stock_kline_data("600519", 60, "daily"),
                mcp_tools.get_stock_realtime_data("600519"),
                mcp_tools.get_stock_kline_data("000001", 30, "daily")
            ]

            results = await asyncio.gather(*tasks)

            # 验证所有调用都成功
            assert len(results) == 3
            assert all(result["success"] for result in results)
            assert results[0]["data"][0]["close"] == 100.0
            assert results[1]["data"]["price"] == 150.5

    @pytest.mark.asyncio
    async def test_fund_flow_concurrent_calls(self):
        """测试资金流向工具的并发调用"""
        mcp_tools = MCPTools()

        # 模拟各种资金流向数据
        mock_individual_data = {
            "data": [{
                "date": "2025-01-15",
                "main_net_inflow": 150000000.0,
                "close_price": 1820.0
            }]
        }
        mock_concept_data = {
            "data": [{
                "板块": "人工智能",
                "净额": 200000000.0
            }]
        }
        mock_industry_data = {
            "data": [{
                "板块": "电子",
                "净额": 180000000.0
            }]
        }
        mock_big_deal_data = {
            "data": [{
                "code": "600519",
                "trade_amount": 9100000.0
            }]
        }

        with patch("dataflows_mcp.tools.mcp_tools.get_individual_fund_flow", return_value=mock_individual_data), \
             patch("dataflows_mcp.tools.mcp_tools.get_concept_fund_flow", return_value=mock_concept_data), \
             patch("dataflows_mcp.tools.mcp_tools.get_industry_fund_flow", return_value=mock_industry_data), \
             patch("dataflows_mcp.tools.mcp_tools.get_big_deal_fund_flow", return_value=mock_big_deal_data):

            # 并发调用所有资金流向工具
            tasks = [
                mcp_tools.get_individual_fund_flow_data("600519", "sh"),
                mcp_tools.get_concept_fund_flow_data("即时", "即时"),
                mcp_tools.get_industry_fund_flow_data("即时", "即时"),
                mcp_tools.get_big_deal_fund_flow_data()
            ]

            results = await asyncio.gather(*tasks)

            # 验证所有调用都成功
            assert len(results) == 4
            assert all(result["success"] for result in results)
            
            # 验证个股资金流数据
            assert results[0]["data"][0]["main_net_inflow"] == 150000000.0
            
            # 验证概念板块数据
            assert results[1]["data"][0]["板块"] == "人工智能"
            
            # 验证行业板块数据
            assert results[2]["data"][0]["板块"] == "电子"
            
            # 验证大单追踪数据
            assert results[3]["data"][0]["code"] == "600519"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])