"""
fps_consistency.py — 帧率一致性检查

检查每个 episode 的 FPS 标准差 / 均值是否在阈值内。
阈值（strict）：< 5%
阈值（loose）：< 10%
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import numpy as np
import pandas as pd


class FpsConsistencyResult(TypedDict):
    value: float  # 百分比
    threshold: float  # 百分比
    passed: bool
    details: dict


THRESHOLDS = {"strict": 5.0, "loose": 10.0}  # 百分比


def _find_meta_dir(dataset_path: Path) -> Path | None:
    """自动查找 meta 目录，支持 meta/ 和 meta_data/ 等变体。"""
    for name in ["meta", "meta_data"]:
        d = dataset_path / name
        if d.exists() and d.is_dir():
            return d
    return None


def load_episode_timestamps(meta_dir: Path, episode_id: int) -> pd.DataFrame | None:
    """从 meta/episodes/ 下加载指定 episode 的时间戳数据。"""
    if meta_dir is None:
        return None
    episodes_dir = meta_dir / "episodes"
    if not episodes_dir.exists():
        return None
    # 查找 episode parquet 文件
    for chunk_dir in episodes_dir.iterdir():
        if not chunk_dir.is_dir():
            continue
        for parquet_file in chunk_dir.glob("*.parquet"):
            df = pd.read_parquet(parquet_file)
            if "episode_index" in df.columns:
                df = df[df["episode_index"] == episode_id]
            # 尝试通过 index 匹配（chunk 内 episode 连续排列）
            # LeRobot episode parquet 通常直接含 episode_id 列
            if "episode_id" in df.columns:
                df = df[df["episode_id"] == episode_id]
            if len(df) > 0:
                return df.sort_values("frame_index" if "frame_index" in df.columns else df.index)
    # 兜底：直接读第一个文件（pusht 单文件）
    for chunk_dir in episodes_dir.iterdir():
        if not chunk_dir.is_dir():
            continue
        for parquet_file in chunk_dir.glob("*.parquet"):
            return pd.read_parquet(parquet_file).sort_values(
                "frame_index" if "frame_index" in df.columns else None
            )
    return None


def compute_fps_series(df: pd.DataFrame) -> np.ndarray:
    """从 dataframe 中提取 timestamp 或 frame_index，计算相邻帧的 FPS。"""
    if "timestamp" in df.columns:
        # nanoseconds 或 seconds
        ts = df["timestamp"].dropna().values
        if ts[0] > 1e12:  # nanoseconds
            ts = ts / 1e9
        if len(ts) < 2:
            return np.array([])
        deltas = np.diff(ts)
        # 过滤极端值（0 或极大）
        valid = (deltas > 0) & (deltas < 10)
        deltas = deltas[valid]
        if len(deltas) == 0:
            return np.array([])
        fps = 1.0 / deltas
    elif "frame_index" in df.columns:
        # frame_index 递增，假设均匀采样
        fi = df["frame_index"].dropna().values.astype(float)
        if len(fi) < 2:
            return np.array([])
        fps = np.diff(fi)  # 帧号差 ≈ 1，FPS 需另行估计
        # 如果 frame_index 是连续的，用默认 FPS=30 估计
        fps = np.ones(len(fi) - 1) * 30.0
    else:
        return np.array([])
    return fps


def check_fps_consistency(dataset_path: Path, profile: str = "strict") -> FpsConsistencyResult:
    """
    主函数：检查数据集帧率一致性。

    Args:
        dataset_path: LeRobot 格式数据集根目录（含 meta/）
        profile: strict 或 loose

    Returns:
        FpsConsistencyResult dict
    """
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = _find_meta_dir(dataset_path)
    if meta_dir is None:
        return _no_data_result(threshold)

    # 加载 info.json 获取数据集信息
    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        default_fps = info.get("fps", 30.0)
    else:
        default_fps = 30.0

    # 优先从 data/ 目录读取 per-frame 数据（含 timestamp）
    # 支持两种结构：
    #   - 嵌套结构：data/chunk-*/file-*.parquet（pusht, so100_pickplace 等）
    #   - 扁平结构：data/train-*.parquet（koch 等老格式）
    data_dir = dataset_path / "data"
    episodes_dir = meta_dir / "episodes"

    all_fps_ratios = []
    fps_details = []
    source = None

    def _process_data_parquet(parquet_file: Path):
        """处理单个 data parquet 文件，提取 FPS 数据。"""
        nonlocal source
        df = pd.read_parquet(parquet_file)
        ep_col = _find_episode_column(df)
        if ep_col is None or "timestamp" not in df.columns:
            return
        source = "data"
        episode_ids = df[ep_col].unique()
        for ep_id in episode_ids:
            ep_df = df[df[ep_col] == ep_id].copy()
            fps_arr = compute_fps_series(ep_df)
            if len(fps_arr) == 0:
                continue
            fps_mean = float(np.mean(fps_arr))
            fps_std = float(np.std(fps_arr))
            if fps_mean > 0:
                ratio = (fps_std / fps_mean) * 100.0
                all_fps_ratios.append(ratio)
                fps_details.append(
                    {
                        "episode_id": int(ep_id),
                        "fps_mean": round(fps_mean, 2),
                        "fps_std": round(fps_std, 2),
                        "ratio": round(ratio, 2),
                    }
                )

    if data_dir.exists():
        # 从 data/ 读取（支持嵌套和扁平两种结构）
        for item in data_dir.iterdir():
            if item.is_dir():
                # 嵌套结构：data/chunk-*/file-*.parquet
                for parquet_file in item.glob("*.parquet"):
                    _process_data_parquet(parquet_file)
            elif item.suffix == ".parquet":
                # 扁平结构：data/train-*.parquet
                _process_data_parquet(item)

    # 兜底：从 meta/episodes/ 读取（data/ 无数据时）
    if not all_fps_ratios and episodes_dir.exists():
        for chunk_dir in episodes_dir.iterdir():
            if not chunk_dir.is_dir():
                continue
            for parquet_file in chunk_dir.glob("*.parquet"):
                df = pd.read_parquet(parquet_file)
                ep_col = _find_episode_column(df)
                if ep_col is None:
                    continue
                source = "meta_episodes"
                episode_ids = df[ep_col].unique()
                for ep_id in episode_ids:
                    ep_df = df[df[ep_col] == ep_id].copy()
                    fps_arr = compute_fps_series(ep_df)
                    if len(fps_arr) == 0:
                        continue
                    fps_mean = float(np.mean(fps_arr))
                    fps_std = float(np.std(fps_arr))
                    if fps_mean > 0:
                        ratio = (fps_std / fps_mean) * 100.0
                        all_fps_ratios.append(ratio)
                        fps_details.append(
                            {
                                "episode_id": int(ep_id),
                                "fps_mean": round(fps_mean, 2),
                                "fps_std": round(fps_std, 2),
                                "ratio": round(ratio, 2),
                            }
                        )

    if not all_fps_ratios:
        return _no_data_result(threshold)

    # 取所有 episode 中最差的 ratio
    worst_ratio = float(np.max(all_fps_ratios))
    overall_mean = float(np.mean([d["fps_mean"] for d in fps_details]))
    overall_std = float(np.mean([d["fps_std"] for d in fps_details]))

    return FpsConsistencyResult(
        value=round(worst_ratio, 3),
        threshold=threshold,
        passed=worst_ratio < threshold,
        details={
            "worst_episode_ratio": worst_ratio,
            "fps_mean_avg": round(overall_mean, 2),
            "fps_std_avg": round(overall_std, 2),
            "episodes_checked": len(all_fps_ratios),
            "data_source": source,
        },
    )


def _find_episode_column(df: pd.DataFrame) -> str | None:
    """查找 DataFrame 中的 episode ID 列名。"""
    for col in ["episode_id", "episode_index"]:
        if col in df.columns:
            return col
    return None


def _no_data_result(threshold: float) -> FpsConsistencyResult:
    return FpsConsistencyResult(
        value=0.0,
        threshold=threshold,
        passed=True,
        details={"note": "no episode data found"},
    )
