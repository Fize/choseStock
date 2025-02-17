#!/usr/bin/env python3
"""
MCP服务器配置诊断脚本
用于检查环境配置是否正确
"""

import sys
import os
from pathlib import Path
import json


def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def check_python_version():
    """检查Python版本"""
    print_section("Python版本检查")
    version = sys.version_info
    print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本符合要求 (>= 3.8)")
        return True
    else:
        print("❌ Python版本过低，需要 >= 3.8")
        return False


def check_project_structure():
    """检查项目结构"""
    print_section("项目结构检查")
    
    # 获取当前脚本路径
    script_path = Path(__file__).resolve()
    print(f"脚本位置: {script_path}")
    
    # 推断项目根目录
    project_root = script_path.parent.parent.parent
    print(f"项目根目录: {project_root}")
    
    # 检查关键目录和文件
    checks = [
        ("dataflows_mcp/", "MCP服务目录"),
        ("dataflows_mcp/core/", "核心功能目录"),
        ("dataflows_mcp/tools/", "工具目录"),
        ("dataflows_mcp/server/", "服务器目录"),
        ("dataflows_mcp/scripts/run_mcp_server.py", "启动脚本"),
        ("pyproject.toml", "项目配置文件"),
    ]
    
    all_ok = True
    for path, desc in checks:
        full_path = project_root / path
        if full_path.exists():
            print(f"✅ {desc}: {path}")
        else:
            print(f"❌ {desc}不存在: {path}")
            all_ok = False
    
    return all_ok, project_root


def check_module_import(project_root):
    """检查模块导入"""
    print_section("模块导入检查")
    
    # 添加项目根目录到Python路径
    sys.path.insert(0, str(project_root))
    print(f"添加到Python路径: {project_root}")
    
    # 尝试导入关键模块
    modules = [
        ("dataflows_mcp", "MCP服务包"),
        ("dataflows_mcp.core", "核心功能模块"),
        ("dataflows_mcp.tools", "工具模块"),
        ("dataflows_mcp.server", "服务器模块"),
    ]
    
    all_ok = True
    for module_name, desc in modules:
        try:
            __import__(module_name)
            print(f"✅ {desc}: {module_name}")
        except ImportError as e:
            print(f"❌ {desc}导入失败: {module_name}")
            print(f"   错误: {str(e)}")
            all_ok = False
    
    return all_ok


def check_dependencies():
    """检查依赖包"""
    print_section("依赖包检查")
    
    dependencies = [
        ("mcp", "MCP协议库"),
        ("akshare", "AkShare数据源"),
        ("pandas", "数据处理库"),
        ("stockstats", "技术指标库"),
        ("pydantic", "数据验证库"),
    ]
    
    all_ok = True
    for package, desc in dependencies:
        try:
            __import__(package)
            print(f"✅ {desc}: {package}")
        except ImportError:
            print(f"❌ {desc}未安装: {package}")
            all_ok = False
    
    return all_ok


def generate_mcp_config(project_root):
    """生成MCP客户端配置"""
    print_section("MCP客户端配置")
    
    config = {
        "mcpServers": {
            "a-share-dataflows": {
                "command": "uv",
                "args": ["run", "python", "dataflows_mcp/scripts/run_mcp_server.py"],
                "cwd": str(project_root),
                "env": {}
            }
        }
    }
    
    print("推荐的配置（复制到MCP客户端配置文件）：")
    print("\n" + json.dumps(config, indent=2, ensure_ascii=False))
    
    print("\n配置文件位置：")
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("  Linux: ~/.config/Claude/claude_desktop_config.json")


def test_server_start(project_root):
    """测试服务器启动"""
    print_section("服务器启动测试")
    
    print("尝试导入服务器主函数...")
    try:
        sys.path.insert(0, str(project_root))
        from dataflows_mcp.server import main
        print("✅ 服务器模块导入成功")
        print("\n可以使用以下命令启动服务器：")
        print(f"  cd {project_root}")
        print("  uv run python dataflows_mcp/scripts/run_mcp_server.py")
        return True
    except Exception as e:
        print(f"❌ 服务器模块导入失败: {str(e)}")
        return False


def main():
    """主函数"""
    print("\n" + "🔍" * 30)
    print("  A股数据流MCP服务器配置诊断工具")
    print("🔍" * 30)
    
    results = []
    
    # 1. 检查Python版本
    results.append(("Python版本", check_python_version()))
    
    # 2. 检查项目结构
    structure_ok, project_root = check_project_structure()
    results.append(("项目结构", structure_ok))
    
    if not structure_ok:
        print("\n❌ 项目结构不完整，请确保在正确的目录运行此脚本")
        return
    
    # 3. 检查依赖包
    results.append(("依赖包", check_dependencies()))
    
    # 4. 检查模块导入
    results.append(("模块导入", check_module_import(project_root)))
    
    # 5. 测试服务器启动
    results.append(("服务器启动", test_server_start(project_root)))
    
    # 6. 生成配置
    generate_mcp_config(project_root)
    
    # 总结
    print_section("诊断总结")
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n🎉 所有检查通过！可以正常使用MCP服务器")
    else:
        print("\n⚠️  部分检查失败，请根据上述提示修复问题")
        print("\n常见问题解决方案：")
        print("1. 依赖包未安装: 运行 'uv sync' 安装依赖")
        print("2. 模块导入失败: 确保在项目根目录运行")
        print("3. 项目结构不完整: 检查是否完整克隆了项目")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
