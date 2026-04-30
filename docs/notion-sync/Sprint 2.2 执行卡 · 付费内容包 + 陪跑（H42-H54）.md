> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `6b9df32d-2f9d-430f-8122-4fe35cca269b`
> 原始链接: https://www.notion.so/6b9df32d2f9d430f81224fe35cca269b

# Sprint 2.2 执行卡 · 付费内容包 + 陪跑（H42-H54）

> 🎯 **Sprint 2.2 唯一目标：** 12 小时内把 Sprint 2.1 的 4 个 Skill 打包成 **可售卖的付费内容包**（4 集 Demo 合集 + 文档 + 录屏），并启动 **订阅/陪跑**的最小闭环（能收款/能交付/能复购）。

## Sprint 2.2 验收清单（H54 检查）

- [ ] 4 集 Demo 合集目录完备（每集：目标/输入/步骤/输出/常见坑/复盘）

- [ ] 至少 2 集有录屏（GIF/MP4）

- [ ] 订阅/会员页（或知识库/星球）已搭建并能完成支付路径

- [ ] 陪跑产品说明明确：周期 1 月、每周节奏、交付物、边界条件

- [ ] 至少触达 10 个潜在用户/客户，并完成 ≥1 个付费转化（哪怕 ¥199 也算）

---

## 交付物结构（建议）

```plain text
docs/paid-pack/
├── README.md
├── episode-01-data-quality-gate.md
├── episode-02-ros2-debug-assistant.md
├── episode-03-fleet-health-checker.md
├── episode-04-vla-experiment-manager.md
├── assets/            # GIF/截图
└── sales/
    ├── pricing.md
    ├── faq.md
    └── launch-post.md
```

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练成“内容与销售流水线”。** Sprint 2.2 的核心是写作与销售物料，最适合练 Team（分脑）+ Hooks（避免空泛/避免编造）。

### A. Task（任务拆解）— 让写作也工程化

```plain text
进入 Task 模式：把 Sprint 2.2 拆成 6-8 个任务（大纲→四集写作→销售物料→触达→复盘）。
每个任务必须给：产物文件路径、字数目标、验收方式（wc/是否引用真实样例）。输出完停下。
```

### B. Team（三角色流水线）— 强制禁止“教程腔”

- Builder：只负责“目录结构与引用真实素材位置”

- Auditor：专门抓“空泛承诺/编造数字/没边界条件”

- Writer：写最终文案

可直接贴：

```plain text
请按 Team 三角色输出并停顿：
1) Builder：docs/paid-pack/ 的目录结构与每个文件要引用哪些真实输出（samples/reports 的路径）
2) Auditor：列出你最可能编造/夸大/写成课程腔的 10 个点，并逐条给规避策略
3) Writer：输出最终四集内容包与三条发布文案
```

### C. Hooks（门禁化）— “禁止编造”检查

写完后强制跑一次 Auditor 门禁：

```plain text
请进入 Auditor：逐文件扫描“编造风险”。凡是出现具体数字/对比/案例但无法引用仓库真实文件，请标红并改成占位符+说明。输出修改表（文件:行号 → 修改建议）。
```

### D. Spec-first（先目录后正文）

写作前必须先输出：

- 4 集大纲（每集 10-15 行）

- 每集要引用的真实素材路径（samples/reports）

### E. Diff 驱动审查（写作一致性）

```plain text
请进入 Auditor：检查四集的结构是否一致（标题、字段、示例引用、限制说明），不一致就给出统一改写建议。
```

### F. Prompt library（内容包资产化）

新增 `docs/prompts/sprint-2.2.md`：

- 写作 prompt

- “禁止编造”审计 prompt

- 发布文案 prompt

### G. Release discipline（可发布版本）

Sprint 2.2 完成后：

- `docs/paid-pack/README.md` 标记版本 v0.1

- `docs/paid-pack/sales/pricing.md` 标记有效期与边界

---

## ⚡ CC CLI：Sprint 2.2 主提示词（内容包写作 + 销售物料）

```plain text
你现在处于 Sprint 2.2：付费内容包 + 陪跑。禁止写新功能代码（可修小 bug）。

请在 docs/paid-pack/ 下产出以下内容（中文）：

1) 四集 Demo 合集（每集一份 md）：
- episode-01-data-quality-gate.md
- episode-02-ros2-debug-assistant.md
- episode-03-fleet-health-checker.md
- episode-04-vla-experiment-manager.md

每集必须包含：
- 这一集解决什么真实痛点
- 前置条件与输入材料
- 运行步骤（命令行级别）
- 输出示例（引用仓库 samples/ 或 reports/ 的真实内容，禁止编造）
- 失败/异常时怎么排查
- “这一集能帮团队省下什么”（时间/返工/风险）

2) 销售物料：docs/paid-pack/sales/
- pricing.md：定价与三档方案（年订阅/早鸟/企业版），含交付物清单
- faq.md：至少 15 个常见问题（适配机器人团队）
- launch-post.md：发布文案（朋友圈/飞书群/知乎三种版本）

要求：
- 语气偏工程交付，不要课程腔
- 所有卖点必须落到“结果/指标/风险降低”

完成后输出：
A. 文件清单 + 字数统计
B. 你建议的最小收费路径（1-2 句话）

最后：git add -A && git commit -m "docs: Sprint 2.2 付费内容包与销售物料" && git push
```

---

## H42-H54 执行节奏（建议时间箱）

- 2h：梳理目录 + 写四集大纲

- 6h：每集写作 + 插入真实输出样例

- 2h：销售物料（pricing/faq/launch）

- 2h：触达 + 成交（至少 10 人）

---

## 复盘模板

```markdown
Sprint 2.2 复盘
- 最有效的获客渠道：
- 最容易成交的产品档位：
- 用户最关心的 3 个问题：
- 下阶段（Phase 3）需要补强的案例：
```
