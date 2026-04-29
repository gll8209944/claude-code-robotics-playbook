#!/usr/bin/env python3
"""
标定时效性校验模块
检查项：
  1. 标定文件修改时间在有效期内（默认 90 天）
  2. 相机内参矩阵格式正确（3x3，非零焦距）
  3. 标定板标识清晰（camera_info.yaml 中有 calibration_date）
有效期阈值：≤30天=PASS，30~90天=WARN，>90天=FAIL
"""

import sys
import argparse
import yaml
from pathlib import Path
from datetime import datetime, timedelta
from typing import Tuple, List, Optional


# 标定有效期阈值（天）
VALIDITY_THRESHOLD_DAYS = 90
SAFE_DAYS = 30
WARN_DAYS = 90


def find_calibration_files(config_dir: Path) -> List[Path]:
    """查找 calibration 目录下的所有 yaml 文件。"""
    cal_dir = config_dir / 'calibration'
    if not cal_dir.exists():
        return []
    return list(cal_dir.glob('*.yaml')) + list(cal_dir.glob('*.yml'))


def parse_calibration_date(content: dict) -> Optional[str]:
    """从标定文件中提取标定日期。"""
    return content.get('calibration_date')


def parse_camera_matrix(content: dict) -> Optional[List[List[float]]]:
    """提取并验证相机内参矩阵。"""
    cm = content.get('camera_matrix', {})
    data = cm.get('data', [])
    rows = cm.get('rows', 0)
    cols = cm.get('cols', 0)

    if rows == 3 and cols == 3 and len(data) == 9:
        matrix = [data[i*3:(i+1)*3] for i in range(3)]
        fx, fy = matrix[0][0], matrix[1][1]
        if fx > 0 and fy > 0:
            return matrix
    return None


def check_file_age(file_path: Path, calibration_date_str: str = None) -> Tuple[str, int, str]:
    """
    检查标定文件年龄。
    优先使用 YAML 中的 calibration_date 字段计算年龄；无该字段则用文件 mtime。
    返回 (status, days_ago, msg)。
    """
    if calibration_date_str:
        try:
            cal_date = datetime.strptime(calibration_date_str, "%Y-%m-%d")
        except ValueError:
            return 'FAIL', -1, f'calibration_date 格式错误（应为 YYYY-MM-DD，实际：{calibration_date_str}）'
        now = datetime.now()
        age = now - cal_date
        days_ago = age.days
    else:
        mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        now = datetime.now()
        age = now - mtime
        days_ago = age.days

    if days_ago <= SAFE_DAYS:
        return 'PASS', days_ago, f'标定文件 {days_ago} 天前更新（安全，≤{SAFE_DAYS}天）'
    elif days_ago <= WARN_DAYS:
        return 'WARN', days_ago, f'标定文件 {days_ago} 天前更新（警告，{SAFE_DAYS}~{WARN_DAYS}天）'
    else:
        return 'FAIL', days_ago, f'标定文件已过期 {days_ago} 天（危险，>{WARN_DAYS}天）'


def check_calibration_file(file_path: Path) -> dict:
    """
    检查单个标定文件。
    返回 dict：{'file': str, 'status': str, 'exit_code': int, 'details': [...]}
    """
    details = []

    # 1. 解析 YAML
    try:
        with open(file_path) as f:
            content = yaml.safe_load(f) or {}
    except Exception as e:
        return {
            'file': str(file_path),
            'status': 'FAIL',
            'exit_code': 2,
            'details': [{'item': 'YAML 解析', 'status': 'FAIL', 'msg': f'解析失败：{e}'}],
        }

    # 2. 提取标定日期
    cal_date = parse_calibration_date(content)

    # 3. 文件年龄（使用 YAML 中的 calibration_date 而非文件 mtime）
    age_status, days_ago, age_msg = check_file_age(file_path, cal_date)
    details.append({'item': '标定时效', 'status': age_status, 'msg': age_msg})

    # 4. 标定日期字段（来自 YAML content）
    if cal_date:
        details.append({'item': '标定日期字段', 'status': 'PASS', 'msg': f'标定日期：{cal_date}'})
    else:
        details.append({'item': '标定日期字段', 'status': 'WARN', 'msg': '未找到 calibration_date 字段'})

    # 5. 相机内参矩阵格式
    cam_matrix = parse_camera_matrix(content)
    if cam_matrix:
        fx, fy = cam_matrix[0][0], cam_matrix[1][1]
        details.append({'item': '内参矩阵', 'status': 'PASS',
                        'msg': f'相机内参有效（fx={fx:.1f}, fy={fy:.1f}）'})
    else:
        details.append({'item': '内参矩阵', 'status': 'FAIL',
                        'msg': '内参矩阵格式错误或缺失（需 3x3 且 fx/fy > 0）'})

    # 汇总
    has_fail = any(d['status'] == 'FAIL' for d in details)
    has_warn = any(d['status'] == 'WARN' for d in details)

    if has_fail:
        status, exit_code = 'FAIL', 2
    elif has_warn:
        status, exit_code = 'WARN', 1
    else:
        status, exit_code = 'PASS', 0

    return {
        'file': str(file_path),
        'status': status,
        'exit_code': exit_code,
        'details': details,
    }


def check_calibration(config_dir: Path) -> dict:
    """
    主检查函数。遍历 calibration 目录下所有 yaml 文件。
    返回 dict：{
        'status': 'PASS' | 'WARN' | 'FAIL',
        'exit_code': 0 | 1 | 2,
        'details': [...],
        'files': [...],
    }
    """
    files = find_calibration_files(config_dir)

    if not files:
        return {
            'status': 'FAIL',
            'exit_code': 2,
            'details': [{'item': '标定文件', 'status': 'FAIL',
                         'msg': 'calibration/ 目录不存在或无 yaml 文件'}],
            'files': [],
        }

    file_results = [check_calibration_file(f) for f in files]
    all_details = []
    has_fail = False
    has_warn = False

    for fr in file_results:
        all_details.extend(fr['details'])
        if fr['status'] == 'FAIL':
            has_fail = True
        elif fr['status'] == 'WARN':
            has_warn = True

    if has_fail:
        status, exit_code = 'FAIL', 2
    elif has_warn:
        status, exit_code = 'WARN', 1
    else:
        status, exit_code = 'PASS', 0

    return {
        'status': status,
        'exit_code': exit_code,
        'details': all_details,
        'files': [fr['file'] for fr in file_results],
    }


def main():
    parser = argparse.ArgumentParser(description='标定时效性校验')
    parser.add_argument('--config-dir', type=str, required=True,
                        help='机器人配置目录')
    args = parser.parse_args()

    config_dir = Path(args.config_dir)
    result = check_calibration(config_dir)

    print(f"标定时效性检查：{result['status']}")
    for detail in result['details']:
        print(f"  [{detail['status']}] {detail['item']}: {detail['msg']}")

    sys.exit(result['exit_code'])


if __name__ == '__main__':
    main()
