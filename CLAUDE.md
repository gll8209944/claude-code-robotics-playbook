# claude-code-robotics-playbook · CLAUDE.md

## 项目使命
本仓库是「机器人智能化 × Claude Code」的实战手册。每个 demo 必须解决机器人研发某个真实环节（数据 / 部署 / 运维 / VLA / 应用执行）的具体痛点，并以可演示、可发文章、可售卖的形式产出。

## 当前优先 Sprint
Sprint 1.1 — `demos/data-quality-gate`：给机器人采集数据加一道质量门禁。其它目录在本 Sprint 内禁止写代码。

## 数据四级标准（强制规范）
所有数据按以下四级管理，任何脚本对数据的处理必须遵循：

| 级别 | 含义 | 进入条件 |
|---|---|---|
| raw | 原始采集 | 落盘即为 raw |
| validated | 通过 data-quality-gate | 帧率一致性 / 缺帧率 / 多视角时间戳偏移 / 任务标签完整性 全部通过 |
| curated | 人工抽查 + 标签精修 | validated 基础上由人工确认任务描述准确、视角覆盖完整 |
| training | 可进入 VLA 训练 | curated 基础上写入 dataset card（版本号、采集时间、任务清单、已知缺陷） |

铁律：未经 validated 的数据禁止直接用于模型训练或对外演示。

## 质量门禁阈值
| 指标 | strict 阈值 | loose 阈值 |
|---|---|---|
| 帧率标准差 / 均值 | < 5% | < 10% |
| 缺帧率 | < 1% | < 3% |
| 多视角时间戳最大偏移 | < 50 ms | < 100 ms |
| 任务标签缺失率 | 0% | < 2% |
| 异常帧（黑屏 / 模糊）比例 | < 0.5% | < 2% |

## 报告输出规范
每次质检必须同时输出：
- `report.json`：机器可读，schema 见 `demos/data-quality-gate/schemas/report.schema.json`
- `report.md`：人可读，模板见 `demos/data-quality-gate/templates/report.md`

Markdown 模板字段：总评、数据集概览、关键指标表、Top 3 异常 episode、修复建议、对 VLA 训练的影响。

## Claude Code 行为准则（本项目）
1. 小步快跑：任何脚本超过 200 行先停下来拆分。
2. 每次写脚本必须同时写测试 — 至少 1 个 fixture 数据 + 1 个断言。
3. 报告永远双份（JSON + Markdown），便于工程系统消费 + 人工阅读。
4. 路径硬编码禁止 — 一律用 pathlib.Path + 命令行参数。
5. 写完一个能跑的版本立即提交，再做优化。提交信息用中文。
6. 任何外部依赖必须先在 requirements.txt 登记。

## 输出风格
- 中文为主，专有名词保留英文（episode、rosbag、FPS 等）。
- 报告语气克制，给数据不给情绪。
- 给建议时附带"为什么"。

## 当前严格不做的事
- 不做通用 Claude Code 教学。
- 不做大而全课程。
- 不在 demos/data-quality-gate 之外的目录写代码（除非显式说明已切换 Sprint）。
- 不引入 lerobot / pandas / numpy / pyarrow / opencv-python / jsonschema / pytest / rosbags 之外的依赖（如需新增，先在本文档登记理由）。
