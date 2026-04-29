# 机器人部署体检报告

## 部署总评

**❌拒绝部署** | 退出码：`2` | 时间：`2026-04-29T12:28:58.868289`

---

## 机器人概览

| 字段 | 值 |
|---|---|
| 型号 | N/A |
| 序列号 | N/A |
| 固件版本 | N/A |

---

## 五项检查详情

| # | 检查项 | 状态 | 详情 |
|---|---|---|---|
| 1 | URDF 完整性 | ❌ FAIL | [FAIL] base_link 存在: base_link 不存在（应为 'base_link'，注意大小写）; [FAIL] 悬挂 link 检查: 发现悬挂 link（无 joint 引用）：['sensor_orphan']; [FAIL] collision 定义: 以下 link 缺失 collision：['base_Link', 'right_wheel_link', 'lidar_link', 'sensor_orphan'] |
| 2 | TF 树连通性 | ❌ FAIL | [FAIL] TF 全链路: 链路断裂：['断裂：odom → base_link 不连通']; [PASS] 环路检测: 无环路 |
| 3 | Nav2 参数合理性 | ❌ FAIL | [PASS] use_sim_time: use_sim_time=false（正确，实机部署）; [FAIL] max_vel_x: max_vel_x=5.0（危险，>1.5）; [FAIL] max_vel_theta: max_vel_theta=4.0（危险，>3.0）; [FAIL] inflation_radius: inflation_radius=0.01（危险，<0.15）; [FAIL] controller_frequency: controller_frequency=5.0Hz（危险，<10Hz） |
| 4 | E-stop 配置 | ❌ FAIL | [FAIL] 启用状态: E-stop 未启用（enabled=false 或缺失），不允许部署; [FAIL] 急停 topic: 急停 topic 未定义（需指定如 /emergency_stop）; [FAIL] 硬件引脚: 硬件引脚未映射（需指定 hardware.pin）; [FAIL] 急停链路: 急停链路未定义（chain 为空）; [FAIL] 响应时间: 急停响应时间未配置（需指定 estop.max_response_time_ms 或 estop.hardware.max_response_time_ms） |
| 5 | 传感器标定 | ❌ FAIL | [FAIL] 标定时效: 标定文件已过期 210 天（危险，>90天）; [PASS] 标定日期字段: 标定日期：2025-10-01; [PASS] 内参矩阵: 相机内参有效（fx=615.0, fy=615.0） |

---

## Top 3 风险项

### 1. URDF 完整性
- **风险描述**：base_link 不存在（应为 'base_link'，注意大小写）
- **后果**：可能导致部署失败

### 2. TF 树连通性
- **风险描述**：链路断裂：['断裂：odom → base_link 不连通']
- **后果**：可能导致部署失败

### 3. Nav2 参数合理性
- **风险描述**：use_sim_time=false（正确，实机部署）
- **后果**：可能导致部署失败



---

## 修复建议优先级

### P1：URDF 完整性
**动作**：检查并修复该配置项

**为什么**：该问题会直接影响机器人正常功能

### P2：TF 树连通性
**动作**：检查并修复该配置项

**为什么**：该问题会直接影响机器人正常功能

### P3：Nav2 参数合理性
**动作**：检查并修复该配置项

**为什么**：该问题会直接影响机器人正常功能

### P4：E-stop 配置
**动作**：检查并修复该配置项

**为什么**：该问题会直接影响机器人正常功能

### P5：传感器标定
**动作**：检查并修复该配置项

**为什么**：该问题会直接影响机器人正常功能



---

## 与上次体检的差异对比

*（首次体检，无对比数据）*
