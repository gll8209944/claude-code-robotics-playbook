"""
anomaly_frames.py — 异常帧检测（支持 cv2 + ffmpeg 双解码器）
A类（parquet）：动作跳变帧、冻结帧
B类（视频）：黑屏帧、模糊帧、曝光异常帧
阈值：strict < 0.5%，loose < 2%
"""
from __future__ import annotations
import json, re, shutil, subprocess, tempfile
from pathlib import Path
from typing import TypedDict
import cv2, numpy as np, pandas as pd

class AnomalyFramesResult(TypedDict):
    value: float; threshold: float; passed: bool; details: dict

THRESHOLDS = {"strict": 0.5, "loose": 2.0}
def _meta(dataset_path: Path) -> Path | None:
    for n in ["meta", "meta_data"]:
        d = dataset_path / n
        if d.exists() and d.is_dir(): return d
    return None
def _fmt(meta_dir: Path) -> str:
    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        if info.get("has_videos") or info.get("video_format"): return "video"
    return "video" if (meta_dir.parent / "videos").exists() else "parquet"
def _video_path(videos_dir: Path, ep_id: int) -> Path | None:
    ep_dir = videos_dir / str(ep_id)
    if ep_dir.exists():
        mp4s = list(ep_dir.glob("*.mp4"))
        if mp4s: return mp4s[0]
    for mp4 in videos_dir.rglob("*.mp4"):
        m = re.search(r"_episode_(\d+)", mp4.stem)
        if m and int(m.group(1)) == ep_id: return mp4
    mp4s = list(videos_dir.rglob("*.mp4"))
    return mp4s[0] if mp4s else None
def _sample_ffmpeg(path: Path, n: int) -> list:
    """ffmpeg seek 快速采样：各均匀位置取 1 帧。"""
    if not path.exists(): return []
    tmp = Path(tempfile.mkdtemp(prefix="af_"))
    try:
        res = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
            capture_output=True, text=True, timeout=10)
        duration = float(res.stdout.strip()) if res.returncode == 0 else 30.0
        frames = []
        for i in range(n):
            cmd = ["ffmpeg", "-y", "-ss", str(duration * i / n), "-i", str(path),
                   "-t", "1", "-vf", "fps=1", "-q:v", "3", str(tmp / f"f{i}.jpg")]
            if subprocess.run(cmd, capture_output=True, timeout=10).returncode == 0:
                for p in sorted(tmp.glob(f"f{i}.*")):
                    f = cv2.imread(str(p))
                    if f is not None: frames.append(f); break
        return frames
    except: return []
    finally: shutil.rmtree(tmp, ignore_errors=True)
def _sample_video(path: Path, n: int) -> list:
    """cv2 seek 采样；AV1 seek 失效则 fallback ffmpeg。"""
    if not path.exists(): return []
    cap = cv2.VideoCapture(str(path))
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    if total <= 0: return _sample_ffmpeg(path, n)
    # 测试 seek 是否有效（比较 0% 和 75% 位置的帧，相同则失效）
    c0, c1 = cv2.VideoCapture(str(path)), cv2.VideoCapture(str(path))
    _, f0 = c0.read(); c1.set(cv2.CAP_PROP_POS_FRAMES, 75); _, f1 = c1.read()
    c0.release(); c1.release()
    if not (f0 is not None and f1 is not None) or np.all(f0 == f1):
        return _sample_ffmpeg(path, n)
    frames = []
    for i in range(n):
        cap = cv2.VideoCapture(str(path))
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(total * i / n))
        ret, f = cap.read()
        if ret and f is not None and f.size: frames.append(f)
        cap.release()
    return frames if len(frames) >= n // 2 else _sample_ffmpeg(path, n)
def _sample_parquet(ep_df: pd.DataFrame, n: int, img_cols: list) -> list:
    rows = ep_df.to_dict("records")
    sel = rows if len(rows) <= n else [rows[i] for i in np.linspace(0, len(rows)-1, n, dtype=int)]
    frames = []
    for row in sel:
        for col in img_cols:
            val = row.get(col)
            if not val: continue
            try:
                img = cv2.imdecode(np.frombuffer(val, np.uint8), cv2.IMREAD_COLOR) if isinstance(val, bytes) else (
                    cv2.imdecode(np.array(val, dtype=np.uint8), cv2.IMREAD_COLOR) if isinstance(val, (list, tuple)) else None)
                if img is not None: frames.append(img); break
            except: continue
    return frames
