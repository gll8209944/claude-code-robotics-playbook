# 我用 Claude Code 给机器人数据采集加了一道质量门禁 — 5个公开数据集横评实录

## 痛点引入

机器人数据采集是 VLA（Vision-Language-Action）模型训练的第一道关口。HuggingFace 上有大量开源的机器人数据集，从 `pusht` 到 `so100` 再到 `aloha`，看起来都很"干净"——官方提供的 demo 视频流畅、标签完整、帧率稳定。但实际上，**大量团队直接拿这些数据喂进训练 pipeline，从不做任何质量校验**。

我做了一件事：写了一道数据质量门禁，在 5 个公开 LeRobot 数据集上跑了一遍。结果让人意外——

> **官方精选数据集在帧率/缺帧/标签等基础指标上全部通过，但在异常帧检测上，5 个数据集全军覆没，全部低于 strict 阈值（< 0.5%）。**

本文记录了这套门禁系统的设计思路、5 个数据集的真实横评结果，以及我发现的那个差点让我在文章里闹笑话的 bug。

<!-- IMG: demo.gif 插入位置：文章封面，展示门禁运行输出的终端动画 -->

## 我做了什么

用 Claude Code CLI，在 **6 小时**内从零生成了一套完整的数据质量门禁系统：

- **4 个检查模块**：帧率一致性、缺帧率、多视角时间戳同步、任务标签完整性
- **异常帧检测（A类 + B类）**：动作跳变/冻结帧（parquet）+ 黑屏/模糊/曝光帧（视频）
- **双引擎解码**：cv2 优先 + ffmpeg fallback（AV1 codec 专用）
- **双份报告**：JSON（机器消费）+ Markdown（人读）
- **strict / loose 两套阈值配置**

代码全部在 GitHub：`claude-code-robotics-playbook/demos/data-quality-gate`

## 门禁设计思路

### 五项检查指标的选择逻辑

| 指标 | 为什么重要 | strict 阈值 | loose 阈值 |
|---|---|---|---|
| 帧率标准差/均值 | 帧率不稳定导致 action 时序错位 | < 5% | < 10% |
| 缺帧率 | 丢帧直接造成机器人动作空洞 | < 1% | < 3% |
| 多视角时间戳偏移 | 多视角数据偏移导致状态估计错误 | < 50ms | < 100ms |
| 任务标签缺失率 | 标签不全是 VLA 训练大忌 | 0% | < 2% |
| 异常帧比例 | 模糊/黑屏帧破坏视觉特征学习 | < 0.5% | < 2% |

### 数据四级标准

所有数据必须经过这道门禁才能"升级"：

```
raw → validated → curated → training
```

- **raw**：原始采集数据，落盘即为 raw
- **validated**：通过全部 5 项质量检查
- **curated**：validated 基础上人工确认任务描述准确、视角覆盖完整
- **training**：curated 基础上写入 dataset card（版本号、采集时间、任务清单、已知缺陷）

铁律：**未经 validated 的数据禁止直接用于模型训练或对外演示。**

### A类 vs B类异常帧

- **A类（parquet 数据）**：动作跳变帧（action vector 的 L2 范数突增 3σ 以上）、冻结帧（连续 5 帧以上相同）
- **B类（视频数据）**：黑屏帧（灰度均值 < 5）、模糊帧（Laplacian 方差 < 50）、曝光异常帧（帧均值偏离均值 3σ 以上）

## 5 数据集横评实录

> 所有数据来自真实门禁运行，非编造。数据集分别来自 HuggingFace LeRobot 组织及社区上传。

### 五项指标总表

| 数据集 | 帧率CV | 缺帧率 | 多视角偏移 | 标签缺失率 | 异常帧率 | 总评 |
|---|---|---|---|---|---|---|
| pusht | 0.001% ✅ | 0.0% ✅ | N/A（单视角）| 0.0% ✅ | **1.559%** ❌ | strict FAIL |
| so100 | 0.001% ✅ | 0.0% ✅ | 0.0ms ✅ | 0.0% ✅ | **1.951%** ❌ | strict FAIL |
| koch | 0.004% ✅ | 0.0% ✅ | N/A | 0.0% ✅ | **1.626%** ❌ | strict FAIL |
| aloha | 0.003% ✅ | 0.0% ✅ | N/A | 0.0% ✅ | **1.085%** ❌ | strict FAIL |
| columbia | 0.001% ✅ | 0.0% ✅ | N/A | 0.0% ✅ | **4.222%** ❌ | strict FAIL |

