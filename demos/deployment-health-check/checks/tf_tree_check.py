#!/usr/bin/env python3
"""
TF 树连通性校验模块
检查项：
  1. map → odom → base_link → sensors 全链路连通
  2. 无环路
  3. 无断裂
输出 TF 树 ASCII 可视化文本。
"""

import sys
import argparse
import yaml
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional


def load_tf_transforms(config_dir: Path) -> List[dict]:
    """加载 tf/transforms.yaml 中的 transform 定义。"""
    tf_path = config_dir / 'tf' / 'transforms.yaml'
    if not tf_path.exists():
        return []
    with open(tf_path) as f:
        data = yaml.safe_load(f)
    return data.get('transforms', [])


def build_tf_graph(transforms: List[dict]) -> Dict[str, List[str]]:
    """构建 TF 有向图：frame_id → [child_frame_ids]"""
    graph = {}
    for t in transforms:
        parent = t.get('frame_id')
        child = t.get('child_frame_id')
        if parent and child:
            if parent not in graph:
                graph[parent] = []
            graph[parent].append(child)
    return graph


def find_path(graph: Dict[str, List[str]], start: str, end: str,
              visited: Optional[Set[str]] = None) -> Tuple[bool, List[str]]:
    """DFS 查找从 start 到 end 的路径。"""
    if visited is None:
        visited = set()
    if start == end:
        return True, [start]
    if start in visited or start not in graph:
        return False, []
    visited.add(start)
    for child in graph.get(start, []):
        found, path = find_path(graph, child, end, visited.copy())
        if found:
            return True, [start] + path
    return False, []


def check_required_chain(graph: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """
    检查必需链路：map → odom → base_link → (lidar_link | camera_link)
    全链路必须连通。
    """
    required_chain = [
        ('map', 'odom'),
        ('odom', 'base_link'),
        ('base_link', 'lidar_link'),
        ('base_link', 'camera_link'),
    ]

    errors = []
    for parent, child in required_chain:
        if child not in graph.get(parent, []):
            errors.append(f'断裂：{parent} → {child} 不连通')

    if errors:
        return False, errors
    return True, []


def detect_cycles(graph: Dict[str, List[str]]) -> Tuple[bool, List[str]]:
    """检测有向图中的环路（DFS）。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}
    parent = {node: None for node in graph}
    cycles = []

    def dfs(node: str) -> bool:
        color[node] = GRAY
        for child in graph.get(node, []):
            if color.get(child) == GRAY:
                # 找到环路
                path = [child]
                p = node
                while p != child:
                    path.append(p)
                    p = parent.get(p, None)
                    if p is None:
                        break
                cycles.append(path[::-1])
                return True
            elif color.get(child) == WHITE:
                parent[child] = node
                if dfs(child):
                    return True
        color[node] = BLACK
        return False

    for node in graph:
        if color[node] == WHITE:
            dfs(node)

    return len(cycles) > 0, cycles


def render_ascii_tree(graph: Dict[str, List[str]], node: str,
                      prefix: str = "", is_last: bool = True) -> str:
    """递归渲染 TF 树为 ASCII 树状图。"""
    lines = []
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{node}")

    children = graph.get(node, [])
    for i, child in enumerate(children):
        new_prefix = prefix + ("    " if is_last else "│   ")
        lines.append(render_ascii_tree(graph, child, new_prefix, i == len(children) - 1))

    return "\n".join(lines)


def check_tf_tree(config_dir: Path) -> dict:
    """
    主检查函数。
    返回 dict：{
        'status': 'PASS' | 'WARN' | 'FAIL',
        'exit_code': 0 | 1 | 2,
        'details': [...],
        'tree_ascii': str,
    }
    """
    transforms = load_tf_transforms(config_dir)
    if not transforms:
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [{'item': 'TF 配置', 'status': 'FAIL', 'msg': 'tf/transforms.yaml 不存在或为空'}],
            'tree_ascii': '',
        }

    graph = build_tf_graph(transforms)
    results = []

    # 1. 必需链路检查
    chain_ok, chain_errors = check_required_chain(graph)
    if chain_ok:
        results.append({'item': 'TF 全链路', 'status': 'PASS', 'msg': 'map→odom→base_link→sensors 全链路连通'})
    else:
        results.append({'item': 'TF 全链路', 'status': 'FAIL', 'msg': f'链路断裂：{chain_errors}'})

    # 2. 环路检测
    has_cycle, cycles = detect_cycles(graph)
    if has_cycle:
        results.append({'item': '环路检测', 'status': 'FAIL', 'msg': f'检测到环路：{cycles}'})
    else:
        results.append({'item': '环路检测', 'status': 'PASS', 'msg': '无环路'})

    # 3. ASCII 树渲染
    all_nodes = set(graph.keys()) | {c for children in graph.values() for c in children}
    tree_root = 'map' if 'map' in graph else (list(graph.keys())[0] if graph else 'unknown')
    tree_ascii = render_ascii_tree(graph, tree_root)

    all_pass = all(r['status'] == 'PASS' for r in results)

    return {
        'status': 'PASS' if all_pass else 'FAIL',
        'exit_code': 0 if all_pass else 2,
        'details': results,
        'tree_ascii': tree_ascii,
    }


def main():
    parser = argparse.ArgumentParser(description='TF 树连通性校验')
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录')
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    result = check_tf_tree(config_dir)

    print(f"TF 树连通性检查：{result['status']}")
    for detail in result['details']:
        print(f"  [{detail['status']}] {detail['item']}: {detail['msg']}")
    if result.get('tree_ascii'):
        print("\nTF 树结构：")
        print(result['tree_ascii'])

    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
