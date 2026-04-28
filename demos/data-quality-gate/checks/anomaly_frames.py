"""
anomaly_frames.py — 异常帧检测
检测 5 类异常帧：
  A类（parquet）：动作跳变帧、冻结帧
  B类（cv2）：黑屏帧、模糊帧、曝光异常帧
阈值（strict）：< 0.5%  （loose）：< 2%
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import TypedDict

import cv2
import numpy as np
import pandas as pd


class AnomalyFramesResult(TypedDict):
    value: float
    threshold: float
    passed: bool
    details: dict


THRESHOLDS = {"strict": 0.5, "loose": 2.0}


def _find_meta_dir(dataset_path: Path) -> Path | None:
    for name in ["meta", "meta_data"]:
        d = dataset_path / name
        if d.exists() and d.is_dir():
            return d
    return None


def _detect_format(meta_dir: Path) -> str:
    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        if info.get("has_videos") or info.get("video_format"):
            return "video"
    if (meta_dir.parent / "videos").exists():
        return "video"
    return "parquet"


def _sample_video(ep_dir: Path, n: int) -> list:
    mp4s = list(ep_dir.glob("*.mp4")) or list(ep_dir.glob("*.mkv"))
    if not mp4s:
        return []
    cap = cv2.VideoCapture(str(mp4s[0]))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    indices = list(range(total)) if total < n else np.linspace(0, total - 1, n, dtype=int).tolist()
    frames = []
    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
    cap.release()
    return frames


def _sample_parquet(ep_df: pd.DataFrame, n: int, img_cols: list) -> list:
    rows = ep_df.to_dict("records")
    selected = rows if len(rows) <= n else [rows[i] for i in np.linspace(0, len(rows) - 1, n, dtype=int)]
    frames = []
    for row in selected:
        for col in img_cols:
            val = row.get(col)
            if not val:
                continue
            try:
                if isinstance(val, bytes):
                    img = cv2.imdecode(np.frombuffer(val, np.uint8), cv2.IMREAD_COLOR)
                elif isinstance(val, (list, tuple)):
                    img = cv2.imdecode(np.array(val, dtype=np.uint8), cv2.IMREAD_COLOR)
                else:
                    continue
                if img is not None:
                    frames.append(img)
                    break
            except Exception:
                continue
    return frames


def _a_anomalies(df: pd.DataFrame, act_col: str | None) -> dict:
    result = {"action_jump": 0, "frozen": 0, "action_jump_by_video_drop": 0}
    if act_col is None or act_col not in df.columns:
        return result
    actions = df[act_col].dropna()
    if len(actions) < 2:
        return result
    arr_raw = actions.values
    try:
        arr = np.stack(arr_raw)
    except (ValueError, TypeError):
        arr = np.asarray(arr_raw)
    if arr.ndim > 1:
        diffs = np.linalg.norm(np.diff(arr, axis=0), axis=1)
        vals = [tuple(v) for v in arr]
    else:
        diffs = np.diff(arr)
        vals = list(arr)
    if len(diffs) == 0:
        return result
    mean_d, std_d = float(diffs.mean()), float(diffs.std())
    if std_d > 0:
        jump_mask = np.abs(diffs - mean_d) / std_d > 3
        result["action_jump"] = int(jump_mask.sum())

    # 若有 action 跳变，进一步用 timestamp 判断是否为视频丢帧引起
    if "timestamp" in df.columns and result["action_jump"] > 0:
        ts = df["timestamp"].dropna().values
        if len(ts) > 1:
            # 转为毫秒
            ts_ms = ts / 1e6 if ts[0] > 1e12 else ts * 1000
            ts_diffs = np.diff(ts_ms)
            ts_mean = float(np.mean(ts_diffs))
            ts_std = float(np.std(ts_diffs))
            if ts_std > 0:
                jump_indices = np.where(jump_mask)[0]
                for ji in jump_indices:
                    # 检查 action 跳变位置对应的 timestamp 间隔是否也异常大
                    if ji < len(ts_diffs) and abs(ts_diffs[ji] - ts_mean) / ts_std > 3:
                        result["action_jump_by_video_drop"] += 1
                # 修正：去掉视频丢帧导致的跳变，保留真实动作跳变
                result["action_jump"] = max(0, result["action_jump"] - result["action_jump_by_video_drop"])
    # frozen frames
    streak = 1
    for i in range(1, len(vals)):
        try:
            if isinstance(vals[i], tuple):
                same = np.allclose(vals[i], vals[i - 1], atol=1e-6)
            else:
                same = bool(vals[i] == vals[i - 1])
            if same:
                streak += 1
            else:
                if streak >= 5:
                    result["frozen"] += 1
                streak = 1
        except Exception:
            break
    return result


def _b_anomalies(frames: list) -> dict:
    result = {"black": 0, "blur": 0, "exposure": 0}
    if not frames:
        return result
    gray_vals, exp_vals = [], []
    valid = []
    for f in frames:
        if f is None or f.size == 0:
            continue
        valid.append(f)
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        gray_vals.append(g.mean())
        exp_vals.append(f.mean())
    if not valid:
        return result
    gray_vals, exp_vals = np.array(gray_vals), np.array(exp_vals)
    result["black"] = int((gray_vals < 5).sum())
    for f in valid:
        lap_var = cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()
        if lap_var < 50:
            result["blur"] += 1
    exp_mean, exp_std = exp_vals.mean(), exp_vals.std()
    if exp_std > 0:
        result["exposure"] = int((np.abs(exp_vals - exp_mean) / exp_std > 3).sum())
    return result


def check_anomaly_frames(dataset_path: Path, profile: str = "strict") -> AnomalyFramesResult:
    threshold = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = _find_meta_dir(dataset_path)
    if meta_dir is None:
        return AnomalyFramesResult(value=0.0, threshold=threshold, passed=True, details={"note": "no meta directory found"})

    data_format = _detect_format(meta_dir)
    total_frames, anomaly_count = 0, 0
    details_list = []
    ep_col_found = None
    action_cols = ["action", "action_vector", "robot_state"]
    data_dir = dataset_path / "data"
    videos_dir = dataset_path / "videos"

    if data_dir.exists():
        for item in data_dir.iterdir():
            parquet_files = [item] if item.is_file() and item.suffix == ".parquet" else (list(item.glob("*.parquet")) if item.is_dir() else [])
            for pf in parquet_files:
                df = pd.read_parquet(pf)
                if ep_col_found is None:
                    for c in ["episode_id", "episode_index"]:
                        if c in df.columns:
                            ep_col_found = c
                            break
                ep_col = ep_col_found
                if ep_col is None:
                    continue
                img_cols = [c for c in df.columns if "image" in c or "frame" in c]
                act_col = next((c for c in action_cols if c in df.columns), None)
                for ep_id in df[ep_col].unique():
                    ep_df = df[df[ep_col] == ep_id].sort_values("frame_index" if "frame_index" in df.columns else df.columns[0])
                    ep_frames = len(ep_df)
                    frames = _sample_parquet(ep_df, 50, img_cols) if data_format == "parquet" and img_cols else (_sample_video(videos_dir / str(ep_id), 50) if data_format == "video" else [])
                    a = _a_anomalies(ep_df, act_col)
                    b = _b_anomalies(frames)
                    ep_anomalies = sum(a.values()) + sum(b.values())
                    total_frames += ep_frames
                    anomaly_count += ep_anomalies
                    if ep_anomalies > 0:
                        details_list.append({"episode_id": int(ep_id), "anomalies": {**a, **b}})

    if total_frames == 0:
        return AnomalyFramesResult(value=0.0, threshold=threshold, passed=True, details={"note": "no frame data found for anomaly check"})

    anomaly_rate = (anomaly_count / total_frames) * 100.0
    return AnomalyFramesResult(
        value=round(anomaly_rate, 3),
        threshold=threshold,
        passed=anomaly_rate < threshold,
        details={
            "total_frames": int(total_frames),
            "anomaly_count": int(anomaly_count),
            "anomalies_by_type": details_list[:5],
            "data_format": data_format,
        },
    )
