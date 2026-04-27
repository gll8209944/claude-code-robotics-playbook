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


def _extract_label(ep_df: pd.DataFrame, label_col: str) -> str | None:
    """从标签列提取文本值，支持 array of string 类型（如 LeRobot 的 tasks 列）。"""
    if label_col not in ep_df.columns:
        return None
    val = ep_df[label_col].iloc[0] if len(ep_df) > 0 else None
    if val is None:
        return None
    # tasks 列是 array of string，取第一个元素
    if isinstance(val, (list, tuple)):
        val = val[0] if len(val) > 0 else None
    if isinstance(val, str):
        return val.strip() if val.strip() else None
    return str(val) if val is not None else None


def _find_meta_dir(dataset_path: Path) -> Path | None:
    """自动查找 meta 目录，支持 meta/ 和 meta_data/ 等变体。"""
    for name in ["meta", "meta_data"]:
        d = dataset_path / name
        if d.exists() and d.is_dir():
            return d
    return None


def check_task_label(dataset_path: Path, profile: str = "strict") -> TaskLabelResult:
    """
    检查任务标签完整性。

    LeRobot 数据集标签字段可能是：
    - language_instruction
    - task
    - instruction
    - tasks  (array of string per episode)

    标签缺失 = 字段为空或不存在。

    Args:
        dataset_path: LeRobot 格式数据集根目录
        profile: strict 或 loose

    Returns:
        TaskLabelResult dict
    """
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = _find_meta_dir(dataset_path)
    if meta_dir is None:
        return TaskLabelResult(
            value=0.0,
            threshold=threshold,
            passed=True,
            details={"note": "no meta directory found, check skipped"},
        )

    label_col = None
    total_episodes = 0
    missing_episodes: list[int] = []
    source = None

    # 路径1：从 meta/tasks.parquet 读取（扁平时使用）
    tasks_path = meta_dir / "tasks.parquet"
    if tasks_path.exists():
        tasks_df = pd.read_parquet(tasks_path)
        for col in ["language_instruction", "task", "instruction", "tasks", "episode_id"]:
            if col in tasks_df.columns:
                if col != "episode_id":
                    label_col = col
                break
        if "episode_id" in tasks_df.columns:
            source = "tasks_parquet"
            total_episodes = len(tasks_df)
            if label_col:
                for _, row in tasks_df.iterrows():
                    val = _extract_label(row.to_frame().T, label_col)
                    ep_id = int(row["episode_id"]) if "episode_id" in tasks_df.columns else 0
                    if not val:
                        missing_episodes.append(ep_id)
            else:
                missing_episodes = []

    # 路径2：从 meta/episodes/*.parquet 读取（每 episode 含标签）
    if not label_col or total_episodes == 0:
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
                    source = "episodes_parquet"
                    episode_ids = df[ep_col].unique()
                    total_episodes = len(episode_ids)
                    for candidate in ["language_instruction", "task", "instruction", "tasks"]:
                        if candidate in df.columns:
                            label_col = candidate
                            break
                    if label_col:
                        for ep_id in episode_ids:
                            ep_df = df[df[ep_col] == ep_id]
                            val = _extract_label(ep_df, label_col)
                            if not val:
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
            "missing_episodes": [int(x) for x in missing_episodes[:10]],
            "label_col": label_col,
            "data_source": source,
        },
    )
