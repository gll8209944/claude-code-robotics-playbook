"""
test_fps_consistency.py — fps_consistency 检查模块单测
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from checks import fps_consistency


def _make_meta(dir_path: Path, episodes_data: list[dict]) -> None:
    """在 dir_path 下创建 LeRobot 格式的 meta/episodes 结构。"""
    meta = dir_path / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    episodes_dir = meta / "episodes"
    episodes_dir.mkdir(exist_ok=True)
    chunk_dir = episodes_dir / "chunk-000"
    chunk_dir.mkdir(exist_ok=True)
    df = pd.DataFrame(episodes_data)
    df.to_parquet(chunk_dir / "file-000.parquet")


def test_strict_fps_consistency_pass():
    """FPS std/mean = 0%，应通过 strict。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        # 模拟 30fps 完美均匀采样，100 帧
        episodes = [
            {
                "episode_id": 0,
                "frame_index": i,
                "timestamp": i / 30.0,
            }
            for i in range(100)
        ]
        _make_meta(p, episodes)
        result = fps_consistency.check_fps_consistency(p, "strict")
        assert result["passed"]
        assert result["value"] == 0.0


def test_strict_fps_consistency_fail():
    """FPS std/mean > 5%，应被 strict 拒绝。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        # 模拟时钟漂移导致部分帧间隔异常
        ts = [0.0]
        for i in range(1, 50):
            ts.append(ts[-1] + 0.033 + (0.01 if i % 10 == 0 else 0.0))
        episodes = [{"episode_id": 0, "frame_index": i, "timestamp": ts[i]} for i in range(50)]
        _make_meta(p, episodes)
        result = fps_consistency.check_fps_consistency(p, "strict")
        assert not result["passed"]
        assert result["value"] > 5.0


def test_loose_fps_consistency_pass():
    """FPS std/mean = 8%，通过 loose 但拒绝 strict。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        # 制造 ~8% 的标准差
        ts = [0.0]
        for i in range(1, 100):
            # ~8% 变异
            ts.append(ts[-1] + 0.033 * (1.0 + 0.08 * ((i % 3) - 1)))
        episodes = [{"episode_id": 0, "frame_index": i, "timestamp": ts[i]} for i in range(100)]
        _make_meta(p, episodes)
        result = fps_consistency.check_fps_consistency(p, "loose")
        assert result["passed"]
        assert 5.0 < result["value"] < 10.0
