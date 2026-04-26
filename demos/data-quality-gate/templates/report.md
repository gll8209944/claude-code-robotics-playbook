# 数据质量门禁报告

**数据集**：{{dataset_name}}
**检查配置**：{{profile}}
**生成时间**：{{timestamp}}
**整体判定**：{{overall_verdict}}

---

## 数据集概览

| 指标 | 值 |
|---|---|
| 总 episode 数 | {{total_episodes}} |
| 总帧数 | {{total_frames}} |
| 数据集体积 | {{storage_human}} |
| 多视角 | {{has_multiview}} |
| 摄像头/key | {{cameras}} |

---

## 关键指标

| 检查项 | 实际值 | 阈值 | 结果 |
|---|---|---|---|
| 帧率一致性（FPSS 标准差/均值） | {{fps_value}} | < {{fps_threshold}} | {{fps_verdict}} |
| 缺帧率 | {{missing_value}} | < {{missing_threshold}} | {{missing_verdict}} |
| 多视角时间戳最大偏移 | {{sync_value}} ms | < {{sync_threshold}} ms | {{sync_verdict}} |
| 任务标签缺失率 | {{label_value}} | < {{label_threshold}} | {{label_verdict}} |
| 异常帧（黑屏/模糊）比例 | {{anomaly_value}} | < {{anomaly_threshold}} | {{anomaly_verdict}} |

---

## Top {{top_n}} 异常 Episode

{{#each anomalies}}
### Episode {{episode_id}}（{{severity}} 级别）

- **原因**：{{reason}}
{{/each}}

{{^anomalies}}
无显著异常 episode。
{{/anomalies}}

---

## 修复建议

{{#each suggestions}}
{{add @index}}. {{this}}
{{/each}}

{{^suggestions}}
本次检查未发现需修复项，数据可直接进入 curated 阶段。
{{/suggestions}}

---

## 对 VLA 训练的影响

**是否可以进入训练**：{{can_proceed}}
**风险等级**：{{risk_level}}
**原因**：{{impact_reason}}

{{#if blocking_issues}}
**阻塞问题**：
{{#each blocking_issues}}
- {{this}}
{{/each}}
{{/if}}

---

*本报告由 data-quality-gate 自动生成，机器可读版本见 `report.json`*
