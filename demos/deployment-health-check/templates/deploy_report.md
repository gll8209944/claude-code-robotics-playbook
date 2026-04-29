# 机器人部署体检报告

## 部署总评

**{{ overall_status }}** | 退出码：`{{ exit_code }}` | 时间：`{{ timestamp }}`

---

## 机器人概览

| 字段 | 值 |
|---|---|
| 型号 | {{ model }} |
| 序列号 | {{ serial_number }} |
| 固件版本 | {{ firmware_version }} |

---

## 五项检查详情

| # | 检查项 | 状态 | 详情 |
|---|---|---|---|
{% for check in checks %}
| {{ loop.index }} | {{ check.item }} | {{ check.status }} | {{ check.msg }} |
{% endfor %}

---

## Top 3 风险项

{% for risk in top_risks %}
### {{ risk.rank }}. {{ risk.item }}
- **风险描述**：{{ risk.risk }}
- **后果**：{{ risk.consequence }}

{% endfor %}

---

## 修复建议优先级

{% for repair in repair_priority %}
### P{{ repair.priority }}：{{ repair.item }}
**动作**：{{ repair.action }}

**为什么**：{{ repair.why }}

{% endfor %}

---

## 与上次体检的差异对比

{% if diff_from_last.changed_items %}
**变更项**：{{ diff_from_last.changed_items | join(', ') }}
{% endif %}
{% if diff_from_last.new_failures %}
**新增失败**：{{ diff_from_last.new_failures | join(', ') }}
{% endif %}
{% if diff_from_last.resolved_items %}
**已解决**：{{ diff_from_last.resolved_items | join(', ') }}
{% endif %}