**如果用 loose 阈值（< 2%）：全部通过。**

### 好数据代表：pusht

`pusht` 是 LeRobot 最经典的数据集，2D 推 T 字块任务，206 episodes，25,650 帧。

| 指标 | 值 | 阈值 | 结果 |
|---|---|---|---|
| 帧率标准差/均值 | 0.001% | < 5% | ✅ |
| 缺帧率 | 0.0% | < 1% | ✅ |
| 任务标签缺失率 | 0.0% | 0% | ✅ |
| 异常帧率 | 1.559% | < 0.5% | ❌ |

异常帧分布（Top 5 episodes）：
- Episode 0：动作跳变 1 + 冻结 1
- Episode 1：动作跳变 2
- Episode 2：动作跳变 3 + 冻结 1
- Episode 3：动作跳变 3
- Episode 4：动作跳变 1

**分析**：pusht 的基础指标几乎完美，但异常帧率仍超出 strict 阈值 3 倍。异常类型 100% 为 A类（动作跳变 + 冻结），B类（黑/糊/曝光）均为 0。这说明 pusht 的帧率和标签都没问题，但**动作序列中存在偶发的跳变和短暂冻结**，可能是机械臂在目标点附近的微小抖动被记录了下来。

### 主推数据集 so100：差点让我在文章里出丑的 bug

`so100_pickplace` 是 SO-100 机械臂真实采集数据，50 episodes，19,631 帧，多视角（top + wrist）。

第一次跑门禁，**异常帧率显示 43.2%**——这个数字离谱到让我以为是代码写错了。

排查过程：

1. 单独跑 B类检测，blur 指标 800（几乎每帧都模糊）
2. 检查采样帧的 Laplacian 值：\[137, 17, 4, 7, 6, 63, 12, 8, 4, 116\]
3. 对比 wrist 摄像头（运动模糊正常）和 top 摄像头（固定安装，应该清晰）
4. **发现问题**：代码按文件名字母排序选中了 wrist 摄像头，而不是 top 摄像头

```python
# 修复前（bug）
mp4s = sorted(videos_dir.rglob("*.mp4"), key=lambda p: p.name)
# wrist < top，所以总是选 wrist

# 修复后
mp4s = sorted(videos_dir.rglob("*.mp4"), key=lambda p: ("wrist" in str(p), "left" in str(p), p.name))
# wrist/left 排到最后，top/base 优先
```

**修复后：so100 异常帧率从 43.2% 降至 1.951%**，全部为 A类（动作跳变 20 + 冻结 25），B类全 0。

这个 bug 的教训：**多摄像头数据集一定要明确选择策略，不能假设字母排序是对的。**

### koch：最大的数据集，最多的异常

`koch_bimanual_folding`，146,030 帧，116 个 episode 视频文件（AV1 编码），双臂折叠任务。

| 指标 | 值 | 阈值 | 结果 |
|---|---|---|---|
| 帧率CV | 0.004% | < 5% | ✅ |
| 缺帧率 | 0.0% | < 1% | ✅ |
| 异常帧率 | 1.626% | < 0.5% | ❌ |

异常分布：动作跳变 164 + 冻结 12 + 曝光异常 3 = 179（Top 5 episodes 合计）。koch 的帧率和缺帧都极好，说明采集硬件稳定，但动作跳变偏多（164），可能与双臂协同任务的复杂性有关——两个臂的动作可能在某些时刻不同步导致状态估计跳变。

### aloha：表现最好的异常帧率

`aloha_static_coffee`，ALOHA 双臂真实复杂任务，55,000 帧。

| 指标 | 值 | 阈值 | 结果 |
|---|---|---|---|
| 异常帧率 | 1.085% | < 0.5% | ❌（但最低）|

aloha 的异常帧率在 5 个数据集中最低（1.085%），且异常类型 100% 为动作跳变（74），无冻结、无 B类异常。这说明 aloha 的采集硬件和任务执行都非常稳定。

### columbia：曝光异常是特色

`columbia_cairlab_pusht_real`，真实机器人版 pusht（vs 仿真版），27,808 帧。

