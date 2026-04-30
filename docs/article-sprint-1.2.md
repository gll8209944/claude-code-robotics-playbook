# 机器人现场部署少返工：Claude Code 帮我做了一份部署体检报告

**副标题：5 项自动检查 + 一份"好配置 vs 坏配置"对比报告，给你看看部署前到底该查什么**

---

## 【痛点引入】到了现场才发现问题，一切都晚了

机器人部署这件事，有一个特别要命的场景：**到了客户现场才发现问题**。

我见过最典型的一次：一个全向底盘机器人运到工厂，工程师花了 2 小时架设基站、调试导航参数，一切就绪后启动——然后机器人疯狂撞墙。排查了半天才发现：TF 树里 `odom` 到 `base_link` 的 transform 链路断了，AMCL 定位漂移到地图外。工厂停工半天，工程师机票改签，项目差点延期三个月。

这不是个例。机器人部署失败的现场问题清单可以列很长：

- URDF 里 `base_link` 大小写写错，`rviz` 里模型直接消失
- `max_vel_x` 设成 5.0 m/s，机器人启动直接飞出去
- E-stop 急停链路没配置，现场人员安全完全没有保障
- 相机标定过期 200 天，深度图像畸变到无法用，导航精度劣化 50%

每一次都是"到了现场才发现"，每一次都是返工、延期、甚至安全事故。

我的解法是：**在部署之前，用 Claude Code 做一套自动部署体检工具，跑完 5 项检查再发车**。

<!-- IMG: ../demos/deployment-health-check/samples/demo.gif -->

---

## 【五项体检设计】每一项都是真实现场踩过的坑

为什么选这 5 项？因为每一项都在真实项目中让人付出过代价。

### 1. URDF 完整性

URDF 是机器人模型的"户口本"——定义了所有的 link、joint、碰撞体、视觉体。常见错误包括：

- `base_link` 大小写写错（`base_Link` vs `base_link`），TF 树加载直接失败
- 某个 link 没有被任何 joint 引用（"悬挂 link"）， rviz 里模型缺胳膊少腿
- collision 缺失，导航规划器和物理引擎行为不一致

URDF 的问题在仿真阶段往往不报错，直到实机部署时才暴露——因为仿真器有时会容错，但实机的 TF 广播器不会。

### 2. TF 树连通性

机器人定位的完整链路是：`map → odom → base_link → sensors`。这条链路断了，导航定位就直接失效。

常见断裂场景：
- 中间的 `odom → base_link` publisher 没启动
- 多机器人时 TF 命名冲突导致覆盖
- 某些 sensor frame 没有正确发布

断裂的 TF 树在现场表现为：机器人"认为自己在哪里"和"实际在哪里"完全不符，路径规划方向对但机器人往反方向走。

### 3. Nav2 参数合理性

Nav2 是 ROS2 机器人的标准导航栈。参数越界是机器人飞车最常见的原因。

**Nav2 三级阈值（我跑通的安全值）：**

| 指标 | 安全值 | 警告值 | 危险值 |
|---|---|---|---|
| max_vel_x (m/s) | ≤ 0.8 | 0.8–1.5 | > 1.5 |
| max_vel_theta (rad/s) | ≤ 1.5 | 1.5–3.0 | > 3.0 |
| inflation_radius (m) | ≥ 0.3 | 0.15–0.3 | < 0.15 |
| controller_frequency (Hz) | ≥ 20 | 10–20 | < 10 |

`inflation_radius` 过小是最容易踩的坑——设成 0.01 米意味着障碍物膨胀区几乎为零，路径规划会贴着障碍物走，一压到障碍物就停。

### 4. E-stop 急停配置

这是唯一一项与安全直接相关的检查。急停链路必须完整：硬件按钮 → 安全控制器 → 电机驱动器，响应时间必须 ≤ 100ms。

没有配置 E-stop 的机器人，在现场人员进入工作区域时没有任何保护手段。这是**不允许部署**的。

