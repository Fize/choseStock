"""
提供统一的A股数据获取接口，封装AkShare的复杂性
使用标准日志系统，符合MCP服务规范
"""

import akshare as ak
import pandas as pd
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
from .session_cache import session_cache
from .utils import format_stock_code, get_exchange_code, series_to_dict
from .logging import logger
from .exceptions import AkshareAPIError, DataFlowError

@dataclass
class AkshareClient:
    """AkShare数据客户端"""

    def get_limit_up_stocks(self) -> dict[str, Any]:
        """获取今日涨停股数据

        供用户根据股池确认第二天的操作
            
        Returns:
            包含涨停股数据的字典，格式: {'data': [...], 'error': None, 'issues': []}
        """
        try:
            df = ak.stock_zt_pool_em(date=datetime.now().strftime('%Y%m%d'))
            if df is None or df.empty:
                return {'data': [], 'error': None}

            limitup_stocks = []
            issuses = []
            for _, row in df.iterrows():
                try:
                    code = str(row.get('代码', '')).strip()
                    name = str(row.get('名称', '')).strip()
                    current_value = row.get('最新价', 0)
                    change_percent = row.get('涨跌幅', 0)
                    amount = row.get('成交额', 0)
                    circulating_market_value = row.get('流通市值', 0)
                    total_market_value = row.get('总市值', 0)
                    turnover_rate = row.get('换手率', 0)
                    funds_for_board_sealing = row.get('封板资金', 0)
                    first_limit_up_time = row.get('首次封板时间', None)
                    last_limit_up_time = row.get('最后封板时间', None)
                    break_times = row.get('炸板次数', None)
                    limit_up_statistics = row.get('涨停统计', None)
                    continuous_limit_up_count = row.get('连板数', None)
                    industry = row.get('所属行业', None)

                    limitup_stocks.append({
                        'code': code,
                        'name': name,
                        'current_value': current_value,
                        'change_percent': change_percent,
                        'amount': amount,
                        'circulating_market_value': circulating_market_value,
                        'total_market_value': total_market_value,
                        'turnover_rate': turnover_rate,
                        'funds_for_board_sealing': funds_for_board_sealing,
                        'first_limit_up_time': first_limit_up_time,
                        'last_limit_up_time': last_limit_up_time,
                        'break_times': break_times,
                        'limit_up_statistics': limit_up_statistics,
                        'continuous_limit_up_count': continuous_limit_up_count,
                        'industry': industry
                    })
                except Exception as e:
                    issuses.append(f"数据行处理异常: {e}")
                    continue

            return {'data': limitup_stocks, 'error': None, 'issues': issuses}
            
        except Exception as e:
            logger.error(f"获取涨停股数据失败: {str(e)}")
            raise AkshareAPIError(f"获取涨停股数据失败: {str(e)}", original_error=e)

    
    
    @session_cache()
    def get_stock_kline(
        self, 
        code: str, 
        lookback_days: int = 60,
        period: str = "daily"
    ) -> dict[str, Any]:
        """
        获取股票K线数据
        
        Args:
            code: 股票代码
            lookback_days: 回溯天数，默认60天
            period: 周期类型，默认daily
            
        Returns:
            K线数据字典
            
        """
        try:
            formatted_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {formatted_code} 最近{lookback_days}天K线数据")
            
            # 计算日期范围
            end_date = datetime.now()
            start_date = end_date - timedelta(days=lookback_days + 10)
            
            # 获取历史数据
            df = ak.stock_zh_a_hist(
                symbol=formatted_code,
                period=period,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust=""
            )
            
            if df.empty:
                logger.error(f"未找到股票{code}的K线数据")
                raise AkshareAPIError(f"未找到股票{code}的K线数据", code=code)
            
            # 只取最近的lookback_days条数据
            df = df.tail(lookback_days)
            
            # 转换为标准格式
            kline_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    kline_data.append({
                        'date': row['日期'].strftime('%Y-%m-%d') if pd.notna(row['日期']) else '',
                        'open': float(row['开盘']) if pd.notna(row['开盘']) else 0.0,
                        'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                        'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                        'close': float(row['收盘']) if pd.notna(row['收盘']) else 0.0,
                        'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                        'change': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0
                    })
                except (ValueError, TypeError) as e:
                    issues.append(f"K线数据转换异常: {str(e)}")
                    continue
            if issues:
                msg = '获取K线数据警告: '
                for k in issues:
                    msg += k + '\n'
                logger.warning(msg)
            if not kline_data:
                logger.error(f"股票{code}的K线数据转换失败")
                raise AkshareAPIError(f"股票{code}的K线数据转换失败", code=code)
            
            # 元数据
            meta = {
                'code': code,
                'period': period,
                'count': len(kline_data),
                'start_date': kline_data[0]['date'] if kline_data else '',
                'end_date': kline_data[-1]['date'] if kline_data else '',
            }

            logger.info(f"成功获取 {len(kline_data)} 条K线数据")
            return {'data': kline_data, 'meta': meta, 'error': None}
        except Exception as e:
            logger.error(f"获取K线数据失败: {str(e)}")
            raise AkshareAPIError(f"获取K线数据失败: {str(e)}", code=code, original_error=e)
    
    @session_cache()
    def get_stock_realtime_eastmoney(self, code: str) -> dict[str, Any]:
        """
        获取股票实时行情 - 东方财富数据源
        
        Args:
            code: 股票代码
            
        Returns:
            实时行情数据字典
        """
        try:
            logger.info(f"获取 {code} 实时行情 (东方财富)")
            clean_code = format_stock_code(code, target_format="plain")
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == clean_code]

            if stock_data.empty:
                error_msg = f'未找到股票{code}的实时数据(东方财富)'
                logger.error(error_msg)
                raise AkshareAPIError(error_msg, code=code)

            row = stock_data.iloc[0]
            realtime_data = {
                'code': code,
                'name': str(row['名称']) if pd.notna(row['名称']) else '',
                'price': float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                'change': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                'amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                'open': float(row['今开']) if pd.notna(row['今开']) else 0.0,
                'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                'pre_close': float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                'source': 'eastmoney',
            }
            logger.info(f"成功获取 {code} 实时行情 (东方财富): {realtime_data['price']}")
            return {'data': realtime_data, 'error': None}
            
        except AkshareAPIError:
            raise
        except Exception as e:
            error_msg = f"东方财富接口异常: {str(e)}"
            logger.error(error_msg)
            raise AkshareAPIError(error_msg, code=code, original_error=e)
    
    @session_cache()
    def get_stock_realtime_sina(self, code: str) -> dict[str, Any]:
        """
        获取股票实时行情 - 新浪数据源
        
        Args:
            code: 股票代码
            
        Returns:
            实时行情数据字典
        """
        try:
            logger.info(f"获取 {code} 实时行情 (新浪)")
            sina_code = format_stock_code(code, target_format="sina")
            df = ak.stock_zh_a_spot()
            stock_data = df[df['代码'] == sina_code]
            
            if stock_data.empty:
                error_msg = f'未找到股票{code}的实时数据(新浪)'
                logger.error(error_msg)
                raise AkshareAPIError(error_msg, code=code)
            
            row = stock_data.iloc[0]
            realtime_data = {
                'code': code,
                'name': str(row['名称']) if pd.notna(row['名称']) else '',
                'price': float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                'change': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                'amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                'open': float(row['今开']) if pd.notna(row['今开']) else 0.0,
                'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                'pre_close': float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                'source': 'sina',
            }
            logger.info(f"成功获取 {code} 实时行情 (新浪): {realtime_data['price']}")
            return {'data': realtime_data, 'error': None}
            
        except AkshareAPIError:
            raise
        except Exception as e:
            error_msg = f"新浪接口异常: {str(e)}"
            logger.error(error_msg)
            raise AkshareAPIError(error_msg, code=code, original_error=e)
    
    @session_cache()
    def get_stock_realtime_xueqiu(self, code: str) -> dict[str, Any]:
        """
        获取股票实时行情 - 雪球数据源
        
        注意：雪球接口可能需要配置 token，或受反爬虫限制。
        如果遇到错误，建议使用东方财富或新浪数据源。
        
        Args:
            code: 股票代码
            
        Returns:
            实时行情数据字典
        """
        try:
            logger.info(f"获取 {code} 实时行情 (雪球)")
            clean_code = format_stock_code(code, target_format="plain")
            exchange = get_exchange_code(clean_code)
            
            # 雪球接口需要格式: SH600519, SZ000001
            xueqiu_code = f"{exchange}{clean_code}"
            
            # 使用雪球接口
            # 注意：此接口可能需要 token 参数，详见 akshare 文档
            df = ak.stock_individual_spot_xq(symbol=xueqiu_code)
            
            if df.empty:
                error_msg = f'未找到股票{code}的实时数据(雪球)'
                logger.error(error_msg)
                raise AkshareAPIError(error_msg, code=code)
            
            row = df.iloc[0]
            realtime_data = {
                'code': code,
                'name': str(row['名称']) if pd.notna(row['名称']) else '',
                'price': float(row['最新价']) if pd.notna(row['最新价']) else 0.0,
                'change': float(row['涨跌额']) if pd.notna(row['涨跌额']) else 0.0,
                'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                'volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                'amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                'open': float(row['今开']) if pd.notna(row['今开']) else 0.0,
                'high': float(row['最高']) if pd.notna(row['最高']) else 0.0,
                'low': float(row['最低']) if pd.notna(row['最低']) else 0.0,
                'pre_close': float(row['昨收']) if pd.notna(row['昨收']) else 0.0,
                'source': 'xueqiu',
            }
            logger.info(f"成功获取 {code} 实时行情 (雪球): {realtime_data['price']}")
            return {'data': realtime_data, 'error': None}
            
        except AkshareAPIError:
            raise
        except Exception as e:
            error_msg = f"雪球接口异常: {str(e)}。提示: 雪球接口可能需要token或受反爬虫限制，建议使用东方财富或新浪数据源"
            logger.error(error_msg)
            raise AkshareAPIError(error_msg, code=code, original_error=e)


    @session_cache()
    def get_stock_financials(
        self, 
        code: str, 
        report_type: str = "balance_sheet",
    ) -> dict[str, Any]:
        """
        获取股票财务数据 - 多数据源回退机制
        
        Args:
            code: 股票代码
            report_type: 报表类型 balance_sheet/income/cashflow
            
        Returns:
            财务数据字典
        """
        clean_code = format_stock_code(code, target_format="plain")
        
        # 数据源优先级列表
        data_sources = [
            ("东方财富", self._get_financial_data_em),
            ("新浪", self._get_financial_data_sina),
            ("同花顺", self._get_financial_data_ths)
        ]
        
        financial_data = None
        used_source = None
        last_error = None
        
        # 尝试所有数据源
        for source_name, get_data_func in data_sources:
            try:
                logger.debug(f"尝试{source_name}数据源获取{code}的{report_type}数据")
                financial_data = get_data_func(clean_code, report_type)
                if financial_data is not None:
                    used_source = source_name
                    break
            except Exception as e:
                last_error = str(e)
                logger.error(f"{source_name}数据源失败: {last_error}")
                continue

        if financial_data is None:
            error_msg = f"所有数据源均无法获取{code}的{report_type}数据"
            if last_error:
                error_msg += f": {last_error}"
            logger.error(error_msg)
            raise AkshareAPIError(error_msg, code=code)
        
        # 清理和格式化数据
        formatted_data = {}
        for key, value in financial_data.items():
            if value is not None and pd.notna(value):
                formatted_data[str(key)] = value
        
        # 添加数据源信息
        formatted_data['_source'] = used_source

        logger.info(f"成功获取 {code} {report_type} 财务数据 ({used_source})")
        return {'data': formatted_data, 'error': None}
    
    def _get_financial_data_em(self, code: str, report_type: str) -> Optional[Dict]:
        """东方财富数据源"""
        try:
            if report_type == "balance_sheet":
                df = ak.stock_balance_sheet_by_report_em(symbol=code)
            elif report_type == "income":
                df = ak.stock_profit_sheet_by_report_em(symbol=code)
            elif report_type == "cashflow":
                df = ak.stock_cash_flow_sheet_by_report_em(symbol=code)
            else:
                return None
            
            if df is None or df.empty:
                return None
            
            # 获取最新一期数据（安全序列化）
            latest_data = series_to_dict(df.iloc[0])
            return latest_data
            
        except Exception as e:
            logger.error(f"东方财富数据源异常: {str(e)}")
            return None
    
    def _get_financial_data_sina(self, code: str, report_type: str) -> Optional[Dict]:
        """新浪数据源"""
        try:
            sina_code = format_stock_code(code, target_format="sina")
            
            symbol_map = {
                "balance_sheet": "资产负债表",
                "income": "利润表",
                "cashflow": "现金流量表"
            }
            symbol = symbol_map.get(report_type, "资产负债表")
            
            df = ak.stock_financial_report_sina(stock=sina_code, symbol=symbol)
            
            if df is None or df.empty:
                return None
            
            # 获取最新一期数据（安全序列化）
            latest_data = series_to_dict(df.iloc[0])
            return latest_data

        except Exception as e:
            logger.error(f"新浪数据源异常: {str(e)}")
            return None
    
    def _get_financial_data_ths(self, code: str, report_type: str) -> Optional[Dict]:
        """同花顺数据源"""
        try:
            ths_map = {
                "balance_sheet": "stock_financial_debt_ths",
                "income": "stock_financial_benefit_ths",
                "cashflow": "stock_financial_cash_ths"
            }
            
            func_name = ths_map.get(report_type, "stock_financial_debt_ths")
            func = getattr(ak, func_name)
            
            df = func(symbol=code, indicator="按报告期")
            
            if df is None or df.empty:
                return None
            
            # 获取最新一期数据（安全序列化）
            latest_data = series_to_dict(df.iloc[0])
            return latest_data
        except Exception as e:
            logger.error(f"同花顺数据源异常: {str(e)}")
            return None
    
    @session_cache()
    def get_stock_news(
        self, 
        code: str, 
        lookback_days: int = 7,
        limit: int = 100
    ) -> dict[str, Any]:
        """
        获取股票相关新闻, 新闻数据获取失败不影响整体流程，可以认为其没有新闻数据
        
        Args:
            code: 股票代码
            lookback_days: 回溯天数
            limit: 新闻数量限制
            
        Returns:
            新闻数据字典

        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 最近{lookback_days}天新闻")
            
            # 获取股票新闻数据
            df = ak.stock_news_em(symbol=clean_code)
            
            if df.empty:
                logger.info(f"未找到股票{code}的新闻数据, 返回空列表")
                return {'data': [], 'error': ''}
            
            # 限制新闻数量
            df = df.head(limit)
            
            # 转换为标准格式
            news_data = []
            issuses = []
            for _, row in df.iterrows():
                try:
                    news_data.append({
                        'title': str(row['新闻标题']) if pd.notna(row['新闻标题']) else '',
                        'content': str(row['新闻内容']) if pd.notna(row['新闻内容']) else '',
                        'publish_time': str(row['发布时间']) if pd.notna(row['发布时间']) else '',
                        'source': str(row.get('新闻来源', row.get('文章来源', ''))) if pd.notna(row.get('新闻来源', row.get('文章来源'))) else '',
                        'url': str(row['新闻链接']) if pd.notna(row['新闻链接']) else ''
                    })
                except Exception as e:
                    issuses.append(f'新闻数据转换异常: {str(e)}')
                    continue
            
            if not news_data:
                error_msg = f"股票{code}的新闻数据转换失败"
                logger.error(f"{error_msg}, 原始数据: {str(df)}")
                return {'data': [], 'error': error_msg}

            logger.info(f"成功获取 {len(news_data)} 条新闻")
            return {'data': news_data, 'error': None}
        except Exception as e:
            error_msg = f"获取新闻数据失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'error': error_msg}
    
    @session_cache()
    def get_stock_comment_score(self, code: str) -> dict[str, Any]:
        """
        获取千股千评-历史评分数据
        
        Args:
            code: 股票代码
            
        Returns:
            历史评分数据字典
        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 千股千评评分数据")
            
            # 获取历史评分数据
            df = ak.stock_comment_detail_zhpj_lspf_em(symbol=clean_code)
            
            if df.empty:
                logger.info(f"未找到股票{code}的评分数据")
                return {'data': [], 'stats': {}, 'error': ''}
            
            # 转换为标准格式
            score_data = []
            issuses = []
            for _, row in df.iterrows():
                try:
                    score_data.append({
                        'date': str(row['交易日']) if pd.notna(row['交易日']) else '',
                        'score': float(row['评分']) if pd.notna(row['评分']) else 0.0
                    })
                except Exception as e:
                    issuses.append(f'评分数据转换异常: {str(e)}')
                    continue
            
            if issuses:
                msg = '获取评分数据警告: '
                for k in issuses:
                    msg += k + '\n'
                logger.warning(msg)

            if not score_data:
                error_msg = f"股票{code}的评分数据转换失败"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}
            
            # 计算评分统计信息
            scores = [item['score'] for item in score_data]
            latest_score = score_data[-1]['score'] if score_data else 0.0
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # 计算趋势（最近5天）
            recent_scores = scores[-5:] if len(scores) >= 5 else scores
            score_trend = "上升" if recent_scores[-1] > recent_scores[0] else "下降"
            
            score_stats = {
                'latest_score': latest_score,
                'average_score': avg_score,
                'max_score': max_score,
                'min_score': min_score,
                'score_trend': score_trend,
                'data_points': len(score_data)
            }

            logger.info(f"成功获取 {len(score_data)} 条评分数据")
            return {
                'data': score_data,
                'stats': score_stats,
                'error': None
            }
        except Exception as e:
            error_msg = f"获取评分数据失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'stats': {}, 'error': error_msg}

    @session_cache()
    def get_stock_comment_focus(self, code: str) -> dict[str, Any]:
        """
        获取千股千评-用户关注指数
        
        Args:
            code: 股票代码
            
        Returns:
            用户关注指数数据字典
        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 千股千评关注指数")

            # 获取用户关注指数数据
            df = ak.stock_comment_detail_scrd_focus_em(symbol=clean_code)
            
            if df.empty:
                logger.info(f"未找到股票{code}的关注指数数据")
                return {'data': [], 'stats': {}, 'error': ''}
            # 转换为标准格式
            focus_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    focus_data.append({
                        'date': str(row['交易日']) if pd.notna(row['交易日']) else '',
                        'focus_index': float(row['用户关注指数']) if pd.notna(row['用户关注指数']) else 0.0
                    })
                except Exception as e:
                    issues.append(f'关注指数数据转换异常: {str(e)}')
                    continue
            
            if issues:
                msg = '获取关注指数数据警告: '
                for k in issues:
                    msg += k + '\n'
                logger.warning(msg)

            if not focus_data:
                error_msg = f"股票{code}的关注指数数据转换失败"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}
            
            # 计算关注指数统计信息
            focus_indices = [item['focus_index'] for item in focus_data]
            latest_focus = focus_data[-1]['focus_index'] if focus_data else 0.0
            avg_focus = sum(focus_indices) / len(focus_indices)
            max_focus = max(focus_indices)
            min_focus = min(focus_indices)
            
            # 计算关注热度等级
            focus_level = "高" if latest_focus > 85 else "中" if latest_focus > 70 else "低"
            
            # 计算趋势（最近5天）
            recent_focus = focus_indices[-5:] if len(focus_indices) >= 5 else focus_indices
            focus_trend = "上升" if recent_focus[-1] > recent_focus[0] else "下降"
            
            focus_stats = {
                'latest_focus': latest_focus,
                'average_focus': avg_focus,
                'max_focus': max_focus,
                'min_focus': min_focus,
                'focus_level': focus_level,
                'focus_trend': focus_trend,
                'data_points': len(focus_data)
            }

            logger.info(f"成功获取 {len(focus_data)} 条关注指数数据")
            return {
                'data': focus_data,
                'stats': focus_stats,
                'error': None
            }
        except Exception as e:
            error_msg = f"获取关注指数数据失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'stats': {}, 'error': error_msg}

    @session_cache()
    def get_stock_comment_desire_daily(self, code: str) -> dict[str, Any]:
        """
        获取千股千评-日度市场参与意愿
        
        Args:
            code: 股票代码
            
        Returns:
            日度市场参与意愿数据字典
        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 千股千评参与意愿")

            # 获取日度市场参与意愿数据
            df = ak.stock_comment_detail_scrd_desire_daily_em(symbol=clean_code)
            
            if df.empty:
                error_msg = f"未找到股票{code}的参与意愿数据"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}

            # 转换为标准格式
            desire_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    desire_data.append({
                        'date': str(row['交易日']) if pd.notna(row['交易日']) else '',
                        'daily_desire_change': float(row['当日意愿上升']) if pd.notna(row['当日意愿上升']) else 0.0,
                        'five_day_avg_change': float(row['5日平均参与意愿变化']) if pd.notna(row['5日平均参与意愿变化']) else 0.0
                    })
                except Exception as e:
                    issues.append(f"参与意愿数据转换异常: {e}")
                    continue

            if issues:
                msg = '获取参与意愿数据警告: '
                for k in issues:
                    msg += k + '\n'
                logger.warning(msg)
            
            if not desire_data:
                error_msg = f"股票{code}的参与意愿数据转换失败"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}
            
            # 计算参与意愿统计信息
            latest_desire = desire_data[-1]['daily_desire_change'] if desire_data else 0.0
            avg_desire = sum(item['daily_desire_change'] for item in desire_data) / len(desire_data)
            
            # 判断参与意愿强度
            desire_strength = "强" if latest_desire > 5 else "中" if latest_desire > 0 else "弱"
            
            desire_stats = {
                'latest_desire_change': latest_desire,
                'average_desire_change': avg_desire,
                'desire_strength': desire_strength,
                'data_points': len(desire_data)
            }

            logger.info(f"成功获取 {len(desire_data)} 条参与意愿数据")
            return {
                'data': desire_data,
                'stats': desire_stats,
                'error': None
            }
        except Exception as e:
            error_msg = f"获取参与意愿数据失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'stats': {}, 'error': error_msg}

    @session_cache()
    def get_stock_comment_institution(self, code: str) -> dict[str, Any]:
        """
        获取千股千评-机构参与度
        
        Args:
            code: 股票代码
            
        Returns:
            机构参与度数据字典
        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 千股千评机构参与度")

            # 获取机构参与度数据
            df = ak.stock_comment_detail_zlkp_jgcyd_em(symbol=clean_code)
            
            if df.empty:
                error_msg = f"未找到股票{code}的机构参与度数据"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}

            # 转换为标准格式
            institution_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    institution_data.append({
                        'date': str(row['交易日']) if pd.notna(row['交易日']) else '',
                        'institution_participation': float(row['机构参与度']) if pd.notna(row['机构参与度']) else 0.0
                    })
                except Exception as e:
                    issues.append(f"机构参与度数据转换异常: {e}")
                    continue
            if issues:
                msg = '获取机构参与度数据警告: '
                for k in issues:
                    msg += k + '\n'
                logger.warning(msg)

            if not institution_data:
                error_msg = f"股票{code}的机构参与度数据转换失败"
                logger.error(error_msg)
                return {'data': [], 'stats': {}, 'error': error_msg}
            
            # 计算机构参与度统计信息
            institution_indices = [item['institution_participation'] for item in institution_data]
            latest_institution = institution_data[-1]['institution_participation'] if institution_data else 0.0
            avg_institution = sum(institution_indices) / len(institution_indices)
            max_institution = max(institution_indices)
            min_institution = min(institution_indices)
            
            # 判断机构参与度等级
            institution_level = "高" if latest_institution > 30 else "中" if latest_institution > 20 else "低"
            
            # 计算趋势（最近5天）
            recent_institution = institution_indices[-5:] if len(institution_indices) >= 5 else institution_indices
            institution_trend = "上升" if recent_institution[-1] > recent_institution[0] else "下降"
            
            institution_stats = {
                'latest_institution_participation': latest_institution,
                'average_institution_participation': avg_institution,
                'max_institution_participation': max_institution,
                'min_institution_participation': min_institution,
                'institution_level': institution_level,
                'institution_trend': institution_trend,
                'data_points': len(institution_data)
            }
            
            logger.info(f"成功获取 {len(institution_data)} 条机构参与度数据")
            return {
                'data': institution_data,
                'stats': institution_stats,
                'error': None
            }
        except Exception as e:
            error_msg = f"获取机构参与度数据失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'stats': {}, 'error': error_msg}

    @session_cache()
    def get_individual_fund_flow(self, code: str, market: str = "sh") -> dict[str, Any]:
        """获取个股资金流向数据（东方财富）
        
        获取指定个股近100个交易日的资金流向数据
        
        Args:
            code: 股票代码
            market: 市场标识，可选值: sh(上海)、sz(深圳)、bj(北京)
            
        Returns:
            包含资金流数据的字典
        """
        try:
            clean_code = format_stock_code(code, target_format="plain")
            logger.info(f"获取 {clean_code} 个股资金流向数据，市场: {market}")
            
            # 调用AkShare接口获取个股资金流
            df = ak.stock_individual_fund_flow(stock=clean_code, market=market)
            
            if df.empty:
                error_msg = f"未找到股票{code}的资金流向数据"
                logger.error(error_msg)
                return {'data': [], 'error': error_msg}
            
            # 转换为标准格式
            fund_flow_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    fund_flow_data.append({
                        'date': str(row['日期']) if pd.notna(row['日期']) else '',
                        'close_price': float(row['收盘价']) if pd.notna(row['收盘价']) else 0.0,
                        'change_percent': float(row['涨跌幅']) if pd.notna(row['涨跌幅']) else 0.0,
                        'main_net_inflow': float(row['主力净流入-净额']) if pd.notna(row['主力净流入-净额']) else 0.0,
                        'main_net_inflow_rate': float(row['主力净流入-净占比']) if pd.notna(row['主力净流入-净占比']) else 0.0,
                        'super_large_net_inflow': float(row['超大单净流入-净额']) if pd.notna(row['超大单净流入-净额']) else 0.0,
                        'super_large_net_inflow_rate': float(row['超大单净流入-净占比']) if pd.notna(row['超大单净流入-净占比']) else 0.0,
                        'large_net_inflow': float(row['大单净流入-净额']) if pd.notna(row['大单净流入-净额']) else 0.0,
                        'large_net_inflow_rate': float(row['大单净流入-净占比']) if pd.notna(row['大单净流入-净占比']) else 0.0,
                        'medium_net_inflow': float(row['中单净流入-净额']) if pd.notna(row['中单净流入-净额']) else 0.0,
                        'medium_net_inflow_rate': float(row['中单净流入-净占比']) if pd.notna(row['中单净流入-净占比']) else 0.0,
                        'small_net_inflow': float(row['小单净流入-净额']) if pd.notna(row['小单净流入-净额']) else 0.0,
                        'small_net_inflow_rate': float(row['小单净流入-净占比']) if pd.notna(row['小单净流入-净占比']) else 0.0,
                    })
                except Exception as e:
                    issues.append(f"资金流数据转换异常: {e}")
                    continue
            
            if issues:
                logger.warning(f"获取资金流数据警告: {'; '.join(issues)}")
            
            logger.info(f"成功获取 {len(fund_flow_data)} 条资金流数据")
            return {'data': fund_flow_data, 'error': None}
            
        except Exception as e:
            error_msg = f"获取个股资金流向失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'error': error_msg}

    @session_cache()
    def get_concept_fund_flow(self, symbol: str = "即时", indicator: str = "即时") -> dict[str, Any]:
        """获取概念板块资金流向数据（同花顺）
        
        获取概念板块的资金流入流出数据
        
        Args:
            symbol: 时间周期，可选值: "即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
            indicator: 数据指标，与symbol保持一致
            
        Returns:
            包含概念资金流数据的字典
        """
        try:
            logger.info(f"获取概念资金流数据，周期: {symbol}")
            
            # 调用AkShare接口获取概念资金流
            df = ak.stock_fund_flow_concept(symbol=symbol)
            
            if df.empty:
                error_msg = f"未找到{symbol}的概念资金流数据"
                logger.error(error_msg)
                return {'data': [], 'error': error_msg}
            
            # 根据周期类型转换数据
            concept_flow_data = []
            issues = []
            
            if symbol == "即时":
                for _, row in df.iterrows():
                    try:
                        concept_flow_data.append({
                            'rank': int(row['序号']) if pd.notna(row['序号']) else 0,
                            'concept': str(row['行业']) if pd.notna(row['行业']) else '',
                            'concept_index': float(row['行业指数']) if pd.notna(row['行业指数']) else 0.0,
                            'change_percent': float(row['行业-涨跌幅']) if pd.notna(row['行业-涨跌幅']) else 0.0,
                            'inflow': float(row['流入资金']) if pd.notna(row['流入资金']) else 0.0,
                            'outflow': float(row['流出资金']) if pd.notna(row['流出资金']) else 0.0,
                            'net_amount': float(row['净额']) if pd.notna(row['净额']) else 0.0,
                            'company_count': float(row['公司家数']) if pd.notna(row['公司家数']) else 0,
                            'leading_stock': str(row['领涨股']) if pd.notna(row['领涨股']) else '',
                            'leading_stock_change': float(row['领涨股-涨跌幅']) if pd.notna(row['领涨股-涨跌幅']) else 0.0,
                            'current_price': float(row['当前价']) if pd.notna(row['当前价']) else 0.0,
                        })
                    except Exception as e:
                        issues.append(f"概念资金流数据转换异常: {e}")
                        continue
            else:
                # 多日排行数据格式
                for _, row in df.iterrows():
                    try:
                        concept_flow_data.append({
                            'rank': int(row['序号']) if pd.notna(row['序号']) else 0,
                            'concept': str(row['行业']) if pd.notna(row['行业']) else '',
                            'company_count': int(row['公司家数']) if pd.notna(row['公司家数']) else 0,
                            'concept_index': float(row['行业指数']) if pd.notna(row['行业指数']) else 0.0,
                            'period_change_percent': str(row['阶段涨跌幅']) if pd.notna(row['阶段涨跌幅']) else '0%',
                            'inflow': float(row['流入资金']) if pd.notna(row['流入资金']) else 0.0,
                            'outflow': float(row['流出资金']) if pd.notna(row['流出资金']) else 0.0,
                            'net_amount': float(row['净额']) if pd.notna(row['净额']) else 0.0,
                        })
                    except Exception as e:
                        issues.append(f"概念资金流数据转换异常: {e}")
                        continue
            
            if issues:
                logger.warning(f"获取概念资金流数据警告: {'; '.join(issues)}")
            
            logger.info(f"成功获取 {len(concept_flow_data)} 条概念资金流数据")
            return {'data': concept_flow_data, 'error': None}
            
        except Exception as e:
            error_msg = f"获取概念资金流向失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'error': error_msg}

    @session_cache()
    def get_industry_fund_flow(self, symbol: str = "即时", indicator: str = "即时") -> dict[str, Any]:
        """获取行业板块资金流向数据（同花顺）
        
        获取行业板块的资金流入流出数据
        
        Args:
            symbol: 时间周期，可选值: "即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
            indicator: 数据指标，与symbol保持一致
            
        Returns:
            包含行业资金流数据的字典
        """
        try:
            logger.info(f"获取行业资金流数据，周期: {symbol}")
            
            # 调用AkShare接口获取行业资金流
            df = ak.stock_fund_flow_industry(symbol=symbol)
            
            if df.empty:
                error_msg = f"未找到{symbol}的行业资金流数据"
                logger.error(error_msg)
                return {'data': [], 'error': error_msg}
            
            # 根据周期类型转换数据
            industry_flow_data = []
            issues = []
            
            if symbol == "即时":
                for _, row in df.iterrows():
                    try:
                        industry_flow_data.append({
                            'rank': int(row['序号']) if pd.notna(row['序号']) else 0,
                            'industry': str(row['行业']) if pd.notna(row['行业']) else '',
                            'industry_index': float(row['行业指数']) if pd.notna(row['行业指数']) else 0.0,
                            'change_percent': str(row['行业-涨跌幅']) if pd.notna(row['行业-涨跌幅']) else '0%',
                            'inflow': float(row['流入资金']) if pd.notna(row['流入资金']) else 0.0,
                            'outflow': float(row['流出资金']) if pd.notna(row['流出资金']) else 0.0,
                            'net_amount': float(row['净额']) if pd.notna(row['净额']) else 0.0,
                            'company_count': float(row['公司家数']) if pd.notna(row['公司家数']) else 0,
                            'leading_stock': str(row['领涨股']) if pd.notna(row['领涨股']) else '',
                            'leading_stock_change': str(row['领涨股-涨跌幅']) if pd.notna(row['领涨股-涨跌幅']) else '0%',
                            'current_price': float(row['当前价']) if pd.notna(row['当前价']) else 0.0,
                        })
                    except Exception as e:
                        issues.append(f"行业资金流数据转换异常: {e}")
                        continue
            else:
                # 多日排行数据格式
                for _, row in df.iterrows():
                    try:
                        industry_flow_data.append({
                            'rank': int(row['序号']) if pd.notna(row['序号']) else 0,
                            'industry': str(row['行业']) if pd.notna(row['行业']) else '',
                            'company_count': int(row['公司家数']) if pd.notna(row['公司家数']) else 0,
                            'industry_index': float(row['行业指数']) if pd.notna(row['行业指数']) else 0.0,
                            'period_change_percent': str(row['阶段涨跌幅']) if pd.notna(row['阶段涨跌幅']) else '0%',
                            'inflow': float(row['流入资金']) if pd.notna(row['流入资金']) else 0.0,
                            'outflow': float(row['流出资金']) if pd.notna(row['流出资金']) else 0.0,
                            'net_amount': float(row['净额']) if pd.notna(row['净额']) else 0.0,
                        })
                    except Exception as e:
                        issues.append(f"行业资金流数据转换异常: {e}")
                        continue
            
            if issues:
                logger.warning(f"获取行业资金流数据警告: {'; '.join(issues)}")
            
            logger.info(f"成功获取 {len(industry_flow_data)} 条行业资金流数据")
            return {'data': industry_flow_data, 'error': None}
            
        except Exception as e:
            error_msg = f"获取行业资金流向失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'error': error_msg}

    @session_cache()
    def get_big_deal_fund_flow(self) -> dict[str, Any]:
        """获取大单追踪数据（同花顺）
        
        获取当前时点的所有大单交易数据
        
        Returns:
            包含大单交易数据的字典
        """
        try:
            logger.info("获取大单追踪数据")
            
            # 调用AkShare接口获取大单追踪
            df = ak.stock_fund_flow_big_deal()
            
            if df.empty:
                error_msg = "未找到大单追踪数据"
                logger.error(error_msg)
                return {'data': [], 'error': error_msg}
            
            # 转换为标准格式
            big_deal_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    big_deal_data.append({
                        'trade_time': str(row['成交时间']) if pd.notna(row['成交时间']) else '',
                        'code': str(row['股票代码']) if pd.notna(row['股票代码']) else '',
                        'name': str(row['股票简称']) if pd.notna(row['股票简称']) else '',
                        'trade_price': float(row['成交价格']) if pd.notna(row['成交价格']) else 0.0,
                        'trade_volume': int(row['成交量']) if pd.notna(row['成交量']) else 0,
                        'trade_amount': float(row['成交额']) if pd.notna(row['成交额']) else 0.0,
                        'deal_type': str(row['大单性质']) if pd.notna(row['大单性质']) else '',
                        'change_percent': str(row['涨跌幅']) if pd.notna(row['涨跌幅']) else '',
                        'change_amount': str(row['涨跌额']) if pd.notna(row['涨跌额']) else '',
                    })
                except Exception as e:
                    issues.append(f"大单数据转换异常: {e}")
                    continue
            
            if issues:
                logger.warning(f"获取大单追踪数据警告: {'; '.join(issues)}")
            
            logger.info(f"成功获取 {len(big_deal_data)} 条大单追踪数据")
            return {'data': big_deal_data, 'error': None}
            
        except Exception as e:
            error_msg = f"获取大单追踪失败: {str(e)}"
            logger.error(error_msg)
            return {'data': [], 'error': error_msg}
    
    @session_cache()
    def get_stock_cyq(self, code: str, adjust: str = "") -> dict[str, Any]:
        """获取股票筹码分布数据（东方财富）
        
        获取近90个交易日的筹码分布数据，包括获利比例、平均成本、
        90%/70%成本区间和集中度等指标。
        
        Args:
            code: 股票代码（如"000001"）
            adjust: 复权类型，可选值："qfq"(前复权)、"hfq"(后复权)、""(不复权,默认)
            
        Returns:
            包含筹码分布数据的字典
            
        数据字段说明:
            - 日期: 交易日期
            - 获利比例: 当前价位下的获利比例
            - 平均成本: 平均持股成本
            - 90成本-低/高: 90%筹码的成本区间
            - 90集中度: 90%筹码的集中程度
            - 70成本-低/高: 70%筹码的成本区间  
            - 70集中度: 70%筹码的集中程度
        """
        try:
            # 格式化股票代码
            formatted_code = format_stock_code(code)
            logger.info(f"获取股票{formatted_code}的筹码分布数据（复权类型：{adjust or '不复权'}）")
            
            # 调用AkShare API获取筹码分布数据
            df = ak.stock_cyq_em(symbol=formatted_code, adjust=adjust)
            
            if df.empty:
                error_msg = f"股票{formatted_code}筹码分布数据为空"
                logger.error(error_msg)
                return {'data': [], 'error': error_msg}
            
            # 转换为标准格式
            cyq_data = []
            issues = []
            for _, row in df.iterrows():
                try:
                    cyq_data.append({
                        'date': str(row['日期']) if pd.notna(row['日期']) else '',
                        'profit_ratio': float(row['获利比例']) if pd.notna(row['获利比例']) else 0.0,
                        'average_cost': float(row['平均成本']) if pd.notna(row['平均成本']) else 0.0,
                        '90_cost_low': float(row['90成本-低']) if pd.notna(row['90成本-低']) else 0.0,
                        '90_cost_high': float(row['90成本-高']) if pd.notna(row['90成本-高']) else 0.0,
                        '90_concentration': float(row['90集中度']) if pd.notna(row['90集中度']) else 0.0,
                        '70_cost_low': float(row['70成本-低']) if pd.notna(row['70成本-低']) else 0.0,
                        '70_cost_high': float(row['70成本-高']) if pd.notna(row['70成本-高']) else 0.0,
                        '70_concentration': float(row['70集中度']) if pd.notna(row['70集中度']) else 0.0,
                    })
                except Exception as e:
                    issues.append(f"筹码分布数据转换异常: {e}")
                    continue
            
            if issues:
                logger.warning(f"获取筹码分布数据警告: {'; '.join(issues)}")
            
            logger.info(f"成功获取股票{formatted_code}的{len(cyq_data)}条筹码分布数据")
            return {'data': cyq_data, 'error': None}
            
        except Exception as e:
            error_msg = f"获取股票{code}筹码分布数据失败: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {'data': [], 'error': error_msg}

# 便捷函数接口 - 使用工厂模式
# 注意：这些函数现在通过工厂创建新实例，不再使用单例模式

def get_akshare_client_instance() -> "AkshareClient":
    """获取 AkshareClient 实例（使用工厂模式）。

    返回一个新的 AkshareClient 实例，使用工厂模式确保更好的并发安全性。

    Returns:
        AkshareClient: 客户端实例。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_akshare_client_instance
        >>> client = get_akshare_client_instance()
    """
    from .factories import get_factory
    return get_factory().create_akshare_client()

def get_limit_up_stocks() -> dict[str, Any]:
    """便捷：获取今日涨停股数据。

    返回值格式示例:
        {'data': [...], 'error': None, 'issues': []}

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_limit_up_stocks
        >>> res = get_limit_up_stocks()
        >>> print(len(res['data']))
    """
    return get_akshare_client_instance().get_limit_up_stocks()

def get_stock_kline(code: str, lookback_days: int = 60, period: str = "daily") -> dict[str, Any]:
    """便捷：获取指定股票的K线数据（封装缓存）。

    参数:
        code: 股票代码（支持 600519 / 600519.SH / 600519.SZ 等格式）
        lookback_days: 回溯天数，默认 60
        period: 周期，如 'daily'、'weekly' 等（参考 AkShare）

    返回:
        dict: 包含 'data'（列表）、'meta'（元数据）和 'error' 字段的字典。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_kline
        >>> res = get_stock_kline('600519', 30)
        >>> print(res['meta'])
    """
    return get_akshare_client_instance().get_stock_kline(code, lookback_days, period)

def get_stock_realtime_eastmoney(code: str) -> dict[str, Any]:
    """便捷：获取股票实时行情（东方财富数据源）。

    参数:
        code: 股票代码

    返回:
        dict: 包含 'data' 和 'error' 字段的字典，data 为实时行情字典。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_realtime_eastmoney
        >>> res = get_stock_realtime_eastmoney('600519')
        >>> print(res['data']['price'])
    """
    return get_akshare_client_instance().get_stock_realtime_eastmoney(code)

def get_stock_realtime_sina(code: str) -> dict[str, Any]:
    """便捷：获取股票实时行情（新浪数据源）。

    参数:
        code: 股票代码

    返回:
        dict: 包含 'data' 和 'error' 字段的字典，data 为实时行情字典。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_realtime_sina
        >>> res = get_stock_realtime_sina('600519')
        >>> print(res['data']['price'])
    """
    return get_akshare_client_instance().get_stock_realtime_sina(code)

def get_stock_realtime_xueqiu(code: str) -> dict[str, Any]:
    """便捷：获取股票实时行情（雪球数据源）。

    参数:
        code: 股票代码

    返回:
        dict: 包含 'data' 和 'error' 字段的字典，data 为实时行情字典。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_realtime_xueqiu
        >>> res = get_stock_realtime_xueqiu('600519')
        >>> print(res['data']['price'])
    """
    return get_akshare_client_instance().get_stock_realtime_xueqiu(code)


def get_stock_financials(code: str, report_type: str = "balance_sheet") -> dict[str, Any]:
    """便捷：获取股票财务报表数据，支持多数据源回退。

    参数:
        code: 股票代码
        report_type: 'balance_sheet' | 'income' | 'cashflow'

    返回:
        dict: 包含 'data' 和 'error' 字段的字典；data 为格式化后的财务数据，并包含 '_source' 字段标注来源。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_financials
        >>> res = get_stock_financials('600519', 'income')
        >>> print(res['data']['_source'])
    """
    return get_akshare_client_instance().get_stock_financials(code, report_type)

def get_stock_news(code: str, lookback_days: int = 7, limit: int = 100) -> dict[str, Any]:
    """便捷：获取指定股票最近若干天的新闻列表。

    参数:
        code: 股票代码
        lookback_days: 回溯天数（仅用于日志/提示），实际数据由 AkShare 接口返回
        limit: 最多返回的新闻条数

    返回:
        dict: 包含 'data'（新闻列表）和 'error' 字段的字典。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_news
        >>> res = get_stock_news('600519', 7, 10)
        >>> print(len(res['data']))
    """
    return get_akshare_client_instance().get_stock_news(code, lookback_days, limit)

def get_stock_comment_score(code: str) -> dict[str, Any]:
    """便捷：获取千股千评的历史评分数据。

    返回示例:
        {
            'data': [{'date': '2025-09-01', 'score': 4.5}, ...],
            'stats': {...},
            'error': None
        }

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_comment_score
        >>> res = get_stock_comment_score('600519')
    """
    return get_akshare_client_instance().get_stock_comment_score(code)

def get_stock_comment_focus(code: str) -> dict[str, Any]:
    """便捷：获取千股千评的用户关注指数时间序列及统计信息。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_comment_focus
        >>> res = get_stock_comment_focus('600519')
    """
    return get_akshare_client_instance().get_stock_comment_focus(code)

def get_stock_comment_desire_daily(code: str) -> dict[str, Any]:
    """便捷：获取千股千评的日度市场参与意愿数据。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_comment_desire_daily
        >>> res = get_stock_comment_desire_daily('600519')
    """
    return get_akshare_client_instance().get_stock_comment_desire_daily(code)

def get_stock_comment_institution(code: str) -> dict[str, Any]:
    """便捷:获取千股千评的机构参与度时间序列及统计信息。

    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_comment_institution
        >>> res = get_stock_comment_institution('600519')
    """
    return get_akshare_client_instance().get_stock_comment_institution(code)


def get_individual_fund_flow(code: str, market: str = "sh") -> dict[str, Any]:
    """便捷:获取个股资金流向数据（东方财富）。
    
    获取指定个股近100个交易日的资金流向数据,包含主力净流入、超大单净流入、
    大单净流入、中单净流入、小单净流入等数据。
    
    参数:
        code: 股票代码,如"600519"
        market: 市场标识,可选值:"sh"(上海)、"sz"(深圳)、"bj"(北京),默认"sh"
        
    返回:
        dict: 包含'data'(资金流数据列表)和'error'字段的字典
        
    示例:
        >>> from dataflows_mcp.core.akshare_client import get_individual_fund_flow
        >>> res = get_individual_fund_flow('600519', 'sh')
        >>> print(res['data'][0].keys())  # 查看包含的字段
    """
    return get_akshare_client_instance().get_individual_fund_flow(code, market)


def get_concept_fund_flow(symbol: str = "即时", indicator: str = "即时") -> dict[str, Any]:
    """便捷:获取概念板块资金流向数据（同花顺）。
    
    获取概念板块的资金流入流出数据,支持即时和多日排行。
    
    参数:
        symbol: 时间周期,可选值:"即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
        indicator: 数据指标,与symbol保持一致
        
    返回:
        dict: 包含'data'(概念资金流数据列表)和'error'字段的字典
        
    示例:
        >>> from dataflows_mcp.core.akshare_client import get_concept_fund_flow
        >>> res = get_concept_fund_flow("即时")
        >>> res = get_concept_fund_flow("3日排行", "3日排行")
    """
    return get_akshare_client_instance().get_concept_fund_flow(symbol, indicator)


def get_industry_fund_flow(symbol: str = "即时", indicator: str = "即时") -> dict[str, Any]:
    """便捷:获取行业板块资金流向数据（同花顺）。
    
    获取行业板块的资金流入流出数据,支持即时和多日排行。
    
    参数:
        symbol: 时间周期,可选值:"即时"、"3日排行"、"5日排行"、"10日排行"、"20日排行"
        indicator: 数据指标,与symbol保持一致
        
    返回:
        dict: 包含'data'(行业资金流数据列表)和'error'字段的字典
        
    示例:
        >>> from dataflows_mcp.core.akshare_client import get_industry_fund_flow
        >>> res = get_industry_fund_flow("即时")
        >>> res = get_industry_fund_flow("5日排行", "5日排行")
    """
    return get_akshare_client_instance().get_industry_fund_flow(symbol, indicator)


def get_big_deal_fund_flow() -> dict[str, Any]:
    """便捷:获取大单追踪数据（同花顺）。
    
    获取当前时点的所有大单交易数据,包含买盘大单和卖盘大单。
    
    返回:
        dict: 包含'data'(大单交易数据列表)和'error'字段的字典
        
    示例:
        >>> from dataflows_mcp.core.akshare_client import get_big_deal_fund_flow
        >>> res = get_big_deal_fund_flow()
        >>> print(len(res['data']))  # 查看大单数量
    """
    return get_akshare_client_instance().get_big_deal_fund_flow()


def get_stock_cyq(code: str, adjust: str = "") -> dict[str, Any]:
    """便捷:获取股票筹码分布数据（东方财富）。
    
    获取近90个交易日的筹码分布数据，包括获利比例、平均成本、
    90%/70%成本区间和集中度等指标。
    
    参数:
        code: 股票代码（如"000001"）
        adjust: 复权类型，可选值："qfq"(前复权)、"hfq"(后复权)、""(不复权,默认)
        
    返回:
        dict: 包含'data'(筹码分布数据列表)和'error'字段的字典
        
    示例:
        >>> from dataflows_mcp.core.akshare_client import get_stock_cyq
        >>> res = get_stock_cyq("000001")  # 获取不复权的筹码分布
        >>> res = get_stock_cyq("600519", "qfq")  # 获取前复权的筹码分布
        >>> print(res['data'][0])  # 查看最新一天的筹码分布
    """
    return get_akshare_client_instance().get_stock_cyq(code, adjust)