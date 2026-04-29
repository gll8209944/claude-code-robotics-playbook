#!/usr/bin/env python3
"""
rosbag-inspector 核心检查逻辑
读取 rosbag 文件（.mcap / .db3 / .bag）的元数据。
"""

from pathlib import Path
from typing import Optional

try:
    from rosbags.rosbag2 import Reader as Rosbag2Reader
    HAS_ROSBAGS = True
except ImportError:
    HAS_ROSBAGS = False

try:
    from rosbags.rosbag1 import Reader as Rosbag1Reader
    HAS_ROSBAGS1 = True
except ImportError:
    HAS_ROSBAGS1 = False


def detect_format(path: Path) -> str:
    """根据扩展名判断 rosbag 格式。"""
    suffix = path.suffix.lower()
    if suffix == '.mcap':
        return 'mcap'
    elif suffix == '.db3':
        return 'rosbag2'
    elif suffix == '.bag':
        return 'rosbag1'
    return 'unknown'


def inspect_rosbag(bag_path: str) -> dict:
    """
    读取 rosbag 文件，返回元数据。
    返回格式：{ status, data, errors }
    错误不 raise，统一通过 errors 数组返回。
    """
    errors = []
    path = Path(bag_path)

    if not path.exists():
        return {
            'status': 'error',
            'data': None,
            'errors': [f'文件不存在：{bag_path}'],
        }

    fmt = detect_format(path)
    if fmt == 'unknown':
        return {
            'status': 'error',
            'data': None,
            'errors': [f'不支持的格式（仅支持 .mcap / .db3 / .bag）：{path.suffix}'],
        }

    try:
        if fmt == 'mcap':
            data = _inspect_mcap(path)
        elif fmt == 'rosbag2':
            data = _inspect_db3(path)
        elif fmt == 'rosbag1':
            data = _inspect_bag(path)
    except Exception as e:
        return {
            'status': 'error',
            'data': None,
            'errors': [f'读取失败：{str(e)}'],
        }

    if errors:
        return {'status': 'partial', 'data': data, 'errors': errors}
    return {'status': 'success', 'data': data, 'errors': []}


def _inspect_mcap(path: Path) -> dict:
    """读取 .mcap / .db3 文件（ROS2）。"""
    if not HAS_ROSBAGS:
        raise RuntimeError('rosbags 库未安装（pip install rosbags）')

    topic_msg_count = {}
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_messages = 0

    with Rosbag2Reader([str(path)]) as reader:
        connections = {c.id: c for c in reader.connections}

        for i, (conn, timestamp, _rawdata) in enumerate(reader.messages()):
            topic = connections[conn].topic
            topic_msg_count[topic] = topic_msg_count.get(topic, 0) + 1
            ts_sec = timestamp / 1e9
            if start_time is None:
                start_time = ts_sec
            end_time = ts_sec
            total_messages = i + 1

    duration = end_time - start_time if start_time and end_time else 0
    topics = _build_topic_list(topic_msg_count, connections, duration)

    return {
        'format': 'mcap',
        'file_path': str(path),
        'file_size_bytes': path.stat().st_size,
        'topic_count': len(topics),
        'total_messages': total_messages,
        'duration_seconds': round(duration, 3),
        'start_timestamp': round(start_time, 3) if start_time else None,
        'end_timestamp': round(end_time, 3) if end_time else None,
        'topics': topics,
    }


def _inspect_db3(path: Path) -> dict:
    """读取 .db3 文件（ROS2 rosbag2 格式）。"""
    return _inspect_mcap(path)


def _inspect_bag(path: Path) -> dict:
    """读取 .bag 文件（ROS1）。"""
    if not HAS_ROSBAGS1:
        raise RuntimeError('rosbags[rosbag1] 未安装（pip install "rosbags[rosbag1]"）')

    topic_msg_count = {}
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    total_messages = 0

    with Rosbag1Reader([str(path)]) as reader:
        connections = {c.id: c for c in reader.connections}

        for i, (conn, timestamp, _rawdata) in enumerate(reader.messages()):
            topic = connections[conn].topic
            topic_msg_count[topic] = topic_msg_count.get(topic, 0) + 1
            if start_time is None:
                start_time = timestamp
            end_time = timestamp
            total_messages = i + 1

    duration = end_time - start_time if start_time and end_time else 0
    topics = _build_topic_list(topic_msg_count, connections, duration)

    return {
        'format': 'rosbag1',
        'file_path': str(path),
        'file_size_bytes': path.stat().st_size,
        'topic_count': len(topics),
        'total_messages': total_messages,
        'duration_seconds': round(duration, 3),
        'start_timestamp': round(start_time, 3) if start_time else None,
        'end_timestamp': round(end_time, 3) if end_time else None,
        'topics': topics,
    }


def _build_topic_list(topic_msg_count: dict, connections: dict, duration: float) -> list:
    """根据 topic 统计构建 topic 列表。"""
    topics = []
    for topic, count in topic_msg_count.items():
        conn = connections.get(topic)
        msg_type = conn.topic_type if conn else 'unknown'
        fps = count / duration if duration > 0 else 0
        topics.append({
            'topic': topic,
            'message_type': msg_type,
            'message_count': count,
            'avg_frequency_hz': round(fps, 2),
        })
    return topics
