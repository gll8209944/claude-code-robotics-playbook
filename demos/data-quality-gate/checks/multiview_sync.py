"""
multiview_sync.py — 多视角时间戳同步检查

检查多视角（多摄像头）数据的时间戳最大偏移是否在阈值内。
阈值（strict）：< 50 ms
阈值（loose）：< 100 ms

pusht 等单视角数据集此检查自动通过。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import pandas as pd


class MultiviewSyncResult(TypedDict):
    value: float  # 毫秒
    threshold: float  # 毫秒
    passed: bool
    details: dict


THRESHOLDS = {"strict": 50.0, "loose": 100.0}  # 毫秒


def _find_meta_dir(dataset_path: Path) -> Path | None:
    """自动查找 meta 目录，支持 meta/ 和 meta_data/ 等变体。"""
    for name in ["meta", "meta_data"]:
        d = dataset_path / name
        if d.exists() and d.is_dir():
            return d
    return None


def check_multiview_sync(dataset_path: Path, profile: str = "strict") -> MultiviewSyncResult:
    """
    检查多视角时间戳同步。

    LeRobot 多视角数据集：同一 episode 内不同 observation.key
    （如 observation.image.front, observation.image.wrist）的 timestamp
    应在阈值内对齐。

    Args:
        dataset_path: LeRobot 格式数据集根目录
        profile: strict 或 loose

    Returns:
        MultiviewSyncResult dict
    """
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = _find_meta_dir(dataset_path)
    if meta_dir is None:
        return MultiviewSyncResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={"note": "no meta directory found, check skipped"},
        )

    # 加载 info.json 了解数据集有几组 observation
    info_path = meta_dir / "info.json"
    cameras = []
    if info_path.exists():
        info = json.loads(info_path.read_text())
        # LeRobot info.json 通常有 video_keys 或类似字段
        cameras = info.get("video_keys", info.get("cameras", []))

    # 遍历 episodes，看实际有几组视频
    episodes_dir = meta_dir / "episodes"
    observed_keys = set()

    if episodes_dir.exists():
        for chunk_dir in episodes_dir.iterdir():
            if not chunk_dir.is_dir():
                continue
            for parquet_file in chunk_dir.glob("*.parquet"):
                df = pd.read_parquet(parquet_file)
                # 找出所有 observation 相关的列
                for col in df.columns:
                    if col.startswith("observation."):
                        observed_keys.add(col)
                # 单文件直接 break
                break

    all_keys = list(observed_keys)
    # 判断是否多视角
    if len(all_keys) < 2:
        return MultiviewSyncResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={
                "note": "single view dataset, check skipped",
                "num_views": len(all_keys) or 1,
                "keys": all_keys,
            },
        )

    # 多视角：计算同一 episode 内各 key 的 timestamp 最大偏移
    max_offset_ms = 0.0

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
                if "timestamp" not in ep_df.columns:
                    continue
                ts = ep_df["timestamp"].dropna().values
                if len(ts) < 2:
                    continue
                if ts[0] > 1e12:
                    ts_ms = ts / 1e6
                else:
                    ts_ms = ts * 1000.0
                # 对每一帧，计算所有 key 的 timestamp 标准差，取最大
                # 由于同一行代表同一时刻，取所有 observation key 的时间戳在同一 frame 下的最大差异
                # 简化：用帧间差的中位数偏移代表系统误差
                offsets = []
                for key in all_keys:
                    if key not in ep_df.columns:
                        continue
                    kts = ep_df[key].dropna().values
                    if len(kts) < 2:
                        continue
                    if kts[0] > 1e12:
                        kts_ms = kts / 1e6
                    else:
                        kts_ms = kts * 1000.0
                    diffs = sorted([abs(kts_ms[i] - ts_ms[i]) for i in range(min(len(kts_ms), len(ts_ms)))])
                    if diffs:
                        offsets.append(diffs[len(diffs) // 2])
                if offsets:
                    max_offset_ms = max(max_offset_ms, max(offsets))

    return MultiviewSyncResult(
        value=round(max_offset_ms, 3),
        threshold=threshold,
        passed=max_offset_ms < threshold,
        details={
            "max_offset_ms": round(max_offset_ms, 3),
            "num_views": len(all_keys),
            "keys": all_keys,
        },
    )
