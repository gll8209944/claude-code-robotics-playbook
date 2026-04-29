#!/usr/bin/env python3
"""
部署体检测试套件
每个检查模块对应至少 1 个测试，覆盖 PASS 和 FAIL 两种 case。
"""

import sys
from pathlib import Path

# 将 demos/deployment-health-check 加入 path（便于 imports）
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import tempfile
import shutil


# ===== 测试数据 fixtures =====

@pytest.fixture
def good_config_dir():
    """正确配置目录（应全部 PASS）。"""
    tmp = Path(tempfile.mkdtemp())

    # URDF
    urdf_dir = tmp / 'urdf'
    urdf_dir.mkdir()
    (urdf_dir / 'robot.urdf').write_text('''<?xml version="1.0" ?>
<robot name="test">
  <link name="base_link">
    <visual><geometry><box size="0.5 0.4 0.2"/></geometry></visual>
    <collision><geometry><box size="0.5 0.4 0.2"/></geometry></collision>
  </link>
  <joint name="wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child link="wheel_link"/>
    <origin xyz="0 0.2 0" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
  <link name="wheel_link">
    <visual><geometry><cylinder radius="0.08" length="0.05"/></geometry></visual>
    <collision><geometry><cylinder radius="0.08" length="0.05"/></geometry></collision>
  </link>
  <joint name="lidar_joint" type="fixed">
    <parent link="base_link"/>
    <child link="lidar_link"/>
  </joint>
  <link name="lidar_link">
    <visual><geometry><cylinder radius="0.05" length="0.08"/></geometry></visual>
    <collision><geometry><cylinder radius="0.05" length="0.08"/></geometry></collision>
  </link>
</robot>''')

    # nav2
    nav2_dir = tmp / 'nav2'
    nav2_dir.mkdir()
    (nav2_dir / 'nav2_params.yaml').write_text('''amcl:
  ros__parameters:
    use_sim_time: false
controller_server:
  ros__parameters:
    use_sim_time: false
    controller_frequency: 20.0
    max_vel_x: 0.5
    max_vel_theta: 1.0
    inflation_radius: 0.35
planner_server:
  ros__parameters:
    use_sim_time: false
    max_vel_x: 0.5
''')

    # tf（完整链路含 camera_link）
    tf_dir = tmp / 'tf'
    tf_dir.mkdir()
    (tf_dir / 'transforms.yaml').write_text('''transforms:
  - frame_id: map
    child_frame_id: odom
  - frame_id: odom
    child_frame_id: base_link
  - frame_id: base_link
    child_frame_id: lidar_link
  - frame_id: base_link
    child_frame_id: camera_link
  - frame_id: base_link
    child_frame_id: wheel_link
''')

    # calibration
    cal_dir = tmp / 'calibration'
    cal_dir.mkdir()
    (cal_dir / 'camera_info.yaml').write_text('''calibration_date: "2026-04-01"
camera_name: test_cam
image_width: 640
image_height: 480
camera_matrix:
  rows: 3
  cols: 3
  data: [615.0, 0.0, 320.0, 0.0, 615.0, 240.0, 0.0, 0.0, 1.0]
distortion_coefficients:
  rows: 1
  cols: 5
  data: [0.0, 0.0, 0.0, 0.0, 0.0]
''')

    # estop
    estop_dir = tmp / 'estop'
    estop_dir.mkdir()
    (estop_dir / 'safety.yaml').write_text('''estop:
  enabled: true
  topic: /emergency_stop
  max_response_time_ms: 40
  hardware:
    pin: GPIO_17
  chain:
    - name: button
      type: digital_input
    - name: driver
      type: disable_signal
''')

    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture
