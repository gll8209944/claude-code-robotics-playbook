"""
test_missing_frames.py — missing_frames 检查模块单测
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from checks import missing_frames


def _make_meta(dir_path: Path, episodes_data: list[dict]) -> None:
    """创建含 frame_index 的 meta/episodes 结构。"""
    meta = dir_path / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    episodes_dir = meta / "episodes"
    episodes_dir.mkdir(exist_ok=True)
    chunk_dir = episodes_dir / "chunk-000"
    chunk_dir.mkdir(exist_ok=True)
    df = pd.DataFrame(episodes_data)
    df.to_parquet(chunk_dir / "file-000.parquet")


def test_missing_frames_none():
    """无缺帧，应通过 strict（阈值 1%）。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        episodes = [{"episode_id": 0, "frame_index": i} for i in range(100)]
        _make_meta(p, episodes)
        result = missing_frames.check_missing_frames(p, "strict")
        assert result["passed"]
        assert result["value"] == 0.0


def test_missing_frames_strict_fail():
    """缺帧率 2%，超过 strict 1% 阈值，应拒绝。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        # 100 个 frame_index，但跳过了几个
        indices = list(range(100))
        indices.remove(10)
        indices.remove(20)
        indices.remove(50)
        episodes = [{"episode_id": 0, "frame_index": i} for i in indices]
        _make_meta(p, episodes)
        result = missing_frames.check_missing_frames(p, "strict")
        assert not result["passed"]
        # 3 missing / 100 expected ≈ 3%
        assert result["value"] > 1.0


def test_missing_frames_loose_pass():
    """缺帧率 2%，通过 loose（阈值 3%）。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        indices = list(range(100))
        indices.remove(10)
        indices.remove(20)
        episodes = [{"episode_id": 0, "frame_index": i} for i in indices]
        _make_meta(p, episodes)
        result = missing_frames.check_missing_frames(p, "loose")
        assert result["passed"]
        assert 1.0 < result["value"] < 3.0