### 5. 传感器标定时效性

相机内参（焦距、主点、畸变系数）和激光雷达外参会随机械结构变化而漂移。超过 90 天未重新标定的传感器，定位精度会明显下降。

我自己实测过：一个标定过期 180 天的相机，深度图像误差达到 15cm，完全无法用于精确导航。

---

## 【好配置 vs 坏配置对比实录】工具到底能不能检出问题？

光说设计不够看，下面是真实跑出来的对比结果。

### good 配置（全部 PASS）

| 检查项 | 状态 | 详情 |
|---|---|---|
| URDF 完整性 | ✅ PASS | base_link 存在 / 无悬挂 link / collision 完整 |
| TF 树连通性 | ✅ PASS | map→odom→base_link→sensors 全链路连通 |
| Nav2 参数 | ✅ PASS | vel_x=0.5(≤0.8✅) / theta=1.0(≤1.5✅) / inflation=0.35(≥0.3✅) / freq=20Hz(≥20Hz✅) |
| E-stop 配置 | ✅ PASS | 已启用 / topic=/emergency_stop / 响应时间 50ms(≤50ms✅) |
| 传感器标定 | ✅ PASS | 标定 28 天前(≤30天✅) / 内参有效(fx=615,fy=615) |

**总评：✅ 可部署（exit_code=0）**

### bad 配置（5 项全部 FAIL）

| 检查项 | 状态 | 植入的错误 |
|---|---|---|
| URDF 完整性 | ❌ FAIL | `base_link` 写成 `base_Link`（大小写）；悬挂 link `sensor_orphan`；4 个 link 缺 collision |
| TF 树连通性 | ❌ FAIL | 缺失 `odom → base_link` transform |
| Nav2 参数 | ❌ FAIL | vel_x=5.0（危险>1.5）/ theta=4.0（危险>3.0）/ inflation=0.01（危险<0.15）/ freq=5Hz（危险<10Hz）|
| E-stop 配置 | ❌ FAIL | `enabled=false`；无 topic/引脚/链路/响应时间 |
| 传感器标定 | ❌ FAIL | calibration_date=2025-10-01（过期 210 天）|

**总评：❌ 拒绝部署（exit_code=2）**

### 事故场景还原

如果不修复直接部署，会发生什么？

**URDF 大小写错误 → 机器人模型消失**
rviz 加载 URDF 时找不到 `base_link`，TF 树直接断裂，所有依赖 TF 的功能（定位、导航、避障）全部失效。在 rviz 里看不到机器人模型，在 Gazebo 里机器人"隐形"。

**TF 树断链 → 导航定位漂移**
AMCL 可以工作，但 `odom → base_link` 不通，机器人不知道自己在哪里。它会在地图里"瞬移"，导航规划器给出的路径方向对但执行方向随机。**工厂里这意味着机器人撞墙或者原地打转。**

**Nav2 参数越界 → 机器人飞车**
`max_vel_x=5.0 m/s` 是安全速度的 6 倍多，机器人启动后会直接冲出安全区域。`inflation_radius=0.01` 意味着路径规划贴着障碍物走，稍微有一点定位误差就会触发碰撞。**工厂里这可能造成设备损坏和人员伤害。**

**E-stop 未配置 → 无任何安全保护**
急停按钮无效，硬件失控时没有办法强制停车。**这是最不可接受的一项，任何工厂安规都不会允许这样的机器人进场。**

### TF 树 ASCII 对比

**正确的树（good）：**
```
map
└── odom
    └── base_link
        ├── lidar_link
        ├── camera_link
        ├── left_wheel_link
        └── right_wheel_link
```

**断裂的树（bad）：**
```
map
└── odom
（断裂：odom → base_link 不连通）
base_link  ← 孤立，TF 树中没有上游连接
    └── lidar_link
```

---

## 【第一个 MCP Server】用 Claude Code 直接对话机器人数据

Sprint 1.2 的另一个产出是启动了第一个机器人 MCP Server：**rosbag-inspector**。

