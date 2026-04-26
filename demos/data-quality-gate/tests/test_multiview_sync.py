"""
test_multiview_sync.py — multiview_sync 检查模块单测
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from checks import multiview_sync


def _make_meta(dir_path: Path, episodes_data: list[dict]) -> None:
    """创建多视角 meta/episodes 结构。"""
    meta = dir_path / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    episodes_dir = meta / "episodes"
    episodes_dir.mkdir(exist_ok=True)
    chunk_dir = episodes_dir / "chunk-000"
    chunk_dir.mkdir(exist_ok=True)
    df = pd.DataFrame(episodes_data)
    df.to_parquet(chunk_dir / "file-000.parquet")


def test_single_view_skipped():
    """单视角数据集，检查跳过，直接通过。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        episodes = [{"episode_id": 0, "frame_index": i, "timestamp": i / 30.0} for i in range(50)]
        _make_meta(p, episodes)
        result = multiview_sync.check_multiview_sync(p, "strict")
        assert result["passed"]
        assert result["details"]["num_views"] == 1


def test_multiview_in_sync():
    """多视角 timestamp 完全对齐，应通过 strict（阈值 50ms）。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        ts_base = [i / 30.0 for i in range(50)]
        episodes = [
            {
                "episode_id": 0,
                "frame_index": i,
                "timestamp": ts_base[i],
                "observation.image.wrist": ts_base[i],
                "observation.image.front": ts_base[i],
            }
            for i in range(50)
        ]
        _make_meta(p, episodes)
        result = multiview_sync.check_multiview_sync(p, "strict")
        assert result["passed"]
        assert result["value"] == 0.0


def test_multiview_out_of_sync():
    """多视角偏移 80ms，strict 拒绝（阈值 50ms），loose 通过（阈值 100ms）。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        ts_base = [i / 30.0 for i in range(50)]
        episodes = [
            {
                "episode_id": 0,
                "frame_index": i,
                "timestamp": ts_base[i],
                "observation.image.wrist": ts_base[i],
                "observation.image.front": ts_base[i] + 0.080,  # 80ms 偏移
            }
            for i in range(50)
        ]
        _make_meta(p, episodes)
        strict_result = multiview_sync.check_multiview_sync(p, "strict")
        assert not strict_result["passed"]
        loose_result = multiview_sync.check_multiview_sync(p, "loose")
        assert loose_result["passed"]