def bad_config_dir():
    """错误配置目录（应触发 FAIL）。"""
    tmp = Path(tempfile.mkdtemp())

    # URDF：base_Link 大小写错误 + 缺失 collision + 悬挂 link
    urdf_dir = tmp / 'urdf'
    urdf_dir.mkdir()
    (urdf_dir / 'robot.urdf').write_text('''<?xml version="1.0" ?>
<robot name="test_bad">
  <link name="base_Link">
    <visual><geometry><box size="0.5 0.4 0.2"/></geometry></visual>
    <!-- collision 故意缺失 -->
  </link>
  <joint name="wheel_joint" type="continuous">
    <parent link="base_Link"/>
    <child link="wheel_link"/>
    <axis xyz="0 1 0"/>
  </joint>
  <link name="wheel_link">
    <visual><geometry><cylinder radius="0.08" length="0.05"/></geometry></visual>
    <!-- collision 缺失 -->
  </link>
  <link name="orphan_link">
    <visual><geometry><box size="0.03 0.03 0.03"/></geometry></visual>
  </link>
</robot>''')

    # nav2：越界参数
    nav2_dir = tmp / 'nav2'
    nav2_dir.mkdir()
    (nav2_dir / 'nav2_params.yaml').write_text('''controller_server:
  ros__parameters:
    use_sim_time: true
    controller_frequency: 5.0
    max_vel_x: 5.0
    max_vel_theta: 4.0
    inflation_radius: 0.01
''')

    # tf：断裂（缺 odom → base_link）
    tf_dir = tmp / 'tf'
    tf_dir.mkdir()
    (tf_dir / 'transforms.yaml').write_text('''transforms:
  - frame_id: map
    child_frame_id: odom
  - frame_id: base_link
    child_frame_id: lidar_link
''')

    # calibration：过期（180天前）
    cal_dir = tmp / 'calibration'
    cal_dir.mkdir()
    (cal_dir / 'camera_info.yaml').write_text('''calibration_date: "2025-10-01"
camera_name: test_cam
image_width: 640
image_height: 480
camera_matrix:
  rows: 3
  cols: 3
  data: [615.0, 0.0, 320.0, 0.0, 615.0, 240.0, 0.0, 0.0, 1.0]
''')

    # estop：未配置
    estop_dir = tmp / 'estop'
    estop_dir.mkdir()
    (estop_dir / 'safety.yaml').write_text('''estop:
  enabled: false
''')

    yield tmp
    shutil.rmtree(tmp)


# ===== URDF 检查测试 =====

class TestUrdfCheck:
    def test_good_urdf_pass(self, good_config_dir):
        from checks.urdf_check import check_urdf
        result = check_urdf(good_config_dir)
        assert result['status'] == 'PASS'
        assert result['exit_code'] == 0

    def test_bad_urdf_fail(self, bad_config_dir):
        from checks.urdf_check import check_urdf
        result = check_urdf(bad_config_dir)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2
        detail_statuses = [d['status'] for d in result['details']]
        assert 'FAIL' in detail_statuses

    def test_missing_urdf_file(self, tmp_path):
        from checks.urdf_check import check_urdf
        result = check_urdf(tmp_path)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2


# ===== TF 树检查测试 =====

class TestTfTreeCheck:
    def test_good_tf_pass(self, good_config_dir):
        from checks.tf_tree_check import check_tf_tree
        result = check_tf_tree(good_config_dir)
        assert result['status'] == 'PASS'
        assert result['exit_code'] == 0

    def test_bad_tf_fail(self, bad_config_dir):
        from checks.tf_tree_check import check_tf_tree
        result = check_tf_tree(bad_config_dir)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2


# ===== Nav2 参数检查测试 =====

class TestNav2ParamsCheck:
    def test_good_nav2_pass(self, good_config_dir):
        from checks.nav2_params_check import check_nav2_params
        result = check_nav2_params(good_config_dir)
        assert result['status'] == 'PASS'
        assert result['exit_code'] == 0

    def test_bad_nav2_fail(self, bad_config_dir):
        from checks.nav2_params_check import check_nav2_params
        result = check_nav2_params(bad_config_dir)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2


# ===== E-stop 检查测试 =====

class TestEstopCheck:
    def test_good_estop_pass(self, good_config_dir):
        from checks.estop_check import check_estop
        result = check_estop(good_config_dir)
        assert result['status'] == 'PASS'
        assert result['exit_code'] == 0

    def test_bad_estop_fail(self, bad_config_dir):
        from checks.estop_check import check_estop
        result = check_estop(bad_config_dir)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2


# ===== 标定检查测试 =====

class TestCalibrationCheck:
    def test_good_calibration_pass(self, good_config_dir):
        from checks.calibration_check import check_calibration
        result = check_calibration(good_config_dir)
        assert result['status'] == 'PASS'
        assert result['exit_code'] == 0

    def test_bad_calibration_fail(self, bad_config_dir):
        from checks.calibration_check import check_calibration
        result = check_calibration(bad_config_dir)
        assert result['status'] == 'FAIL'
        assert result['exit_code'] == 2
