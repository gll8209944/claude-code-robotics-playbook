#!/usr/bin/env python3
"""
run_gate.py — 数据质量门禁入口脚本

用法：
    python3 demos/data-quality-gate/scripts/run_gate.py \
        --dataset ./datasets/pusht \
        --output ./demos/data-quality-gate/reports \
        --profile strict

退出码：
    0 — 通过
    1 — 有条件通过
    2 — 拒绝
"""
from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path


def _import_gate_module(name: str, path: Path):
    """从 demos/data-quality-gate/ 目录加载模块（绕过连字符目录名限制）。"""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# demos/data-quality-gate/ 目录（脚本的父目录的父目录）
_gate_dir = Path(__file__).resolve().parent.parent
if str(_gate_dir) not in sys.path:
    sys.path.insert(0, str(_gate_dir))

reporter = _import_gate_module("reporter", _gate_dir / "reporter.py")
generate_report = reporter.generate_report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LeRobot 数据质量门禁检查",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        required=True,
        help="LeRobot 格式数据集根目录路径",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="报告输出目录路径",
    )
    parser.add_argument(
        "--profile",
        type=str,
        default="strict",
        choices=["strict", "loose"],
        help="质量阈值配置：strict（默认）或 loose",
    )
    args = parser.parse_args()

    # 校验数据集路径
    if not args.dataset.exists():
        print(f"错误：数据集路径不存在：{args.dataset}", file=sys.stderr)
        return 2
    # 自动查找 meta 目录，支持 meta/ 和 meta_data/ 等变体
    meta_dir = None
    for name in ["meta", "meta_data"]:
        d = args.dataset / name
        if d.exists() and d.is_dir():
            meta_dir = d
            break
    if meta_dir is None:
        print(
            f"错误：数据集路径不是 LeRobot 格式（缺少 meta/ 或 meta_data/ 目录）：{args.dataset}",
            file=sys.stderr,
        )
        return 2

    # 生成报告
    print(f"开始检查数据集：{args.dataset}")
    print(f"使用阈值配置：{args.profile}")
    print("---")

    report = generate_report(
        dataset_path=args.dataset,
        output_dir=args.output,
        profile=args.profile,
    )

    exit_code = report["exit_code"]
    overall = (
        "✅ 通过"
        if exit_code == 0
        else ("⚠️ 有条件通过" if exit_code == 1 else "❌ 拒绝")
    )

    print(f"\n整体判定：{overall}")
    print(f"退出码：{exit_code}")
    print(f"\n报告已生成：")
    print(f"  JSON：{args.output / 'report.json'}")
    print(f"  Markdown：{args.output / 'report.md'}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
