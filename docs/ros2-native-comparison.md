# ROS2 原生工具对比验证

## 测试时间
2026-04-29

## 测试配置
- Good: `demos/deployment-health-check/configs/good/`
- Bad: `demos/deployment-health-check/configs/bad/`

## 结果对比

| 检查项 | Good (ROS2) | Good (CC) | Bad (ROS2) | Bad (CC) |
|--------|-------------|-----------|------------|----------|
| URDF 解析 | ✅ PASS | ✅ PASS | ❌ FAIL (两个 root link) | ❌ FAIL |
| Nav2 参数 | N/A | ✅ PASS | N/A | ❌ FAIL (速度/频率超限) |
| E-stop | N/A | ✅ PASS | N/A | ❌ FAIL (未配置) |
| 传感器标定 | N/A | ✅ PASS | N/A | ❌ FAIL (过期210天) |

## ROS2 原生工具输出

### Good URDF
```
robot name is: my_robot
---------- Successfully Parsed XML ---------------
root Link: base_link has 4 child(ren)
    child(1):  camera_link
    child(2):  left_wheel_link
    child(3):  lidar_link
    child(4):  right_wheel_link
```

### Bad URDF
```
Error:   Failed to find root link: Two root links found: [base_Link] and [sensor_orphan]
         at line 264 in ./urdf_parser/src/model.cpp
ERROR: Model Parsing the xml failed
```

## 结论

- **一致性好**: ROS2 原生工具与 CC 体检结论完全一致
- **CC 更全面**: CC 体检覆盖 URDF、Nav2 参数、E-stop、传感器标定等多维度
- **ROS2 工具专项**: check_urdf 仅验证 URDF 语法和结构，无法检测业务参数合理性
- **互补关系**: ROS2 原生工具可作为 CC 体检的底层验证补充

## 结论
✅ ROS2 对比验证完成
