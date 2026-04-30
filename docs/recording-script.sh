#!/bin/bash
# 录屏提词卡 — Sprint 1.1 data-quality-gate 演示
# 使用方法：逐行复制粘贴到终端执行

# === 准备 ===
# 此刻画面：终端 clear，干净状态

# === 第1步：展示仓库结构 ===
# 画面：tree 输出展示 demos/data-quality-gate 目录结构
tree -L 2 demos/data-quality-gate/
# 停3秒，让观众看清目录结构

# === 第2步：运行数据质量门禁 ===
# 画面：run_gate.py 逐行输出指标，最终显示 ❌ 拒绝（因为 strict 阈值严格）
# 注意：如果用 loose 则显示 ⚠️ 有条件通过
python3 demos/data-quality-gate/scripts/run_gate.py \
    --dataset ./datasets/so100_pickplace \
    --output ./demos/data-quality-gate/reports/so100 \
    --profile strict

# === 第3步：展示报告 ===
# 画面：report.md 内容
cat demos/data-quality-gate/reports/so100/report.md | head -50
# 停2秒