MCP（Model Context Protocol）是 Claude Code 的扩展协议，允许大模型直接调用外部工具。rosbag-inspector 就是这样一个工具：接入 Claude Code 后，可以直接用自然语言查询 rosbag 文件。

### 一行配置接入 Claude Code

在 Claude Code 的 MCP 设置中加入：

```json
{
  "mcpServers": {
    "rosbag-inspector": {
      "command": "python3.11",
      "args": ["/path/to/mcp-servers/rosbag-inspector/server.py"]
    }
  }
}
```

重启后就可以用 `inspect_rosbag` 这个 tool 查询任意 rosbag 文件。

### inspect_rosbag 返回格式

```json
{
  "status": "success",
  "data": {
    "format": "mcap",
    "file_size_bytes": 123456789,
    "topic_count": 3,
    "total_messages": 15230,
    "duration_seconds": 60.5,
    "start_timestamp": 1700000000.0,
    "end_timestamp": 1700000060.5,
    "topics": [
      {
        "topic": "/scan",
        "message_type": "sensor_msgs/LaserScan",
        "message_count": 605,
        "avg_frequency_hz": 10.0
      },
      {
        "topic": "/odom",
        "message_type": "nav_msgs/Odometry",
        "message_count": 6050,
        "avg_frequency_hz": 100.0
      }
    ]
  },
  "errors": []
}
```

返回格式统一为 `{ status, data, errors }`，错误不 raise 而是通过 errors 数组返回——这是 MCP Server 的统一规范，任何 tool 都应该遵守。

---

## 【Claude Code 体验】两个闭环的共同模式

Sprint 1.1 我做了数据质量门禁，Sprint 1.2 做了部署体检。两个 Sprint 有一个共同的底层模式：

**CLAUDE.md 宪法 + 检查模块 + 双份报告 + 自检审计**

**CLAUDE.md 宪法**：项目行为准则全部写进 CLAUDE.md，每次写代码前先读一遍。准则包括小步快跑（脚本不超过 200 行）、测试先行（每个功能配套测试）、报告双份（JSON + Markdown）等。

**检查模块独立**：每个检查项（URDF、TF 树、Nav2 参数、E-stop、标定）都是独立文件，可以单独运行。这符合单一职责原则，也方便定位问题。

**双份报告**：一份 JSON 给工程系统消费（CI/CD 接入），一份 Markdown 给人类阅读（报告存档）。两份报告字段完全对齐。

**自检审计**：每个 Sprint 结束后，用审计 Prompt 逐条对照 CLAUDE.md 自查——有几条违反？证据是什么？这是一种强制性的反思机制，防止代码和规范逐渐脱节。

---

## 【下一步 & 服务】

### Sprint 1.3 预告

Sprint 1.3 会做 VLA（Vision-Language-Action Model）训练复盘：机器人采集数据训练 VLA 后，如何评估模型效果、如何发现训练过程中的问题。同样会遵循 CLAUDE.md 宪法 + 检查闭环的模式。

### 服务推广

如果你的机器人项目正在经历部署返工、数据质量不稳定、VLA 训练效果不达预期，欢迎预约**单点闭环诊断服务**：

**¥999 / 2 小时**（数据 / 部署 / VLA 三选一）

我会用这套 CLAUDE.md 宪法 + 检查闭环的方法论，帮你定位根因、出具诊断报告。

预约：微信 13738170552 · gll8209944@hotmail.com

---

**相关产出：**

- 部署体检工具：[demos/deployment-health-check/](https://github.com/gll8209944/claude-code-robotics-playbook/tree/main/demos/deployment-health-check)
- rosbag-inspector MCP：[mcp-servers/rosbag-inspector/](https://github.com/gll8209944/claude-code-robotics-playbook/tree/main/mcp-servers/rosbag-inspector)
- 数据质量门禁：[demos/data-quality-gate/](https://github.com/gll8209944/claude-code-robotics-playbook/tree/main/demos/data-quality-gate)
