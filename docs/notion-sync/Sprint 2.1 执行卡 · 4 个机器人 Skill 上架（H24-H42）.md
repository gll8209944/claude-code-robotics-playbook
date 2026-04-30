> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `49c6710e-9058-4aea-b75e-4978d7745c06`
> 原始链接: https://www.notion.so/49c6710e90584aeab75e4978d7745c06

# Sprint 2.1 执行卡 · 4 个机器人 Skill 上架（H24-H42）

> 🎯 **Sprint 2.1 唯一目标：** 18 小时内把 Phase 1 的成果产品化为 **4 个可复用机器人 Skill**（最小可用版），并形成“可演示 + 可复用 + 可对外销售”的交付形态。

## Sprint 2.1 验收清单（H42 检查）

- [ ] 4 个 Skill 目录齐全（README + 示例 + 最小测试）：
1) `data-quality-gate`
2) `ros2-debug-assistant`
3) `fleet-health-checker`
4) `vla-experiment-manager`

- [ ] 每个 Skill 至少 1 个端到端 demo（命令行/脚本可跑）+ 1 份样例输出

- [ ] 每个 Skill 都有明确输入/输出契约（schema）+ 错误返回规范

- [ ] 至少 2 个 Skill 完成对外可展示录屏（GIF/MP4 任一）

- [ ] 发布/上架材料齐备：一句话卖点、适用场景、限制说明、安装方式

---

## 关键策略：先“最小可用”再“完美”

> 🛑 **铁律：每个 Skill 先做到 60 分能跑通。** 不要为了追求“覆盖所有机器人/所有数据格式”把 18h 拖成 60h。

---

## 目录规范（强制）

每个 Skill 目录结构一致（便于后续规模化）：

```plain text
skills/<skill-name>/
├── README.md
├── skill.md              # 给 Claude/客户看的使用说明
├── input.schema.json
├── output.schema.json
├── run.py                # 最小可运行入口
├── tests/
└── samples/
```

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练到“可规模化复制”。** Sprint 2.1 你会重复做 4 个 Skill，最适合练 Task/Team/Hooks：任务化拆解、三角色流水线、提交前门禁。

### A. Task（任务拆解）— 开工第 1 条指令（必须执行）

```plain text
进入 Task 模式：把 Sprint 2.1 拆成 7-9 个任务，并且对每个 Skill 都有：
- 目录结构完成
- schema 完成
- run.py 可跑通
- samples 有真实输出
- pytest 至少 1 个
- README 一句话卖点 + 使用示例

输出每个任务的验收命令与预计时间。输出完停下。
```

### B. Team（Builder/Auditor/Writer）— 每个 Skill 都走一遍

对每个 Skill 先 Builder 出方案，再 Auditor 列风险与合规证据，再 Writer 写对外卖点。

```plain text
请对 skill: <skill-name> 按 3 角色输出：
1) Builder：文件清单 + 接口契约
2) Auditor：如何证明“能跑、可复现、无新增依赖”
3) Writer：一句话卖点 + 1 个演示命令
每个角色输出后停下。
```

### C. Hooks（门禁化）— 本 Sprint 必须把 preflight 变成习惯

在仓库根新增并坚持使用：`scripts/preflight.sh`（如果 Sprint 1.3 已有则复用并扩展）。

门禁要求：

- `pytest -q`

- 行数门禁（skills/ 下核心文件 <200 行）

- 依赖门禁（禁止新增依赖）

- 样例门禁（每个 Skill samples/ 必须存在且非空）

让 CC CLI 生成/扩展的指令：

```plain text
请更新 scripts/preflight.sh：新增对 skills/ 的检查：
1) 确认 skills/ 下 4 个 skill 目录齐全
2) 每个目录必须含 README.md、input.schema.json、output.schema.json、run.py、samples/、tests/
3) pytest -q
4) 任一 run.py >200 行则 FAIL
输出清晰 PASS/FAIL。
```

