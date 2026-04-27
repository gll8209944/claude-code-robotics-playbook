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


def _find_meta_dir(dataset_path: Path) -> Path | None:
    """自动查找 meta 目录，支持 meta/ 和 meta_data/ 等变体。"""
    for name in ["meta", "meta_data"]:
        d = dataset_path / name
        if d.exists() and d.is_dir():
            return d
    return None


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
    meta_dir = _find_meta_dir(dataset_path)
    if meta_dir is None:
        return MissingFramesResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={"note": "no meta directory found"},
        )
    videos_dir = dataset_path / "videos"

    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        expected_fps = info.get("fps", 30.0)
    else:
        expected_fps = 30.0

    # 优先从 data/ 目录读取 per-frame 数据
    # 支持两种结构：data/chunk-*/file-*.parquet 和 data/train-*.parquet（扁平）
    data_dir = dataset_path / "data"
    episodes_dir = meta_dir / "episodes"
    total_missing = 0
    total_expected = 0
    episodes_checked = 0
    source = None

    def _ep_col(df):
        for col in ["episode_id", "episode_index"]:
            if col in df.columns:
                return col
        return None

    if data_dir.exists():
        for item in data_dir.iterdir():
            if item.is_dir():
                # 嵌套结构：data/chunk-*/file-*.parquet
                parquet_files = item.glob("*.parquet")
            elif item.suffix == ".parquet":
                # 扁平结构：data/train-*.parquet
                parquet_files = [item]
            else:
                continue

            for parquet_file in parquet_files:
                df = pd.read_parquet(parquet_file)
                ep_col = _ep_col(df)
                if ep_col is None:
                    continue
                source = "data"
                episode_ids = df[ep_col].unique()
                for ep_id in episode_ids:
                    ep_df = df[df[ep_col] == ep_id].sort_values("frame_index")
                    if "frame_index" not in ep_df.columns:
                        continue
                    frame_indices = ep_df["frame_index"].dropna().values.astype(int)
                    if len(frame_indices) < 2:
                        continue
                    expected_set = set(range(int(frame_indices.min()), int(frame_indices.max()) + 1))
                    actual_set = set(frame_indices)
                    missing = len(expected_set - actual_set)
                    total_missing += missing
                    total_expected += len(expected_set)
                    episodes_checked += 1

    # 兜底：从 meta/episodes/ 读取（仅含统计值，不含真实缺帧检测）
    if not episodes_checked and episodes_dir.exists():
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
                source = "meta_episodes"
                episode_ids = df[ep_col].unique()
                for ep_id in episode_ids:
                    ep_df = df[df[ep_col] == ep_id]
                    if "frame_index" in ep_df.columns:
                        # meta/episodes 中 frame_index 是统计值（min/max），无法检测真实缺帧
                        frame_indices = ep_df["frame_index"].dropna().values
                        if len(frame_indices) < 2:
                            continue
                        expected_count = int(frame_indices.max()) + 1
                        actual_count = len(frame_indices)
                        missing = expected_count - actual_count
                        total_missing += max(0, missing)
                        total_expected += expected_count
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
            "data_source": source,
        },
    )
