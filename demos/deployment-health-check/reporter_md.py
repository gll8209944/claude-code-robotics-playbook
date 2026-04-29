#!/usr/bin/env python3
"""
部署体检报告生成模块（Markdown 部分）
生成 deploy_report.md
"""

from pathlib import Path
from typing import List, Dict


def _status_emoji(s: str) -> str:
    return {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(s, '❌')


def _status_text(s: str) -> str:
    return {'PASS': '✅可部署', 'WARN': '⚠️有条件部署', 'FAIL': '❌拒绝部署'}.get(s, '❌拒绝部署')


def generate_report_md(output_dir: Path, summary: dict, checks_results: List[dict],
                       top_risks: List[dict], repair_priority: List[dict]) -> Path:
    """生成 deploy_report.md。"""
    # 渲染检查详情表格
    check_rows = []
    for i, check in enumerate(checks_results, 1):
        status = check.get('status', 'FAIL')
        emoji = _status_emoji(status)
        detail_msgs = []
        for d in check.get('details', []):
            detail_msgs.append(f"[{d.get('status','')}] {d.get('item','')}: {d.get('msg','')}")
        detail_text = '; '.join(detail_msgs) if detail_msgs else check.get('msg', '')
        check_rows.append(f"| {i} | {check.get('item','')} | {emoji} {status} | {detail_text} |")

    checks_table = '\n'.join(check_rows)

    # 渲染 Top 风险
    risks_section = ''
    for risk in top_risks:
        risks_section += f"### {risk['rank']}. {risk['item']}\n"
        risks_section += f"- **风险描述**：{risk['risk']}\n"
        risks_section += f"- **后果**：{risk['consequence']}\n\n"

    # 渲染修复建议
    repair_section = ''
    for rp in repair_priority:
        repair_section += f"### P{rp['priority']}：{rp['item']}\n"
        repair_section += f"**动作**：{rp['action']}\n\n"
        repair_section += f"**为什么**：{rp['why']}\n\n"

    overall_status = summary.get('overall_status', 'FAIL')

    content = f"""# 机器人部署体检报告

## 部署总评

**{_status_text(overall_status)}** | 退出码：`{summary.get('exit_code', -1)}` | 时间：`{summary.get('timestamp', '')}`

---

## 机器人概览

| 字段 | 值 |
|---|---|
| 型号 | {summary.get('robot_overview', {{}}).get('model', 'N/A')} |
| 序列号 | {summary.get('robot_overview', {{}}).get('serial_number', 'N/A')} |
| 固件版本 | {summary.get('robot_overview', {{}}).get('firmware_version', 'N/A')} |

---

## 五项检查详情

| # | 检查项 | 状态 | 详情 |
|---|---|---|---|
{checks_table}

---

## Top 3 风险项

{risks_section if risks_section else '*（无高风险项）*'}

---

## 修复建议优先级

{repair_section if repair_section else '*（无需修复）*'}

---

## 与上次体检的差异对比

*（首次体检，无对比数据）*
"""

    output_path = output_dir / 'deploy_report.md'
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path
