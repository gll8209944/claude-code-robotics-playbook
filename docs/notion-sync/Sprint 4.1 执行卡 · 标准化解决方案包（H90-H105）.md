> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `4303c31a-89f7-4fe9-9a91-63c85e382b58`
> 原始链接: https://www.notion.so/4303c31a89f74fe99a9163c85e382b58

# Sprint 4.1 执行卡 · 标准化解决方案包（H90-H105）

> 🎯 **Sprint 4.1 唯一目标：** 15 小时内把 Phase 1-3 的产出标准化成「可复制交付包」：
《机器人研发 AI 化导入手册》+ 模板库 + 工具清单 + 交付流程。

## Sprint 4.1 验收清单（H105 检查）

- [ ] 《机器人研发 AI 化导入手册》初版（≥30 页等量内容：Notion/Markdown/PDF 任一）

- [ ] 5 份模板齐全：数据门禁报告模板、部署体检报告模板、VLA 复盘模板、调度闭环评估表、工作坊交付清单

- [ ] 解决方案包报价与边界条件明确（¥5-10 万/单示例）

- [ ] 至少 1 个脱敏案例贯穿全手册（从痛点→工具→结果）

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练成“标准化交付工厂”。** Sprint 4.1 的核心是模板化与一致性，这最适合练 Hooks（门禁化一致性）+ Team（Auditor 抓矛盾）。

### A. Task（任务拆解）

```plain text
进入 Task 模式：把 Sprint 4.1 拆成 6-8 个任务（handbook 大纲→五大闭环章节→模板库→SOW/报价→案例贯穿→一致性审计）。
每个任务给产物与验收方式（目录/字数/是否可复制）。输出完停下。
```

### B. Team（Builder/Auditor/Writer）— 强制“先审再写”

```plain text
按 Team 输出：
1) Builder：handbook 目录与每章要引用的模板
2) Auditor：列出最可能不一致的地方（术语/定价/交付物）并给统一词表
3) Writer：开始生成正文（按章节逐个生成，不要一次性铺满）
每个角色输出后停下。
```

### C. Hooks（门禁化）— 术语表与一致性检查

要求新增 `docs/solution-pack/glossary.md`（术语表），并用 Auditor 扫描整包是否一致。

```plain text
请生成 docs/solution-pack/glossary.md：列出核心术语（数据门禁/部署体检/VLA复盘/技能调度等）的统一定义。
然后进入 Auditor：扫描 docs/solution-pack/ 下所有文件，找出同一概念不同叫法并统一，输出替换清单。
```

### D. Spec-first（先模板后正文）

先做 templates/，再写 handbook。每个章节必须引用至少 1 个模板（链接/路径）。

### E. Diff 驱动审查（全包一致性）

```plain text
请进入 Auditor：对 docs/solution-pack/ 做一致性审计（术语/定价/交付物/闭环命名），输出替换清单，并给出一次性 replace 方案。
```

### F. Release discipline（交付包版本）

- `docs/solution-pack/handbook.md` 标记 v0.1

- `pricing-and-sow.md` 标记有效期

### G. Prompt library（解决方案包提示词库）

新增 `docs/prompts/sprint-4.1.md`：

- handbook 生成 prompt

- 模板生成 prompt

- 一致性审计 prompt

---

## ⚡ CC CLI：Sprint 4.1 主提示词（手册与模板库）

```plain text
你现在处于 Sprint 4.1：标准化解决方案包。禁止写新功能代码（最多修文档引用）。

请在 docs/solution-pack/ 下生成：

1) docs/solution-pack/handbook.md
- 结构：
  - 方案定位与适用范围
  - 五大闭环地图（数据/部署/运维/VLA/应用执行）
  - 每个闭环：痛点→诊断→工具→交付物→验收指标
  - 典型落地路线（2周/4周/8周）
  - 风险与合规

2) docs/solution-pack/templates/
- data-quality-report-template.md
- deployment-health-report-template.md
- vla-training-review-template.md
- skill-orchestration-eval-template.md
- workshop-deliverables-template.md

3) docs/solution-pack/pricing-and-sow.md
- 报价分档 + SOW 范围边界 + 客户需要准备什么

要求：
- 不能编造数据；示例用“占位符 + 说明”
- 模板要可直接复制给客户

完成后输出：
A. 目录树
B. handbook 的章节目录

最后：git add -A && git commit -m "docs: Sprint 4.1 标准化解决方案包" && git push
```
