# claude-code-robotics-playbook

用 Claude Code 重构机器人研发全生命周期。当前阶段：Sprint 1.1 — 数据质量门禁。

## 这是什么
机器人智能化 × Claude Code 的实战手册。每个 demo 都解决一个真实痛点，并以可演示、可售卖的形式开源。

## 路线图（120 小时冲刺）
- [x] Sprint 1.1 数据质量门禁（H0-H6） ← 当前
- [ ] Sprint 1.2 部署前体检（H6-H12）
- [ ] Sprint 1.3 VLA 训练复盘（H12-H18）
- [ ] Sprint 3.1 对话式机械臂调度（LIBERO + MiniMax M2.1 × Pi05 VLA）

## 快速开始

```bash
git clone https://github.com/gll8209944/claude-code-robotics-playbook
cd claude-code-robotics-playbook
pip install -r requirements.txt

# 下载示例数据
huggingface-cli download --repo-type dataset lerobot/pusht \
    --local-dir ./datasets/pusht

# 跑数据质量门禁
python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ./datasets/pusht \
    --output ./demos/data-quality-gate/reports/ \
    --profile strict
```

## 提供的服务
| 服务 | 内容 | 定价 |
|---|---|---|
| 机器人 AI 化诊断（早鸟） | 45 分钟在线 + 一份痛点诊断 | ¥199 |
| 单点闭环诊断 | 2 小时 + 书面报告（数据/部署/VLA 三选一） | ¥999 |
| 机器人公司专项工作坊 | 2 天现场/线上 + 实操 Demo | ¥19,800 |

预约：飞书/微信 13738170552

## 关注我
- 知乎 / 掘金 / 微信公众号：<占位>
- GitHub Star + Issue 即可参与共建。

## License
MIT for code. 数据集请遵循各原始数据集 license。
