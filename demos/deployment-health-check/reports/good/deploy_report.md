# 机器人部署体检报告

## 部署总评

**✅可部署** | 退出码：`0` | 时间：`2026-04-29T12:28:58.805960`

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
| 1 | URDF 完整性 | ✅ PASS | [PASS] base_link 存在: base_link 存在; [PASS] 悬挂 link 检查: 无悬挂 link; [PASS] collision 定义: 所有 link 均定义 collision |
| 2 | TF 树连通性 | ✅ PASS | [PASS] TF 全链路: map→odom→base_link→sensors 全链路连通; [PASS] 环路检测: 无环路 |
| 3 | Nav2 参数合理性 | ✅ PASS | [PASS] use_sim_time: use_sim_time=false（正确，实机部署）; [PASS] max_vel_x: max_vel_x=0.5（安全，≤0.8）; [PASS] max_vel_theta: max_vel_theta=1.0（安全，≤1.5）; [PASS] inflation_radius: inflation_radius=0.35（安全，≥0.3）; [PASS] controller_frequency: controller_frequency=20.0Hz（安全，≥20Hz） |
| 4 | E-stop 配置 | ✅ PASS | [PASS] 启用状态: E-stop 已启用; [PASS] 急停 topic: 急停 topic 已定义：/emergency_stop; [PASS] 硬件引脚: 硬件引脚已映射：GPIO_17; [PASS] 急停链路: 急停链路完整，共 3 级; [PASS] 响应时间: 急停响应时间 50ms（安全，≤50ms） |
| 5 | 传感器标定 | ✅ PASS | [PASS] 标定时效: 标定文件 28 天前更新（安全，≤30天）; [PASS] 标定日期字段: 标定日期：2026-04-01; [PASS] 内参矩阵: 相机内参有效（fx=615.0, fy=615.0） |

---

## Top 3 风险项

*（无高风险项）*

---

## 修复建议优先级

*（无需修复）*

---

## 与上次体检的差异对比

*（首次体检，无对比数据）*
