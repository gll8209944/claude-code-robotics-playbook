#!/usr/bin/env python3
"""
URDF 完整性校验模块
检查项：
  1. 所有 link 是否有对应 joint 连接（无悬挂 link）
  2. 每个 link 是否定义了 collision
  3. base_link 是否存在
无 ROS2 时用 lxml 解析 URDF XML。
"""

import sys
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple


def parse_urdf(urdf_path: Path) -> Tuple[ET.Element, dict, dict]:
    """
    解析 URDF 文件，返回根元素和 link/joint 字典。

    Returns:
        (root, links, joints)
        - links: {name: element}
        - joints: {name: {'parent': ..., 'child': ...}}
    """
    tree = ET.parse(urdf_path)
    root = tree.getroot()

    links = {}
    joints = {}

    for elem in root:
        if elem.tag == 'link':
            links[elem.attrib['name']] = elem
        elif elem.tag == 'joint':
            joint_name = elem.attrib['name']
            parent = elem.find('parent')
            child = elem.find('child')
            joints[joint_name] = {
                'parent': parent.attrib['link'] if parent is not None else None,
                'child': child.attrib['link'] if child is not None else None,
            }

    return root, links, joints


def check_base_link(links: dict) -> Tuple[bool, str]:
    """检查 base_link 是否存在。"""
    if 'base_link' in links:
        return True, "base_link 存在"
    return False, "base_link 不存在（应为 'base_link'，注意大小写）"


def check_no_dangling_links(links: dict, joints: dict) -> Tuple[bool, list]:
    """检查是否有悬挂 link（无 joint 引用）。"""
    referenced = set()
    for j in joints.values():
        if j['parent']:
            referenced.add(j['parent'])
        if j['child']:
            referenced.add(j['child'])

    dangling = [name for name in links if name not in referenced]
    if dangling:
        return False, dangling
    return True, []


def check_collision(links: dict) -> Tuple[bool, list]:
    """
    检查每个 link 是否定义了 collision。
    collision 可以直接定义，也可以通过 xacro 宏生成，此处只检查直接定义。
    """
    missing = []
    for name, elem in links.items():
        collision = elem.find('collision')
        if collision is None:
            missing.append(name)
    if missing:
        return False, missing
    return True, []


def check_urdf(config_dir: Path) -> dict:
    """
    主检查函数。
    返回 dict：{
        'status': 'PASS' | 'WARN' | 'FAIL',
        'exit_code': 0 | 1 | 2,
        'details': [...],
    }
    """
    urdf_path = config_dir / 'urdf' / 'robot.urdf'
    if not urdf_path.exists():
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [f'URDF 文件不存在：{urdf_path}'],
        }

    try:
        root, links, joints = parse_urdf(urdf_path)
    except Exception as e:
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [f'URDF 解析失败：{e}'],
        }

    results = []
    all_pass = True

    # 1. base_link 检查
    base_ok, base_msg = check_base_link(links)
    results.append({'item': 'base_link 存在', 'status': 'PASS' if base_ok else 'FAIL', 'msg': base_msg})
    if not base_ok:
        all_pass = False

    # 2. 悬挂 link 检查
    dangling_ok, dangling_links = check_no_dangling_links(links, joints)
    if dangling_links:
        results.append({
            'item': '悬挂 link 检查',
            'status': 'FAIL',
            'msg': f'发现悬挂 link（无 joint 引用）：{dangling_links}',
        })
        all_pass = False
    else:
        results.append({'item': '悬挂 link 检查', 'status': 'PASS', 'msg': '无悬挂 link'})

    # 3. collision 检查
    collision_ok, missing_collision = check_collision(links)
    if missing_collision:
        results.append({
            'item': 'collision 定义',
            'status': 'FAIL',
            'msg': f'以下 link 缺失 collision：{missing_collision}',
        })
        all_pass = False
    else:
        results.append({'item': 'collision 定义', 'status': 'PASS', 'msg': '所有 link 均定义 collision'})

    if all_pass:
        return {'status': 'PASS', 'exit_code': 0, 'details': results}
    else:
        return {'status': 'FAIL', 'exit_code': 2, 'details': results}


def main():
    parser = argparse.ArgumentParser(description='URDF 完整性校验')
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录')
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    result = check_urdf(config_dir)

    print(f"URDF 完整性检查：{result['status']}")
    for detail in result['details']:
        print(f"  [{detail['status']}] {detail['item']}: {detail['msg']}")

    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
