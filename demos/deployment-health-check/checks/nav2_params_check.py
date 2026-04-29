#!/usr/bin/env python3
"""
Nav2 参数合理性校验模块
检查项：
  1. max_vel_x、max_vel_theta 在安全范围内
  2. inflation_radius 合理（≥ 0.3m）
  3. controller_frequency ≥ 10Hz
  4. use_sim_time 必须为 false（实机部署）
阈值按 CLAUDE.md 中的安全/警告/危险三级判定。
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Tuple, List, Optional


# 阈值定义（来自 CLAUDE.md）
THRESHOLDS = {
    'max_vel_x':         {'safe': 0.8, 'warn': 1.5, 'danger': 1.5},    # m/s
    'max_vel_theta':     {'safe': 1.5, 'warn': 3.0, 'danger': 3.0},    # rad/s
    'inflation_radius':  {'safe': 0.3, 'warn': 0.15, 'danger': 0.15},  # m（越小越危险）
    'controller_frequency': {'safe': 20, 'warn': 10, 'danger': 10},     # Hz（越小越危险）
}


def load_nav2_params(config_dir: Path) -> dict:
    """加载 nav2_params.yaml。"""
    nav2_path = config_dir / 'nav2' / 'nav2_params.yaml'
    if not nav2_path.exists():
        return {}
    with open(nav2_path) as f:
        return yaml.safe_load(f) or {}


def get_value(params: dict, *keys, default=None) -> Optional[float]:
    """支持嵌套 key 查找，如 controller_server.ros__parameters.max_vel_x"""
    for key in keys:
        if isinstance(params, dict):
            params = params.get(key, default)
        else:
            return default
    return params


def check_velocity(params: dict, key: str, thresholds: dict) -> Tuple[str, str]:
    """
    检查速度类参数。
    返回 (status, msg)：PASS=安全，WARN=警告，FAIL=危险。
    """
    val = get_value(params, 'controller_server', 'ros__parameters', key,
                     default=get_value(params, 'planner_server', 'ros__parameters', key))
    if val is None:
        return 'FAIL', f'{key} 未配置'

    safe_th = thresholds['safe']
    warn_th = thresholds['warn']
    danger_th = thresholds['danger']

    if key in ('max_vel_x', 'max_vel_theta'):
        # 越大越危险
        if val <= safe_th:
            return 'PASS', f'{key}={val}（安全，≤{safe_th}）'
        elif val <= warn_th:
            return 'WARN', f'{key}={val}（警告，{safe_th}~{warn_th}）'
        else:
            return 'FAIL', f'{key}={val}（危险，>{warn_th}）'
    elif key == 'inflation_radius':
        # 越小越危险
        if val >= safe_th:
            return 'PASS', f'{key}={val}（安全，≥{safe_th}）'
        elif val >= warn_th:
            return 'WARN', f'{key}={val}（警告，{warn_th}~{safe_th}）'
        else:
            return 'FAIL', f'{key}={val}（危险，<{warn_th}）'
    elif key == 'controller_frequency':
        # 越小越危险
        if val >= safe_th:
            return 'PASS', f'{key}={val}Hz（安全，≥{safe_th}Hz）'
        elif val >= warn_th:
            return 'WARN', f'{key}={val}Hz（警告，{warn_th}~{safe_th}Hz）'
        else:
            return 'FAIL', f'{key}={val}Hz（危险，<{warn_th}Hz）'
    return 'FAIL', f'{key} 未知参数'


def check_sim_time(params: dict) -> Tuple[str, str]:
    """检查 use_sim_time 必须为 false（实机部署）。"""
    sim_time = get_value(params, 'controller_server', 'ros__parameters', 'use_sim_time',
                          default=get_value(params, 'amcl', 'ros__parameters', 'use_sim_time'))
    if sim_time is None:
        return 'FAIL', 'use_sim_time 未配置（实机部署必须为 false）'
    if sim_time is False:
        return 'PASS', 'use_sim_time=false（正确，实机部署）'
    return 'WARN', f'use_sim_time={sim_time}（实机部署应为 false，sim_time 会导致定位漂移）'


def check_nav2_params(config_dir: Path) -> dict:
    """
    主检查函数。
    返回 dict：{
        'status': 'PASS' | 'WARN' | 'FAIL',
        'exit_code': 0 | 1 | 2,
        'details': [...],
    }
    """
    params = load_nav2_params(config_dir)
    if not params:
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [{'item': 'Nav2 配置', 'status': 'FAIL', 'msg': 'nav2_params.yaml 不存在或为空'}],
        }

    results = []
    has_fail = False
    has_warn = False

    # 1. use_sim_time
    sim_status, sim_msg = check_sim_time(params)
    results.append({'item': 'use_sim_time', 'status': sim_status, 'msg': sim_msg})
    if sim_status == 'FAIL':
        has_fail = True
    elif sim_status == 'WARN':
        has_warn = True

    # 2. 各项阈值
    check_keys = ['max_vel_x', 'max_vel_theta', 'inflation_radius', 'controller_frequency']
    for key in check_keys:
        th = THRESHOLDS[key]
        status, msg = check_velocity(params, key, th)
        results.append({'item': key, 'status': status, 'msg': msg})
        if status == 'FAIL':
            has_fail = True
        elif status == 'WARN':
            has_warn = True

    if has_fail:
        status = 'FAIL'
        exit_code = 2
    elif has_warn:
        status = 'WARN'
        exit_code = 1
    else:
        status = 'PASS'
        exit_code = 0

    return {'status': status, 'exit_code': exit_code, 'details': results}


def main():
    parser = argparse.ArgumentParser(description='Nav2 参数合理性校验')
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录')
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    result = check_nav2_params(config_dir)

    print(f"Nav2 参数合理性检查：{result['status']}")
    for detail in result['details']:
        print(f"  [{detail['status']}] {detail['item']}: {detail['msg']}")

    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
