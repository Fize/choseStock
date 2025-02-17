"""
Schema验证测试模块
验证所有MCP工具Schema的定义正确性
"""

import pytest
from typing import Dict, Any, List

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
    StockCommentInstitutionSchema,
    IndividualFundFlowSchema,
    ConceptFundFlowSchema,
    IndustryFundFlowSchema,
    BigDealFundFlowSchema,
    SCHEMA_MAPPING,
    get_tool_schema,
    get_all_tool_names
)


class TestSchemaDefinitions:
    """Schema定义测试类"""

    def test_kline_data_schema(self):
        """测试K线数据Schema"""
        # 测试输入Schema
        input_data = {
            "code": "600519",
            "lookback_days": 60,
            "period": "daily"
        }
        input_schema = KLineDataSchema.Input(**input_data)
        assert input_schema.code == "600519"
        assert input_schema.lookback_days == 60
        assert input_schema.period == "daily"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {"date": "2025-10-01", "open": 100.0, "close": 105.0},
                {"date": "2025-10-02", "open": 105.0, "close": 110.0}
            ],
            "meta": {"code": "600519", "period": "daily", "count": 2},
            "error": None
        }
        output_schema = KLineDataSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 2
        assert output_schema.meta["code"] == "600519"
        assert output_schema.error is None

    def test_realtime_quotes_schema(self):
        """测试实时行情Schema"""
        # 测试输入Schema
        input_data = {"code": "600519"}
        input_schema = RealTimeQuotesSchema.Input(**input_data)
        assert input_schema.code == "600519"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": {
                "price": 150.5,
                "change": 2.5,
                "change_percent": 1.69,
                "volume": 1000000
            },
            "error": None
        }
        output_schema = RealTimeQuotesSchema.Output(**output_data)
        assert output_schema.success is True
        assert output_schema.data["price"] == 150.5
        assert output_schema.error is None

    def test_technical_indicator_schema(self):
        """测试技术指标Schema"""
        # 测试输入Schema
        input_data = {
            "code": "600519",
            "indicator": "rsi",
            "lookback_days": 100
        }
        input_schema = TechnicalIndicatorSchema.Input(**input_data)
        assert input_schema.code == "600519"
        assert input_schema.indicator == "rsi"
        assert input_schema.lookback_days == 100

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": {
                "indicator": "rsi",
                "latest_value": 65.5,
                "values": [60.0, 62.5, 65.5],
                "description": "相对强弱指标"
            },
            "error": None
        }
        output_schema = TechnicalIndicatorSchema.Output(**output_data)
        assert output_schema.success is True
        assert output_schema.data["indicator"] == "rsi"
        assert output_schema.data["latest_value"] == 65.5
        assert output_schema.error is None

    def test_financial_data_schema(self):
        """测试财务数据Schema"""
        # 测试输入Schema
        input_data = {
            "code": "600519",
            "report_type": "balance_sheet"
        }
        input_schema = FinancialDataSchema.Input(**input_data)
        assert input_schema.code == "600519"
        assert input_schema.report_type == "balance_sheet"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": {
                "total_assets": 1000000000,
                "net_profit": 50000000,
                "_source": "akshare"
            },
            "error": None
        }
        output_schema = FinancialDataSchema.Output(**output_data)
        assert output_schema.success is True
        assert output_schema.data["total_assets"] == 1000000000
        assert output_schema.data["_source"] == "akshare"
        assert output_schema.error is None

    def test_news_data_schema(self):
        """测试新闻数据Schema"""
        # 测试输入Schema
        input_data = {
            "code": "600519",
            "lookback_days": 7,
            "limit": 100
        }
        input_schema = NewsDataSchema.Input(**input_data)
        assert input_schema.code == "600519"
        assert input_schema.lookback_days == 7
        assert input_schema.limit == 100

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {
                    "title": "测试新闻标题",
                    "content": "测试新闻内容",
                    "publish_time": "2025-10-10 10:00:00",
                    "source": "新浪财经",
                    "url": "http://example.com"
                }
            ],
            "error": None
        }
        output_schema = NewsDataSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["title"] == "测试新闻标题"
        assert output_schema.error is None

    def test_limit_up_stocks_schema(self):
        """测试涨停股Schema"""
        # 测试输入Schema (无参数)
        input_schema = LimitUpStocksSchema.Input()
        assert input_schema is not None

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {
                    "code": "600519",
                    "name": "贵州茅台",
                    "current_value": 1800.0,
                    "change_percent": 10.0
                }
            ],
            "error": None
        }
        output_schema = LimitUpStocksSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["code"] == "600519"
        assert output_schema.error is None

    def test_stock_comment_score_schema(self):
        """测试评分数据Schema"""
        # 测试输入Schema
        input_data = {"code": "600519"}
        input_schema = StockCommentScoreSchema.Input(**input_data)
        assert input_schema.code == "600519"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {"date": "2025-10-01", "score": 85},
                {"date": "2025-10-02", "score": 82}
            ],
            "stats": {
                "latest_score": 82,
                "average_score": 83.5,
                "score_trend": "stable"
            },
            "error": None
        }
        output_schema = StockCommentScoreSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 2
        assert output_schema.stats["latest_score"] == 82
        assert output_schema.error is None

    def test_stock_comment_focus_schema(self):
        """测试关注指数Schema"""
        # 测试输入Schema
        input_data = {"code": "600519"}
        input_schema = StockCommentFocusSchema.Input(**input_data)
        assert input_schema.code == "600519"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {"date": "2025-10-01", "focus_index": 75},
                {"date": "2025-10-02", "focus_index": 80}
            ],
            "stats": {
                "latest_focus": 80,
                "average_focus": 77.5,
                "focus_level": "high"
            },
            "error": None
        }
        output_schema = StockCommentFocusSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 2
        assert output_schema.stats["latest_focus"] == 80
        assert output_schema.error is None

    def test_stock_comment_desire_schema(self):
        """测试参与意愿Schema"""
        # 测试输入Schema
        input_data = {"code": "600519"}
        input_schema = StockCommentDesireSchema.Input(**input_data)
        assert input_schema.code == "600519"

        # 测试输出Schema
        output_data = {
            "success": True,
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
            },
            "error": None
        }
        output_schema = StockCommentDesireSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["daily_desire_change"] == 2.5
        assert output_schema.stats["desire_strength"] == "strong"
        assert output_schema.error is None

    def test_stock_comment_institution_schema(self):
        """测试机构参与度Schema"""
        # 测试输入Schema
        input_data = {"code": "600519"}
        input_schema = StockCommentInstitutionSchema.Input(**input_data)
        assert input_schema.code == "600519"

        # 测试输出Schema
        output_data = {
            "success": True,
            "data": [
                {"date": "2025-10-01", "institution_participation": 65},
                {"date": "2025-10-02", "institution_participation": 70}
            ],
            "stats": {
                "latest_institution_participation": 70,
                "average_institution_participation": 67.5
            },
            "error": None
        }
        output_schema = StockCommentInstitutionSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 2
        assert output_schema.stats["latest_institution_participation"] == 70
        assert output_schema.error is None

    def test_individual_fund_flow_schema(self):
        """测试个股资金流向Schema"""
        # 测试输入Schema (默认值)
        input_data = {"code": "600519"}
        input_schema = IndividualFundFlowSchema.Input(**input_data)
        assert input_schema.code == "600519"
        assert input_schema.market == "sh"  # 默认值

        # 测试输入Schema (指定market)
        input_data_with_market = {"code": "000001", "market": "sz"}
        input_schema2 = IndividualFundFlowSchema.Input(**input_data_with_market)
        assert input_schema2.code == "000001"
        assert input_schema2.market == "sz"

        # 测试输出Schema
        output_data = {
            "success": True,
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
            ],
            "error": None
        }
        output_schema = IndividualFundFlowSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["main_net_inflow"] == 150000000.0
        assert output_schema.data[0]["super_large_net_inflow"] == 80000000.0
        assert output_schema.error is None

    def test_concept_fund_flow_schema(self):
        """测试概念板块资金流向Schema"""
        # 测试输入Schema (默认值)
        input_schema = ConceptFundFlowSchema.Input()
        assert input_schema.symbol == "即时"  # 默认值
        assert input_schema.indicator == "即时"  # 默认值

        # 测试输入Schema (指定参数)
        input_data = {"symbol": "3日排行", "indicator": "3日排行"}
        input_schema2 = ConceptFundFlowSchema.Input(**input_data)
        assert input_schema2.symbol == "3日排行"
        assert input_schema2.indicator == "3日排行"

        # 测试输出Schema (即时数据)
        output_data = {
            "success": True,
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
            ],
            "error": None
        }
        output_schema = ConceptFundFlowSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["板块"] == "人工智能"
        assert output_schema.data[0]["净额"] == 150000000.0
        assert output_schema.error is None

    def test_industry_fund_flow_schema(self):
        """测试行业板块资金流向Schema"""
        # 测试输入Schema (默认值)
        input_schema = IndustryFundFlowSchema.Input()
        assert input_schema.symbol == "即时"
        assert input_schema.indicator == "即时"

        # 测试输入Schema (多日排行)
        input_data = {"symbol": "5日排行", "indicator": "5日排行"}
        input_schema2 = IndustryFundFlowSchema.Input(**input_data)
        assert input_schema2.symbol == "5日排行"
        assert input_schema2.indicator == "5日排行"

        # 测试输出Schema
        output_data = {
            "success": True,
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
            ],
            "error": None
        }
        output_schema = IndustryFundFlowSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["板块"] == "电子"
        assert output_schema.data[0]["净额"] == 200000000.0
        assert output_schema.error is None

    def test_big_deal_fund_flow_schema(self):
        """测试大单追踪Schema"""
        # 测试输入Schema (无参数)
        input_schema = BigDealFundFlowSchema.Input()
        assert input_schema is not None

        # 测试输出Schema
        output_data = {
            "success": True,
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
            ],
            "error": None
        }
        output_schema = BigDealFundFlowSchema.Output(**output_data)
        assert output_schema.success is True
        assert len(output_schema.data) == 1
        assert output_schema.data[0]["code"] == "600519"
        assert output_schema.data[0]["deal_type"] == "买盘"
        assert output_schema.data[0]["trade_amount"] == 9100000.0
        assert output_schema.error is None

    def test_schema_mapping_completeness(self):
        """测试Schema映射完整性"""
        # 验证所有工具都有对应的Schema
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

        for tool_name in expected_tools:
            assert tool_name in SCHEMA_MAPPING, f"工具 {tool_name} 缺少Schema定义"
            schema_class = SCHEMA_MAPPING[tool_name]
            assert schema_class is not None
        
        # 验证SCHEMA_MAPPING中的工具数量
        assert len(SCHEMA_MAPPING) == 14, f"预期14个工具，实际有{len(SCHEMA_MAPPING)}个"

    def test_get_tool_schema_function(self):
        """测试获取工具Schema函数"""
        # 测试存在的工具
        schema = get_tool_schema("get_stock_kline_data")
        assert schema is KLineDataSchema

        # 测试不存在的工具
        schema = get_tool_schema("nonexistent_tool")
        assert schema is None

    def test_get_all_tool_names_function(self):
        """测试获取所有工具名称函数"""
        tool_names = get_all_tool_names()
        assert isinstance(tool_names, list)
        assert len(tool_names) > 0
        assert "get_stock_kline_data" in tool_names

    def test_schema_validation_errors(self):
        """测试Schema验证错误"""
        # 测试无效的输入数据
        with pytest.raises(Exception):
            KLineDataSchema.Input(code="", lookback_days=0, period="invalid")

        # 测试超出范围的参数
        with pytest.raises(Exception):
            KLineDataSchema.Input(code="600519", lookback_days=2000, period="daily")

        # 测试缺少必需字段
        with pytest.raises(Exception):
            KLineDataSchema.Input()  # type: ignore  # 缺少code字段，故意触发错误


if __name__ == "__main__":
    pytest.main([__file__, "-v"])