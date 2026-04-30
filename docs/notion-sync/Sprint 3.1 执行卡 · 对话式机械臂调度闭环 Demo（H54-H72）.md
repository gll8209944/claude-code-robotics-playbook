> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `865ffea4-97dd-4b57-be44-a47da6cb4155`
> 原始链接: https://www.notion.so/865ffea497dd4b57be44a47da6cb4155

# Sprint 3.1 执行卡 · 对话式机械臂调度闭环 Demo（H54-H72）

> 🎯 **Sprint 3.1 唯一目标：** 18 小时内交付一个可对外演示的端到端闭环：
**自然语言 → 任务拆解 → 技能调度 → 动作执行（VLA）→ 视觉验证 → 失败自动重规划**。
首版以 **LIBERO 仿真**为主，形成 3 个可复现实验任务 + 1 段 3-5 分钟演示视频。

## Sprint 3.1 验收清单（H72 检查）

- [ ] LIBERO 环境 + VLA 推理链路跑通（最小 hello-world）

- [ ] `robot-skill-orchestrator` MCP 最小可用：技能注册表 + 调用协议 + 失败恢复策略（至少 3 个 tool）

- [ ] `task-decomposer` Skill 最小可用：自然语言 → atomic skill DAG（含失败重规划策略）

- [ ] 3 个 LIBERO 任务端到端跑通（含失败自动重规划）

- [ ] 录屏：3-5 分钟演示视频（对话式调度）+ 1 篇文章草稿/讲稿

---

## 关键策略：先打穿链路，不追求最优

> 🛑 **铁律：优先连通而非最强。** 本 Sprint 的 KPI 是“端到端可演示”，不是“成功率 95%”。

---

## H54-H56：2 小时准备清单

### Step 1：GPU 算力就绪（必须）

- A10/4090 24GB+（按量）

- 镜像/环境：Python + CUDA + 必要依赖

### Step 2：目录与仓库结构

```bash
cd ~/work/claude-code-robotics-playbook
mkdir -p demos/robot-skill-orchestrator/{scripts,schemas,reports,samples,tests}
mkdir -p skills/task-decomposer/{samples,tests}
mkdir -p mcp-servers/robot-skill-orchestrator/{tests,samples}
mkdir -p docs/sprint-3.1
```

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练到“系统编排者”。** Sprint 3.1 是最像真实工程的：多组件、多接口、多失败兜底。你要刻意练 Task（严格里程碑）、Team（Builder/Auditor/Writer 分脑）、Hooks（端到端门禁）。

### A. Task（任务拆解）— 端到端链路必须先拆 3 层

```plain text
进入 Task 模式，把 Sprint 3.1 拆成 8-10 个任务，并强制分三层：
Layer 0：mock 打通（无 VLA）
Layer 1：接入真实组件（VLA/LIBERO/视觉）
Layer 2：可演示化（录屏/讲稿/可复现实验）

每个任务必须给：产物、验收命令、失败兜底。
输出完停下。
```

### B. Team（Builder/Auditor/Writer）— 每次“接入真实组件”前必须跑 Auditor

```plain text
在你开始接入任何真实组件之前，按 Team 输出：
1) Builder：接入点与接口契约（输入/输出/失败语义）
2) Auditor：最可能失败的 5 个点 + 如何观测（日志/指标）+ 回滚策略
3) Writer：对外演示叙事（30秒讲清楚）
每个角色输出后停下。
```

### C. Hooks（门禁化）— 端到端 smoke test

在 `scripts/` 加一个 `smoke_sprint31.sh`（或纳入 preflight），门禁要求：

- 至少跑通 1 个任务脚本

- 必须出现一次可观测的 replan

- 输出日志必须包含：DAG、step 状态、失败原因

让 CC CLI 生成的指令：

```plain text
请新增 scripts/smoke_sprint31.sh：
1) 运行 task_01_block_to_plate
2) 强制制造一次失败（例如随机失败或 mock 返回 error）
3) 观察并断言触发 replan（最多2次）
4) 最终输出 PASS/FAIL
禁止引入新依赖。
```

