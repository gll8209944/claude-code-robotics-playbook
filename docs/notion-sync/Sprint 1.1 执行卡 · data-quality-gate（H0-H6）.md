<!--
  自动同步自 Notion
  同步时间: 2026-04-28 08:36:00
  页面 ID: b94fd2c4-f151-4f46-a9b7-3f76df5e7cab
  原始链接: https://www.notion.so/b94fd2c4f1514f46a9b73f76df5e7cab
-->

# Sprint 1.1 执行卡 · data-quality-gate（H0-H6）

> 🎯 ****Sprint 1.1 唯一目标：** 6 小时内产出可演示、可发布、可售卖的最小数据闭环 Demo。本执行卡覆盖 **H0-H1（前 1 小时）准备工作**，确保后续 5 小时纯做核心交付。**
## Sprint 1.1 验收清单（H6 检查）
- [x] `data-quality-gate` 在真实 LeRobot 数据上跑通，输出 JSON + Markdown 双份报告 ✅ pusht(206ep) + so100_pickplace(50ep) 均 strict 全通过
- [ ] GitHub 仓库 `claude-code-robotics-playbook` 已建并含 [CLAUDE.md](http://claude.md/) / README / demo 目录
- [ ] 第一篇文章草稿（≥1500 字 + 1 段录屏 GIF）已写完
- [ ] 早鸟价 ¥199 / 45min 机器人 AI 化诊断服务挂出至少 1 个渠道（朋友圈/飞书群/知乎签名）
---
## 🖥️ 设备角色分工（Sprint 全局）
> 🧭 ****一句话：** Mac 写代码 + 阿里云 ECS 拉数据/跑后台 + 无影云桌面兜底 Linux + iPhone/iPad 做审与发。**Sprint 1.1-1.4（H0-H24）现有设备完全够；Sprint 3.1（H54-H72）必须新增 GPU 算力**。**
### 现有设备分工
| 设备 | 主角色 | 具体承担 |
| --- | --- | --- |
| **Mac** ⭐ | 主力开发机 | Claude Code IDE 入口 / Python 环境 / 录屏（Kap）/ Git 提交 / 文章撰写 |
| **阿里云 ECS Ubuntu** | 数据与长任务后台 | HuggingFace 数据下载（hf-mirror 国内带宽好）/ 跑 pytest 全量回归 / MCP server 公网部署 |
| **无影云桌面 Ubuntu** | 备用 Linux 沙箱 | 当 Mac 上 rosbags / lerobot / ROS2 等原生依赖装不动时的兜底环境 |
| **iPhone** | 移动获客 + 监控 | 朋友圈/飞书发文 / 客户咨询响应 / 「手机端一句话运维」演示场景（Phase 2-3） |
| **iPad mini 6** | 阅读 + 审稿副屏 | 看 [CLAUDE.md](http://claude.md/) 自检产出 / 审 Claude Code 输出 / Notion 计划同步 |
### 按 Sprint 阶段的设备使用
| Sprint | 主操作设备 | 支援设备 | 是否需新增算力 |
| --- | --- | --- | --- |
| **1.1 数据质量门禁**（H0-H6） | Mac（开发 + 录屏） | ECS（数据存储 + 质量门禁运行，仅同步报告回 Mac） | 否 |
| **1.2 部署前体检**（H6-H12） | Mac | 无影 Ubuntu（跑 ROS2 / URDF 校验，避免 Mac 装 ROS 工具链） | 否 |
| **1.3 VLA 训练复盘**（H12-H18） | Mac | ECS（对接日志服务 / RCMS） | 否（仅做日志分析，不训练） |
| **1.4 首笔收入 + 复盘**（H18-H24） | Mac + iPhone（客户对接） | iPad 做审稿副屏 | 否 |
| **2.1-2.2 Skill / MCP 产品化**（H24-H54） | Mac | ECS 部署 MCP server + 公网入口 | 否 |
| **3.1 对话式机械臂调度**（H54-H72） | **新增 GPU 实例** ⚠️ | Mac（顶层编排 + 录屏）+ ECS（API 中转） | **是**（A10 / 4090 24GB+） |
| **3.2 工作坊**（H72-H90） | Mac + iPad（双屏演示） | iPhone 录花絮 | 否 |
### Sprint 3.1 GPU 算力补强方案（H50 前必须拍板）
| 方案 | 规格 | 18h 成本估算 | 推荐指数 |
| --- | --- | --- | --- |
| **阿里云 GPU ECS 按量付费** | [ecs.gn](http://ecs.gn/)7i-c8g1（A10 24GB） | ¥150-220 | ⭐⭐⭐⭐⭐ 首选，与现有阿里云账号打通 |
| AutoDL / 趋动云 / 揽睿星舟 | RTX 4090 24GB | ¥30-60 | ⭐⭐⭐⭐ 最便宜，适合纯仿真推理 |
| 公司机器人组训练机 | 看团队规则 | 0 | ⭐⭐⭐ 若有权限 |
| Colab Pro+ | T4 / A100 不定 | ¥80/月 | ⭐⭐ 网络不稳，仅备选 |
> ⚠️ ****H50 前必做：** GPU 实例开机 → 拉好 Pi05 VLA 权重 + LIBERO 镜像。否则 H54 才开始 ≈ 起码再吞 2-3h，Sprint 3.1 直接溢出预算。**
### 数据下载推荐路径（数据留 ECS，不同步到 Mac）
> ⚡ ****核心原则：数据太大不同步。** 数据集全部留在 ECS 上，质量门禁也在 ECS 上跑，Mac 只拉报告。代码通过 Git 同步（Mac push → ECS pull）。**
```bash
# 在阿里云 ECS 上下载数据（数据永远留在 ECS）
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_ENABLE_HF_TRANSFER=1
hf download --repo-type dataset \
    lerobot/svla_so100_pickplace --local-dir ~/datasets/so100_pickplace

# Mac 只同步报告（不拉数据！）
rsync -avz --progress \
    ecs-host:~/work/claude-code-robotics-playbook/demos/data-quality-gate/reports/ \
    ./demos/data-quality-gate/reports/
```
### 三个易踩坑提醒
- **Mac 不存数据集** → 数据集全部留 ECS，Mac 只存代码 + 报告
- **ECS 上跑门禁前先 git pull** → Mac push 代码后，ECS 上 `cd ~/work/claude-code-robotics-playbook && git pull` 拉最新代码再跑
- **ECS 默认 40GB 系统盘易被数据集打爆** → 下载前 `df -h` 检查，不够就挂 100GB 数据盘（按量几块钱/月）
- **录屏只用 Mac**（Kap/QuickTime）→ 录屏时 SSH 到 ECS 跑门禁，终端画面一样好看
---
## H0-H1：1 小时准备清单（5 步）
### Step 1（10 min）：网络与镜像配置
国内访问 HuggingFace 不稳定，先把镜像配好，整个 120 小时冲刺都受益。
```bash
# 永久写入 ~/.zshrc 或 ~/.bashrc
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_ENABLE_HF_TRANSFER=1   # 大文件并行下载
export HF_HUB_DOWNLOAD_TIMEOUT=120

# Modelscope 备选（阿里云国内镜像，VLA 模型权重很全，Sprint 1.3 会用上）
pip install modelscope
export MODELSCOPE_CACHE=$HOME/.cache/modelscope

# 验证镜像通畅
curl -I https://hf-mirror.com
```
### Step 2（10 min）：Python 环境
```bash
# 推荐 conda（也可用 uv / venv）
conda create -n robot-cc python=3.10 -y
conda activate robot-cc

pip install lerobot pandas pyarrow numpy opencv-python jsonschema pytest
pip install hf_transfer rosbags   # rosbags 给后面 Foxglove sample 用
```
### Step 3（15 min）：数据下载 — LeRobot 精选清单
**筛选维度：** 体积 ＜3GB ｜ episodes ≥20 ｜ 多视角 ｜ 任务标签完整 ｜ 含 language + state + action 三元组（VLA 训练标配）
| 优先级 | 数据集 | 体积 | 特点 | Sprint 1.1 用途 |
| --- | --- | --- | --- | --- |
| **冒烟测试 ⭐** | `lerobot/pusht` | ＜100 MB | 2D 推 T 字块，最经典最小 | 1 分钟下完，验证质检管线通畅 |
| **主推 ⭐⭐⭐** | `lerobot/svla_so100_pickplace` | ~1-2 GB | SO-100 真实机械臂 + 多视角 + pick-place | 主 Demo + 文章封面 |
| 双臂叙事 | `lerobot/aloha_static_coffee` | ~2-3 GB | ALOHA 双臂 + 真实复杂任务 | 备选，给"双臂操作"客户演示 |
| 低成本路线 | `lerobot/koch_pick_place_lego` | ~1-2 GB | Koch 廉价臂 + 乐高任务 | 对应你"低成本可复制"叙事 |
| **故意找茬 🐛** | 任挑一份社区上传质量参差的 | ＜500 MB | 专门挑"问题数据" | 给你的 gate 抓 bug 用，文章里展示"找到了什么" |
```bash
# 一键下载首选 + 主推
hf download --repo-type dataset lerobot/pusht \
    --local-dir ./datasets/pusht
hf download --repo-type dataset lerobot/svla_so100_pickplace \
    --local-dir ./datasets/so100_pickplace

# 附赠：1 份原生 ROS2 MCAP（给 rosbag-inspector MCP 的 hello-world）
mkdir -p datasets/rosbag-samples && cd datasets/rosbag-samples
wget https://assets.foxglove.dev/nuScenes-v1.0-mini-scene-0061.mcap
cd ../..
```
> 💡 **如果某个 LeRobot 数据集名字略有出入，直接去 [huggingface.co/lerobot](http://huggingface.co/lerobot) 搜对应关键词。lerobot 组织页有完整可视化预览，挑数据集时**优先看 episode 数 ≥ 20、最近半年内更新、stars > 5**。**
### Step 4（15 min）：仓库初始化
```bash
mkdir -p claude-code-robotics-playbook && cd claude-code-robotics-playbook
git init -b main

# 目录结构
mkdir -p demos/data-quality-gate/{scripts,checks,schemas,reports,tests,samples}
mkdir -p demos/deployment-health-check demos/vla-training-review
mkdir -p skills mcp-servers docs

# 占位文件
touch CLAUDE.md README.md requirements.txt
cat > .gitignore <<'EOF'
datasets/
*.mcap
*.parquet
__pycache__/
.venv/
.DS_Store
reports/*.html
EOF

cat > requirements.txt <<'EOF'
lerobot>=0.3.0
pandas
numpy
pyarrow
opencv-python
jsonschema
pytest
rosbags
EOF
```
### Step 5（10 min）：把 [CLAUDE.md](http://claude.md/) / [README.md](http://readme.md/) 落到仓库
直接复制下面两节内容到对应文件，然后：
```bash
git add . && git commit -m "init: Sprint 1.1 脚手架 + 数据质量门禁规范"
gh repo create claude-code-robotics-playbook --public --source=. --push
# 没装 gh：先在 github.com 手动建仓，再 git remote add origin ... && git push -u origin main
```
---
## [CLAUDE.md](http://claude.md/) 首版（复制到仓库根）
> 📜 **这份 [CLAUDE.md](http://claude.md/) 是项目"宪法"。所有 Claude Code 会话默认先读它；后续每个 Skill / MCP 都通过引用这份文件保证规范一致 — 这是 120 小时冲刺最重要的元模式。**
```markdown
# claude-code-robotics-playbook · CLAUDE.md

## 项目使命
本仓库是「机器人智能化 × Claude Code」的实战手册。每个 demo 必须解决机器人研发某个真实环节（数据 / 部署 / 运维 / VLA / 应用执行）的具体痛点，并以可演示、可发文章、可售卖的形式产出。

## 当前优先 Sprint
Sprint 1.1 — `demos/data-quality-gate`：给机器人采集数据加一道质量门禁。其它目录在本 Sprint 内禁止写代码。

## 数据四级标准（强制规范）
所有数据按以下四级管理，任何脚本对数据的处理必须遵循：

| 级别 | 含义 | 进入条件 |
|---|---|---|
| raw | 原始采集 | 落盘即为 raw |
| validated | 通过 data-quality-gate | 帧率一致性 / 缺帧率 / 多视角时间戳偏移 / 任务标签完整性 全部通过 |
| curated | 人工抽查 + 标签精修 | validated 基础上由人工确认任务描述准确、视角覆盖完整 |
| training | 可进入 VLA 训练 | curated 基础上写入 dataset card（版本号、采集时间、任务清单、已知缺陷） |

铁律：未经 validated 的数据禁止直接用于模型训练或对外演示。

## 质量门禁阈值
| 指标 | strict 阈值 | loose 阈值 |
|---|---|---|
| 帧率标准差 / 均值 | < 5% | < 10% |
| 缺帧率 | < 1% | < 3% |
| 多视角时间戳最大偏移 | < 50 ms | < 100 ms |
| 任务标签缺失率 | 0% | < 2% |
| 异常帧（黑屏 / 模糊）比例 | < 0.5% | < 2% |

## 报告输出规范
每次质检必须同时输出：
- `report.json`：机器可读，schema 见 `demos/data-quality-gate/schemas/report.schema.json`
- `report.md`：人可读，模板见 `demos/data-quality-gate/templates/report.md`

Markdown 模板字段：总评、数据集概览、关键指标表、Top 3 异常 episode、修复建议、对 VLA 训练的影响。

## Claude Code 行为准则（本项目）
1. 小步快跑：任何脚本超过 200 行先停下来拆分。
2. 每次写脚本必须同时写测试 — 至少 1 个 fixture 数据 + 1 个断言。
3. 报告永远双份（JSON + Markdown），便于工程系统消费 + 人工阅读。
4. 路径硬编码禁止 — 一律用 pathlib.Path + 命令行参数。
5. 写完一个能跑的版本立即提交，再做优化。提交信息用中文。
6. 任何外部依赖必须先在 requirements.txt 登记。

## 输出风格
- 中文为主，专有名词保留英文（episode、rosbag、FPS 等）。
- 报告语气克制，给数据不给情绪。
- 给建议时附带"为什么"。

## 当前严格不做的事
- 不做通用 Claude Code 教学。
- 不做大而全课程。
- 不在 demos/data-quality-gate 之外的目录写代码（除非显式说明已切换 Sprint）。
- 不引入 lerobot / pandas / numpy / pyarrow / opencv-python / jsonschema / pytest / rosbags 之外的依赖（如需新增，先在本文档登记理由）。
```
---
## [README.md](http://readme.md/) 首版（复制到仓库根）
```markdown
# claude-code-robotics-playbook

用 Claude Code 重构机器人研发全生命周期。当前阶段：Sprint 1.1 — 数据质量门禁。

## 这是什么
机器人智能化 × Claude Code 的实战手册。每个 demo 都解决一个真实痛点，并以可演示、可售卖的形式开源。

## 路线图（120 小时冲刺）
- [x] Sprint 1.1 数据质量门禁（H0-H6） ← 当前
- [ ] Sprint 1.2 部署前体检（H6-H12）
- [ ] Sprint 1.3 VLA 训练复盘（H12-H18）
- [ ] Sprint 3.1 对话式机械臂调度（LIBERO + MiniMax M2.1 × Pi05 VLA）

## 快速开始
```
```bash
git clone https://github.com/<your>/claude-code-robotics-playbook
cd claude-code-robotics-playbook
pip install -r requirements.txt

# 下载示例数据
hf download --repo-type dataset lerobot/pusht \
    --local-dir ./datasets/pusht

# 跑数据质量门禁
python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ./datasets/pusht \
    --output ./demos/data-quality-gate/reports/ \
    --profile strict
```
```markdown
## 提供的服务
| 服务 | 内容 | 定价 |
|---|---|---|
| 机器人 AI 化诊断（早鸟） | 45 分钟在线 + 一份痛点诊断 | ¥199 |
| 单点闭环诊断 | 2 小时 + 书面报告（数据/部署/VLA 三选一） | ¥999 |
| 机器人公司专项工作坊 | 2 天现场/线上 + 实操 Demo | ¥19,800 |

预约：<填上你的飞书 / 微信 / 邮箱>

## 关注我
- 知乎 / 掘金 / 微信公众号：<占位>
- GitHub Star + Issue 即可参与共建。

## License
MIT for code. 数据集请遵循各原始数据集 license。
```
---
## ⚡ H0-H1 执行顺序（Claude Code CLI 加速版）
> 🚀 ****核心思路：** 上面的 Step 1-5 是「内容清单」，这一节是「实际执行剧本」。**你只在 T1 启动一次 **`claude`**主会话**，让 CC CLI 接管 90% 的命令执行 — 包括建仓、写四份文件、通过 ssh 远程指挥 ECS 下数据、git push、rsync 验证。你的角色降为「任务下达者 + diff 审核者」。**
### 窗口分配
| 窗口 | 位置 | 用途 |
| --- | --- | --- |
| **T1** ⭐ | Mac · Claude Code CLI 主会话 | 所有写文件 / git / ssh / rsync 操作的执行者 |
| T2 | Mac · 普通 shell（备用） | 查 ECS 下载进度 / 应急手动操作 |
| T3 | iPhone Termius 或 Mac 独立 SSH | 仅当 CC CLI ssh 失败时备用直连 ECS |
| T4 | 浏览器 / iPhone | GitHub 建仓 / Notion 决策项填空 / 验证结果 |
### 60 min 时间轴
```plain text
分钟   人类动作                T1 (Claude Code CLI 主会话)              旁路任务
──────────────────────────────────────────────────────────────────
0-2    GitHub 建仓 (T4)        —                                       验证 ssh ecs-host 免密
2-5    贴 Bootstrap Prompt    ▸ 建仓结构 + 写 4 份文件 + git init/commit  
5-10   贴 ECS Remote Prompt   ▸ ssh 配 HF 镜像 + 后台 nohup 下载           
10-15  贴 Push Prompt         ▸ git remote add + push                      T4: 验证 GitHub 页面
15-45  等数据 (30 min)         ▸ 写 docs/decisions.md + dev_setup.md      T2: tail 进度
45-55  贴 Sync & Verify       ▸ rsync 拉回 + Python 验证                  
55-60  H1 飞行员清单          —                                       Notion 勾 ✅
```
### 0-2 min：人类只做两件事
1. **T4 浏览器**：[github.com](http://github.com/) → New repo → `claude-code-robotics-playbook` → **Public** → **不勾** README/.gitignore/license（本地都会写）→ Create
1. **T2 验证 ssh 免密**：`ssh ecs-host hostname` 必须**无需密码直接返回主机名**；如失败先 `ssh-copy-id ecs-host`。顺便把主机别名设好（`~/.ssh/config`）：
```javascript
Host ecs-host
    HostName <你的 ECS 公网 IP>
    User <云服务器用户名>
    IdentityFile ~/.ssh/id_ed25519
    ServerAliveInterval 60
```
### 2-5 min：T1 启动 CC CLI + 贴 Bootstrap Prompt
```bash
cd ~/work     # 你的工作目录
claude        # 进入交互会话
```
进入后贴下面的 **Bootstrap Prompt**（中间 4 份文件内容从上方「[CLAUDE.md](http://claude.md/) 首版」/「[README.md](http://readme.md/) 首版」章节整块复制）：
```plain text
我要在当前目录初始化 Sprint 1.1 项目仓库。请按顺序执行，每个写文件操作展示完整内容供我审，bash 命令逐条提示授权。

【步骤 1】mkdir claude-code-robotics-playbook && cd 进入 && git init -b main

【步骤 2】创建目录树：
  demos/data-quality-gate/{scripts,checks,schemas,reports,tests,samples,templates}
  demos/deployment-health-check
  demos/vla-training-review
  skills, mcp-servers, docs

【步骤 3】写 4 份文件（内容逐份贴在下方，一字不改）：
  - CLAUDE.md
  - README.md  （其中 <your> 替换为：<我的 GitHub 用户名>，联系方式填：<我的飞书或微信>）
  - .gitignore
  - requirements.txt

--- CLAUDE.md 内容开始 ---
<把 Notion 执行卡「[CLAUDE.md](http://CLAUDE.md) 首版」代码块里的全部内容贴这里>
--- CLAUDE.md 内容结束 ---

--- README.md 内容开始 ---
<把 Notion 执行卡「[README.md](http://README.md) 首版」代码块里的全部内容贴这里>
--- README.md 内容结束 ---

--- .gitignore 内容 ---
datasets/
*.mcap
*.parquet
__pycache__/
.venv/
.DS_Store
reports/*.html
--- .gitignore 结束 ---

--- requirements.txt 内容 ---
lerobot>=0.3.0
pandas
numpy
pyarrow
opencv-python
jsonschema
pytest
rosbags
--- requirements.txt 结束 ---

【步骤 4】git add . && git commit -m "init: Sprint 1.1 脚手架 + 数据质量门禁规范"

【输出】完成后给我：
A. tree -L 3 输出
B. wc -l CLAUDE.md README.md
C. git log --oneline
D. 有没有任何地方你躲不过动了文件内容（比如加了自己的注释）？如有请明说。
```
> 💡 ****授权体验优化：** CC CLI 默认每个 bash 命令问一次 (y/n)。熟练后用 `/help` 查当前版本的「批量授权」快捷键（多为 Shift+Tab 切换模式，以你本地版本为准）。**H0-H1 最安全的做法是逐条 y**，犹其是写 [CLAUDE.md](http://claude.md/) 那一步一定要督 diff。**
### 5-10 min：T1 贴 ECS Remote Prompt（同一会话里续贴）
```plain text
【步骤 5】远程触发 ECS 数据下载（我已配置 ssh ecs-host 免密）。请逐条执行并输出每条结果摘要：

1. 配 HF 镜像（幂等，已配跳过）：
   ssh ecs-host 'grep -q HF_ENDPOINT ~/.bashrc || printf "\nexport HF_ENDPOINT=https://hf-mirror.com\nexport HF_HUB_ENABLE_HF_TRANSFER=1\n" >> ~/.bashrc'

2. 检查磁盘 ≥ 5GB：
   ssh ecs-host 'df -BG ~/ | tail -1'

3. 装/升 HF CLI：
   ssh ecs-host 'pip install -U "huggingface_hub[cli]" hf_transfer 2>&1 | tail -3'

4. 后台守护式下载（nohup，断 ssh 不中断）：
   ssh ecs-host 'source ~/.bashrc && mkdir -p ~/datasets && cd ~/datasets && \
     nohup bash -lc "set -e; \
       hf download --repo-type dataset lerobot/pusht --local-dir ./pusht && \
       hf download --repo-type dataset lerobot/svla_so100_pickplace --local-dir ./so100_pickplace; \
       echo DONE >> download.log" > download.log 2>&1 & echo started_pid=$!'

5. 给我一行查进度的命令，我贴到 T2 每 5 min 运行一次：
   echo "ssh ecs-host 'tail -5 ~/datasets/download.log; du -sh ~/datasets/*'"

【输出】每步摘要 + 下载是否启动成功 + 进度查询命令。
```
### 10-15 min：T1 贴 GitHub Push Prompt
```plain text
【步骤 6】我已在 GitHub 建好仓库，URL：git@github.com:gll8209944/claude-code-robotics-playbook.git

请：
1. git remote add origin <url>
2. git push -u origin main
3. 输出仓库 web 链接（https://github.com/gll8209944/claude-code-robotics-playbook）
```
同时 T4 打开 GitHub 仓库页，验证 4 份文件均在、[CLAUDE.md](http://claude.md/) 与 Notion 执行卡逐字一致。
### 15-45 min：等数据期间，CC CLI 不闲着
```plain text
【步骤 7】等 ECS 下载期间（大约 30 min），请预写 2 份本地参考文档（只写文档，不写代码）：

1. docs/decisions.md — Sprint 1.1 决策记录：
   - 仓库可见性：公开
   - 主推数据集：svla_so100_pickplace
   - 联系方式：<填上>
   - 录屏工具：Kap
   - Claude Code 入口：CLI（即你）

2. docs/dev_setup.md — 摘要当前设备分工：Mac 主开发 / 阿里云 ECS 数据后台 / 无影 Ubuntu 兜底 Linux / iPhone 获客 + 应急 ssh / iPad 审稿。按 Sprint 1.1-3.1 列出哪个 Sprint 用哪个设备（参考我在 Notion 执行卡「设备角色分工」章节）。

写完不要 git commit，等我审。
```
同时 **T2** 每 5 min 跑一次进度查询命令。看到 `download.log` 尾部出现 `DONE` 即表示两份数据集都下完。
### 45-55 min：T1 贴 Sync & Verify Prompt
> ⚡ ****数据留 ECS，验证也在 ECS 跑。** 不拉数据回 Mac，直接 SSH 到 ECS 远程验证数据完整性。**
```plain text
【步骤 8】ECS 下载已完成（download.log 含 DONE）。请在 ECS 上远程验证：

1. SSH 到 ECS 远程验证数据完整性：
ssh ecs-host 'python3 -c "
import os, json, glob
for ds_name in [\"pusht\", \"so100_pickplace\"]:
    ds_path = os.path.expanduser(f\"~/datasets/{ds_name}\")
    files = sum(1 for _ in glob.iglob(os.path.join(ds_path, \"**\"), recursive=True))
    size_mb = sum(os.path.getsize(f) for f in glob.iglob(os.path.join(ds_path, \"**\"), recursive=True) if os.path.isfile(f)) / 1024 / 1024
    has_meta = os.path.exists(os.path.join(ds_path, \"meta\", \"info.json\"))
    ep_count = len(glob.glob(os.path.join(ds_path, \"data\", \"*.parquet\"))) if os.path.isdir(os.path.join(ds_path, \"data\")) else \"N/A\"
    print(f\"{ds_name}: {files} files, {size_mb:.0f} MB, meta/info.json={has_meta}, episodes={ep_count}\")
"'

【输出】两个数据集体检小结 + 是否符合 LeRobot 标准格式 + Sprint 1.1 主推数据集是否可用。
```
### 55-60 min：H1 飞行员清单
回 Notion 执行卡「**H1 前最后准备**」章节逐项勾 ✅，所有填空项拍板完成。
---
### 故障兑底（按出现频率排序）
| 现象 | 根因 / 处置 | 替代动作 |
| --- | --- | --- |
| CC CLI 接连失败 / API 超时 | 网络或 anthropic 侧抽动 | `/clear` 后重启；Mac 走 Cloudflare WARP 或 VPN；极端情况下手动执行上面那些 ssh 命令 |
| CC CLI 把 [CLAUDE.md](http://claude.md/) 写「歪」了（自作主张加了注释或改了阈值） | 它在写「规范类」文件时容易加「改进」 | **先停**：让 CC 跑 `git diff CLAUDE.md`、与 Notion 执行卡逐字比对、不一致就 `git checkout` 丢弃重写 |
| ECS 下载速度 < 1 MB/s | hf-mirror 偶发拥塞 | 让 CC 改走 Modelscope：`ssh ecs-host 'pip install modelscope && modelscope download --dataset lerobot/svla_so100_pickplace --local_dir ~/datasets/so100_pickplace'` |
| Mac 装 lerobot 失败（M 系列芯片 native 编译卡） | 原生依赖与 arm64 不兼容 | **让 CC 改 ssh 目标为 wuying-host**，在无影 Ubuntu 上建 conda 环境；Mac 只保留 git/编辑器角色 |
| hf 中途断 | 资源版本变化或网络抖动 | 同命令重跑，HF CLI 默认续传 |
| rsync 卡断 | 网络抖动 | 加 `--partial --append-verify` 重跑（上面 prompt 已含） |
| CC 会话上下文塞满 | H0-H1 拢共不超过 30k tokens，一般够 | 实在不够：`/clear` 后只贴最新一段 prompt，并把已完成步骤截图存档 |
| 忘了某条 prompt 该贴哪 | 站点迷失 | 回本章节，按时间轴手表 ± 5 min 对齐即可 |
> 🛡️ ****最关键的一条防御：** 任何写入 [CLAUDE.md](http://claude.md/) 的内容必须由你逐字与 Notion 执行卡比对一次。[CLAUDE.md](http://claude.md/) 是项目宪法，CC 在后续 100+ 次会话中都会读它；这里写歪了，后面 120h 全部跑偏。**
---
## H1 前最后准备（≈ 3 分钟过一遍）
> 🛫 **这是你按回车启动 Claude Code 之前的最后一道飞行员清单。每项 30 秒以内，全部勾完再发第一段 prompt。**
### 操作清单
- [x] **GitHub 用户名替换：** `gll8209944`（README 里 `<your>` → CC CLI 写文件时替换）
- [x] **联系方式锁定：** ✅ 微信/飞书 13738170552 · 邮箱 [gll8209944@hotmail.com](mailto:gll8209944@hotmail.com)
- [x] **仓库可见性：** ✅ 公开 — [github.com/gll8209944/claude-code-robotics-playbook](http://github.com/gll8209944/claude-code-robotics-playbook)
- [ ] **录屏工具就位：** QuickTime / OBS / Kap 任选其一，提前测一次能录到键盘和终端音
- [x] **Claude Code 入口确认：** ✅ CLI `claude`
- [ ] `**gh**`** CLI（可选但推荐）：** `brew install gh && gh auth login`，后续推送 / 建仓快很多
- [ ] **不被打断的时间块：** H1-H2.5 是 AI 高密度产出窗口，被打断会让自检变形
### 决策项（需要你拍板，不要让 AI 替你决定）
| 决策 | 默认建议 | 你的选择 |
| --- | --- | --- |
| 仓库可见性 | 公开 | ✅ 公开 |
| 主推数据集 | svla_so100_pickplace | ✅ svla_so100_pickplace |
| 联系方式露出 | 微信 + 飞书任选其一 | ✅ 微信/飞书：13738170552 · [邮箱：gll8209944@hotmail.com](mailto:%E9%82%AE%E7%AE%B1%EF%BC%9Agll8209944@hotmail.com) |
| 录屏工具 | Kap（轻、Mac 友好） | ✅ Kap |
| Claude Code 入口 | IDE 插件（VS Code / Cursor） | ✅ CLI `claude` |
### 三件不要做的事
- ❌ 不要在 H1 之前预先写代码 — 所有写代码动作交给 Claude Code，你的工作是审与改
- ❌ 不要边下数据边启动 prompt — 数据下完再启动，否则 AI 会写一堆"等数据可用时"的兜底逻辑浪费上下文
- ❌ 不要同时开多个 Claude Code 会话 — 一个会话打透 `demos/data-quality-gate`，避免上下文污染
---
## 给 Claude Code 的第一个 Prompt（H1-H4 用）
> ⚡ **在仓库根目录启动 Claude Code（`claude` CLI 或 IDE 插件均可），把下面整段一次性粘贴进去。它会以 [CLAUDE.md](http://claude.md/) 为"宪法"自动遵守规范。**
```plain text
请阅读项目根目录的 CLAUDE.md，然后在 demos/data-quality-gate/ 下创建以下脚手架（严格遵守 CLAUDE.md 行为准则）：

1. scripts/run_gate.py — 入口脚本
   - 命令行参数：--dataset <path>（LeRobot 格式数据集路径）、--output <dir>（报告输出目录）、--profile <strict|loose>（默认 strict）
   - 调用 4 个检查模块（见下），收集结果，调用 reporter 生成报告
   - 退出码：0=通过，1=有条件通过，2=拒绝

2. checks/ — 4 个检查模块，每个独立文件 + 独立单测
   - fps_consistency.py：帧率标准差 / 均值，阈值见 CLAUDE.md
   - missing_frames.py：缺帧率
   - multiview_sync.py：多视角时间戳最大偏移
   - task_label.py：任务标签存在性与语言一致性

3. schemas/report.schema.json — 按 CLAUDE.md 报告字段建模的 JSON Schema

4. templates/report.md — Markdown 报告模板，字段 100% 对齐 CLAUDE.md

5. reporter.py — 同时输出 report.json 和 report.md，使用上面两份模板

6. tests/ — 至少 4 个 pytest 单测，每个 check 一个；用 LeRobot 格式的最小 fixture（10 帧 × 2 episodes，可手工伪造 parquet）

7. samples/sample_report.md — 用 datasets/pusht 跑一遍后保存的真实样例报告，作为给客户演示的素材

硬约束：
- 任何外部依赖只能用 CLAUDE.md 已登记的包
- 运行示例命令必须能在 datasets/pusht 上跑通
- 写完后给我一行命令复现整个流程
- 全部脚本中文注释 + 关键函数 docstring

完成后请输出：
A. 文件树（tree -L 3 demos/data-quality-gate）
B. 一行复现命令
C. 在 datasets/pusht 上的实测报告摘要（5 行内，含具体数字）
D. 你认为下一步最该做什么（不超过 3 条）
E. 你在实现过程中违反 CLAUDE.md 的次数（诚实自查）
```
> 🛡️ ****Claude Code 卡住时的 3 句魔法话：**
1. 「请重新读一遍 [CLAUDE.md](http://claude.md/)，然后告诉我你刚才哪一步违反了行为准则」
2. 「先停止写代码。用 5 行中文告诉我现在的实现思路 + 你判断会出问题的地方」
3. 「把刚才的改动 git diff 出来，逐文件解释为什么这么改，我才决定是否合并」**
---
## [CLAUDE.md](http://claude.md/) 自检 Prompt（H1.5 用）
> 🔍 ****什么时候用：** Claude Code 完成第一段 prompt 的所有产出（A-E 五项报告都给出）之后，立即把下面整段贴回去，让它**反向逐条对照 **[**CLAUDE.md**](http://claude.md/)** 自查**。这是抓"假装合规"的关键关卡。**
```plain text
现在请暂停所有新代码改动，进入【自检模式】。

请重新完整读一遍项目根目录的 CLAUDE.md，然后逐项审计你刚才的产出，**带证据举证**。任何"我应该是做了"的回答都不接受 — 必须给出文件路径 + 行号、命令输出或其它具体证据。

【强制审计项】

A. 行为准则 6 条逐条检查：
   1. 小步快跑：任一脚本是否 > 200 行？贴出 `wc -l demos/data-quality-gate/**/*.py` 输出
   2. 测试覆盖：每个脚本是否有配套测试？列出脚本 → 测试的映射表
   3. 双份报告：report.json 和 report.md 是否都真的生成了？贴出文件路径和大小
   4. 路径硬编码：`grep -rn "/Users/\|/home/\|C:\\\\" demos/data-quality-gate` 输出贴出
   5. 提交信息：`git log --oneline` 输出贴出，确认全部中文
   6. 依赖登记：列出所有 import 语句，逐个对比 requirements.txt，是否有未登记项？

B. 数据四级标准是否被代码语义遵守：
   - run_gate 的退出码（0/1/2）与 raw → validated 的语义是否对齐？
   - 拒绝入库（退出码 2）的数据是否被明确标记为 raw 而非误标 validated？

C. 阈值表实现：
   - strict / loose 两套阈值是否都在 checks/ 里实现？
   - 阈值是否集中配置？还是散落在多个文件里硬编码？给出阈值出现的所有位置。

D. 报告字段对齐：
   - report.md 是否包含 CLAUDE.md「报告输出规范」列出的 6 个字段：
     总评 / 数据集概览 / 关键指标表 / Top 3 异常 episode / 修复建议 / 对 VLA 训练的影响
   - 缺哪个？多哪个？

E. 范围纪律：
   - demos/data-quality-gate 之外有没有写任何文件？
   - 是否引入了禁止的依赖？

F. 自报次数核对：
   - 你上一轮自报的"违反 CLAUDE.md 次数"是否准确？
   - 现在重新数一次，与上一轮对比；如不一致，说明哪次更准确以及为什么。

【输出格式】

请按下表逐行作答，每行必须有证据：

| 审计项 | 结论 | 证据（路径:行号 或 命令输出） | 整改动作 |
|---|---|---|---|
| A.1 小步快跑 | ✅/⚠️/❌ | ... | ... |
| A.2 测试覆盖 | ... | ... | ... |
| ... 全部 6+5 项 ... |

最后给出三件事：
1. 必须立即整改的项（阻塞 H4 验收）
2. 可以延后到 Sprint 1.2 整改的项（不阻塞当前 Sprint）
3. 你建议我（人类）此刻额外检查的 1 件事

【禁止】
- 禁止在自检中写新代码或新文件
- 禁止用"应该没问题"等模糊表达
- 任何 ✅ 必须有证据，否则强制降级为 ⚠️
```
> 💡 ****为什么这一步是关键关卡：** Claude Code 在第一轮高强度生成时容易"自我感觉良好但局部违规"。强制 grep 自查 + 重新数违反次数能抓出 80% 的隐藏违规。且这个自检 prompt 模板本身就是你后续所有 Skill / MCP 开发的复用资产 — 一次写好，永久收益。**
---
## H2.5-H6：后续执行剧本（接上文）
> 🗺️ ****接力点：** 上方两段 Prompt 就是 H1-H2.5 的全部执行内容 — 先贴「第一个 Prompt」让 CC CLI 产出脚手架（H1-H2，~30-60 min），再贴「自检 Prompt」让它反向审计（H2-H2.5，~5-15 min）。CC CLI 交出自检审计表后，**从这里接力往下走**。**
---
### 🔧 H2.5-H4：自检整改 + 真实数据门禁
> 💡 ****自检整改：** 自检审计表出来后，根据其中的 ⚠️ / ❌ 项在同一会话中让 CC CLI 逐条修复并提交。具体整改内容取决于实际自检结果，无法预写 Prompt。完成整改后，立即进入真实数据门禁 ↓**
**Phase 1：触发 ECS 并行下载扩展数据集（整改完成后立即贴）**
> 🎯 ****为什么要扩展：** pusht 和 so100_pickplace 都是官方精选数据集，质量太好 — strict 门禁全通过，文章没有「发现真实问题」的素材，说服力不足。需要拉社区/OXE 子集数据，大概率能抓到帧率不一致、标签缺失等真实质量问题。**
```plain text
【扩展数据集下载】请在 ECS 上后台下载以下社区 / OXE 数据集（与本地门禁并行）：

ssh ecs-host 'source ~/.bashrc && cd ~/datasets && \
  nohup bash -lc "set -e; \
    echo "[1/4] cadene/koch_bimanual_folding" && \
    hf download --repo-type dataset cadene/koch_bimanual_folding --local-dir ./koch_bimanual_folding && \
    echo "[2/4] lerobot/aloha_static_coffee" && \
    hf download --repo-type dataset lerobot/aloha_static_coffee --local-dir ./aloha_static_coffee && \
    echo "[3/4] lerobot/columbia_cairlab_pusht_real" && \
    hf download --repo-type dataset lerobot/columbia_cairlab_pusht_real --local-dir ./columbia_cairlab_pusht_real && \
    echo "[4/4] lerobot/utokyo_xarm_bimanual_converted" && \
    hf download --repo-type dataset lerobot/utokyo_xarm_bimanual_converted --local-dir ./utokyo_xarm_bimanual_converted && \
    echo ALL_EXT_DONE >> download_ext.log" > download_ext.log 2>&1 &'

进度查询命令
ssh ecs-host 'tail -5 ~/datasets/download_ext.log; du -sh ~/datasets/{koch_bimanual_folding,aloha_static_coffee,columbia_cairlab_pusht_real,utokyo_xarm_bimanual_converted} 2>/dev/null'
```
**扩展数据集选择逻辑：**
| 数据集 | 体积 | 选择理由 | 预期能抓到的问题 |
| --- | --- | --- | --- |
| `cadene/koch_bimanual_folding` | ~1-2 GB | 社区个人上传，双臂折叠任务 | 帧率不一致、任务标签格式不规范 |
| `lerobot/aloha_static_coffee` | ~2-3 GB | ALOHA 双臂，执行卡原备选 | 多视角时间戳偏移 |
| `lerobot/columbia_cairlab_pusht_real` | ~500 MB | 真实机器人版 pusht（vs 仿真版） | 真实采集 vs 仿真的帧率对比，可能有缺帧 |
| `lerobot/utokyo_xarm_bimanual_converted` | ~1-2 GB | OXE 转换格式，东京大学 | 格式转换时的元数据丢失、时间戳精度降级 |
> 💡 ****如果某个数据集名字有变或下载失败：** 去 [huggingface.co/lerobot](http://huggingface.co/lerobot) 搜同类关键词替换。核心目标是拿到至少 1 个「能抓出质量问题」的数据集。社区个人上传的数据集（非 lerobot 官方组织）质量问题概率最高。**
---
**Phase 2：在 ECS 上对 pusht + so100 跑基准门禁**
> ⚡ ****数据留 ECS，门禁也在 ECS 跑。** 先 Mac push 代码，然后 SSH 到 ECS 拉代码 + 跑门禁，最后 ECS push 报告回 GitHub，Mac pull 报告。**
```plain text
现在在 ECS 上对两份已有数据集跑完整门禁，使用 strict 配置：

【1】先把最新代码推到 GitHub：
git add -A && git commit -m "feat: 门禁脚手架" && git push

【2】SSH 到 ECS，拉代码 + 装依赖 + 跑门禁：
ssh ecs-host 'cd ~/work/claude-code-robotics-playbook && git pull && \
  pip install -r requirements.txt && \
  python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ~/datasets/pusht \
    --output demos/data-quality-gate/reports/pusht \
    --profile strict && \
  python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ~/datasets/so100_pickplace \
    --output demos/data-quality-gate/reports/so100_pickplace \
    --profile strict && \
  git add demos/data-quality-gate/reports/ && \
  git commit -m "data: pusht + so100 门禁报告" && git push'

【3】Mac 上拉报告回来：
git pull

【4】简要摘要：
A. pusht exit_code + 关键指标（1 行）
B. so100_pickplace exit_code + 关键指标（1 行）
C. 说 "基准门禁完成，等 ECS 扩展数据集下载完毕"
```
---
**Phase 3：扩展数据集拉回 + 全量横评门禁**
> ⚡ ****触发时机：** ECS 上 `download_ext.log` 出现 `ALL_EXT_DONE` 后贴此 Prompt。**
```plain text
扩展数据集下载完成。请执行：

【1】在 ECS 上对所有扩展数据集跑门禁（数据不拉回 Mac）：
ssh ecs-host 'cd ~/work/claude-code-robotics-playbook && git pull && \
  for ds in koch_bimanual_folding aloha_static_coffee columbia_cairlab_pusht_real utokyo_xarm_bimanual_converted; do
    echo "=== 检测: $ds ==="
    python demos/data-quality-gate/scripts/run_gate.py \
      --dataset ~/datasets/$ds \
      --output demos/data-quality-gate/reports/$ds \
      --profile strict
    echo ""
  done && \
  git add demos/data-quality-gate/reports/ && \
  git commit -m "data: 6数据集全量横评报告" && git push'

【2】Mac 上拉报告回来：
git pull

【3】输出全量横评对比表（这是文章的核心素材）：

请按以下格式输出：

A. 六个数据集横评总表：
| 数据集 | exit_code | 帧率CV | 缺帧率 | 多视角偏移 | 标签缺失率 | 异常帧率 | 总评 |
（帧率 CV = 帧率标准差/均值，即变异系数）

B. 🔴 问题数据集深挖（exit_code != 0 或任一指标 ⚠️ 的数据集）：
   - 具体哪些 episode 有问题？
   - 问题模式是什么？（如：前 N 帧采集速率异常 / 某个视角丢帧 / 标签语言不一致）
   - 对 VLA 训练的具体影响（如：帧率抖动导致 action chunk 时间轴错位）

C. 🟢 好数据 vs 🔴 问题数据对比摘要（3 行内，给文章用）

D. 你建议文章重点展示哪 2-3 个数据集的对比？为什么？

完成后 say "全量横评门禁跑完了"
```
**预期结果与文章素材策略：**
- **官方精选数据集**（pusht、so100_pickplace）大概率全绿 ✅ → 作为「好数据」的基准线
- **社区/转换数据集**（koch_bimanual、columbia_real、utokyo_converted）大概率出 ⚠️ 或 ❌ → 作为「发现真实问题」的素材
- **文章叙事线：**「我们的门禁在 6 个公开数据集上跑了一遍，官方精选数据全绿，但社区上传和格式转换的数据集暴露了 X、Y、Z 问题 — 这些问题如果不拦截，直接喂给 VLA 训练会导致……」
---
### 🎬 H4-H5：录屏 + 最终整改提交
> 🎯 ****目标：** 产出 30-60 秒的演示 GIF，作为文章封面素材。同时完成代码最终提交。**
> 🧭 ****CC CLI 能力边界：** 录屏是 GUI 操作，CC CLI 无法控制 Kap/QuickTime/OBS，也无法让命令渲染到你的终端画面。因此本阶段分为 **CC CLI 自动段**（安装、预验证、生成提词卡、文件整理、git 提交）和 **人类手动段**（录屏那 10 分钟）。约 60% 工作量可交给 CC CLI。**
Phase A — CC CLI 自动段：安装 + 预验证 + 生成提词卡（10 min）
在 CC CLI 主会话中贴下面的 Prompt：
```plain text
请按顺序执行以下准备工作：

【1】安装 Kap（幂等，已装跳过）：
brew install --cask kap

【2】SSH 到 ECS 预跑一次门禁，确认无报错（确认 exit_code=0 即可）：
ssh ecs-host 'cd ~/work/claude-code-robotics-playbook && git pull && \
  python demos/data-quality-gate/scripts/run_gate.py \
    --dataset ~/datasets/so100_pickplace \
    --output demos/data-quality-gate/reports/so100_pickplace \
    --profile strict'

【3】生成录屏提词卡 docs/recording-script.sh：
内容为纯注释 + 可直接复制粘贴的命令，按以下顺序：
  a. clear
  b. tree -L 2 demos/data-quality-gate/     # 展示仓库结构，停 3 秒
  c. python demos/data-quality-gate/scripts/run_gate.py --dataset ./datasets/so100_pickplace --output ./reports --profile strict    # 等指标逐行 ✅ 弹出
  d. cat reports/report.md | head -40       # 展示报告，停 2 秒
每条命令上方加一行中文注释说明「此刻画面应该展示什么」。

【4】输出：
A. 预跑门禁 exit_code
B. cat docs/recording-script.sh 全文
C. 提醒我接下来该做什么（人类手动段）
```
Phase B — 人类手动段：录屏（10 min）
> 🎬 ****此阶段 CC CLI 不参与。** 你亲自在终端里操作，Kap 录你的屏幕。**
**操作步骤：**
1. 终端字号调大到 **16-18pt**（Preferences → Profiles → Text）
1. 打开 Kap → 选择录制区域（只框终端窗口）→ 点击录制
1. 打开 `docs/recording-script.sh`，**逐行复制粘贴命令到终端执行**：
  - `clear`
  - `tree -L 2 demos/data-quality-gate/` → 停 3 秒
  - `python demos/data-quality-gate/scripts/run_gate.py --dataset ./datasets/so100_pickplace --output ./reports --profile strict` → 等指标逐行弹出 + exit_code=0
  - `cat reports/report.md | head -40` → 停 2 秒
1. 点击 Kap 停止录制 → 导出 **GIF**（文章用）+ **MP4**（备用高清）
1. 将 GIF 文件拖到项目目录：`demos/data-quality-gate/samples/demo.gif`
**录屏技巧：**
- 提前 `clear`，避免录到无关内容
- 全程 30-60 秒即可，不要拖
- 如果中间命令报错，停止录制、修复后重录（不要带着报错发布）
Phase C — CC CLI 自动段：文件整理 + 最终提交（5 min）
录屏完成、GIF 已放到 `demos/data-quality-gate/samples/` 后，回到 CC CLI 贴：
```plain text
请执行最终提交：

【1】确认 GIF 存在：
ls -lh demos/data-quality-gate/samples/demo.gif

【2】清理临时文件（如有）：
rm -f reports/report.json reports/report.md   # 临时输出目录，正式报告在 demos/ 下

【3】提交并推送：
git add -A && git commit -m "feat: 真实数据门禁报告 + 演示录屏素材" && git push

【4】输出：
A. git log --oneline -5
B. du -sh demos/data-quality-gate/samples/demo.gif
C. 确认 GitHub 仓库可访问
```
时间轴总览
| 时段 | 执行者 | 内容 | 耗时 |
| --- | --- | --- | --- |
| Phase A | **CC CLI** | 安装 Kap + 预跑门禁 + 生成录屏提词卡 | 10 min |
| Phase B | **人类** | 打开 Kap → 照提词卡录屏 → 导出 GIF | 10 min |
| Phase C | **CC CLI** | 确认 GIF + 清理 + git commit + push | 5 min |
---
### ✍️ H5-H6：写文章 + 挂早鸟价
> 🎯 ****目标：** ≥1500 字的第一篇文章草稿 + ¥199 早鸟价至少挂 1 个渠道。**
Step 1（30 min）：写文章草稿
**标题：** 《我用 Claude Code 给机器人数据采集加了一道质量门禁 — 6 个公开数据集横评实录》
**CC CLI 写文章 Prompt：**
```plain text
请在 docs/ 目录下创建 article-sprint-1.1.md，写一篇技术博文草稿。

要求：
- 标题：我用 Claude Code 给机器人数据采集加了一道质量门禁 — 6 个公开数据集横评实录
- 字数 ≥ 2000 字，中文为主
- 目标读者：机器人研发工程师 / AI 工程师 / 对 Claude Code 感兴趣的开发者
- 语气：实战经验分享，不是教程，不是广告

文章结构：
1. 【痛点引入】（300字）机器人数据采集的质量问题有多普遍？先讲「我们在 6 个公开数据集上跑了一遍门禁，官方精选数据全绿，但社区上传和格式转换的数据集暴露了 X、Y、Z 问题」作为钩子，然后展开背景：大量团队直接拿 HuggingFace 数据喂 VLA 训练，从不做质量校验，踩过哪些坑。
2. 【我做了什么】（300字）用 Claude Code CLI 在 6 小时内生成了一套完整的数据质量门禁系统：4 个检查模块 + 双份报告 + 自检审计 + 6 个数据集横评
3. 【门禁设计】（400字）5 项检查指标的选择逻辑 + strict/loose 双配置 + 数据四级标准（raw→validated→curated→training）
4. 【6 数据集横评实录】（500字，文章核心高潮）
   请读取 demos/data-quality-gate/reports/ 下所有 6 个数据集的报告，输出：
   a. 六数据集横评总表（exit_code / 帧率CV / 缺帧率 / 多视角偏移 / 标签缺失率 / 总评）
   b. 🟢 好数据代表（pusht / so100_pickplace）的关键指标
   c. 🔴 问题数据集深挖：具体哪些 episode 出问题、问题模式是什么、对 VLA 训练的具体影响
   d. 一段「如果不做门禁，这些问题数据直接进训练会怎样」的分析
   6 个数据集：pusht, svla_so100_pickplace, koch_bimanual_folding, aloha_static_coffee, columbia_cairlab_pusht_real, utokyo_xarm_bimanual_converted
5. 【Claude Code 体验】（200字）CC CLI 的工作模式：人类下达 → AI 执行 → 人类审 diff → 自检审计闭环。6 小时内完成从零到「6 数据集横评报告」的全流程。
6. 【下一步 & 服务】（100字）Sprint 1.2 部署前体检预告 + ¥199 早鸟诊断服务

关键素材（请融入文中）：
- 六数据集横评总表（从 reports/ 读取真实数据，不要编造数字）
- 🟢 vs 🔴 数据集对比叙事（官方精选 vs 社区上传 vs 格式转换）
- 问题数据集的具体 episode 案例 + 对 VLA 训练的影响分析
- CLAUDE.md 自检审计表（精简版，2-3 行即可）
- 门禁报告截图描述（文字描述即可，实际图片我后续插入，用 <!-- IMG: xxx --> 标注插入位置）
- 录屏 GIF 插入位置标注

写作要点：
- 横评结果是文章最大卖点，要用数据说话，不要空泛
- 「连 XXX 这种知名数据集都有问题」的叙事比「我们做了个工具」更有传播力
- 如果某个数据集全绿且另一个有问题，用对比强化冲击力

写完不要 commit，等我审。
```
Step 2（15 min）：审稿 + 插入录屏 GIF
- iPad 上打开 docs/[article-sprint-1.1.md](http://article-sprint-1.1.md/) 审阅
- 在文章中标注 GIF 插入位置：`![demo](../demos/data-quality-gate/samples/demo.gif)`
- 调整措辞、数据准确性、删掉 AI 味过重的表达
- CC CLI 提交：`git add -A && git commit -m "docs: Sprint 1.1 第一篇文章草稿" && git push`
Step 3（15 min）：挂 ¥199 早鸟价
**至少 1 个渠道（按优先级）：**
1. **朋友圈**（iPhone）：发一条带录屏 GIF + 文字的朋友圈
> 「用 Claude Code 给机器人数据采集加了一道质量门禁 🤖
> XX 分钟出完整工具 + 自检，附真实数据报告。
> 早鸟服务：¥199 / 45min 在线诊断你的机器人数据 / 部署 / VLA 痛点。
> 预约：微信 <手机号> · 邮箱 <邮箱>」
1. **飞书群**：如果有相关技术群，转发同样内容
1. **知乎签名**：改为「机器人 AI 化诊断 ¥199 → 微信 <手机号>」
1. **GitHub README**：确认服务定价表和联系方式已更新
---
### 🏁 H6 验收（Sprint 1.1 完结）
> 📌 ****Sprint 1.1 死线：** H6 时逐项对照验收清单。若任一缺失，立即停下复盘 — 绝不允许 H6 之后还在写代码，否则 Sprint 1.2 直接被压缩，120h 冲刺会塌方。**
**验收清单对照：**
- [ ] `data-quality-gate` 在真实 LeRobot 数据上跑通，输出 JSON + Markdown 双份报告
- [ ] GitHub 仓库含 [CLAUDE.md](http://claude.md/) / README / demo 目录 → 检查 git log + 仓库页面
- [ ] 第一篇文章草稿 ≥1500 字 + 1 段录屏 GIF → 检查 docs/[article-sprint-1.1.md](http://article-sprint-1.1.md/) 字数
- [ ] ¥199 早鸟价至少 1 个渠道 → 截图存档到 Notion
**如果 H6 未完成怎么办：**
- 文章没写完 → 降级为 800 字短文 + 录屏 GIF，先发出去再迭代
- 录屏没录 → 截图代替 GIF，文章改为纯文字版
- 早鸟价没挂 → 先发朋友圈（最快 2 分钟），其他渠道延后
- 代码有 bug → 冻结代码，带 bug 发文章（诚实说明"这是 Sprint 1.1 产出，已知限制见 XX"）
- [Sprint 1.1 决策记录](docs/notion-sync/Sprint 1.1 决策记录.md)
- [设备角色分工](docs/notion-sync/设备角色分工.md)