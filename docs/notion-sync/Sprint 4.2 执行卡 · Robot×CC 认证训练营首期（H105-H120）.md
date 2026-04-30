> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `14345b4f-61c3-4407-be7e-2dcda3b249d2`
> 原始链接: https://www.notion.so/14345b4f61c34407be7e2dcda3b249d2

# Sprint 4.2 执行卡 · Robot×CC 认证训练营首期（H105-H120）

> 🎯 **Sprint 4.2 唯一目标：** 15 小时内把「Robot×Claude Code 认证」做成首期可开营：
课程大纲 + 作业与评分标准 + 招生页 + 首期 30 人招募触达。

## Sprint 4.2 验收清单（H120 检查）

- [ ] 三级认证体系（L1/L2/L3）定义清晰：能力、作业、验收标准

- [ ] 首期训练营排期（4 周或 2 周密集）+ 每周产出

- [ ] 作业包：至少 4 个作业（对应 4 个闭环/Skill/MCP）

- [ ] 招生页（Notion/Markdown）+ FAQ + 3 条招生文案

- [ ] 触达 ≥ 30 人，形成 ≥ 10 个明确意向（记录名单）

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练到“可验收体系设计者”。** Sprint 4.2 的关键是 rubric 与验收标准，不是写漂亮文案。你要练 Task（验收拆解）+ Hooks（一致性/可验收门禁）。

### A. Task（任务拆解）— 先把“验收”拆出来

```plain text
进入 Task 模式：把 Sprint 4.2 拆成 7-9 个任务，并且每个任务都要包含“评分 rubic/验收标准”。
输出完停下。
```

### B. Team（Builder/Auditor/Writer）— Auditor 先行

```plain text
按 Team 输出：
1) Builder：L1/L2/L3 的能力-作业-验收映射表
2) Auditor：找出所有不可验收/过于主观的标准，改成可观察证据（命令输出/报告/录屏）
3) Writer：招生页与文案
每个角色输出后停下。
```

### C. Hooks（门禁化）— “可验收”检查

```plain text
请进入 Auditor：逐作业检查是否都包含：输入材料、步骤、提交物、评分 rubric、失败示例。缺任何一项就标红并补齐建议。输出缺口清单。
```

### D. Spec-first（先 rubric 后内容）

每个作业先定义：

- 提交物清单

- 评分 rubric（可观察证据）

- 失败示例

再写讲解与招生文案。

### E. Diff 驱动审查（避免主观标准）

```plain text
请进入 Auditor：扫描 levels/cohort-plan/assignments 中所有“主观词”（例如：优秀/熟练/理解），把它们改成可观察证据（命令输出/报告/录屏/测试通过）。输出修改表。
```

### F. Release discipline（可开营版本）

- 招生页标记 v0.1

- 作业包标记 v0.1

- 记录“适合谁/不适合谁”边界

### G. Prompt library（认证体系提示词库）

新增 `docs/prompts/sprint-4.2.md`：

- rubric 生成 prompt

- “主观词→证据”改写 prompt

- 招生文案 prompt

---

## ⚡ CC CLI：Sprint 4.2 主提示词（认证体系 + 招生物料）

```plain text
你现在处于 Sprint 4.2：Robot×Claude Code 认证训练营。禁止写新功能代码。

请在 docs/certification/ 下生成：

1) docs/certification/levels.md
- L1 实践者 / L2 架构师 / L3 布道者
- 每级：能力定义、必须完成的项目、评分标准、常见失败点

2) docs/certification/cohort-1-plan.md
- 首期训练营排期（建议 4 周）
- 每周：讲解主题、实操任务、交付物、验收方式

3) docs/certification/assignments/
- assignment-01-data-gate.md
- assignment-02-deploy-check.md
- assignment-03-vla-review.md
- assignment-04-orchestration.md
每个作业：目标、输入材料、步骤、提交物、评分 rubric

4) docs/certification/enrollment-page.md
- 招生页：适合谁、不适合谁、你将获得什么、价格占位、FAQ

5) docs/certification/outreach-messages.md
- 3 条招生文案（朋友圈/飞书群/私聊）

要求：
- 所有作业必须绑定仓库已有 demo/skill/mcp
- 标准要可执行、可验收

完成后输出：
A. 目录树
B. L1/L2/L3 对照表

最后：git add -A && git commit -m "docs: Sprint 4.2 认证训练营首期" && git push
```
