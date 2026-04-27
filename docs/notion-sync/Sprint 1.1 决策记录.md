<!--
  自动同步自 Notion
  同步时间: 2026-04-27 13:50:57
  页面 ID: 34ea4400-33e1-8112-967f-d2ca2fc89bd8
  原始链接: https://www.notion.so/34ea440033e18112967fd2ca2fc89bd8
-->

# Sprint 1.1 决策记录

> 本文件记录 Sprint 1.1 的关键拍板决策，供后续 Sprint 回顾和新人 onboarding 参考。
---
## 仓库与可见性
```plain text
| 决策项 | 拍板值 |
|---|---|
| 仓库名 | `claude-code-robotics-playbook` |
| 可见性 | **公开**（GitHub public） |
| 仓库 URL | https://github.com/gll8209944/claude-code-robotics-playbook |
| GitHub 用户 | gll8209944 |
```
---
## 数据集策略
```plain text
| 决策项 | 拍板值 |
|---|---|
| 冒烟测试数据集 | `lerobot/pusht`（< 100 MB，1 分钟下完） |
| **主推数据集** | `lerobot/svla_so100_pickplace`（~1-2 GB，SO-100 真实机械臂 + 多视角 + pick-place） |
| 双臂备选 | `lerobot/aloha_static_coffee` |
| 低成本叙事备选 | `lerobot/koch_pick_place_lego` |
| 下载路径 | 阿里云 ECS → rsync 回 Mac（比 Mac 直连 hf-mirror 快 3-5×） |
```
---
## Claude Code 入口
```plain text
| 决策项 | 拍板值 |
|---|---|
| 入口形式 | **CLI**（`claude` 命令，非 IDE 插件） |
| 启动目录 | 仓库根目录 |
| 会话策略 | 一个会话打透 `demos/data-quality-gate`，不开多个并发会话 |
```
---
## 录屏工具
```plain text
| 决策项 | 拍板值 |
|---|---|
| 录屏工具 | **Kap**（Mac 原生，轻量，支持导出 GIF/MP4） |
| 备用录屏 | QuickTime / OBS |
| 适用场景 | 技术 Demo 录屏（iPhone 录屏分辨率/字号不适合技术演示） |
```
---
## 联系方式
```plain text
| 渠道 | 值 |
|---|---|
| 飞书 | 13738170552 |
| 微信 | 13738170552 |
| 邮箱 | gll8209944@hotmail.com |
```
✅ 已锁定（2026-04-26 H4）
---
## 质量门禁阈值（拍板版）
```plain text
| 指标 | strict 阈值 | loose 阈值 |
|---|---|---|
| 帧率标准差 / 均值 | < 5% | < 10% |
| 缺帧率 | < 1% | < 3% |
| 多视角时间戳最大偏移 | < 50 ms | < 100 ms |
| 任务标签缺失率 | 0% | < 2% |
| 异常帧（黑屏 / 模糊）比例 | < 0.5% | < 2% |
```
---
## 数据四级标准（强制规范）
```plain text
| 级别 | 含义 | 进入条件 |
|---|---|---|
| raw | 原始采集 | 落盘即为 raw |
| validated | 通过 data-quality-gate | 帧率一致性 / 缺帧率 / 多视角时间戳偏移 / 任务标签完整性全部通过 |
| curated | 人工抽查 + 标签精修 | validated 基础上人工确认任务描述准确、视角覆盖完整 |
| training | 可进入 VLA 训练 | curated 基础上写入 dataset card（版本号、采集时间、任务清单、已知缺陷） |
```
铁律：未经 validated 的数据禁止直接用于模型训练或对外演示。
---
## 当前 Sprint 不做的事
- 不做通用 Claude Code 教学
- 不做大而全课程
- 不在 demos/data-quality-gate 之外的目录写代码（Sprint 明确切换前）
- 不引入 lerobot / pandas / numpy / pyarrow / opencv-python / jsonschema / pytest / rosbags 之外的依赖
---
## 🔍 关键发现 & 文章素材
### 发现 1：so100_pickplace 多视角「幽灵目录」（2026-04-26 H4）
**现象：** so100_pickplace 数据集目录结构声称含多视角（`observation.images.top` / `observation.images.wrist`），但实际 parquet 中**未存储对应图像数据字段**。`multiview_sync` 检查走了单视角跳过路径，结果为 ✅。
**根因：** 元数据（目录名/文件结构）与实际数据内容（parquet schema）不一致。这是 LeRobot 社区数据集常见的质量隐患 — 采集管线创建了多视角目录，但写入流程只落盘了部分视角。
**启示（3 条）：**
1. **门禁通过 ≠ 数据完美** — 当前 5 项检查覆盖的是「数据本身的质量」，但没有覆盖「元数据与数据的一致性」。这恰好说明了四级标准的必要性：validated 只是第一道防线，curated 阶段才由人工确认视角覆盖完整性。
1. **Sprint 1.2 新增检查项 **`**metadata_consistency**` — 检查目录结构声称的视角数 vs parquet 实际列数、info.json features vs parquet schema 对齐。声称多视角但实际单视角 → 报 ⚠️ 警告。
1. **文章「故事弧」素材** — 「5 项全绿但仔细一看发现幽灵目录」→ 引出「自动化是第一道防线，不是最后一道」→ 自然过渡到四级标准设计。这个故事比「全绿无 bug」有说服力得多。
**数据佐证：**
```plain text
pusht:           206 episodes, 7.2 MB, 单视角, strict 全通过
so100_pickplace: 50 episodes, 448.3 MB, 目录声称双视角/实际单视角, strict 全通过
两份数据集 5 项指标完全一致（均为 0.0%），无显著差异
```
---
## 拍板时间
- 拍板人：待填（所有者）
- 拍板时间：2026-04-26（Sprint 1.1 H0）
- 下次回顾：Sprint 1.4 结束（H24）