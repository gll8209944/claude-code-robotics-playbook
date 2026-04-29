#!/usr/bin/env python3
"""
部署体检入口脚本
调用 5 个检查模块，收集结果，调用 reporter 生成双份报告。

退出码：
  0 = 可部署（全 PASS）
  1 = 有条件部署（有 WARN 无 FAIL）
  2 = 拒绝部署（有 FAIL）
"""

import sys
import argparse
from pathlib import Path

# 添加 demos/deployment-health-check 到 path（便于直接调用）
sys.path.insert(0, str(Path(__file__).parent.parent))

from checks.urdf_check import check_urdf
from checks.tf_tree_check import check_tf_tree
from checks.nav2_params_check import check_nav2_params
from checks.estop_check import check_estop
from checks.calibration_check import check_calibration
from reporter import generate_reports


CHECK_REGISTRY = {
    'urdf': {
        'label': 'URDF 完整性',
        'fn': check_urdf,
    },
    'tf_tree': {
        'label': 'TF 树连通性',
        'fn': check_tf_tree,
    },
    'nav2_params': {
        'label': 'Nav2 参数合理性',
        'fn': check_nav2_params,
    },
    'estop': {
        'label': 'E-stop 配置',
        'fn': check_estop,
    },
    'calibration': {
        'label': '传感器标定',
        'fn': check_calibration,
    },
}


def run_all_checks(config_dir: Path) -> list:
    """
    依次运行 5 项检查，返回结果列表。
    """
    results = []

    print(f"部署体检开始：{config_dir}")
    print("=" * 50)

    for key, entry in CHECK_REGISTRY.items():
        label = entry['label']
        fn = entry['fn']

        print(f"\n[{label}] 检查中...")
        try:
            result = fn(config_dir)
        except Exception as e:
            result = {
                'item': label,
                'status': 'FAIL',
                'exit_code': 2,
                'details': [{'item': '执行异常', 'status': 'FAIL', 'msg': str(e)}],
            }

        status = result.get('status', 'FAIL')
        exit_code = result.get('exit_code', 2)

        # 标准化格式
        results.append({
            'item': label,
            'status': status,
            'exit_code': exit_code,
            'details': result.get('details', []),
            'msg': result.get('details', [{}])[0].get('msg', '') if result.get('details') else '',
        })

        emoji = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(status, '❌')
        print(f"[{emoji}] {label}：{status}")

        # 打印详情
        for detail in result.get('details', []):
            detail_status = detail.get('status', '')
            detail_msg = detail.get('msg', '')
            print(f"      [{detail_status}] {detail.get('item','')}: {detail_msg}")

    print("\n" + "=" * 50)

    # 汇总
    statuses = [r['status'] for r in results]
    has_fail = 'FAIL' in statuses
    has_warn = 'WARN' in statuses

    if has_fail:
        overall = 'FAIL'
        overall_text = '❌ 拒绝部署'
        exit_code = 2
    elif has_warn:
        overall = 'WARN'
        overall_text = '⚠️ 有条件部署'
        exit_code = 1
    else:
        overall = 'PASS'
        overall_text = '✅ 可部署'
        exit_code = 0

    print(f"部署总评：{overall_text}（exit_code={exit_code}）")

    return results, exit_code


def main():
    parser = argparse.ArgumentParser(
        description='机器人部署体检工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
退出码：
  0 = 可部署（全 PASS）
  1 = 有条件部署（有 WARN 无 FAIL）
  2 = 拒绝部署（有 FAIL）
        ''',
    )
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录（含 urdf/nav2/tf/calibration/estop 子目录）')
    parser.add_argument('--output', type=str, required=True,
                        help='报告输出目录')

    args = parser.parse_args()
    config_dir = Path(args.config_dir)
    output_dir = Path(args.output)

    if not config_dir.exists():
        print(f"错误：配置目录不存在：{config_dir}", file=sys.stderr)
        sys.exit(2)

    results, exit_code = run_all_checks(config_dir)
    json_path, md_path, summary = generate_reports(output_dir, results)

    print(f"\n报告已生成：")
    print(f"  JSON：{json_path}")
    print(f"  Markdown：{md_path}")

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
