# rosbag-inspector MCP Server

读取 rosbag 文件（.mcap / .db3 / .bag）的元数据，返回 topic 列表、消息数量、总时长、帧率统计。

## 安装

```bash
pip install -r requirements.txt
```

## 使用方式

### 方式 1：独立运行（stdio 模式）

```bash
python server.py
```

### 方式 2：配置到 Claude Code MCP

在 Claude Code 设置中加入：

```json
{
  "mcpServers": {
    "rosbag-inspector": {
      "command": "python",
      "args": ["/path/to/mcp-servers/rosbag-inspector/server.py"]
    }
  }
}
```

重启 Claude Code 后可使用 `inspect_rosbag` tool。

## inspect_rosbag 参数

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| bag_path | string | ✅ | rosbag 文件路径（支持 .mcap / .db3 / .bag） |

## 输出示例

```json
{
  "status": "success",
  "data": {
    "format": "mcap",
    "file_path": "/data/scene0061.mcap",
    "file_size_bytes": 104857600,
    "topic_count": 3,
    "total_messages": 15230,
    "duration_seconds": 60.5,
    "start_timestamp": 1700000000.0,
    "end_timestamp": 1700000060.5,
    "topics": [
      {
        "topic": "/scan",
        "message_type": "sensor_msgs/LaserScan",
        "message_count": 605,
        "avg_frequency_hz": 10.0
      },
      {
        "topic": "/odom",
        "message_type": "nav_msgs/Odometry",
        "message_count": 6050,
        "avg_frequency_hz": 100.0
      }
    ]
  },
  "errors": []
}
```

## 错误返回格式

```json
{
  "status": "error",
  "data": null,
  "errors": ["文件不存在：/data/scene.mcap"]
}
```

## 支持格式

| 格式 | 扩展名 | 说明 |
|---|---|---|
| ROS2 MCAP | .mcap | Foxglove 主导的 rosbag2 格式 |
| ROS2 DB3 | .db3 | rosbag2 默认压缩格式 |
| ROS1 Bag | .bag | rosbag1 传统格式 |
