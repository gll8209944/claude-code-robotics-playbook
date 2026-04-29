#!/usr/bin/env python3
"""
E-stop 急停配置校验模块
检查项：
  1. safety.yaml / estop 配置文件存在且非空
  2. 急停 topic 已定义（如 /emergency_stop）
  3. 急停响应时间配置 ≤ 100ms
"""

import sys
import argparse
import yaml
from pathlib import Path


def load_safety_config(config_dir: Path) -> dict:
    """加载 estop/safety.yaml。"""
    safety_path = config_dir / 'estop' / 'safety.yaml'
    if not safety_path.exists():
        return {}
    with open(safety_path) as f:
        return yaml.safe_load(f) or {}


def check_estop_enabled(config: dict) -> tuple:
    """检查 E-stop 是否启用。"""
    estop = config.get('estop', {})
    enabled = estop.get('enabled', False)
    if enabled is True:
        return 'PASS', 'E-stop 已启用'
    return 'FAIL', 'E-stop 未启用（enabled=false 或缺失），不允许部署'


def check_estop_topic(config: dict) -> tuple:
    """检查急停 topic 是否定义。"""
    estop = config.get('estop', {})
    topic = estop.get('topic')
    if topic:
        return 'PASS', f'急停 topic 已定义：{topic}'
    return 'FAIL', '急停 topic 未定义（需指定如 /emergency_stop）'


def check_estop_response_time(config: dict) -> tuple:
    """
    检查急停响应时间。
    阈值：≤50ms=安全，50~100ms=警告，>100ms=危险（阻塞）
    """
    estop = config.get('estop', {})
    hw = estop.get('hardware', {})
    # 支持两种路径：estop.max_response_time_ms 或 estop.hardware.max_response_time_ms
    response_ms = estop.get('max_response_time_ms') or hw.get('max_response_time_ms')

    if response_ms is None:
        return 'FAIL', '急停响应时间未配置（需指定 estop.max_response_time_ms 或 estop.hardware.max_response_time_ms）'

    if response_ms <= 50:
        return 'PASS', f'急停响应时间 {response_ms}ms（安全，≤50ms）'
    elif response_ms <= 100:
        return 'WARN', f'急停响应时间 {response_ms}ms（警告，51~100ms）'
    else:
        return 'FAIL', f'急停响应时间 {response_ms}ms（危险，>100ms）'


def check_estop_hardware_pin(config: dict) -> tuple:
    """检查硬件引脚是否映射。"""
    estop = config.get('estop', {})
    hw = estop.get('hardware', {})
    pin = hw.get('pin')
    if pin:
        return 'PASS', f'硬件引脚已映射：{pin}'
    return 'FAIL', '硬件引脚未映射（需指定 hardware.pin）'


def check_estop_chain(config: dict) -> tuple:
    """检查急停链路是否完整（chain 定义）。"""
    estop = config.get('estop', {})
    chain = estop.get('chain', [])
    if not chain:
        return 'FAIL', '急停链路未定义（chain 为空）'
    return 'PASS', f'急停链路完整，共 {len(chain)} 级'


def check_estop(config_dir: Path) -> dict:
    """
    主检查函数。
    返回 dict：{
        'status': 'PASS' | 'WARN' | 'FAIL',
        'exit_code': 0 | 1 | 2,
        'details': [...],
    }
    """
    config = load_safety_config(config_dir)

    if not config:
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [{'item': 'E-stop 配置', 'status': 'FAIL',
                         'msg': 'estop/safety.yaml 不存在或为空'}],
        }

    results = []
    has_fail = False
    has_warn = False

    checks = [
        ('启用状态', check_estop_enabled),
        ('急停 topic', check_estop_topic),
        ('硬件引脚', check_estop_hardware_pin),
        ('急停链路', check_estop_chain),
        ('响应时间', check_estop_response_time),
    ]

    for name, fn in checks:
        status, msg = fn(config)
        results.append({'item': name, 'status': status, 'msg': msg})
        if status == 'FAIL':
            has_fail = True
        elif status == 'WARN':
            has_warn = True

    if has_fail:
        status, exit_code = 'FAIL', 2
    elif has_warn:
        status, exit_code = 'WARN', 1
    else:
        status, exit_code = 'PASS', 0

    return {'status': status, 'exit_code': exit_code, 'details': results}


def main():
    parser = argparse.ArgumentParser(description='E-stop 急停配置校验')
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录')
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    result = check_estop(config_dir)

    print(f"E-stop 急停配置检查：{result['status']}")
    for detail in result['details']:
        print(f"  [{detail['status']}] {detail['item']}: {detail['msg']}")

    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