### D. Spec-first（先接口后接入真实组件）

接入 LIBERO/VLA/视觉之前，必须先定：

- orchestrator tool 的输入/输出 schema

- 失败语义（retryable/原因/建议动作）

- 观测点（日志字段）

### E. Diff 驱动审查（系统级变更必须解释）

```plain text
请输出本次变更的 git diff --stat 与关键 diff 段落，并逐条解释：为什么改、对端到端 smoke 有何影响、如何回滚。
```

### F. Test engineering（失败重规划必须可测）

至少 1 个测试用例：强制失败 → replan → 最终成功/终止 的可观察断言。

### G. Observability（端到端可解释日志）

要求统一输出日志字段（建议 JSONL）：

- run_id, task_id, step_id, skill_name, status, error_reason, retry_count, replan_count

### H. Release discipline（可演示版本）

完成后打 tag：`sprint-3.1-demo-v0.1`，并在 `docs/sprint-3.1/` 写一页：复现实验命令 + 已知限制。

---

## ⚡ CC CLI：Sprint 3.1 主提示词（链路骨架 + 可演示闭环）

```plain text
你现在处于 Sprint 3.1：对话式机械臂调度闭环 Demo（LIBERO 起步）。请遵守仓库根 CLAUDE.md 的全部规范。

【目标】
在 18 小时内交付一个端到端可演示闭环：自然语言 → 任务拆解 → 技能调度 → VLA 执行 → 视觉验证 → 失败重规划。

【实现范围】
1) MCP Server：mcp-servers/robot-skill-orchestrator/
- 提供最小 3 个 tool：
  a) list_skills()
  b) run_skill(skill_name, inputs)
  c) register_skill(skill_schema)
- 约定统一返回：{ status, data, errors }
- 支持失败恢复：当 run_skill 返回 error 时，输出可重试信息（retryable/原因/建议动作）

2) Skill：skills/task-decomposer/
- 输入：natural_language_instruction + available_skills + constraints
- 输出：atomic skill DAG（JSON），包含：节点、依赖、每步输入、成功条件、失败重试策略

3) Demo：demos/robot-skill-orchestrator/
- 使用 LIBERO（或 mock）提供至少 3 个任务脚本：
  - task_01_block_to_plate
  - task_02_open_drawer_put_cup
  - task_03_bread_to_oven_get_milk
- 每个任务脚本都能：
  - 接收自然语言
  - 调用 task-decomposer 生成 DAG
  - 调用 orchestrator 依次执行
  - 若失败：触发 replan（最多 2 次）

【硬约束】
- 先用 mock skill 把链路跑通（无需真实 VLA），再逐步替换为真实组件
- 所有关键 JSON 都要有 schema（放 schemas/）
- 至少 3 个 pytest（覆盖：DAG 生成、orchestrator 调用、失败重试）

【完成后输出】
A. tree -L 3 mcp-servers/robot-skill-orchestrator skills/task-decomposer demos/robot-skill-orchestrator
B. 运行 1 个任务的命令
C. 一段端到端日志（20 行内）展示 replan

最后：git add -A && git commit -m "feat: Sprint 3.1 调度闭环骨架" && git push
```

---

## 自检审计 Prompt（生成后立刻贴）

```plain text
进入【自检模式】。
A. 是否端到端可运行一个任务？给出命令与输出摘要
B. 是否有 3 个任务脚本？
C. 是否有失败重规划（最多 2 次）且可观察？
D. 是否有 schema + pytest？
用表格输出证据与整改项。
```

---

## 录屏提词卡（演示视频结构）

- 30s：背景（为什么“应用执行层”最缺）

- 60s：给一句自然语言指令

- 120s：展示 DAG + 执行日志

- 60s：制造一次失败 → 自动重规划

- 30s：总结：这就是可产品化的技能调度粘合层
