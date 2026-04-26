"""
test_task_label.py — task_label 检查模块单测
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from checks import task_label


def _make_tasks_parquet(dir_path: Path, data: list[dict]) -> None:
    """创建 meta/tasks.parquet。"""
    meta = dir_path / "meta"
    meta.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(data)
    df.to_parquet(meta / "tasks.parquet")


def test_all_labels_present_strict():
    """所有 episode 有标签，strict 阈值 0%，应通过。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        tasks = [
            {"episode_id": i, "language_instruction": f"push the T-block {i}"}
            for i in range(20)
        ]
        _make_tasks_parquet(p, tasks)
        result = task_label.check_task_label(p, "strict")
        assert result["passed"]
        assert result["value"] == 0.0


def test_some_labels_missing_strict():
    """2/20 标签缺失，缺失率 10%，超过 strict 0% 阈值，应拒绝。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        tasks = [
            {"episode_id": i, "language_instruction": f"push the T-block {i}" if i % 10 != 0 else None}
            for i in range(20)
        ]
        _make_tasks_parquet(p, tasks)
        result = task_label.check_task_label(p, "strict")
        assert not result["passed"]
        assert result["value"] == 10.0


def test_labels_missing_loose():
    """1/50 标签缺失，缺失率 2%，strict 拒绝，loose 通过。"""
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "pusht"
        tasks = [
            {"episode_id": i, "language_instruction": f"task {i}" if i != 25 else None}
            for i in range(50)
        ]
        _make_tasks_parquet(p, tasks)
        strict_result = task_label.check_task_label(p, "strict")
        assert not strict_result["passed"]
        loose_result = task_label.check_task_label(p, "loose")
        assert loose_result["passed"]
