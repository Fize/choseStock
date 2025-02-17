# A股数据流 MCP 服务

这是一个符合 Model Context Protocol (MCP) 标准的 A股市场数据服务模块。

## 快速开始

```bash
# 启动 MCP 服务器
uv run a-share-mcp

# 或使用 Python 模块
uv run python -m dataflows_mcp.server.mcp_server
```

## 模块结构

- `core/` - 核心功能（数据获取、技术分析、缓存等）
- `tools/` - MCP 工具实现
- `server/` - MCP 服务器
- `tests/` - 测试套件
- `scripts/` - 实用脚本

## 开发

```bash
# 运行测试
uv run pytest

# 诊断工具
uv run python scripts/diagnose.py
```

## 文档

完整文档请查看项目根目录的 [README.md](../README.md)
