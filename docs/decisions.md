# Sprint 1.1 决策记录

> 本文件记录 Sprint 1.1 的关键拍板决策，供后续 Sprint 回顾和新人 onboarding 参考。

---

## 仓库与可见性

| 决策项 | 拍板值 |
|---|---|
| 仓库名 | `claude-code-robotics-playbook` |
| 可见性 | **公开**（GitHub public） |
| 仓库 URL | https://github.com/gll8209944/claude-code-robotics-playbook |
| GitHub 用户 | gll8209944 |

---

## 数据集策略

| 决策项 | 拍板值 |
|---|---|
| 冒烟测试数据集 | `lerobot/pusht`（< 100 MB，1 分钟下完） |
| **主推数据集** | `lerobot/svla_so100_pickplace`（~1-2 GB，SO-100 真实机械臂 + 多视角 + pick-place） |
| 双臂备选 | `lerobot/aloha_static_coffee` |
| 低成本叙事备选 | `lerobot/koch_pick_place_lego` |
| 下载路径 | 阿里云 ECS → rsync 回 Mac（比 Mac 直连 hf-mirror 快 3-5×） |

---

## Claude Code 入口

| 决策项 | 拍板值 |
|---|---|
| 入口形式 | **CLI**（`claude` 命令，非 IDE 插件） |
| 启动目录 | 仓库根目录 |
| 会话策略 | 一个会话打透 `demos/data-quality-gate`，不开多个并发会话 |

---

## 录屏工具

| 决策项 | 拍板值 |
|---|---|
| 录屏工具 | **Kap**（Mac 原生，轻量，支持导出 GIF/MP4） |
| 备用录屏 | QuickTime / OBS |
| 适用场景 | 技术 Demo 录屏（iPhone 录屏分辨率/字号不适合技术演示） |

---

## 联系方式

| 渠道 | 值 |
|---|---|
| 飞书 | 13738170552 |
| 微信 | 13738170552 |
| 邮箱 | gll8209944@hotmail.com |

---

## 质量门禁阈值（拍板版）

| 指标 | strict 阈值 | loose 阈值 |
|---|---|---|
| 帧率标准差 / 均值 | < 5% | < 10% |
| 缺帧率 | < 1% | < 3% |
| 多视角时间戳最大偏移 | < 50 ms | < 100 ms |
| 任务标签缺失率 | 0% | < 2% |
| 异常帧（黑屏 / 模糊）比例 | < 0.5% | < 2% |

---

## 数据四级标准（强制规范）

| 级别 | 含义 | 进入条件 |
|---|---|---|
| raw | 原始采集 | 落盘即为 raw |
| validated | 通过 data-quality-gate | 帧率一致性 / 缺帧率 / 多视角时间戳偏移 / 任务标签完整性全部通过 |
| curated | 人工抽查 + 标签精修 | validated 基础上人工确认任务描述准确、视角覆盖完整 |
| training | 可进入 VLA 训练 | curated 基础上写入 dataset card（版本号、采集时间、任务清单、已知缺陷） |

**铁律：未经 validated 的数据禁止直接用于模型训练或对外演示。**

---

## 当前 Sprint 不做的事

- 不做通用 Claude Code 教学
- 不做大而全课程
- 不在 `demos/data-quality-gate` 之外的目录写代码（Sprint 明确切换前）
- 不引入 lerobot / pandas / numpy / pyarrow / opencv-python / jsonschema / pytest / rosbags 之外的依赖

---

## 拍板时间

- 拍板人：待填（所有者）
- 拍板时间：2026-04-26（Sprint 1.1 H0）
- 下次回顾：Sprint 1.4 结束（H24）
