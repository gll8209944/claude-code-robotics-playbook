> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `01fd3e12-7c67-4361-899a-fbaf65b2f1cf`
> 原始链接: https://www.notion.so/01fd3e127c674361899afbaf65b2f1cf

# Sprint 3.2 执行卡 · 第一家机器人公司工作坊（H72-H90）

> 🎯 **Sprint 3.2 唯一目标：** 18 小时内完成「机器人公司专项工作坊」的可交付化：
形成 2 天工作坊大纲 + 讲义 + 实操 Demo + 报价单，并完成至少 3 个潜在客户触达与 1 个明确意向（含时间/预算/决策人）。

## Sprint 3.2 验收清单（H90 检查）

- [ ] 2 天工作坊大纲（按小时颗粒度）

- [ ] 3 套可复用实操 Demo（数据门禁 / 部署体检 / VLA 复盘 / 调度闭环选四其三）

- [ ] 工作坊交付物清单（学员带走什么）

- [ ] 报价单与三档方案（¥19,800 / ¥29,800 / ¥49,800 示例）

- [ ] 获客物料：一页 PDF/Notion 产品页 + 3 条对外文案

- [ ] 触达 ≥ 10 人，且 ≥ 1 个明确意向（记录在 CRM/Notion）

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 练成“交付产品经理”。** Sprint 3.2 的本质是：把能力翻译成企业能买的交付。你要练 Team（分脑写作）+ Hooks（一致性门禁）。

### A. Task（任务拆解）— 工作坊也要工程化

```plain text
进入 Task 模式：把 Sprint 3.2 拆成 6-8 个任务（大纲→交付物→报价→onepager→触达→意向记录）。
每个任务必须包含产物文件与验收标准。输出完停下。
```

### B. Team（三角色流水线）— 防止“课程腔”

```plain text
按 Team 输出并停顿：
1) Builder：交付结构（两天大纲与每个模块产出）
2) Auditor：找出所有“空泛承诺/没有边界条件/无法验收”的地方并修正
3) Writer：输出最终 onepager + 3 条触达文案
```

### C. Hooks（门禁化）— 价格/交付/边界一致性

```plain text
请进入 Auditor：检查 outline/deliverables/pricing/onepager 四份文件中，定价、人数、交付物、准备周期是否一致；输出不一致表格并给出统一版本。
```

### D. Spec-first（先交付合同）

先输出一个“可签约 SOW 摘要表”：

- 交付物、验收方式、客户需准备、风险/排除项

### E. Diff 驱动审查（销售物料一致性）

对 outline/deliverables/pricing/onepager/outreach 做一次统一审计 diff。

### F. Prompt library（工作坊销售资产化）

新增 `docs/prompts/sprint-3.2.md`：

- onepager 生成 prompt

- 报价与边界 prompt

- 私聊推进 prompt

### G. Release discipline（对外可发版本）

在 H90 完成时：给 onepager 标记 v0.1，并记录适用范围与不适用范围。

---

## ⚡ CC CLI：Sprint 3.2 主提示词（工作坊产品化）

```plain text
你现在处于 Sprint 3.2：第一家机器人公司工作坊产品化。禁止写新功能代码（最多修演示 bug）。

请在 docs/workshop/ 下生成以下内容（中文，偏交付型）：

1) docs/workshop/outline-2days.md
- 2 天工作坊按小时排程
- 每个模块：目标、输入材料、讲解要点、实操任务、产出物

2) docs/workshop/deliverables.md
- 客户能带走的交付物清单（模板、报告、检查清单、脚本、复盘方法）

3) docs/workshop/pricing.md
- 三档报价（基础/标准/企业）
- 每档包含什么、不包含什么、准备周期

4) docs/workshop/onepager.md
- 一页式产品页（可直接发给客户）

5) docs/workshop/outreach-messages.md
- 3 种触达文案：老朋友私聊/飞书群/邮件

要求：
- 每个模块都必须绑定“数据/部署/运维/VLA/应用执行”闭环之一
- 用词克制，不要课程腔

完成后输出：
A. 文件列表 + 字数
B. 你建议我用哪 2 个 demo 作为工作坊主轴？为什么？

最后：git add -A && git commit -m "docs: Sprint 3.2 工作坊产品化物料" && git push
```

---

## 触达记录模板（复制到 Notion/表格）

```markdown
客户/联系人：
公司：
角色：
痛点闭环（数据/部署/运维/VLA/应用执行）：
预算范围：
预期时间：
下一步动作：
证据（聊天截图/邮件）：
```
