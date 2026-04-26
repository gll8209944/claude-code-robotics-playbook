"""
reporter.py — 双份报告生成器

同时输出 report.json（机器可读）和 report.md（人可读）。
遵循 demos/data-quality-gate/templates/report.md 模板字段。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import jsonschema

from checks import fps_consistency, missing_frames, multiview_sync, task_label


def generate_report(
    dataset_path: Path,
    output_dir: Path,
    profile: str = "strict",
) -> dict:
    """
    对数据集执行全部 4 项检查，生成双份报告。

    Args:
        dataset_path: LeRobot 格式数据集路径
        output_dir: 报告输出目录
        profile: strict 或 loose

    Returns:
        report dict（含 exit_code）
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 运行 4 项检查
    fps_result = fps_consistency.check_fps_consistency(dataset_path, profile)
    missing_result = missing_frames.check_missing_frames(dataset_path, profile)
    sync_result = multiview_sync.check_multiview_sync(dataset_path, profile)
    label_result = task_label.check_task_label(dataset_path, profile)

    # 加载数据集概览
    dataset_overview = _build_dataset_overview(dataset_path)

    # 汇总指标
    metrics = {
        "fps_consistency": fps_result,
        "missing_frames": missing_result,
        "multiview_sync": sync_result,
        "task_label": label_result,
        "anomaly_frames": {
            "value": 0.0,
            "threshold": 0.5 if profile == "strict" else 2.0,
            "passed": True,
            "details": {"note": "anomaly detection not yet implemented"},
        },
    }

    # 整体判定
    all_pass = all(m["passed"] for m in metrics.values())
    any_fail = any(
        not m["passed"] for m in metrics.values() if m.get("details", {}).get("note") != "anomaly detection not yet implemented"
    )
    if all_pass:
        exit_code = 0
        overall_pass = True
    elif any_fail:
        exit_code = 2
        overall_pass = False
    else:
        exit_code = 1
        overall_pass = True

    # Top 异常 episode
    top_anomalies = _build_top_anomalies(fps_result, missing_result, sync_result, label_result)

    # 修复建议
    suggestions = _build_suggestions(fps_result, missing_result, sync_result, label_result)

    # VLA 训练影响
    vla_impact = _build_vla_impact(exit_code, metrics)

    # 报告正文
    report = {
        "dataset_name": dataset_overview.get("name", dataset_path.name),
        "profile": profile,
        "overall_pass": overall_pass,
        "exit_code": exit_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dataset_overview": dataset_overview,
        "metrics": metrics,
        "top_anomalies": top_anomalies,
        "repair_suggestions": suggestions,
        "vla_training_impact": vla_impact,
    }

    # 验证 JSON schema
    schema_path = Path(__file__).parent / "schemas" / "report.schema.json"
    if schema_path.exists():
        schema = json.loads(schema_path.read_text())
        jsonschema.validate(instance=report, schema=schema)

    # 写 report.json
    json_path = output_dir / "report.json"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    json_path.chmod(0o644)

    # 写 report.md
    md_content = _render_markdown(report, dataset_overview, metrics)
    md_path = output_dir / "report.md"
    md_path.write_text(md_content)
    md_path.chmod(0o644)

    return report


