#!/usr/bin/env python3
"""
rosbag-inspector MCP Server（stdio 模式）
提供 inspect_rosbag tool，读取 .mcap / .db3 / .bag 文件元数据。
"""

import json
import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool

from bag_inspector import inspect_rosbag


def create_server() -> Server:
    """创建 MCP Server 实例。"""
    app = Server('rosbag-inspector')

    @app.list_tools()
    def list_tools():
        return [
            Tool(
                name='inspect_rosbag',
                description='读取 rosbag 文件（.mcap/.db3/.bag）的元数据：topic 列表、消息数量、总时长、帧率统计',
                inputSchema={
                    'type': 'object',
                    'properties': {
                        'bag_path': {
                            'type': 'string',
                            'description': 'rosbag 文件路径（支持 .mcap / .db3 / .bag）',
                        },
                    },
                    'required': ['bag_path'],
                },
            )
        ]

    @app.call_tool()
    def call_tool(name: str, arguments: Any):
        if name == 'inspect_rosbag':
            bag_path = arguments.get('bag_path')
            if not bag_path:
                return json.dumps({
                    'status': 'error',
                    'data': None,
                    'errors': ['bag_path 参数必填'],
                })
            result = inspect_rosbag(bag_path)
            return json.dumps(result, ensure_ascii=False)
        return json.dumps({
            'status': 'error',
            'data': None,
            'errors': [f'未知 tool：{name}'],
        })

    return app


async def run():
    """stdio 模式运行入口。"""
    app = create_server()
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run())


if __name__ == '__main__':
    main()
