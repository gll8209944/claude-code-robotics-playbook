> 自动同步自 Notion，同步时间: 2026-04-30
> 页面 ID: `6bdcc984-1cd0-4bca-b1c4-413749d4bd41`
> 原始链接: https://www.notion.so/6bdcc9841cd04bcab1c4413749d4bd41

# Sprint 1.3 执行卡 · vla-training-review（H12-H18）

> 🎯 **Sprint 1.3 唯一目标：** 6 小时内交付一份「VLA 训练复盘报告生成器」最小 Demo：输入一份真实/脱敏训练日志（+ 配置/指标），输出 **复盘结论 + 可执行的下一轮调参建议**（JSON + Markdown 双份）。同时启动第二个机器人 MCP：`robot-config-manager`（对接 RCMS 的最小版本）。

## Sprint 1.3 验收清单（H18 检查）

- [ ] `vla-training-review` 在 1 份真实/脱敏训练日志上跑通，输出 **review_report.json + review_**[**report.md**](http://report.md/)

- [ ] 复盘报告包含：训练概览、关键曲线/指标摘要、3 个异常点与证据、下一轮实验建议（含具体参数/改动点）、风险与假设

- [ ] 启动第二个机器人 MCP：`robot-config-manager` 最小可用版（stdio 模式），至少 2 个 tool 可用

- [ ] 第三篇文章草稿完成（≥2000 字）：《用 Claude Code 给一次 VLA 训练做复盘：发现了三件人不会注意到的事》

- [ ] GitHub 仓库 `demos/vla-training-review/` + `mcp-servers/robot-config-manager/` 已提交（含 README + 最小测试）

---

## 🖥️ 设备角色分工（沿用 1.1/1.2）

> ⚡ **加速原则：** 让 Claude Code CLI 做 80%：建脚手架、写解析器、写报告模板、写文章草稿、生成自检审计表。你只做 20%：提供日志样本、拍板关键假设、审 diff、确认建议是否可信。

| 设备 | Sprint 1.3 角色 | 具体承担 |
| --- | --- | --- |
| **Mac** ⭐ | CC CLI 主会话 + 录屏 + 写作 | 代码生成 / Git 提交 / 生成报告 / 文章草稿 / Kap 录屏 |
| **阿里云 ECS** | 日志后台 + 批量跑报告 | 保存脱敏日志、跑长任务解析、将报告 commit 回仓库（Mac 只拉报告） |
| （可选）无影 Ubuntu | 备用 Linux 沙箱 | 当某些依赖在 Mac 上装不动时兜底 |
| iPhone / iPad | 审稿 + 发文 | 审报告、发文章、客户响应 |

---

## ⭐ Claude Code CLI 顶尖高手训练（本 Sprint 强制融入）

> 🧠 **目标：把 CC CLI 从“写代码工具”升级为“工程流水线操作系统”。** 本 Sprint 你不只交付 demo，还要交付一套可复用的 CC CLI 工作法。

### A. Task（任务拆解）— 开工第 1 条指令（必须执行）

在仓库根目录启动 `claude` 后，先贴这段，把本 Sprint 拆成 5-9 个可验收任务；**拆完再写任何代码**：

```plain text
进入 Task 模式：把我接下来的目标拆成 5-9 个可执行任务，每个任务必须包含：
- 输出产物（文件/命令/报告/录屏）
- 验收标准（用命令验证）
- 预计时间（分钟）
- 失败兜底（降级版本）

目标：Sprint 1.3 — VLA 训练复盘最小 Demo + robot-config-manager MCP
约束：不引入新依赖；单文件<200行；必须双份报告（json+md）
输出格式：编号列表；最后给出“建议我先做哪 1 个任务”

输出完请停下，等待我确认。
```

### B. Team（角色流水线）— 每个里程碑都跑一遍

对每个里程碑（parser/checks/reporter/MCP/文章）都走一遍三角色，避免混脑：

```plain text
我们用 Team 流水线做这件事。请按 3 个角色依次输出（不要混在一起）：

1) Builder：给出实现方案 + 文件清单 + 关键接口（先不写代码）
2) Auditor：列出你将如何证明自己没违规（依赖/范围/测试/报告字段/退出码），以及你最担心的 3 个风险
3) Writer：用 120 字写对外卖点，并列出 3 个可演示截图/录屏点位

每个角色输出后停下，等我确认再继续。
```

### C. Hooks（门禁化自检）— 本 Sprint 必须落地一个“提交前体检”脚本

你将把 [CLAUDE.md](http://claude.md/) 的行为准则变成自动门禁：

- 在仓库新增：`scripts/preflight.sh`

- 规则：commit 前必须跑过；失败则禁止提交

让 CC CLI 生成的指令（在实现完成后贴）：

```plain text
请在 scripts/ 下创建 preflight.sh（可执行），用于提交前门禁。要求：
1) pytest -q
2) JSON Schema 校验（如无 jsonschema CLI，用 python -m jsonschema）
3) 行数门禁：任一 .py >200 行则失败（仅检查 demos/vla-training-review 与 mcp-servers/robot-config-manager）
4) 范围门禁：本 Sprint 只允许改动 demos/vla-training-review、mcp-servers/robot-config-manager、以及 CLAUDE.md 追加；否则失败
5) 依赖门禁：扫描 import，与 requirements.txt 对比，发现新增依赖则失败并列出
6) 输出清晰的 PASS/FAIL 摘要

完成后给我：
A. cat scripts/preflight.sh
B. 演示一次通过与一次失败（用 echo 模拟即可）
禁止引入新依赖。
```

---

## ⭐ CC CLI 进阶覆盖（本 Sprint 额外强制）

### D. Spec-first（先契约后实现）— 每个模块先出 schema + 示例

在写 parser/check/reporter/MCP 任何代码之前，先让 CC 输出并让你确认：

- `input.schema.json` / `output.schema.json`

- `samples/` 的最小样例输入与预期输出（允许占位符，但要写清楚）

可直接贴：

```plain text
先不要写实现代码。请先输出“接口契约包”：
1) run_review.py 的 CLI 参数与退出码表
2) review_report.json 的 JSON Schema（字段+类型+必填）
3) review_report.md 的标题结构（必须覆盖 7 个问题）
4) synthetic_min 的样例输入（train.log/metrics.csv/config.yaml）与预期输出摘要

输出完停下，等我确认后再写实现。
```

### E. Diff 驱动审查（人类把关）— 关键文件必须先 diff 再 commit

关键文件：`CLAUDE.md`、所有 `*.schema.json`、`templates/*.md`、`scripts/preflight.sh`。

规则：任何一次改动这些文件，都必须先执行：

```plain text
请输出 git diff，并逐文件解释：你为什么这么改？它满足了哪条规范？有什么潜在副作用？
```

你确认后才能 `git commit`。

### F. Test engineering（合成样本驱动）— 必须覆盖缺失输入与异常触发

除 happy path 外，必须有：

- 缺少 metrics/config 的降级测试（退出码=1 或报告标注 N/A）

- divergence/overfit/throughput 至少 2 个异常触发测试

Auditor 指令：

```plain text
请列出 tests/ 覆盖矩阵：每个 check 覆盖 PASS/WARN/FAIL 的哪些 case？缺哪个？给出要补的最小 fixture。
```

### G. Observability（证据可解释）— 报告必须带 Evidence snippets

要求在 `review_report.md` 固定一个附录：

- 证据摘录（日志行/step 区间/关键指标窗口）

- 每条建议必须引用至少 1 条证据

### H. Release discipline（可回滚版本点）— Sprint 完成打 tag

本 Sprint 完成并通过 preflight 后：

- `git tag sprint-1.3-v0.1`（或同等命名）

- `docs/decisions.md` 追加：输入格式假设、退出码语义、已知限制

### I. Prompt library（提示词资产化）— 把本 Sprint 最有效 prompts 沉淀到仓库

新增：`docs/prompts/sprint-1.3.md`，至少包含：

- Task 拆解 prompt

- Team 三角色 prompt

- Auditor 自检表 prompt

### J. Multi-env orchestration（Mac↔ECS）— 生成一键跑脚本

让 CC 生成（不引入依赖）：

- `scripts/run_review_on_ecs.sh`：push→ECS pull→run→commit reports→push

- `scripts/pull_reports.sh`：Mac 拉回 reports

---

## H12-H13：1 小时准备清单（5 步）

### Step 1（10 min）：确定“输入素材”格式（必须拍板）

> 📌 **Sprint 1.3 成败取决于输入素材。** 先别写代码，先把你能拿到的训练日志形态定死。

请从下面三类中选 **至少 1 类**（越多越好，但别拖）：

- **A. 训练日志文本**：如 `train.log`（含 step/iter、loss、lr、grad_norm、throughput、eval 指标）

- **B. 指标文件**：如 TensorBoard 导出的 `metrics.csv` / `events.out.tfevents*` / W&B 导出 CSV

- **C. 配置文件**：如 `config.yaml` / Hydra 配置 / 命令行参数 / 模型与数据版本信息

最小可用输入（建议）：

- `train.log` + `config.yaml` + `metrics.csv`（或 W&B 导出）

### Step 2（10 min）：在仓库中创建 Sprint 1.3 目录树

```bash
cd ~/work/claude-code-robotics-playbook
mkdir -p demos/vla-training-review/{scripts,parsers,checks,schemas,reports,tests,samples,templates,input_samples}
mkdir -p demos/vla-training-review/input_samples/{real_sanitized,synthetic_min}
mkdir -p mcp-servers/robot-config-manager/{tests,samples}
```

### Step 3（15 min）：准备“真实/脱敏日志”与“合成最小样本”

> 🛡️ **隐私/保密策略：** 真实日志放 `input_samples/real_sanitized/` 只保留脱敏版本；任何公司内部路径、IP、key、SN 号必须替换为 `<REDACTED>`。

建议你准备两个样本：

1) **real_sanitized**：你手里的一份真实训练日志（脱敏）

2) **synthetic_min**：你手写/AI 生成的最小日志（30-60 行），用于单测和跑通脚手架

### Step 4（10 min）：追加 Sprint 1.3 的 [CLAUDE.md](http://claude.md/) 规范（只追加，不改旧内容）

（沿用本卡原有追加段落）

### Step 5（15 min）：准备 Kap/QuickTime 录屏（可选但建议）

录 30-60 秒：运行 `run_review.py` → 输出 `review_report.md` 头部（能看到“3 个异常点 + 3 个建议”）

---

## ⚡ Sprint 1.3 的 CC CLI 主提示词（直接复制粘贴）

（沿用本卡原有主提示词 + 自检审计 + 文章提示词）

---

## H18 复盘模板（完成后填写）

```markdown
本 Sprint：Sprint 1.3（H12-H18）
最重要成果：
工作提效指标（哪一步更快/更稳）：
内容/获客动作：
收入：
最大卡点：
下个 Sprint 唯一主线：Sprint 1.4（首笔收入 + 路线校准）
```