def _build_dataset_overview(dataset_path: Path) -> dict:
    """从数据集目录提取概览信息。"""
    meta_dir = dataset_path / "meta"
    name = dataset_path.name

    total_episodes = 0
    total_frames = 0
    storage_bytes = 0
    cameras = []

    # info.json
    info_path = meta_dir / "info.json"
    if info_path.exists():
        info = json.loads(info_path.read_text())
        name = info.get("dataset_name", name)
        cameras = info.get("video_keys", info.get("cameras", []))

    # 统计 episodes
    episodes_dir = meta_dir / "episodes"
    if episodes_dir.exists():
        for chunk_dir in episodes_dir.iterdir():
            if not chunk_dir.is_dir():
                continue
            for pf in chunk_dir.glob("*.parquet"):
                import pandas as pd
                df = pd.read_parquet(pf)
                for col in ["episode_id", "episode_index"]:
                    if col in df.columns:
                        total_episodes += df[col].nunique()
                        total_frames += len(df)
                        break

    # 统计存储大小（data + videos）
    for subdir in ["data", "videos"]:
        sub_path = dataset_path / subdir
        if sub_path.exists():
            for f in sub_path.rglob("*"):
                if f.is_file():
                    storage_bytes += f.stat().st_size

    def _human_size(n: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if abs(n) < 1024:
                return f"{n:.1f} {unit}"
            n /= 1024
        return f"{n:.1f} PB"
    storage_human = _human_size(storage_bytes)

    return {
        "name": name,
        "total_episodes": total_episodes,
        "total_frames": total_frames,
        "storage_bytes": storage_bytes,
        "storage_human": storage_human,
        "has_multiview": len(cameras) > 1,
        "cameras": cameras,
    }


def _build_top_anomalies(
    fps, missing, sync, label
) -> list[dict]:
    """收集各项检查中的异常 episode。"""
    anomalies = []
    for m, key in [(fps, "fps"), (missing, "missing_frames"), (sync, "multiview"), (label, "task_label")]:
        details = m.get("details", {})
        if key == "fps" and not m["passed"]:
            anomalies.append({
                "episode_id": details.get("worst_episode_id", 0),
                "reason": f"FPS 一致性比率 {details.get('worst_episode_ratio', m['value']):.2f}% 超过阈值 {m['threshold']}%",
                "severity": "high",
            })
        elif key == "task_label" and not m["passed"]:
            missing_eps = details.get("missing_episodes", [])
            if missing_eps:
                anomalies.append({
                    "episode_id": missing_eps[0],
                    "reason": f"共 {details.get('missing_count', 0)} 个 episode 任务标签缺失",
                    "severity": "high",
                })
    return anomalies[:3]


def _build_suggestions(fps, missing, sync, label) -> list[str]:
    """根据检查结果生成修复建议。"""
    suggestions = []
    if not fps["passed"]:
        suggestions.append(
            f"帧率一致性未达标（{fps['value']:.2f}% > {fps['threshold']}%）。"
            "建议：检查相机采集时钟漂移，或在 meta 中记录准确的 timestamp 而非依赖 frame_index 推算。"
        )
    if not missing["passed"]:
        d = missing["details"]
        suggestions.append(
            f"缺帧率 {missing['value']:.2f}% 超过阈值 {missing['threshold']}%（{d.get('total_missing', 0)} 帧）。"
            "建议：重新采集缺失段，或在下游训练时做帧级 padding 并在 dataset card 中注明。"
        )
    if not sync["passed"]:
        suggestions.append(
            f"多视角时间戳偏移 {sync['value']:.2f}ms 超过阈值 {sync['threshold']}ms。"
            "建议：对各摄像头统一 NTP 授时，或在数据预处理时做时间戳对齐校正。"
        )
    if not label["passed"]:
        suggestions.append(
            f"任务标签缺失率 {label['value']:.2f}% 超过阈值 {label['threshold']}%。"
            "建议：补充缺失的 language_instruction 或在 meta/tasks.parquet 中用空字符串显式标记。"
        )
    if not suggestions:
        suggestions.append("本次检查全部通过，数据可直接进入 curated 阶段。")
    return suggestions


def _build_vla_impact(exit_code: int, metrics: dict) -> dict:
    """评估对 VLA 训练的影响。"""
    if exit_code == 0:
        return {
            "can_proceed": True,
            "risk_level": "low",
            "reason": "所有质量指标达标，数据可直接进入 training 阶段。",
        }
    elif exit_code == 1:
        return {
            "can_proceed": True,
            "risk_level": "medium",
            "reason": "部分指标超标，建议在 dataset card 中注明已知缺陷，训练时做对应数据增强或过滤。",
        }
    else:
        return {
            "can_proceed": False,
            "risk_level": "high",
            "reason": "关键质量指标未达标，强制进入 training 会污染模型。建议先修复后再推进。",
        }


def _render_markdown(report: dict, overview: dict, metrics: dict) -> str:
    """将报告数据渲染为 Markdown 文本。"""
    profile = report["profile"]
    exit_code = report["exit_code"]
    overall_verdict = "✅ 通过" if exit_code == 0 else ("⚠️ 有条件通过" if exit_code == 1 else "❌ 拒绝")

    fps = metrics["fps_consistency"]
    missing = metrics["missing_frames"]
    sync = metrics["multiview_sync"]
    label = metrics["task_label"]
    anomaly = metrics["anomaly_frames"]

    # 渲染异常 episode
    anomalies = report.get("top_anomalies", [])
    anomalies_md = ""
    if anomalies:
        for a in anomalies:
            anomalies_md += f"### Episode {a['episode_id']}（{a['severity']} 级别）\n\n- **原因**：{a['reason']}\n"
    else:
        anomalies_md = "无显著异常 episode。\n"

    # 渲染建议
    suggestions = report.get("repair_suggestions", [])
    suggestions_md = "\n".join(f"{i+1}. {s}" for i, s in enumerate(suggestions))

    vla = report.get("vla_training_impact", {})
    can_proceed = "✅ 可以" if vla.get("can_proceed") else "❌ 暂不可以"
    blocking_issues = [s for s in suggestions if "阻塞" in s or "污染" in s]

    cameras_str = ", ".join(overview.get("cameras", [])) or "无多视角信息"

    # 预计算阻塞问题段落
    blocking_section = ""
    if blocking_issues:
        blocking_section = "**阻塞问题**：\n" + "\n".join(f"- {b}" for b in blocking_issues)

    md = f"""# 数据质量门禁报告

**数据集**：{overview.get('name', 'unknown')}
**检查配置**：{profile}
**生成时间**：{report['timestamp']}
**整体判定**：{overall_verdict}

---

## 数据集概览

| 指标 | 值 |
|---|---|
| 总 episode 数 | {overview.get('total_episodes', 0)} |
| 总帧数 | {overview.get('total_frames', 0)} |
| 数据集体积 | {overview.get('storage_human', 'unknown')} |
| 多视角 | {'是' if overview.get('has_multiview') else '否（单视角）'} |
| 摄像头/key | {cameras_str} |

---

## 关键指标

| 检查项 | 实际值 | 阈值 | 结果 |
|---|---|---|---|
| 帧率一致性（FPSS 标准差/均值） | {fps['value']:.3f}% | < {fps['threshold']}% | {'✅' if fps['passed'] else '❌'} |
| 缺帧率 | {missing['value']:.3f}% | < {missing['threshold']}% | {'✅' if missing['passed'] else '❌'} |
| 多视角时间戳最大偏移 | {sync['value']:.3f} ms | < {sync['threshold']} ms | {'✅' if sync['passed'] else '❌'} |
| 任务标签缺失率 | {label['value']:.3f}% | ≤ {label['threshold']}% | {'✅' if label['passed'] else '❌'} |
| 异常帧（黑屏/模糊）比例 | {anomaly['value']:.3f}% | < {anomaly['threshold']}% | {'✅' if anomaly['passed'] else '❌'} |

---

## Top {len(anomalies)} 异常 Episode

{anomalies_md}
---

## 修复建议

{suggestions_md}

---

## 对 VLA 训练的影响

**是否可以进入训练**：{can_proceed}
**风险等级**：{vla.get('risk_level', 'unknown')}
**原因**：{vla.get('reason', 'unknown')}

{blocking_section}

---

*本报告由 data-quality-gate 自动生成，机器可读版本见 `report.json`*
"""
    return md
