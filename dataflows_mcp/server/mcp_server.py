"""
MCP服务器实现
提供符合MCP协议的A股数据服务
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from dataflows_mcp.tools.mcp_tools import get_mcp_tools
from dataflows_mcp.tools.schemas import get_all_tool_names, SCHEMA_MAPPING
from dataflows_mcp.core.logging import logger
from dataflows_mcp.core.exceptions import DataFlowError



class AShareMCPServer:
    """A股数据MCP服务器"""

    def __init__(self):
        """初始化MCP服务器"""
        self.server = Server("a-share-dataflows")
        self.mcp_tools = get_mcp_tools()
        self._setup_handlers()
        logger.info("A股数据MCP服务器已初始化")

    def _setup_handlers(self):
        """设置MCP协议处理器"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """
            列出所有可用的工具
            
            Returns:
                工具列表
            """
            logger.info("收到list_tools请求")
            
            tools = [
                Tool(
                    name="get_stock_kline_data",
                    description="获取股票K线数据（OHLCV），支持日线、周线、月线等多种周期",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码，支持格式：600519、600519.SH、000001.SZ等"
                            },
                            "lookback_days": {
                                "type": "integer",
                                "description": "回溯天数，范围1-1000天",
                                "default": 60,
                                "minimum": 1,
                                "maximum": 1000
                            },
                            "period": {
                                "type": "string",
                                "description": "周期类型：daily(日线)、weekly(周线)、monthly(月线)",
                                "enum": ["daily", "weekly", "monthly"],
                                "default": "daily"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_realtime_eastmoney_data",
                    description="获取股票实时行情数据（东方财富数据源），包含最新价格、涨跌幅、成交量等信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_realtime_sina_data",
                    description="获取股票实时行情数据（新浪数据源），包含最新价格、涨跌幅、成交量等信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_realtime_xueqiu_data",
                    description="获取股票实时行情数据（雪球数据源），包含最新价格、涨跌幅、成交量等信息",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_technical_indicator_data",
                    description="计算股票技术指标，支持RSI、MACD、BOLL、均线等多种指标",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            },
                            "indicator": {
                                "type": "string",
                                "description": "技术指标名称，如rsi、macd、boll、close_20_sma等"
                            },
                            "lookback_days": {
                                "type": "integer",
                                "description": "回溯天数，范围1-1000天",
                                "default": 100,
                                "minimum": 1,
                                "maximum": 1000
                            }
                        },
                        "required": ["code", "indicator"]
                    }
                ),
                Tool(
                    name="get_stock_financial_data",
                    description="获取股票财务数据，包含资产负债表、利润表、现金流量表",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            },
                            "report_type": {
                                "type": "string",
                                "description": "报表类型：balance_sheet(资产负债表)、income(利润表)、cashflow(现金流量表)",
                                "enum": ["balance_sheet", "income", "cashflow"],
                                "default": "balance_sheet"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_news_data",
                    description="获取股票相关新闻数据",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            },
                            "lookback_days": {
                                "type": "integer",
                                "description": "回溯天数，范围1-30天",
                                "default": 7,
                                "minimum": 1,
                                "maximum": 30
                            },
                            "limit": {
                                "type": "integer",
                                "description": "新闻数量限制，范围1-500条",
                                "default": 100,
                                "minimum": 1,
                                "maximum": 500
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_limit_up_stocks_data",
                    description="获取今日涨停股票列表",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_stock_comment_score_data",
                    description="获取千股千评评分数据，包含综合评分和历史趋势",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_comment_focus_data",
                    description="获取用户关注指数数据，反映市场关注度",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_comment_desire_data",
                    description="获取市场参与意愿数据，反映投资者参与热情",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_stock_comment_institution_data",
                    description="获取机构参与度数据，反映机构投资者关注程度",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_individual_fund_flow_data",
                    description="获取个股资金流向数据（东方财富），包含主力净流入、超大单、大单、中单、小单等资金流向",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码，如600519"
                            },
                            "market": {
                                "type": "string",
                                "description": "市场标识，可选值: sh(上海)、sz(深圳)、bj(北京)，默认sh",
                                "enum": ["sh", "sz", "bj"],
                                "default": "sh"
                            }
                        },
                        "required": ["code"]
                    }
                ),
                Tool(
                    name="get_concept_fund_flow_data",
                    description="获取概念板块资金流向数据（同花顺），包含概念板块的资金流入流出情况",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行",
                                "enum": ["即时", "3日排行", "5日排行", "10日排行", "20日排行"],
                                "default": "即时"
                            },
                            "indicator": {
                                "type": "string",
                                "description": "数据指标，与symbol保持一致",
                                "enum": ["即时", "3日排行", "5日排行", "10日排行", "20日排行"],
                                "default": "即时"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_industry_fund_flow_data",
                    description="获取行业板块资金流向数据（同花顺），包含行业板块的资金流入流出情况",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "symbol": {
                                "type": "string",
                                "description": "时间周期，可选值: 即时、3日排行、5日排行、10日排行、20日排行",
                                "enum": ["即时", "3日排行", "5日排行", "10日排行", "20日排行"],
                                "default": "即时"
                            },
                            "indicator": {
                                "type": "string",
                                "description": "数据指标，与symbol保持一致",
                                "enum": ["即时", "3日排行", "5日排行", "10日排行", "20日排行"],
                                "default": "即时"
                            }
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_big_deal_fund_flow_data",
                    description="获取大单追踪数据（同花顺），包含当前时点的所有大单交易数据",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_stock_cyq_data",
                    description="获取股票筹码分布数据（东方财富），包含近90个交易日的获利比例、平均成本、成本区间和集中度等筹码分析数据",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "股票代码"
                            },
                            "adjust": {
                                "type": "string",
                                "description": "复权类型：\"\"(不复权)、\"qfq\"(前复权)、\"hfq\"(后复权)",
                                "default": "",
                                "enum": ["", "qfq", "hfq"]
                            }
                        },
                        "required": ["code"]
                    }
                )
            ]
            
            logger.info(f"返回{len(tools)}个可用工具")
            return tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """
            调用指定的工具
            
            Args:
                name: 工具名称
                arguments: 工具参数
                
            Returns:
                工具执行结果
            """
            logger.info(f"收到call_tool请求: {name}, 参数: {arguments}")
            
            try:
                # 验证工具是否存在
                if name not in get_all_tool_names():
                    error_msg = f"未知的工具: {name}"
                    logger.error(error_msg)
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": error_msg
                        }, ensure_ascii=False, indent=2)
                    )]
                
                # 获取工具方法
                tool_method = getattr(self.mcp_tools, name, None)
                if tool_method is None:
                    error_msg = f"工具方法未实现: {name}"
                    logger.error(error_msg)
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": error_msg
                        }, ensure_ascii=False, indent=2)
                    )]
                
                # 调用工具方法
                result = await tool_method(**arguments)
                
                # 格式化返回结果
                logger.info(f"工具{name}执行完成，成功: {result.get('success', False)}")
                return [TextContent(
                    type="text",
                    text=json.dumps(result, ensure_ascii=False, indent=2)
                )]
                
            except TypeError as e:
                error_msg = f"参数错误: {str(e)}"
                logger.error(f"工具{name}调用失败: {error_msg}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": error_msg
                    }, ensure_ascii=False, indent=2)
                )]
            except Exception as e:
                error_msg = f"工具执行异常: {str(e)}"
                logger.error(f"工具{name}执行异常: {error_msg}")
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": error_msg
                    }, ensure_ascii=False, indent=2)
                )]

    async def run(self):
        """运行MCP服务器"""
        logger.info("启动A股数据MCP服务器...")
        async with stdio_server() as (read_stream, write_stream):
            logger.info("MCP服务器已启动，等待客户端连接...")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


def main():
    """主函数 - MCP服务器入口点"""
    async def run_server():
        """异步运行服务器"""
        try:
            server = AShareMCPServer()
            await server.run()
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        except Exception as e:
            logger.error(f"服务器运行异常: {str(e)}")
            sys.exit(1)
    
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
