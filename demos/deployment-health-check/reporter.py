#!/usr/bin/env python3
"""
部署体检报告生成模块（聚合入口）
调用 reporter_json.py 和 reporter_md.py 生成双份报告
"""

from pathlib import Path
from typing import List

from reporter_json import build_summary, build_top_risks, build_repair_priority, generate_report_json
from reporter_md import generate_report_md


def generate_reports(output_dir: Path, checks_results: List[dict]) -> tuple:
    """
    主函数：生成 JSON + Markdown 双份报告。
    返回 (json_path, md_path, summary)
    """
    summary = build_summary(checks_results)
    top_risks = build_top_risks(checks_results)
    repair_priority = build_repair_priority(checks_results)

    json_path = generate_report_json(output_dir, summary, checks_results, top_risks, repair_priority)
    md_path = generate_report_md(output_dir, summary, checks_results, top_risks, repair_priority)

    return json_path, md_path, summary
