#!/bin/bash
set -e
cd /home/guolinlin/claude-code-robotics-playbook
git pull origin main

python3 << 'PYEOF'
import time
from pathlib import Path
import sys
sys.path.insert(0, '/home/guolinlin/claude-code-robotics-playbook/demos/data-quality-gate')
from checks import anomaly_frames

dataset_path = Path('/home/guolinlin/datasets/pusht')
start = time.time()
result = anomaly_frames.check_anomaly_frames(dataset_path, 'strict')
elapsed = time.time() - start

print(f"Time: {elapsed:.1f}s")
print(f"Passed: {result['passed']}")
print(f"Value: {result['value']}%")
print(f"Threshold: {result['threshold']}%")
d = result['details']
print(f"Total frames: {d.get('total_frames', 0)}")
print(f"Anomaly count: {d.get('anomaly_count', 0)}")
print(f"Data format: {d.get('data_format', '?')}")
print(f"Anomalies by type (top 3): {d.get('anomalies_by_type', [])[:3]}")
PYEOF