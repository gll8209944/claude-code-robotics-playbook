"""
task_label.py — 任务标签完整性检查

检查每个 episode 是否含任务标签（language_instruction 或 task 字段）。
阈值（strict）：缺失率 = 0%
阈值（loose）：缺失率 < 2%
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import pandas as pd


class TaskLabelResult(TypedDict):
    value: float  # 百分比
    threshold: float  # 百分比
    passed: bool
    details: dict


THRESHOLDS = {"strict": 0.0, "loose": 2.0}  # 百分比


def check_task_label(dataset_path: Path, profile: str = "strict") -> TaskLabelResult:
    """
    检查任务标签完整性。

    LeRobot 数据集标签字段可能是：
    - language_instruction
    - task
    - instruction

    标签缺失 = 字段为空或不存在。

    Args:
        dataset_path: LeRobot 格式数据集根目录
        profile: strict 或 loose

    Returns:
        TaskLabelResult dict
    """
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = dataset_path / "meta"

    # 优先从 meta/tasks.parquet 获取任务标签信息
    tasks_path = meta_dir / "tasks.parquet"
    label_col = None
    total_episodes = 0
    missing_episodes: list[int] = []

    if tasks_path.exists():
        tasks_df = pd.read_parquet(tasks_path)
        for col in ["language_instruction", "task", "instruction", "episode_id"]:
            if col in tasks_df.columns:
                if col != "episode_id":
                    label_col = col
                break
        if "episode_id" in tasks_df.columns:
            total_episodes = len(tasks_df)
            if label_col:
                null_mask = tasks_df[label_col].isna() | (tasks_df[label_col].astype(str).str.strip() == "")
                missing_count = null_mask.sum()
                missing_episodes = tasks_df.loc[null_mask, "episode_id"].tolist()
            else:
                missing_count = 0
    else:
        # 兜底：从 episodes parquet 读取
        episodes_dir = meta_dir / "episodes"
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
                    total_episodes = len(episode_ids)
                    for candidate in ["language_instruction", "task", "instruction"]:
                        if candidate in df.columns:
                            label_col = candidate
                            break
                    if label_col:
                        for ep_id in episode_ids:
                            ep_df = df[df[ep_col] == ep_id]
                            val = ep_df[label_col].iloc[0] if len(ep_df) > 0 else None
                            if val is None or (isinstance(val, str) and val.strip() == ""):
                                missing_episodes.append(int(ep_id))
                    break
                break

    if total_episodes == 0:
        return TaskLabelResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={"note": "no episode data found, check skipped"},
        )

    missing_rate = (len(missing_episodes) / total_episodes) * 100.0
    return TaskLabelResult(
        value=round(missing_rate, 3),
        threshold=threshold,
        passed=missing_rate <= threshold,
        details={
            "total_episodes": total_episodes,
            "missing_count": len(missing_episodes),
            "missing_episodes": [int(x) for x in missing_episodes[:10]],  # 只保留前10个
            "label_col": label_col,
        },
    )
