<!--
  自动同步自 Notion
  同步时间: 2026-04-27 13:50:46
  页面 ID: 24c53fc5-43d3-4757-a9b3-2fc568b2afe8
  原始链接: https://www.notion.so/24c53fc543d34757a9b32fc568b2afe8
-->

# Sprint 1.2 执行卡 · deployment-health-check（H6-H12）

> 🎯 ****Sprint 1.2 唯一目标：** 6 小时内产出可演示的部署前体检 Demo + 启动第一个机器人 MCP（rosbag-inspector 最小版）。本执行卡覆盖 **H6-H7（前 1 小时）准备工作**，确保后续 5 小时纯做核心交付。**
## Sprint 1.2 验收清单（H12 检查）
- [ ] `deployment-health-check` 在一台真实机器人配置上跑通，输出 JSON + Markdown 双份部署体检报告
- [ ] [CLAUDE.md](http://claude.md/) 已追加部署闭环规范（URDF 校验 / TF 树 / Nav2 参数 / E-stop / 标定）
- [ ] `rosbag-inspector` MCP Server 最小可用版本已跑通（本地 stdio 模式）
- [ ] 第二篇文章草稿（≥2000 字 + 1 段录屏 GIF）已写完
- [ ] GitHub 仓库 `demos/deployment-health-check/` 目录已提交
---
## 🖥️ 设备角色分工（引用 Sprint 1.1）
> 🧭 ****与 Sprint 1.1 相同的设备分工，但主要差异：** Sprint 1.2 需要 ROS2 工具链，**Mac 不装 ROS2**。**两台机器都装 CC CLI**，Mac 为主力开发 + 录屏，无影为 ROS2 验证专用 CC CLI 会话。Mac ↔ 无影无法 SSH，文件同步走 Git。**
> ⚡ ****加速原则：能用 CC CLI 的地方全部用 CC CLI。** 手动操作仅限：Kap 录屏、iPad 审稿、iPhone 发文。其他一切（写代码、跑测试、git 操作、ROS2 验证脚本、MCP 测试）全部通过 CC CLI Prompt 驱动。**
| 设备 | Sprint 1.2 角色 | CC CLI 用法 |
| --- | --- | --- |
| **Mac** ⭐ | **CC CLI 主会话**  • 录屏 | 所有代码生成 / 配置生成 / 文章撰写 / git push / 报告生成 / Kap 录屏 |
| **无影云桌面 Ubuntu** ⭐ | **CC CLI 第二会话**（ROS2 专用） | git pull → CC CLI 驱动 ROS2 验证（check_urdf / TF 树 / Nav2 校验 / MCP server 测试） |
| **阿里云 ECS** | 数据后台（沿用） | 存放 Sprint 1.1 数据集 / 备用 MCP server 部署测试 |
| **iPhone** | 获客 + 应急 | 发文 / 客户响应（唯一不用 CC CLI 的设备） |
---
## H6-H7：1 小时准备清单（6 步）
### Step 1（10 min）：无影安装 CC CLI + ROS2 环境确认
> ⚠️ ****关键前置：** Mac 无法 SSH 到无影。无影上也装一个 CC CLI，这样两台机器都能用 CC CLI 加速。文件同步走 Git 仓库中转。**
**在无影云桌面本地终端执行（打开无影客户端 → 桌面 → 终端）：**
```bash
# ===== 1a. 安装 Claude Code CLI（如未安装）=====
npm install -g @anthropic-ai/claude-code
claude --version

# ===== 1b. 进入仓库目录，启动 CC CLI =====
cd ~/work/claude-code-robotics-playbook
claude
```
**在无影 CC CLI 中贴入以下 Prompt：**
```plain text
请帮我验证当前环境的 ROS2 工具链是否可用，依次执行并报告结果：

1. source /opt/ros/humble/setup.bash && ros2 --version
2. which check_urdf
3. ros2 run tf2_tools view_frames --help 2>/dev/null && echo "tf2_tools OK" || echo "tf2_tools 缺失"
4. python3 -c "import lxml; import yaml; import jsonschema; print('Python 依赖 OK')"

如果任何工具缺失，请自动安装：
- ROS2 工具：sudo apt update && sudo apt install -y ros-humble-urdfdom ros-humble-tf2-tools ros-humble-nav2-bringup ros-humble-robot-state-publisher liburdfdom-tools
- Python 依赖：pip install urdfpy lxml pyyaml jsonschema

最后输出一个环境状态表：
| 工具 | 状态 | 版本 |
|---|---|---|
| ROS2 Humble | ✅/❌ | ... |
| check_urdf | ✅/❌ | ... |
| tf2_tools | ✅/❌ | ... |
| Python deps | ✅/❌ | ... |
| CC CLI | ✅ | ... |
```
### Step 2（10 min）：准备真实机器人配置样本
> 💡 ****核心素材：** 部署体检需要「一台真实机器人的配置」作为输入。你工作中接触过的机器人配置（全向底盘 + Nav2 + 机械臂）是最佳素材。以下是需要收集的 5 类文件。**
**需要收集的配置文件清单：**
| 序号 | 文件类型 | 用途 | 来源建议 |
| --- | --- | --- | --- |
| 1 | **URDF / xacro 文件** | 机器人模型描述（关节、link、碰撞体） | 公司机器人 URDF 或开源 TurtleBot4 / UR5 URDF |
| 2 | **nav2_params.yaml** | Nav2 导航参数（AMCL / 规划器 / 控制器） | 你的 Nav2 部署验证页面中有完整模板 |
| 3 | **TF 树配置 / launch 文件** | 坐标变换链（map→odom→base_link→sensors） | launch 文件中的 static_transform_publisher |
| 4 | **标定文件**（camera_info.yaml / 手眼标定矩阵） | 相机内参 / 手眼标定外参 | 标定输出目录 |
| 5 | **E-stop 配置**（safety.yaml / 急停逻辑描述） | 急停按钮 → 硬件中断链路 | 底盘控制接口文档 / 安全配置 |
```bash
# 在仓库中准备样本目录
cd ~/work/claude-code-robotics-playbook
mkdir -p demos/deployment-health-check/{configs,checks,schemas,reports,tests,samples,templates}
mkdir -p demos/deployment-health-check/configs/{urdf,nav2,tf,calibration,estop}

# 如果用开源替代（脱敏演示用）：
# TurtleBot4 URDF
wget -O demos/deployment-health-check/configs/urdf/robot.urdf \
  https://raw.githubusercontent.com/turtlebot/turtlebot4/humble/turtlebot4_description/urdf/standard/turtlebot4.urdf.xacro

# Nav2 默认参数
wget -O demos/deployment-health-check/configs/nav2/nav2_params.yaml \
  https://raw.githubusercontent.com/ros-navigation/navigation2/humble/nav2_bringup/params/nav2_params.yaml
```
> 🎯 ****最佳路径：** 如果能拿到你公司真实机器人的配置（哪怕是脱敏版），Demo 说服力远大于开源替代品。建议用你实际部署过的全向底盘 + Nav2 配置。如果涉密，去掉 SN 号和内部 IP 即可。**
### Step 3（10 min）：故意植入典型部署错误
> 🐛 ****与 Sprint 1.1 同样的策略：** 好数据跑出全绿没有素材。需要准备一份「有问题的配置」让体检工具抓出来，作为文章和 Demo 的核心卖点。**
**常见部署错误清单（选 3-5 个植入）：**
| 错误类型 | 植入方式 | 体检工具应检出的结果 |
| --- | --- | --- |
| **URDF link 名称不匹配** | 把 `base_link` 改成 `base_Link`（大小写） | ❌ TF 树断裂：base_link 未定义 |
| **TF 树断链** | 删掉 `odom → base_link` 的 transform publisher | ❌ TF 链不完整：map→odom→??? 断裂 |
| **Nav2 参数越界** | `max_vel_x: 5.0`（正常应 ＜1.0）/ `inflation_radius: 0.01` | ⚠️ 最大速度超限 / 膨胀半径过小 |
| **E-stop 未配置** | 整个 safety.yaml 为空 | ❌ 急停配置缺失：不允许部署 |
| **标定文件过期** | camera_info.yaml 的时间戳 ＞90 天 | ⚠️ 标定超过 90 天未更新，建议重新标定 |
```bash
# 创建两份配置：一份正确（good/）一份有bug（bad/）
mkdir -p demos/deployment-health-check/configs/{good,bad}
# good/ 放正确的完整配置
# bad/ 放植入错误的配置
# CC CLI 会帮你批量生成
```
### Step 4（5 min）：CC CLI 扩展 [CLAUDE.md](http://claude.md/) 部署章节
**在 Mac CC CLI（T1）中贴入：**
```plain text
请在 CLAUDE.md 末尾追加下面这段部署闭环规范（不动 Sprint 1.1 的任何原有内容）。
追加前先 git stash，追加后 git diff CLAUDE.md 确认只有末尾新增。

追加内容见本执行卡「CLAUDE.md 部署闭环追加章节」段落（已在下方提供）。

完成后：
1. git diff CLAUDE.md | head -30  # 确认只有末尾追加
2. git add CLAUDE.md && git commit -m "docs: 追加 Sprint 1.2 部署闭环规范" && git push
3. 输出 CLAUDE.md 总行数
```
### Step 5（5 min）：CC CLI 安装 MCP 依赖
> 📚 ****rosbag-inspector 是 Sprint 1.2 的新增交付。** 先用 CC CLI 安装依赖、验证 SDK 可用。MCP 的参考代码已写在下方「rosbag-inspector MCP 最小可用版本」段落。**
**在 Mac CC CLI（T1）中贴入：**
```plain text
请安装 MCP 开发依赖并验证：
1. pip install mcp rosbags
2. python -c "from mcp.server import Server; print('MCP SDK OK')"
3. python -c "from rosbags.rosbag2 import Reader; print('rosbags OK')"
如果安装失败，给出替代方案。
```
### Step 6（5 min）：双 CC CLI 同步 Sprint 1.1 产出
**在 Mac CC CLI（T1）中贴入：**
```plain text
请验证 Sprint 1.1 产出完整性：
1. git pull origin main
2. ls demos/data-quality-gate/scripts/run_gate.py && echo "run_gate OK"
3. ls demos/data-quality-gate/reports/ && echo "reports OK"
4. head -5 CLAUDE.md
5. git log --oneline -5
所有 OK 后 say "Sprint 1.1 产出完整，准备开始 Sprint 1.2"
```
**同时切到无影 CC CLI（T3）贴入：**
```plain text
请同步仓库并确认：
1. cd ~/work/claude-code-robotics-playbook && git pull origin main
2. ls demos/data-quality-gate/scripts/run_gate.py && echo "OK"
3. source /opt/ros/humble/setup.bash && ros2 --version
Say "无影同步完成，ROS2 就绪"
```
---
## [CLAUDE.md](http://claude.md/) 部署闭环追加章节（复制追加到仓库根 [CLAUDE.md](http://claude.md/) 末尾）
> 📜 **这段内容追加到 Sprint 1.1 已有的 [CLAUDE.md](http://claude.md/) 末尾。部署闭环的「宪法」——所有部署体检脚本、MCP Server 都必须遵守这些规范。**
```markdown
## Sprint 1.2 — 部署闭环规范（追加）

### 当前优先 Sprint
Sprint 1.2 — `demos/deployment-health-check`：给机器人部署加一道体检门禁。
同时启动 `mcp-servers/rosbag-inspector`（最小可用版本）。

### 部署体检五项检查（强制规范）
所有部署前必须通过以下五项检查，任何一项 ❌ 即拒绝部署：

| 检查项 | 检查内容 | 阻塞级别 |
|---|---|---|
| URDF 完整性 | link/joint 定义完整、无悬挂 link、碰撞体与视觉体一致 | ❌ 阻塞 |
| TF 树连通性 | map→odom→base_link→sensors 全链路连通、无环、无断裂 | ❌ 阻塞 |
| Nav2 参数合理性 | 速度/加速度在安全范围、膨胀半径合理、控制频率 ≥10Hz | ⚠️ 警告（越界则阻塞） |
| E-stop 配置 | 急停链路已定义、硬件中断引脚已映射、急停响应时间 <100ms | ❌ 阻塞 |
| 标定时效性 | 相机内参/手眼标定/里程计标定在有效期内（默认 90 天） | ⚠️ 警告 |

### 部署体检阈值
| 指标 | 安全值 | 警告值 | 危险值 |
|---|---|---|---|
| max_vel_x (m/s) | ≤ 0.8 | 0.8-1.5 | > 1.5 |
| max_vel_theta (rad/s) | ≤ 1.5 | 1.5-3.0 | > 3.0 |
| inflation_radius (m) | ≥ 0.3 | 0.15-0.3 | < 0.15 |
| controller_frequency (Hz) | ≥ 20 | 10-20 | < 10 |
| 标定有效期 (天) | ≤ 30 | 30-90 | > 90 |
| E-stop 响应时间 (ms) | ≤ 50 | 50-100 | > 100 |

### 部署体检报告规范
每次体检必须同时输出：
- `deploy_report.json`：机器可读，schema 见 `demos/deployment-health-check/schemas/deploy_report.schema.json`
- `deploy_report.md`：人可读

Markdown 报告字段：部署总评（✅可部署/⚠️有条件部署/❌拒绝部署）、机器人概览（型号/SN/固件版本）、五项检查详情表、Top 3 风险项、修复建议优先级列表、与上次体检的差异对比。

### MCP Server 开发规范（rosbag-inspector 起步）
1. 所有 MCP Server 使用 Python + mcp SDK，stdio 模式优先
2. 每个 tool 必须有 inputSchema + description
3. 返回值统一 JSON 格式，含 status/data/errors 三字段
4. 错误不 raise，统一通过 errors 数组返回
5. 每个 MCP Server 独立目录：mcp-servers/<name>/server.py + requirements.txt + README.md

### 部署闭环行为准则（追加）
7. 部署体检脚本必须支持 --config-dir 指定配置目录，不硬编码路径
8. 每项检查独立文件，可单独运行也可被 run_check.py 统一调用
9. 检查结果三级：PASS / WARN / FAIL，对应退出码 0 / 1 / 2
10. 所有 ROS2 依赖的检查必须能在有 ROS2 和无 ROS2 环境下降级运行（无 ROS2 时用纯 Python 解析）
```
---
## ⚡ H6-H7 执行顺序（Claude Code CLI 加速版）
> 🚀 ****核心思路：双 CC CLI 并行加速。** Mac CC CLI（T1）负责代码生成 + git push，无影 CC CLI（T3）负责 ROS2 验证 + MCP 测试。两边通过 Git 仓库同步。人手只做：贴 Prompt + Kap 录屏 + 审稿。**
### 窗口分配
| 窗口 | 位置 | CC CLI 用法 |
| --- | --- | --- |
| **T1** ⭐ | Mac · **CC CLI 主会话** | 所有代码 / 配置 / 文章 / git push — 人只贴 Prompt |
| T2 | Mac · 普通 shell（备用） | 查进度 / 应急（极少用） |
| **T3** ⭐ | 无影 · **CC CLI 第二会话**（⚠️ Mac 无法 SSH） | git pull → CC CLI 驱动 ROS2 验证 / check_urdf / MCP 测试 |
| T4 | 浏览器 / iPhone | GitHub / Notion / 验证结果 |
### 60 min 时间轴（双 CC CLI 并行）
```plain text
分钟   人类动作                T1 Mac CC CLI                        T3 无影 CC CLI
───────────────────────────────────────────────────────────────────────────────
0-3    无影开 CC CLI           —                                    ▸ 贴环境检查 Prompt（Step 1）
3-8    回 Mac 贴 Prompt        ▸ CLAUDE.md 追加 + commit + push       ▸ 自动装依赖 + 验证 ROS2
8-18   贴 Config Gen Prompt   ▸ 生成 good/bad 两套配置 + push         ▸ 等 T1 push 完 → git pull
18-25  等 T1 完成              ▸ git push 完成                        ▸ 贴 URDF 验证 Prompt → check_urdf
25-45  贴 checklist Prompt    ▸ 写 docs/deploy-checklist.md           ▸ 贴 ROS2 对比验证 Prompt
45-55  检查两边产出            ▸ git pull（拉无影的提交）               ▸ git push（推验证结果）
55-60  H7 飞行员清单           ▸ 输出状态表                            ▸ 输出状态表

⚠️ 同步节奏：T1 push → T3 pull → T3 push → T1 pull（避免冲突）
```
---
## 给 Claude Code 的第一个 Prompt（H7-H10 用）
> ⚡ **在仓库根目录启动 Claude Code CLI，把下面整段一次性粘贴。它会以 [CLAUDE.md](http://claude.md/)（含追加的部署闭环规范）为宪法自动遵守。**
```plain text
请阅读项目根目录的 CLAUDE.md（包括刚追加的 Sprint 1.2 部署闭环规范），然后在 demos/deployment-health-check/ 下创建以下脚手架（严格遵守 CLAUDE.md 全部行为准则）：

1. scripts/run_check.py — 入口脚本
   - 命令行参数：--config-dir <path>（机器人配置目录）、--output <dir>（报告输出目录）
   - 调用 5 个检查模块（见下），收集结果，调用 reporter 生成报告
   - 退出码：0=可部署（全 PASS），1=有条件部署（有 WARN 无 FAIL），2=拒绝部署（有 FAIL）

2. checks/ — 5 个检查模块，每个独立文件 + 独立单测
   - urdf_check.py：URDF 完整性校验
     · 解析 URDF XML，检查所有 link 是否有对应 joint 连接（无悬挂 link）
     · 检查碰撞体（collision）是否定义
     · 检查 base_link 是否存在
     · 无 ROS2 时用 urdfpy 或纯 lxml 解析；有 ROS2 时额外调用 check_urdf
   - tf_tree_check.py：TF 树连通性校验
     · 从 URDF + launch 文件中提取 TF 树
     · 验证 map→odom→base_link→各传感器 frame 全链路连通
     · 检测环路和断裂
     · 输出 TF 树可视化文本（ASCII 树状图）
   - nav2_params_check.py：Nav2 参数合理性校验
     · 解析 nav2_params.yaml
     · 逐项对比 CLAUDE.md 中的阈值表（安全/警告/危险三级）
     · 检查关键节点是否配置（controller_server / planner_server / bt_navigator）
     · 检查 use_sim_time 是否为 false（实机部署）
   - estop_check.py：E-stop 配置校验
     · 检查 safety.yaml / estop 配置文件是否存在且非空
     · 检查急停 topic 是否定义（如 /emergency_stop）
     · 检查急停响应时间配置
   - calibration_check.py：标定时效性校验
     · 遍历标定目录下的 .yaml 文件
     · 检查文件修改时间是否在有效期内（默认 90 天）
     · 检查相机内参矩阵格式正确性

3. schemas/deploy_report.schema.json — 按 CLAUDE.md 部署报告字段建模的 JSON Schema

4. templates/deploy_report.md — Markdown 报告模板，字段 100% 对齐 CLAUDE.md

5. reporter.py — 同时输出 deploy_report.json 和 deploy_report.md

6. tests/ — 至少 5 个 pytest 单测，每个 check 一个
   - 用最小 fixture：1 个正确 URDF + 1 个断裂 URDF、1 份正确 nav2 YAML + 1 份越界 YAML 等
   - 必须覆盖 PASS 和 FAIL 两种 case

7. configs/good/ — 完整正确的机器人配置（可部署）
   - urdf/robot.urdf（简化版，至少含 base_link + 2 个 sensor frame + 1 个 wheel joint）
   - nav2/nav2_params.yaml（全部在安全阈值内）
   - tf/transforms.yaml（完整 TF 链定义）
   - calibration/camera_info.yaml（30 天内的标定）
   - estop/safety.yaml（完整急停配置）

8. configs/bad/ — 植入 5 个错误的配置（拒绝部署）
   - URDF：base_Link 大小写错误 + 悬挂 link
   - Nav2：max_vel_x=5.0 + inflation_radius=0.01
   - TF：删掉 odom→base_link
   - E-stop：空文件
   - 标定：时间戳 180 天前

硬约束：
- 遵守 CLAUDE.md 全部行为准则（含 Sprint 1.1 的 6 条 + Sprint 1.2 追加的 4 条）
- 无 ROS2 环境也能运行所有检查（纯 Python 降级模式）
- 运行示例命令必须能在 configs/good/ 和 configs/bad/ 上分别跑通
- 全部脚本中文注释 + 关键函数 docstring

完成后请输出：
A. 文件树（tree -L 3 demos/deployment-health-check）
B. 两行复现命令（good 和 bad 各一行）
C. 在 configs/good/ 上的实测报告摘要（5 行内，exit_code=0）
D. 在 configs/bad/ 上的实测报告摘要（5 行内，exit_code=2，列出具体 FAIL 项）
E. 你认为下一步最该做什么（不超过 3 条）
F. 你在实现过程中违反 CLAUDE.md 的次数（诚实自查）
```
> 🛡️ ****Claude Code 卡住时的 3 句魔法话（沿用 Sprint 1.1）：**
1. 「请重新读一遍 [CLAUDE.md](http://claude.md/)，然后告诉我你刚才哪一步违反了行为准则」
2. 「先停止写代码。用 5 行中文告诉我现在的实现思路 + 你判断会出问题的地方」
3. 「把刚才的改动 git diff 出来，逐文件解释为什么这么改，我才决定是否合并」**
---
## [CLAUDE.md](http://claude.md/) 自检 Prompt（H8.5 用）
> 🔍 ****什么时候用：** Claude Code 完成第一段 Prompt 的所有产出（A-F 六项报告都给出）之后，立即贴回去，让它反向逐条对照 [CLAUDE.md](http://claude.md/) 自查。**
```plain text
现在请暂停所有新代码改动，进入【自检模式】。

请重新完整读一遍项目根目录的 CLAUDE.md（含 Sprint 1.1 + 1.2 两段），然后逐项审计你刚才的产出，带证据举证。

【强制审计项】

A. 行为准则 10 条逐条检查（Sprint 1.1 的 6 条 + Sprint 1.2 的 4 条）：
   1. 小步快跑：任一脚本是否 > 200 行？`wc -l demos/deployment-health-check/**/*.py`
   2. 测试覆盖：每个 check 是否有配套测试？列出脚本 → 测试的映射表
   3. 双份报告：deploy_report.json 和 deploy_report.md 是否都真的生成了？
   4. 路径硬编码：`grep -rn "/Users/\|/home/\|C:\\\\" demos/deployment-health-check`
   5. 提交信息：`git log --oneline` 确认全部中文
   6. 依赖登记：列出所有 import，逐个对比 requirements.txt
   7. --config-dir 参数：run_check.py 是否支持？是否有硬编码路径？
   8. 独立运行：每个 check 能否单独执行？`python -m demos.deployment_health_check.checks.urdf_check --help`
   9. 三级结果：PASS/WARN/FAIL 输出是否一致？退出码是否对应 0/1/2？
   10. 无 ROS2 降级：在本机（无 ROS2）跑一遍 `python demos/deployment-health-check/scripts/run_check.py --config-dir demos/deployment-health-check/configs/good/ --output /tmp/test`，是否能正常完成？

B. 部署体检五项检查是否完整实现：
   - URDF 校验、TF 树、Nav2 参数、E-stop、标定时效 —— 是否全部实现？
   - 有无遍漏的检查子项？

C. 阈值表实现：
   - 安全/警告/危险三级阈值是否都在 checks/ 里实现？
   - 阈值是否集中配置？还是散落在多个文件里硬编码？

D. 报告字段对齐：
   - deploy_report.md 是否包含 CLAUDE.md 列出的 6 个字段：
     部署总评 / 机器人概览 / 五项检查详情表 / Top 3 风险项 / 修复建议优先级列表 / 与上次体检差异对比

E. good/bad 配置对比：
   - configs/good/ 是否真的 exit_code=0？
   - configs/bad/ 是否真的 exit_code=2 且 5 个错误都被抓到？
   - 贴出两次运行的实际输出。

F. 自报次数核对：
   - 你上一轮自报的“违反 CLAUDE.md 次数”是否准确？
   - 现在重新数一次。

【输出格式】
请按下表逐行作答，每行必须有证据：

| 审计项 | 结论 | 证据（路径:行号 或 命令输出） | 整改动作 |
|---|---|---|---|
| A.1 小步快跑 | ✅/⚠️/❌ | ... | ... |
| ... 全部 10+5 项 ... |

最后给出三件事：
1. 必须立即整改的项（阻塞 H10 验收）
2. 可以延后到 Sprint 1.3 整改的项
3. 你建议我（人类）此刻额外检查的 1 件事

【禁止】
- 禁止在自检中写新代码或新文件
- 禁止用“应该没问题”等模糊表达
- 任何 ✅ 必须有证据，否则强制降级为 ⚠️
```
---
## H8.5-H10：自检整改 + 真实机器人配置体检
> 💡 ****自检整改：** 自检审计表出来后，在同一 CC CLI 会话中让它逐条修复并提交。完成整改后，立即进入下面的真实配置体检 ↓**
**Mac CC CLI（T1）整改 Prompt：**
```plain text
根据上面自检表中的所有 ⚠️ 和 ❌ 项，逐条修复：
1. 每修一项，立即 git add -A && git commit -m "fix: 整改 <审计项编号> <描述>"
2. 全部修完后 git push
3. 重新跑一遍 configs/good/ 和 configs/bad/ 确认修复有效
4. 输出整改汇总表：| 审计项 | 修复前 | 修复后 | 证据 |
```
**Mac CC CLI（T1）真实配置体检 Prompt（整改完成后贴）：**
```plain text
现在对两套配置分别跑部署体检，验证工具效果：

【1】对正确配置跑体检（应得 exit_code=0）：
python demos/deployment-health-check/scripts/run_check.py \
    --config-dir demos/deployment-health-check/configs/good/ \
    --output demos/deployment-health-check/reports/good/

【2】对错误配置跑体检（应得 exit_code=2）：
python demos/deployment-health-check/scripts/run_check.py \
    --config-dir demos/deployment-health-check/configs/bad/ \
    --output demos/deployment-health-check/reports/bad/

【3】输出对比表（这是文章的核心素材）：

A. good vs bad 对比总表：
| 配置 | exit_code | URDF | TF树 | Nav2 | E-stop | 标定 | 总评 |

B. 🔴 bad 配置深挖：
   - 每个 FAIL 项的具体错误描述
   - 对应的修复建议
   - 如果不修复直接部署会发生什么（现场事故场景）

C. 🟢 good 配置的报告摘要（3 行内）

D. cat 两份 report.md 的前 30 行，我要确认格式正确

【4】git add -A && git commit -m "feat: good/bad 体检对比报告" && git push

完成后 say "部署体检对比完成，准备开始 MCP"
```
**同时在无影 CC CLI（T3）贴入 ROS2 原生对比验证 Prompt：**
```plain text
请 git pull 拉取最新代码，然后用 ROS2 原生工具对比验证体检结果：

1. source /opt/ros/humble/setup.bash
2. check_urdf demos/deployment-health-check/configs/good/urdf/robot.urdf && echo "✅ good URDF OK"
3. check_urdf demos/deployment-health-check/configs/bad/urdf/robot.urdf 2>&1 || echo "❌ bad URDF 预期失败"
4. 对比 CC 生成的体检报告 vs ROS2 原生工具输出，确认结论一致
5. 如有差异，记录到 docs/ros2-native-comparison.md
6. git add -A && git commit -m "docs: ROS2 原生对比验证" && git push

Say "ROS2 对比验证完成"
```
---
## H10-H11：rosbag-inspector MCP 最小可用版本
> 🔧 ****目标：** 1 小时内交出一个能跑通的 MCP Server，只需支持 1 个 tool（`inspect_rosbag`）。它能读取 .mcap / .db3 文件的元数据，返回 topic 列表、消息数量、时间范围。这是你的第一个 MCP Server，也是对外展示「Claude Code 对接机器人系统」的入门卡。**
**Mac CC CLI（T1）MCP Server Prompt（部署体检对比完成后贴）：**
```plain text
现在启动 Sprint 1.2 的第二个交付：rosbag-inspector MCP Server 最小可用版本。

请在 mcp-servers/rosbag-inspector/ 下创建：

1. server.py — MCP Server 主文件（stdio 模式）
   - 注册 1 个 tool：inspect_rosbag
   - inputSchema：bag_path (string, required)
   - 功能：读取 .mcap 或 .db3 文件，返回：
     · topic 列表（名称 + 消息类型 + 消息数量）
     · 总时长（秒）
     · 开始/结束时间戳
     · 文件大小
     · 帧率统计（每个 topic 的平均帧率）
   - 使用 rosbags 库解析（同时支持 ROS1 .bag 和 ROS2 .db3 格式）
   - 错误不 raise，通过 JSON { status, data, errors } 返回

2. requirements.txt
   - mcp
   - rosbags

3. README.md
   - 用途说明
   - 安装命令
   - 使用示例（如何配置到 Claude Code 的 MCP 设置中）
   - 输出示例

4. tests/test_server.py — 至少 2 个测试
   - 读取 datasets/rosbag-samples/nuScenes-v1.0-mini-scene-0061.mcap（Sprint 1.1 已下载）
   - 测试无效路径返回错误而不崩溃

硬约束：
- 遵守 CLAUDE.md 的 MCP Server 开发规范（5 条）
- 代码 < 200 行
- 全部中文注释

完成后：
A. tree mcp-servers/rosbag-inspector/
B. 在 nuScenes mcap 上的实测输出（5 行内）
C. 如何配置到 Claude Code 的一行配置示例
D. pytest 运行结果

git add -A && git commit -m "feat: rosbag-inspector MCP Server 最小可用版" && git push
```
**同时在无影 CC CLI（T3）贴入 MCP 测试 Prompt：**
```plain text
请 git pull 拉取最新的 rosbag-inspector MCP Server 代码，然后：

1. cd ~/work/claude-code-robotics-playbook
2. pip install -r mcp-servers/rosbag-inspector/requirements.txt
3. 如果 datasets/rosbag-samples/ 下没有 mcap 文件：
   wget https://assets.foxglove.dev/nuScenes-v1.0-mini-scene-0061.mcap -O datasets/rosbag-samples/nuScenes-v1.0-mini-scene-0061.mcap
4. pytest mcp-servers/rosbag-inspector/tests/ -v
5. 输出测试结果汇总
6. 如有问题，记录到 docs/mcp-test-issues.md && git add -A && git commit -m "docs: MCP 测试问题记录" && git push

Say "MCP 无影测试完成"
```
> 💡 ****双 CC CLI 并行：** Mac T1 写 MCP 代码 + push，无影 T3 pull + 测试。两边同时进行，1 小时内完成。**
---
## 🎬 H11-H11.5：录屏 + 最终提交
> 🎯 ****目标：** 产出 30-60 秒的演示 GIF，展示「正确配置全绿 → 错误配置报错」的对比冲击力。同 Sprint 1.1 的三段式：CC CLI 准备 → 人手录屏 → CC CLI 提交。**
Phase A — CC CLI 自动段：生成录屏提词卡（5 min）
```plain text
请生成录屏提词卡 docs/recording-script-sprint12.sh：

内容为纯注释 + 可直接复制粘贴的命令，按以下顺序：
  a. clear
  b. tree -L 2 demos/deployment-health-check/    # 展示仓库结构，停 3 秒
  c. echo "=== ✅ 正确配置体检 ===" && python demos/deployment-health-check/scripts/run_check.py --config-dir demos/deployment-health-check/configs/good/ --output /tmp/good-report    # 等指标逐行 PASS
  d. echo "" && echo "=== ❌ 错误配置体检 ===" && python demos/deployment-health-check/scripts/run_check.py --config-dir demos/deployment-health-check/configs/bad/ --output /tmp/bad-report    # 等 FAIL 项跳出
  e. echo "" && diff <(head -20 /tmp/good-report/deploy_report.md) <(head -20 /tmp/bad-report/deploy_report.md) || true    # 对比两份报告
每条命令上方加一行中文注释说明「此刻画面应该展示什么」。

同时预跑一次确认无报错。
```
Phase B — 人手录屏（10 min）
> 🎬 **此阶段 CC CLI 不参与。你亲自在终端操作，Kap 录屏。**
1. 终端字号调大到 **16-18pt**
1. 打开 Kap → 只框终端窗口 → 开始录制
1. 照 `docs/recording-script-sprint12.sh` 逐行复制粘贴执行
1. **核心画面：** 正确配置全绿 PASS → 错误配置红色 FAIL → 报告对比
1. Kap 停止 → 导出 GIF + MP4
1. GIF 放到：`demos/deployment-health-check/samples/demo.gif`
Phase C — CC CLI 自动段：最终提交（5 min）
```plain text
请执行最终提交：
1. ls -lh demos/deployment-health-check/samples/demo.gif
2. git add -A && git commit -m "feat: 部署体检报告 + 演示录屏 + rosbag-inspector MCP" && git push
3. git log --oneline -5
4. 确认 GitHub 仓库可访问
```
---
## ✍️ H11.5-H12：写文章 + 挂早鸟价
> 🎯 ****目标：** ≥2000 字的第二篇文章草稿 + 服务升级推广。**
Step 1（20 min）：CC CLI 写文章
```plain text
请在 docs/ 目录下创建 article-sprint-1.2.md，写一篇技术博文草稿。

要求：
- 标题：机器人现场部署少返工：Claude Code 帮我做了一份部署体检报告
- 副标题：5 项自动检查 + 一份“好配置 vs 坏配置”对比报告，给你看看部署前到底该查什么
- 字数 ≥ 2000 字，中文为主
- 目标读者：机器人现场工程师 / ROS2 开发者 / 机器人公司技术管理者
- 语气：实战经验分享，不是教程

文章结构：
1. 【痛点引入】（300字）机器人现场部署的“到了现场才发现问题”现象：TF 树断裂导致导航失败、URDF 大小写错导致模型加载异常、Nav2 参数越界导致机器人飞车。先给结论：我用 Claude Code 做了一套部署前自动体检。
2. 【五项体检设计】（400字）为什么选这 5 项（URDF / TF / Nav2 / E-stop / 标定）—— 每一项都是真实现场踩过的坑。附三级阈值表。
3. 【好配置 vs 坏配置对比实录】（500字，文章核心高潮）
   请读取 demos/deployment-health-check/reports/ 下 good 和 bad 的报告，输出：
   a. good vs bad 对比表（五项检查状态）
   b. bad 配置中每个 FAIL 项的具体错误 + 现场事故场景（如果不修复直接部署会怎样）
   c. 可视化对比（TF 树 ASCII 图：正确 vs 断裂）
4. 【第一个 MCP Server】（200字）rosbag-inspector 的设计 + 一行配置即可接入 Claude Code
5. 【Claude Code 体验】（200字）与 Sprint 1.1 的对比：数据质量门禁 vs 部署体检，两个闭环的共同模式（CLAUDE.md 宪法 + 检查模块 + 双份报告 + 自检审计）
6. 【下一步 & 服务】（100字）Sprint 1.3 VLA 训练复盘预告 + ¥999 单点闭环诊断服务（数据/部署/VLA 三选一）

关键素材（请融入文中）：
- good vs bad 对比表（从 reports/ 读取真实数据）
- TF 树 ASCII 对比图（正确的树 vs 断裂的树）
- Nav2 参数阈值表
- 录屏 GIF 插入位置标注（<!-- IMG: demo.gif -->）
- rosbag-inspector 一行配置示例

写作要点：
- 「到了现场才发现 XXX ”的叙事比「我做了个工具」更有传播力
- 给真实的现场事故场景（TF 断裂 → 导航失败 → 机器人撞墙）
- 与 Sprint 1.1 文章的系列感：上一篇数据门禁、这一篇部署体检、下一篇 VLA 复盘

写完不要 commit，等我审。
```
Step 2（10 min）：审稿 + 提交 + 推广
- iPad 上审阅 `docs/article-sprint-1.2.md`
- 插入 GIF：`![demo](../demos/deployment-health-check/samples/demo.gif)`
- CC CLI 提交：`git add -A && git commit -m "docs: Sprint 1.2 第二篇文章草稿" && git push`
- **服务升级推广（iPhone）：**
> 「机器人部署前到底该查什么？🤖
用 Claude Code 做了一套 5 项自动体检（URDF / TF 树 / Nav2 / E-stop / 标定），还启动了第一个 rosbag MCP Server。
↳ 上一篇：数据质量门禁（6 个数据集横评）
↳ 这一篇：部署体检（好配置 vs 坏配置对比）
单点闭环诊断升级：¥999 / 2小时（数据 / 部署 / VLA 三选一）
预约：微信 13738170552 · [gll8209944@hotmail.com](mailto:gll8209944@hotmail.com)」
---
## 🏁 H12 验收（Sprint 1.2 完结）
> 📌 ****Sprint 1.2 死线：** H12 时逐项对照验收清单。若任一缺失，立即停下复盘 —— 绝不允许 H12 之后还在写代码，否则 Sprint 1.3 直接被压缩。**
**验收清单对照：**
- [ ] `deployment-health-check` 在 good/bad 配置上分别跑通，输出 JSON + Markdown 双份报告 → git log 确认
- [ ] [CLAUDE.md](http://claude.md/) 含部署闭环规范 → `grep "部署体检五项检查" CLAUDE.md`
- [ ] rosbag-inspector MCP 在 nuScenes mcap 上跑通 → 本地 stdio 测试通过
- [ ] 文章草稿 ≥2000 字 + GIF → `wc -c docs/article-sprint-1.2.md`
- [ ] GitHub 仓库含 `demos/deployment-health-check/` + `mcp-servers/rosbag-inspector/` → 检查 GitHub 页面
**如果 H12 未完成怎么办：**
- MCP 没写完 → 降级为只要 [server.py](http://server.py/) + 1 个 tool 能跑通，测试和 README 延后
- 文章没写完 → 降级为 1000 字短文 + GIF，先发出去再迭代
- 录屏没录 → 截图代替 GIF
- 代码有 bug → 冻结代码，带 bug 发文章（说明“这是 Sprint 1.2 产出，已知限制见 XX”）
---
## 故障兑底
| 现象 | 根因 / 处置 | 替代动作 |
| --- | --- | --- |
| **无影 Ubuntu 没装 ROS2 且 apt 安装失败** | 镜像源或版本不对 | 所有检查切纯 Python 降级模式：urdfpy + lxml + pyyaml，不依赖 ROS2 |
| **Mac 上 urdfpy 安装失败** | M 芯片 native 编译问题 | 改用纯 lxml 解析 URDF XML，不用 urdfpy |
| **check_urdf 命令不存在** | liburdfdom-tools 未装 | `sudo apt install liburdfdom-tools`；如仍失败则纯 Python 降级 |
| **拿不到公司真实机器人 URDF** | 涉密 / 权限 | 用 TurtleBot4 + UR5 开源 URDF 替代，文章中说明“演示用开源配置，实际服务用客户真实配置” |
| **nuScenes mcap 样本下载失败** | 网络 / Foxglove CDN | 用你手头任何一份 rosbag 替代；或 `ros2 bag record -o test /scan /odom -t 10` 录一份最小的 |
| **MCP SDK 版本不兼容** | mcp 包快速迭代 | `pip install mcp==1.0.0` 锁定版本；或看报错信息调整 import 路径 |
| **CC CLI 写 **[**CLAUDE.md**](http://claude.md/)** 追加章节时篡改了 Sprint 1.1 原有内容** | AI “改进”本能 | **先停**：`git diff CLAUDE.md` 逐行核对，只保留末尾追加，不动其他部分 |
| **H12 时间不够，MCP 和文章二选一** | 范围过大 | **优先 MCP**：它是 Sprint 1.2 的独有交付，文章可以延后 1-2h 补。反过来，文章没有 MCP 的素材会缺少亮点。 |
| **无影 CC CLI 安装失败**（npm/node 版本不够） | 无影 Ubuntu 默认 Node 版本过低 | 1. `curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs`
2. 重试 `npm install -g @anthropic-ai/claude-code`
3. 如仍失败：无影降级为手动终端（手动执行 CC CLI Prompt 中的命令），Mac CC CLI 承担全部自动化 |
> 🛡️ ****最关键的一条防御：** [CLAUDE.md](http://claude.md/) 追加部署章节时，必须确保 Sprint 1.1 的原有内容一字不动。追加前先 `git stash`，追加后 `git diff CLAUDE.md` 逐行确认只有末尾新增。**
---
## Sprint 1.2 复盘模板（H12 完成后填写）
```markdown
本周阶段：L? → L?
本周最重要成果：
本周工作提效指标：
本周内容/获客动作：
本周收入：
最大卡点：
下周唯一主线：Sprint 1.3 VLA 训练复盘
```