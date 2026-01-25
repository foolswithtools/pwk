# Dashboard Updates Required

## Summary

The existing dashboard JSON files (`gpwk-metrics.json` and `gpwk-productivity.json`) need to be updated to reflect the new hybrid push/pull metrics architecture.

## Changes Required

### 1. GPWK Operations Dashboard (`gpwk-metrics.json`)

**Current State**: Only includes `gpwk.capture.*` and `gpwk.github.*` metrics

**Required Additions**:

#### Add Triage Metrics Panels:
```json
{
  "title": "Triage Operations/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_triage_operations_total[5m])) by (mode, status)"
  }]
}

{
  "title": "Triage Duration p95",
  "targets": [{
    "expr": "histogram_quantile(0.95, sum(rate(gpwk_triage_duration_bucket[5m])) by (le))"
  }]
}

{
  "title": "Items Moved/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_triage_items_moved_total[5m])) by (from, to)"
  }]
}
```

#### Add Delegate Metrics Panels:
```json
{
  "title": "Delegate Operations/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_delegate_operations_total[5m])) by (mode, status)"
  }]
}

{
  "title": "AI Tasks Executed/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_delegate_tasks_executed_total[5m]))"
  }]
}

{
  "title": "Delegate Duration p95",
  "targets": [{
    "expr": "histogram_quantile(0.95, sum(rate(gpwk_delegate_duration_bucket[5m])) by (le))"
  }]
}
```

#### Add Review Metrics Panels:
```json
{
  "title": "Review Operations/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_review_operations_total[5m])) by (mode, status)"
  }]
}

{
  "title": "Review Duration p95",
  "targets": [{
    "expr": "histogram_quantile(0.95, sum(rate(gpwk_review_duration_bucket[5m])) by (le))"
  }]
}
```

#### Add Plan Metrics Panels:
```json
{
  "title": "Plan Operations/sec",
  "targets": [{
    "expr": "sum(rate(gpwk_plan_operations_total[5m])) by (mode, status)"
  }]
}

{
  "title": "Plan Duration p95",
  "targets": [{
    "expr": "histogram_quantile(0.95, sum(rate(gpwk_plan_duration_bucket[5m])) by (le))"
  }]
}
```

#### Update Overview Row:
```json
{
  "title": "Total Operations (5m)",
  "targets": [{
    "expr": "sum(rate(gpwk_capture_total[5m])) + sum(rate(gpwk_triage_operations_total[5m])) + sum(rate(gpwk_delegate_operations_total[5m])) + sum(rate(gpwk_review_operations_total[5m])) + sum(rate(gpwk_plan_operations_total[5m]))"
  }]
}

{
  "title": "Overall Success Rate",
  "targets": [{
    "expr": "(sum(rate(gpwk_capture_total{status=\"success\"}[5m])) + sum(rate(gpwk_triage_operations_total{status=\"success\"}[5m])) + sum(rate(gpwk_delegate_operations_total{status=\"success\"}[5m])) + sum(rate(gpwk_review_operations_total{status=\"success\"}[5m])) + sum(rate(gpwk_plan_operations_total{status=\"success\"}[5m]))) / (sum(rate(gpwk_capture_total[5m])) + sum(rate(gpwk_triage_operations_total[5m])) + sum(rate(gpwk_delegate_operations_total[5m])) + sum(rate(gpwk_review_operations_total[5m])) + sum(rate(gpwk_plan_operations_total[5m]))) * 100"
  }]
}
```

---

### 2. GPWK Productivity Dashboard (`gpwk-productivity.json`)

**Current State**: May have old push-based metrics like `gpwk_issues_created_total`

**Required Changes**:

#### Remove Old Push-Based Metrics:
- ❌ `gpwk_issues_created_total`
- ❌ `gpwk_issues_closed_total`
- ❌ `gpwk_tasks_completed_total`
- ❌ `gpwk_work_sessions_duration`

#### Replace with New Pull-Based Metrics:

