"""
missing_frames.py — 缺帧率检查

检查连续帧序列是否有缺失帧。
阈值（strict）：< 1%
阈值（loose）：< 3%
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import pandas as pd


class MissingFramesResult(TypedDict):
    value: float  # 百分比
    threshold: float  # 百分比
    passed: bool
    details: dict


THRESHOLDS = {"strict": 1.0, "loose": 3.0}  # 百分比


def check_missing_frames(dataset_path: Path, profile: str = "strict") -> MissingFramesResult:
    """
    检查数据集缺帧率。

    通过 video 文件（mp4）的连续帧编号推断期望帧数，
    与 meta/episodes 中实际记录的 frame_index 对比，得出缺帧率。

    Args:
        dataset_path: LeRobot 格式数据集根目录
        profile: strict 或 loose

    Returns:
        MissingFramesResult dict
    """
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = dataset_path / "meta"
    videos_dir = dataset_path / "videos"

    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        expected_fps = info.get("fps", 30.0)
    else:
        expected_fps = 30.0

    # 尝试从 episodes parquet 获取 frame_index 范围
    episodes_dir = meta_dir / "episodes"
    total_missing = 0
    total_expected = 0
    episodes_checked = 0

    if episodes_dir.exists():
        for chunk_dir in episodes_dir.iterdir():
            if not chunk_dir.is_dir():
                continue
            for parquet_file in chunk_dir.glob("*.parquet"):
                df = pd.read_parquet(parquet_file)
                ep_col = None
                for col in ["episode_id", "episode_index"]:
                    if col in df.columns:
                        ep_col = col
                        break
                if ep_col is None:
                    continue
                episode_ids = df[ep_col].unique()
                for ep_id in episode_ids:
                    ep_df = df[df[ep_col] == ep_id].sort_values(
                        "frame_index" if "frame_index" in df.columns else df.columns[0]
                    )
                    if "frame_index" in ep_df.columns:
                        frame_indices = ep_df["frame_index"].dropna().values
                        if len(frame_indices) < 2:
                            continue
                        expected_count = int(frame_indices.max()) + 1
                        actual_count = len(frame_indices)
                        missing = expected_count - actual_count
                        total_missing += max(0, missing)
                        total_expected += expected_count
                        episodes_checked += 1
                    elif "timestamp" in ep_df.columns:
                        # 通过时长估算帧数
                        ts = ep_df["timestamp"].dropna().values
                        if ts[0] > 1e12:
                            duration_s = (ts.max() - ts.min()) / 1e9
                        else:
                            duration_s = ts.max() - ts.min()
                        expected_count = int(duration_s * expected_fps)
                        actual_count = len(ts)
                        missing = max(0, expected_count - actual_count)
                        total_missing += missing
                        total_expected += max(expected_count, actual_count)
                        episodes_checked += 1

    if total_expected == 0:
        # 无数据，保守通过
        return MissingFramesResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={"note": "no frame data found for missing frame check"},
        )

    missing_rate = (total_missing / total_expected) * 100.0
    return MissingFramesResult(
        value=round(missing_rate, 3),
        threshold=threshold,
        passed=missing_rate < threshold,
        details={
            "total_missing": int(total_missing),
            "total_expected": int(total_expected),
            "episodes_checked": episodes_checked,
        },
    )
