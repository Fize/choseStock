"""
集成测试 - 心跳端点

验证心跳端点在实际运行环境中的功能，包括：
- 端点可访问性（SSE和Streamable HTTP模式）
- 响应时间性能（<100ms目标）
- 连续请求稳定性
- HTTP响应头正确性

这些测试需要启动实际的MCP服务器实例。
"""

import asyncio
import time
from typing import Any, Dict

import pytest
import httpx


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["sse", "streamable-http"])
async def test_heartbeat_endpoint_accessible(
    mcp_server_url: str,
    transport: str,
    heartbeat_response_from_server: Dict[str, Any]
):
    """
    测试：心跳端点在SSE和Streamable HTTP模式下可访问
    
    参数化测试，验证两种HTTP传输模式都支持心跳端点。
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{mcp_server_url}/")
        
        # 验证HTTP状态码
        assert response.status_code == 200, (
            f"心跳端点返回非200状态码: {response.status_code}"
        )
        
        # 验证Content-Type
        assert response.headers.get("content-type") == "application/json", (
            f"Content-Type错误: {response.headers.get('content-type')}"
        )
        
        # 验证响应可解析为JSON
        data = response.json()
        assert isinstance(data, dict), "响应不是有效的JSON对象"
        
        # 验证transport字段匹配当前模式
        assert data["transport"] == transport, (
            f"transport字段不匹配。期望: {transport}, 实际: {data['transport']}"
        )


@pytest.mark.asyncio
async def test_heartbeat_response_time(mcp_server_url: str):
    """
    测试：心跳端点响应时间 < 100ms
    
    测试10次请求的平均响应时间和p95响应时间。
    """
    response_times = []
    
    async with httpx.AsyncClient() as client:
        for _ in range(10):
            start_time = time.perf_counter()
            
            response = await client.get(f"{mcp_server_url}/")
            
            end_time = time.perf_counter()
            elapsed_ms = (end_time - start_time) * 1000
            
            assert response.status_code == 200, "请求失败"
            response_times.append(elapsed_ms)
    
    # 计算统计数据
    avg_time = sum(response_times) / len(response_times)
    sorted_times = sorted(response_times)
    p95_index = int(len(sorted_times) * 0.95)
    p95_time = sorted_times[p95_index]
    
    # 断言性能目标
    assert p95_time < 100, (
        f"p95响应时间超过100ms: {p95_time:.2f}ms\n"
        f"平均响应时间: {avg_time:.2f}ms\n"
        f"所有响应时间: {[f'{t:.2f}ms' for t in response_times]}"
    )


@pytest.mark.asyncio
async def test_heartbeat_consecutive_requests(mcp_server_url: str):
    """
    测试：连续10次请求都成功返回200
    
    验证端点的稳定性和无状态设计。
    """
    async with httpx.AsyncClient() as client:
        for i in range(10):
            response = await client.get(f"{mcp_server_url}/")
            
            assert response.status_code == 200, (
                f"第{i+1}次请求失败: 状态码 {response.status_code}"
            )
            
            data = response.json()
            assert data["status"] == "healthy", (
                f"第{i+1}次请求返回非健康状态: {data['status']}"
            )


@pytest.mark.asyncio
async def test_heartbeat_cache_control_header(mcp_server_url: str):
    """
    测试：响应包含正确的Cache-Control头
    
    验证响应禁用缓存，确保实时性。
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{mcp_server_url}/")
        
        cache_control = response.headers.get("cache-control")
        
        assert cache_control is not None, "缺少Cache-Control头"
        assert "no-cache" in cache_control.lower(), (
            f"Cache-Control未包含no-cache: {cache_control}"
        )
        assert "no-store" in cache_control.lower(), (
            f"Cache-Control未包含no-store: {cache_control}"
        )


@pytest.mark.asyncio
async def test_heartbeat_contract_integration(
    mcp_server_url: str,
    heartbeat_response_from_server: Dict[str, Any]
):
    """
    测试：集成契约测试
    
    从实际服务器获取响应，然后运行所有契约测试。
    这确保契约测试的断言与实际响应一致。
    """
    from dataflows_mcp.tests.contract.test_heartbeat_contract import TestHeartbeatContract
    
    # 创建契约测试实例
    contract_test = TestHeartbeatContract()
    
    # 运行所有契约测试
    contract_test.test_response_has_required_fields(heartbeat_response_from_server)
    contract_test.test_status_field_valid_enum(heartbeat_response_from_server)
    contract_test.test_status_field_type(heartbeat_response_from_server)
    contract_test.test_timestamp_field_type(heartbeat_response_from_server)
    contract_test.test_timestamp_field_iso8601_format(heartbeat_response_from_server)
    contract_test.test_transport_field_type(heartbeat_response_from_server)
    contract_test.test_transport_field_valid_enum(heartbeat_response_from_server)
    contract_test.test_server_field_type(heartbeat_response_from_server)
    contract_test.test_server_field_value(heartbeat_response_from_server)
    contract_test.test_version_field_type(heartbeat_response_from_server)
    contract_test.test_version_field_semantic_format(heartbeat_response_from_server)
    contract_test.test_no_extra_fields(heartbeat_response_from_server)
    contract_test.test_response_is_dict(heartbeat_response_from_server)


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mcp_server_url(request) -> str:
    """
    Fixture: MCP服务器URL
    
    可以通过pytest命令行参数覆盖：
        pytest --mcp-url=http://localhost:8000
    """
    return request.config.getoption("--mcp-url", default="http://localhost:8000")


@pytest.fixture
async def heartbeat_response_from_server(mcp_server_url: str) -> Dict[str, Any]:
    """
    Fixture: 从实际服务器获取心跳响应
    
    这个fixture用于集成契约测试，确保契约测试使用实际响应数据。
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{mcp_server_url}/")
        assert response.status_code == 200, "无法获取心跳响应"
        return response.json()

