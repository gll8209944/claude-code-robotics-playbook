#!/usr/bin/env python3
"""
部署体检报告生成模块（JSON 部分）
生成 deploy_report.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


def build_summary(checks_results: List[dict]) -> dict:
    """
    根据所有检查结果构建总评。
    - 任意 FAIL → FAIL / exit_code=2
    - 有 WARN 无 FAIL → WARN / exit_code=1
    - 全部 PASS → PASS / exit_code=0
    """
    statuses = [r.get('status', 'FAIL') for r in checks_results]

    if 'FAIL' in statuses:
        overall_status = 'FAIL'
        exit_code = 2
    elif 'WARN' in statuses:
        overall_status = 'WARN'
        exit_code = 1
    else:
        overall_status = 'PASS'
        exit_code = 0

    return {
        'overall_status': overall_status,
        'exit_code': exit_code,
        'timestamp': datetime.now().isoformat(),
    }


def build_top_risks(checks_results: List[dict]) -> List[dict]:
    """提取 FAIL 项作为 Top 风险。"""
    risks = []
    risk_consequences = {
        'urdf_check': 'TF 树加载失败，rviz/Gazebo 无法启动机器人模型',
        'tf_tree_check': '导航定位断裂，机器人将无法完成自主导航',
        'nav2_params_check': '机器人运动超速或控制震荡，可能导致碰撞或飞车',
        'estop_check': '无急停保护，现场人员伤害风险极高',
        'calibration_check': '感知精度下降，导航定位精度劣化至不可用',
    }

    for result in checks_results:
        if result.get('status') == 'FAIL':
            item = result.get('item', '未知')
            risks.append({
                'rank': len(risks) + 1,
                'item': item,
                'risk': result.get('msg', '未知错误'),
                'consequence': risk_consequences.get(item, '可能导致部署失败'),
            })
        if len(risks) >= 3:
            break
    return risks


def build_repair_priority(checks_results: List[dict]) -> List[dict]:
    """根据检查结果构建修复优先级列表（FAIL 优先）。"""
    priorities = []
    priority = 1
    _actions = {
        'urdf_check': '修复 URDF：确保 base_link 存在、所有 link 有 collision、无线挂 link',
        'tf_tree_check': '补全 TF 链路：确保 map→odom→base_link→sensors 全链路连通',
        'nav2_params_check': '调整 Nav2 参数：将越界参数恢复至安全阈值内',
        'estop_check': '配置 E-stop：定义急停 topic、硬件引脚和响应链路',
        'calibration_check': '重新标定：相机/激光雷达内参外参需在有效期内重新标定',
    }
    _whys = {
        'urdf_check': 'URDF 是机器人模型的定义，错误会导致 rviz/Gazebo 无法加载或 TF 树断裂',
        'tf_tree_check': 'TF 树断裂会导致导航定位失效，机器人无法感知自身位置',
        'nav2_params_check': 'Nav2 参数越界直接威胁现场人员和设备安全',
        'estop_check': 'E-stop 是安全底线，无急停配置的机器人禁止部署',
        'calibration_check': '过期标定导致感知精度下降，导航精度无法保证',
    }

    for result in checks_results:
        if result.get('status') == 'FAIL':
            item = result.get('item', '未知')
            priorities.append({
                'priority': priority,
                'item': item,
                'action': _actions.get(item, '检查并修复该配置项'),
                'why': _whys.get(item, '该问题会直接影响机器人正常功能'),
            })
            priority += 1

    for result in checks_results:
        if result.get('status') == 'WARN':
            item = result.get('item', '未知')
            priorities.append({
                'priority': priority,
                'item': item,
                'action': _actions.get(item, '检查并修复该配置项'),
                'why': _whys.get(item, '该问题会直接影响机器人正常功能'),
            })
            priority += 1

    return priorities


def generate_report_json(output_dir: Path, summary: dict, checks_results: List[dict],
                        top_risks: List[dict], repair_priority: List[dict]) -> Path:
    """生成 deploy_report.json。"""
    report = {
        'summary': summary,
        'robot_overview': {
            'model': '机器人型号（待配置）',
            'serial_number': '序列号（待配置）',
            'firmware_version': '固件版本（待配置）',
        },
        'checks': checks_results,
        'top_risks': top_risks,
        'repair_priority': repair_priority,
        'diff_from_last': {
            'changed_items': [],
            'new_failures': [],
            'resolved_items': [],
        },
    }

    output_path = output_dir / 'deploy_report.json'
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return output_path