def _a(df: pd.DataFrame, act_col: str | None) -> dict:
    r = {"action_jump": 0, "frozen": 0, "action_jump_by_video_drop": 0}
    if act_col is None or act_col not in df.columns: return r
    acts = df[act_col].dropna()
    if len(acts) < 2: return r
    try: arr = np.stack(acts.values)
    except: arr = np.asarray(acts.values)
    diffs = np.linalg.norm(np.diff(arr, axis=0), axis=1) if arr.ndim > 1 else np.diff(arr)
    vals = [tuple(v) for v in arr] if arr.ndim > 1 else list(arr)
    if len(diffs) == 0: return r
    mu, sigma = float(diffs.mean()), float(diffs.std())
    if sigma > 0:
        mask = np.abs(diffs - mu) / sigma > 3
        r["action_jump"] = int(mask.sum())
        if "timestamp" in df.columns and r["action_jump"] > 0:
            ts = df["timestamp"].dropna().values
            if len(ts) > 1:
                ts_ms = ts / 1e6 if ts[0] > 1e12 else ts * 1000
                td = np.diff(ts_ms); tm, ts2 = float(td.mean()), float(td.std())
                if ts2 > 0:
                    r["action_jump_by_video_drop"] = sum(1 for ji in np.where(mask)[0] if ji < len(td) and abs(td[ji] - tm) / ts2 > 3)
                    r["action_jump"] = max(0, r["action_jump"] - r["action_jump_by_video_drop"])
    streak = 1
    for i in range(1, len(vals)):
        try:
            same = np.allclose(vals[i], vals[i-1], atol=1e-6) if isinstance(vals[i], tuple) else bool(vals[i] == vals[i-1])
            if same: streak += 1
            else:
                if streak >= 5: r["frozen"] += 1
                streak = 1
        except: break
    if streak >= 5: r["frozen"] += 1
    return r
def _b(frames: list) -> dict:
    r = {"black": 0, "blur": 0, "exposure": 0}
    if not frames: return r
    gray, exp, valid = [], [], []
    for f in frames:
        if f is None or f.size == 0: continue
        valid.append(f)
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
        gray.append(float(g.mean())); exp.append(float(f.mean()))
    if not valid: return r
    gray, exp = np.array(gray), np.array(exp)
    r["black"] = int((gray < 5).sum())
    for f in valid:
        if float(cv2.Laplacian(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), cv2.CV_64F).var()) < 50: r["blur"] += 1
    mu, sigma = float(exp.mean()), float(exp.std())
    if sigma > 0: r["exposure"] = int((np.abs(exp - mu) / sigma > 3).sum())
    return r
def check_anomaly_frames(dataset_path: Path, profile: str = "strict") -> AnomalyFramesResult:
    thr = THRESHOLDS.get(profile, THRESHOLDS["strict"])
    meta_dir = _meta(dataset_path)
    if meta_dir is None: return AnomalyFramesResult(value=0.0, threshold=thr, passed=True, details={"note": "no meta"})
    fmt = _fmt(meta_dir)
    tot_f, tot_anom = 0, 0
    details_list = []
    ep_col = None
    act_cols = ["action", "action_vector", "robot_state"]
    data_dir, videos_dir = dataset_path / "data", dataset_path / "videos"

    per_ep = videos_dir.exists() and (
        any(d.is_dir() and d.name.isdigit() for d in videos_dir.iterdir()) or
        any("_episode_" in f.name for f in videos_dir.rglob("*.mp4")))

    shared_frames, shared_b = [], {"black": 0, "blur": 0, "exposure": 0}
    if fmt == "video" and videos_dir.exists() and not per_ep:
        mp4s = sorted(videos_dir.rglob("*.mp4"), key=lambda p: p.name)
        if mp4s and _sample_video(mp4s[0], 200):
            shared_frames = _sample_video(mp4s[0], 200)
            if shared_frames: shared_b = _b(shared_frames)

    if data_dir.exists():
        for item in data_dir.iterdir():
            pqs = [item] if item.is_file() and item.suffix == ".parquet" else (list(item.glob("*.parquet")) if item.is_dir() else [])
            for pf in pqs:
                df = pd.read_parquet(pf)
                if ep_col is None:
                    for c in ["episode_id", "episode_index"]:
                        if c in df.columns: ep_col = c; break
                if ep_col is None: continue
                img_cols = [c for c in df.columns if "image" in c or "frame" in c]
                act_col = next((c for c in act_cols if c in df.columns), None)
                for eid in sorted(df[ep_col].unique()):
                    ep_df = df[df[ep_col] == eid].sort_values("frame_index" if "frame_index" in df.columns else df.columns[0])
                    frames = []
                    if fmt == "parquet" and img_cols: frames = _sample_parquet(ep_df, 50, img_cols)
                    elif fmt == "video" and videos_dir.exists():
                        if per_ep:
                            vp = _video_path(videos_dir, int(eid))
                            frames = _sample_video(vp, 50) if vp else []
                        else: frames = shared_frames
                    a = _a(ep_df, act_col)
                    b = _b(frames) if frames else (shared_b if not per_ep else {"black": 0, "blur": 0, "exposure": 0})
                    ep_anom = sum(a.values()) + sum(b.values())
                    tot_f += len(ep_df); tot_anom += ep_anom
                    if ep_anom > 0: details_list.append({"episode_id": int(eid), "anomalies": {**a, **b}})

    if tot_f == 0: return AnomalyFramesResult(value=0.0, threshold=thr, passed=True, details={"note": "no frame data"})
    rate = tot_anom / tot_f * 100.0
    return AnomalyFramesResult(
        value=round(rate, 3), threshold=thr, passed=rate < thr,
        details={"total_frames": int(tot_f), "anomaly_count": int(tot_anom),
                 "anomalies_by_type": details_list[:5], "data_format": fmt},
    )