| 指标 | 值 | 阈值 | 结果 |
|---|---|---|---|
| 异常帧率 | **4.222%** | < 0.5% | ❌（最高）|

**columbia 是唯一一个以 B类曝光异常为主的数据集**（30帧曝光异常，分布在 Top 5 episodes 各 6 帧）。这说明 columbia 的相机硬件或光照环境存在周期性波动——可能是实验室灯光的交流电频率（50/60Hz）导致的频闪。

## 如果不做门禁直接训练会怎样

**对 VLA 训练的具体影响：**

- **动作跳变帧**：action vector 出现突变，模型可能学到错误的"瞬移"动作，特别是在 imitation learning 中这类帧会被直接复制进训练数据
- **冻结帧**：连续相同动作被模型解释为"保持"状态，但实际上可能是传感器故障或机械卡滞
- **曝光异常帧**：视觉特征被破坏，模型对光照变化的鲁棒性下降，在真实部署时容易失效

**columbia 的周期性曝光异常**尤其危险——如果这类帧进入训练，模型可能学到对灯光频闪的虚假相关性，而非真实的物体和动作特征。

## Claude Code 体验

整个门禁系统从设计到实现到 debug，全部在 Claude Code CLI 中完成。关键体验：

1. **自顶向下下达指令**：我只描述"需要什么"，Claude Code 生成代码并解释实现思路
2. **逐条审核 diff**：每次写文件我都检查是否有违规（如路径硬编码、超过 200 行等）
3. **ECS 远程执行**：代码在 Mac 写，数据在 ECS，通过 git 同步，Mac 只拉报告
4. **Bug 排查闭环**：so100 的 43.2% bug 是我自己分析出来的（看 Laplacian 分布），然后指示 Claude Code 修复

**最有用的一句魔法话**：
> 「请重新读一遍 CLAUDE.md，然后告诉我你刚才哪一步违反了行为准则」

这句话让 Claude Code 在高压生成后主动自我审计，抓出了"摄像头排序"这个隐蔽的违反项。

## 下一步

Sprint 1.1 数据质量门禁已完成。下一个 Sprint（1.2）方向：

- **部署前体检**：URDF 完整性、TF 树连通性、Nav2 参数合理性、E-stop 配置、传感器标定
- **MCP Server**：rosbag-inspector 最小可用版本，支持通过标准化的 MCP 协议查询 rosbag 元数据

同时，早鸟价诊断服务已开放：

| 服务 | 内容 | 定价 |
|---|---|---|
| 机器人 AI 化诊断（早鸟） | 45 分钟在线 + 痛点诊断 | ¥199 |
| 单点闭环诊断 | 2 小时 + 书面报告（数据/部署/VLA 三选一） | ¥999 |
| 机器人公司专项工作坊 | 2 天现场/线上 + 实操 Demo | ¥19,800 |

预约：微信/飞书 13738170552 · 邮箱 gll8209944@hotmail.com

<!-- IMG: 各数据集 report.md 截图插入位置 -->

## 技术附录

### 门禁模块组成

```
demos/data-quality-gate/
├── scripts/run_gate.py        # 入口脚本
├── checks/
│   ├── fps_consistency.py     # 帧率一致性
│   ├── missing_frames.py      # 缺帧检测
│   ├── multiview_sync.py      # 多视角同步
│   ├── task_label.py          # 标签完整性
│   └── anomaly_frames.py      # 异常帧检测（A类+B类）
├── reporter.py                # 双份报告生成器
├── schemas/report.schema.json # JSON Schema
└── templates/report.md       # Markdown 模板
```

### 门禁运行命令

```bash
python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ./datasets/so100_pickplace \
    --output ./reports \
    --profile strict
```

### 摄像头选择策略（so100 bug 修复核心）

```python
# 优先选择 top/base 摄像头，避免 wrist/left 的运动模糊干扰
mp4s = sorted(
    videos_dir.rglob("*.mp4"),
    key=lambda p: ("wrist" in str(p), "left" in str(p), p.name)
)
# ("wrist" in path, "left" in path, filename)
# False < True，所以 wrist/left 会被排到最后
# 结果：top/base 摄像头排在前面，被优先选中
```

---

*本文是 Sprint 1.1 数据质量门禁的产出记录。代码和数据均已开源至 [claude-code-robotics-playbook](https://github.com/gll8209944/claude-code-robotics-playbook)。*