```json
{
  "title": "Issues Created Today",
  "targets": [{
    "expr": "gpwk_productivity_issues_created_today"
  }]
}

{
  "title": "Issues Closed Today",
  "targets": [{
    "expr": "gpwk_productivity_issues_closed_today"
  }]
}

{
  "title": "Completion Rate",
  "targets": [{
    "expr": "gpwk_productivity_completion_rate_percent"
  }]
}

{
  "title": "Total Open Issues",
  "targets": [{
    "expr": "gpwk_productivity_issues_open"
  }]
}

{
  "title": "Work Time Today (minutes)",
  "targets": [{
    "expr": "gpwk_productivity_work_time_minutes"
  }]
}

{
  "title": "Backlog Age (days)",
  "targets": [{
    "expr": "gpwk_productivity_backlog_age_days"
  }]
}
```

#### Add Issue Breakdown Pie Charts:
```json
{
  "title": "Issues by Type",
  "type": "piechart",
  "targets": [{
    "expr": "sum(gpwk_productivity_issues_by_type) by (type)",
    "legendFormat": "{{type}}"
  }]
}

{
  "title": "Issues by Priority",
  "type": "piechart",
  "targets": [{
    "expr": "sum(gpwk_productivity_issues_by_priority) by (priority)",
    "legendFormat": "{{priority}}"
  }]
}

{
  "title": "Issues by Energy",
  "type": "piechart",
  "targets": [{
    "expr": "sum(gpwk_productivity_issues_by_energy) by (energy)",
    "legendFormat": "{{energy}}"
  }]
}
```

#### Add Trend Graphs:
```json
{
  "title": "Daily Issues Over Time",
  "targets": [
    {
      "expr": "gpwk_productivity_issues_created_today",
      "legendFormat": "Created"
    },
    {
      "expr": "gpwk_productivity_issues_closed_today",
      "legendFormat": "Closed"
    }
  ]
}

{
  "title": "Completion Rate Trend",
  "targets": [{
    "expr": "gpwk_productivity_completion_rate_percent"
  }]
}

{
  "title": "Work Time Trend",
  "targets": [{
    "expr": "gpwk_productivity_work_time_minutes"
  }]
}
```

---

## Recommended Approach

Given the complexity of manually editing JSON files, here are two approaches:

### Approach 1: Manual Update (Tedious but Precise)
1. Open each dashboard JSON file
2. Find and update/add panels based on the queries above
3. Test in Grafana Cloud
4. Export updated dashboard and save

### Approach 2: Rebuild in Grafana UI (Recommended)
1. Log into Grafana Cloud
2. Create new dashboard
3. Add panels one by one using the queries above
4. Use the updated README.md as a guide for panel layout
5. Export as JSON when complete
6. Save to `gpwk/config/alloy/dashboards/`

### Approach 3: Use Dashboard Generator (Future)
Create a Python script to generate dashboard JSON programmatically from templates.

---

## Validation

After updating dashboards:

1. **Check Metrics Exist**: Run queries in Grafana Explore to verify metrics are being collected
   ```promql
   # Should return data
   gpwk_triage_operations_total
   gpwk_productivity_issues_open
   ```

2. **Verify Visualizations**: Each panel should show data (or "No data" if command hasn't been run)

3. **Test Refresh**: Enable auto-refresh (10s) and run commands to see live updates
   ```bash
   # Run commands and watch dashboards update
   gpwk/bin/gpwk-capture "Test telemetry"
   gpwk/bin/gpwk-triage
   gpwk/bin/gpwk-review
   ```

4. **Compare Push vs Pull**:
   - Operational metrics should update immediately
   - Productivity metrics should update within 60 seconds (next collector poll)

---

## Priority

**HIGH PRIORITY UPDATES**:
1. ✅ README.md - UPDATED
2. 🔄 gpwk-productivity.json - **NEEDS UPDATE** (remove old push-based metrics, add new pull-based)
3. 🔄 gpwk-metrics.json - **NEEDS UPDATE** (add triage, delegate, review, plan metrics)

**CURRENT STATUS**:
- Metrics are being collected and exported correctly ✅
- Dashboards reference old metric names ❌
- Need to update dashboard JSON files to match new architecture

---

## Next Steps

1. **Immediate**: Start metrics collector daemon
   ```bash
   nohup gpwk/bin/gpwk-metrics-collector 60 > /tmp/gpwk-metrics.log 2>&1 &
   ```

2. **Short-term**: Manually update dashboards in Grafana Cloud UI using queries above

3. **Long-term**: Export updated dashboards and save JSON files for version control
