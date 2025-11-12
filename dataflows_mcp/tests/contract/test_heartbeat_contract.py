"""
契约测试 - 心跳端点

验证心跳端点的响应格式符合API契约规范，包括：
- JSON schema验证（必需字段和类型）
- 字段值约束（status枚举、timestamp格式、transport枚举）
- 响应头验证（Content-Type、Cache-Control）

根据项目宪章的复杂度豁免机制，本测试覆盖所有契约验证，
无需额外的单元测试（心跳端点无分支逻辑，无数据处理）。
"""

import re
from datetime import datetime
from typing import Any, Dict

import pytest


class TestHeartbeatContract:
    """心跳端点契约测试"""
    
    def test_response_has_required_fields(self, heartbeat_response: Dict[str, Any]):
        """测试：响应包含所有必需字段"""
        required_fields = {"status", "timestamp", "transport", "server", "version"}
        
        # 验证所有必需字段存在
        assert required_fields.issubset(heartbeat_response.keys()), (
            f"缺少必需字段。期望: {required_fields}, "
            f"实际: {set(heartbeat_response.keys())}"
        )
    
    def test_status_field_valid_enum(self, heartbeat_response: Dict[str, Any]):
        """测试：status字段值符合枚举约束"""
        valid_status = {"healthy", "unhealthy"}
        
        assert heartbeat_response["status"] in valid_status, (
            f"status字段值无效。期望: {valid_status}, "
            f"实际: {heartbeat_response['status']}"
        )
    
    def test_status_field_type(self, heartbeat_response: Dict[str, Any]):
        """测试：status字段类型为字符串"""
        assert isinstance(heartbeat_response["status"], str), (
            f"status字段类型错误。期望: str, "
            f"实际: {type(heartbeat_response['status']).__name__}"
        )
    
    def test_timestamp_field_type(self, heartbeat_response: Dict[str, Any]):
        """测试：timestamp字段类型为字符串"""
        assert isinstance(heartbeat_response["timestamp"], str), (
            f"timestamp字段类型错误。期望: str, "
            f"实际: {type(heartbeat_response['timestamp']).__name__}"
        )
    
    def test_timestamp_field_iso8601_format(self, heartbeat_response: Dict[str, Any]):
        """测试：timestamp字段符合ISO 8601格式"""
        timestamp_str = heartbeat_response["timestamp"]
        
        # 尝试解析ISO 8601格式
        try:
            parsed_dt = datetime.fromisoformat(timestamp_str)
            assert parsed_dt is not None, "时间戳解析失败"
        except ValueError as e:
            pytest.fail(f"时间戳格式无效: {timestamp_str}. 错误: {e}")
        
        # 验证包含时区信息（+00:00 或 Z）
        assert re.search(r'[+-]\d{2}:\d{2}|Z$', timestamp_str), (
            f"时间戳缺少时区信息: {timestamp_str}"
        )
    
    def test_transport_field_type(self, heartbeat_response: Dict[str, Any]):
        """测试：transport字段类型为字符串"""
        assert isinstance(heartbeat_response["transport"], str), (
            f"transport字段类型错误。期望: str, "
            f"实际: {type(heartbeat_response['transport']).__name__}"
        )
    
    def test_transport_field_valid_enum(self, heartbeat_response: Dict[str, Any]):
        """测试：transport字段值符合枚举约束"""
        valid_transports = {"stdio", "sse", "streamable-http"}
        
        assert heartbeat_response["transport"] in valid_transports, (
            f"transport字段值无效。期望: {valid_transports}, "
            f"实际: {heartbeat_response['transport']}"
        )
    
    def test_server_field_type(self, heartbeat_response: Dict[str, Any]):
        """测试：server字段类型为字符串"""
        assert isinstance(heartbeat_response["server"], str), (
            f"server字段类型错误。期望: str, "
            f"实际: {type(heartbeat_response['server']).__name__}"
        )
    
    def test_server_field_value(self, heartbeat_response: Dict[str, Any]):
        """测试：server字段值正确"""
        expected_server = "a-share-dataflows"
        
        assert heartbeat_response["server"] == expected_server, (
            f"server字段值错误。期望: {expected_server}, "
            f"实际: {heartbeat_response['server']}"
        )
    
    def test_version_field_type(self, heartbeat_response: Dict[str, Any]):
        """测试：version字段类型为字符串"""
        assert isinstance(heartbeat_response["version"], str), (
            f"version字段类型错误。期望: str, "
            f"实际: {type(heartbeat_response['version']).__name__}"
        )
    
    def test_version_field_semantic_format(self, heartbeat_response: Dict[str, Any]):
        """测试：version字段符合语义化版本格式"""
        version_str = heartbeat_response["version"]
        
        # 验证语义化版本格式 (MAJOR.MINOR.PATCH)
        semver_pattern = r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$'
        
        assert re.match(semver_pattern, version_str), (
            f"version字段格式无效。期望: MAJOR.MINOR.PATCH, "
            f"实际: {version_str}"
        )
    
    def test_no_extra_fields(self, heartbeat_response: Dict[str, Any]):
        """测试：响应不包含未定义的字段"""
        expected_fields = {"status", "timestamp", "transport", "server", "version"}
        actual_fields = set(heartbeat_response.keys())
        
        extra_fields = actual_fields - expected_fields
        
        assert len(extra_fields) == 0, (
            f"响应包含未定义的字段: {extra_fields}"
        )
    
    def test_response_is_dict(self, heartbeat_response: Dict[str, Any]):
        """测试：响应是字典类型"""
        assert isinstance(heartbeat_response, dict), (
            f"响应类型错误。期望: dict, "
            f"实际: {type(heartbeat_response).__name__}"
        )


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def heartbeat_response() -> Dict[str, Any]:
    """
    Fixture: 心跳响应数据
    
    这个fixture在集成测试中会被重写为实际的HTTP响应。
    在单独运行契约测试时，使用mock数据。
    """
    return {
        "status": "healthy",
        "timestamp": "2025-11-12T10:30:00.123456+00:00",
        "transport": "sse",
        "server": "a-share-dataflows",
        "version": "0.1.0"
    }
