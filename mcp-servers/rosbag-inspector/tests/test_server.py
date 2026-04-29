#!/usr/bin/env python3
"""
rosbag-inspector MCP Server 测试
验证 inspect_rosbag 函数的错误处理和返回格式。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


class TestInspectRosbag:
    """inspect_rosbag 函数测试。"""

    def test_file_not_found(self):
        """无效路径返回 error status。"""
        from bag_inspector import inspect_rosbag
        result = inspect_rosbag('/nonexistent/path/bag.mcap')
        assert result['status'] == 'error'
        assert len(result['errors']) > 0
        assert result['data'] is None
        assert 'errors' in result
        assert 'status' in result
        assert 'data' in result

    def test_unsupported_format(self, tmp_path):
        """不支持的格式返回 error。"""
        from bag_inspector import inspect_rosbag
        fake = tmp_path / 'fake.txt'
        fake.write_text('not a rosbag')
        result = inspect_rosbag(str(fake))
        assert result['status'] == 'error'
        assert '不支持的格式' in result['errors'][0]
        assert result['data'] is None

    def test_return_structure(self):
        """返回 dict 包含 status/data/errors 三字段。"""
        from bag_inspector import inspect_rosbag
        result = inspect_rosbag('/nonexistent.mcap')
        assert isinstance(result, dict)
        assert 'status' in result
        assert 'data' in result
        assert 'errors' in result
        assert isinstance(result['errors'], list)

    def test_rosbags_library_available(self):
        """验证 rosbags 库可用。"""
        try:
            from rosbags.rosbag2 import Reader
            HAS_ROSBAGS = True
        except ImportError:
            HAS_ROSBAGS = False
        assert HAS_ROSBAGS, 'rosbags 库未安装，测试无法执行'

    def test_mcp_library_available(self):
        """验证 mcp 库可用。"""
        try:
            from mcp.server import Server
            HAS_MCP = True
        except ImportError:
            HAS_MCP = False
        assert HAS_MCP, 'mcp 库未安装，测试无法执行'