### D. Spec-first（先契约后实现）— 每个 Skill 先定 I/O 合同

每个 Skill 开始前必须先产出并确认：

- input/output schema

- 一条可复制的 demo 命令

- samples 的“真实输出”落点（文件路径）

### E. Diff 驱动审查（防止 4 个 Skill 风格漂移）

在做完第 2 个 Skill 后强制跑一次“风格一致性 diff 审计”：

```plain text
请进入 Auditor：对比 skills/ 下已完成的 Skill，检查：返回结构、README 模板、schema 命名、退出码/错误语义是否一致。输出差异表 + 统一方案。
```

### F. Test engineering（最小样本与异常覆盖）

每个 Skill 的 tests 至少覆盖：

- 1 个正常输入

- 1 个缺失字段/非法字段

### G. Release discipline（可回滚版本点）

Sprint 2.1 完成后：

- 打 tag：`sprint-2.1-v0.1`

- 更新 `CHANGELOG.md`（或 docs/[decisions.md](http://decisions.md/)）记录 4 个 Skill 的接口与限制

### H. Prompt library（Skill 生成提示词资产化）

新增 `docs/prompts/sprint-2.1.md`：

- Skill 模板生成 prompt

- Skill 审计 prompt

- Skill README 卖点 prompt

---

## ⚡ CC CLI：Sprint 2.1 主提示词（生成 4 个 Skill 脚手架）

```plain text
你现在处于 Sprint 2.1：4 个机器人 Skill 上架。请遵守仓库根 CLAUDE.md 的全部规范。

任务：在 skills/ 下生成 4 个 Skill 的最小可用版本，分别是：
1) data-quality-gate
2) ros2-debug-assistant
3) fleet-health-checker
4) vla-experiment-manager

通用要求（对 4 个 Skill 都适用）：
- 目录结构按我提供的模板
- 每个 Skill 生成 input.schema.json + output.schema.json
- run.py 必须可运行（即使内部逻辑先是调用已有 demos/ 或 mock）
- 每个 Skill 至少 1 个 pytest
- README.md 必须包含：一句话卖点、输入输出、运行示例、限制、样例输出
- 错误返回统一结构：{ status: "ok"|"error", data: ..., errors: [...] }

实现策略：
- data-quality-gate：直接复用 demos/data-quality-gate 的核心逻辑
- ros2-debug-assistant：先做“日志解析 + 常见错误诊断规则库（10条）+ 建议输出”
- fleet-health-checker：先做“输入一份 fleet 状态 JSON → 输出健康巡检报告”
- vla-experiment-manager：复用 demos/vla-training-review 的解析器，做“多 run 对比汇总”最小版

硬约束：
- 不引入新依赖（如必须引入，先列清单让我确认）
- 单文件尽量 <200 行

完成后输出：
A. tree -L 3 skills/
B. 每个 Skill 的一行运行命令
C. 每个 Skill 的 samples/ 样例输出摘要（各 5 行内）
D. pytest 结果

最后：git add -A && git commit -m "feat: Sprint 2.1 4 个 Skill 最小可用版" && git push
```

---

## 自检审计 Prompt（生成后立刻贴）

```plain text
现在暂停写新代码，进入【自检模式】。

请审计：
1) skills/ 下是否 4 个 Skill 都存在且目录结构一致？
2) 每个 Skill 是否有 README/示例/最小测试？
3) 是否引入了未登记依赖？（列 import 对照 requirements）
4) 是否每个 Skill 都能跑通一条端到端 demo 命令？

输出：
| 项 | 结论 ✅/⚠️/❌ | 证据 | 整改动作 |
```

---

## H42 复盘模板

```markdown
Sprint 2.1 复盘
- 四个 Skill 哪两个最有市场？证据：
- 哪两个最耗时？原因：
- 录屏完成度：
- 下一 Sprint 唯一主线（2.2 内容包/订阅）：
```
