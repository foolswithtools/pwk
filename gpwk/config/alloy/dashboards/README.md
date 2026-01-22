# GPWK Grafana Dashboards

This directory contains Grafana dashboard definitions for GPWK telemetry visualization using a **hybrid push/pull metrics architecture**.

## Architecture Overview

GPWK uses two complementary metrics systems:

### Operational Metrics (Push-Based) → `gpwk-metrics.json`
**Real-time system health monitoring**
- Metrics recorded inline during operations
- Immediate feedback on performance
- Track errors, latency, retries in real-time
- Namespace: `gpwk.capture.*`, `gpwk.triage.*`, `gpwk.delegate.*`, `gpwk.review.*`, `gpwk.plan.*`, `gpwk.github.*`

### Productivity Metrics (Pull-Based) → `gpwk-productivity.json`
**Truth from GitHub/logs**
- Metrics queried every 60s by collector daemon
- Reflects actual GitHub state (source of truth)
- Catches external edits made via GitHub UI
- Resilient to telemetry downtime
- Namespace: `gpwk.productivity.*`

## Available Dashboards

### 1. GPWK Operations Dashboard (`gpwk-metrics.json`)

**Purpose**: Monitor GPWK system health and performance (Technical/DevOps focused)

**Panels:**

#### Overview Row
- **Total Operations (5m)**: All GPWK command executions (capture, triage, delegate, review, plan)
- **Overall Success Rate**: Percentage of successful operations across all commands
- **Avg Operation Duration (p50)**: Median operation duration
- **Total Errors (5m)**: Number of errors across all operations

#### Capture Operations Row
- **Capture Operations/sec**: Rate of capture operations by type and status
- **Capture Duration Percentiles**: p50, p95, p99 duration metrics
- **Capture Success Rate**: Success percentage over time
- **Capture Errors by Type**: Error breakdown

#### Triage Operations Row
- **Triage Operations/sec**: Rate of triage operations (manual vs auto)
- **Triage Duration Percentiles**: p50, p95, p99 duration metrics
- **Items Moved/sec**: Rate of issues moved between columns
- **Triage Success Rate**: Success percentage

#### Delegate Operations Row
- **Delegate Operations/sec**: Rate of AI task delegation operations
- **Tasks Executed/sec**: Rate of AI tasks actually executed
- **Delegate Duration Percentiles**: p50, p95, p99 duration metrics
- **Delegate Success Rate**: Success percentage

#### Review Operations Row
- **Review Operations/sec**: Rate of daily review generations
- **Review Duration Percentiles**: p50, p95, p99 duration metrics
- **Review Success Rate**: Success percentage

#### Plan Operations Row
- **Plan Operations/sec**: Rate of daily plan generations
- **Plan Duration Percentiles**: p50, p95, p99 duration metrics
- **Plan Success Rate**: Success percentage

#### GitHub API Metrics Row
- **GitHub API Calls/sec by Operation**: API call rate for create_issue, add_to_project, etc.
- **GitHub API Latency Percentiles**: p50, p95, p99 latency by operation
- **GitHub Retry Count Distribution**: How many retries are needed for project operations
- **GitHub API Error Rate**: Error rate by operation type

---

### 2. GPWK Productivity Dashboard (`gpwk-productivity.json`)

**Purpose**: Track actual work accomplished (User/Productivity focused)

**Panels:**

#### Daily Overview Row
- **Issues Created Today**: GitHub issues created today (from GitHub API)
- **Issues Closed Today**: GitHub issues closed today (from GitHub API)
- **Completion Rate**: Percentage of issues closed vs created (closed/created * 100)
- **Work Time Today**: Total minutes tracked in daily log

#### Current State Row
- **Total Open Issues**: Current number of open issues
- **Issues by Type**: Pie chart showing distribution (task, ai-task, work-item, capture)
- **Issues by Priority**: Pie chart showing high/medium/low distribution
- **Issues by Energy**: Pie chart showing deep/shallow/quick distribution

#### Productivity Trends Row
- **Daily Issues Over Time**: Line chart comparing created vs closed issues
- **Completion Rate Trend**: Completion rate percentage over time
- **Work Time Trend**: Daily work minutes over time

#### Backlog Health Row
- **Backlog Age**: Age of oldest open issue in days
- **Open Issues by Type**: Stacked area chart showing issue type breakdown over time
- **Open Issues by Priority**: Stacked area chart showing priority breakdown over time

---

## Metrics Reference

### Operational Metrics (Push - Real-time Performance)

#### Capture Command
- `gpwk_capture_total{status, type, completed}` (Counter) - Total capture operations
- `gpwk_capture_duration{status}` (Histogram) - Capture operation duration in ms
- `gpwk_capture_errors{error_type, type}` (Counter) - Failed capture operations

#### Triage Command
- `gpwk_triage_operations_total{status, mode}` (Counter) - Total triage operations
- `gpwk_triage_duration{status}` (Histogram) - Triage operation duration in ms
- `gpwk_triage_items_moved_total{from, to}` (Counter) - Items moved between columns
- `gpwk_triage_errors{error_type}` (Counter) - Failed triage operations

#### Delegate Command
- `gpwk_delegate_operations_total{status, mode}` (Counter) - Total delegate operations
- `gpwk_delegate_duration{status}` (Histogram) - Delegate operation duration in ms
- `gpwk_delegate_tasks_executed_total{issue_number}` (Counter) - AI tasks executed
- `gpwk_delegate_errors{error_type}` (Counter) - Failed delegate operations

#### Review Command
- `gpwk_review_operations_total{status, mode}` (Counter) - Total review operations
- `gpwk_review_duration{status}` (Histogram) - Review operation duration in ms
- `gpwk_review_errors{error_type}` (Counter) - Failed review operations

#### Plan Command
- `gpwk_plan_operations_total{status, mode}` (Counter) - Total plan operations
- `gpwk_plan_duration{status}` (Histogram) - Plan operation duration in ms
- `gpwk_plan_errors{error_type}` (Counter) - Failed plan operations

#### GitHub API Operations
- `gpwk_github_api_calls_total{operation, status}` (Counter) - Total GitHub API calls
- `gpwk_github_api_latency{operation}` (Histogram) - GitHub API latency in ms
- `gpwk_github_retry_count{operation}` (Histogram) - Number of retries needed
- `gpwk_github_api_errors_total{operation}` (Counter) - GitHub API errors

### Productivity Metrics (Pull - Actual State from GitHub/Logs)

#### Current State (from GitHub API)
- `gpwk_productivity_issues_open` (Histogram) - Current number of open issues
- `gpwk_productivity_issues_by_type{type}` (Histogram) - Open issues by type (task, ai-task, etc.)
- `gpwk_productivity_issues_by_priority{priority}` (Histogram) - Open issues by priority
- `gpwk_productivity_issues_by_energy{energy}` (Histogram) - Open issues by energy level
- `gpwk_productivity_backlog_age_days` (Histogram) - Age of oldest open issue

#### Daily Metrics (from GitHub API)
- `gpwk_productivity_issues_created_today` (Histogram) - Issues created today
- `gpwk_productivity_issues_closed_today` (Histogram) - Issues closed today
- `gpwk_productivity_completion_rate_percent` (Histogram) - Completion rate (closed/created * 100)

#### Work Time (from daily logs)
- `gpwk_productivity_work_time_minutes` (Histogram) - Total work time tracked today

---

## How to Import

### Option 1: Grafana Cloud Web UI

1. Log into your Grafana Cloud instance
2. Navigate to **Dashboards** → **Import**
3. Click **Upload JSON file**
4. Select `gpwk-metrics.json` (for operational metrics) or `gpwk-productivity.json` (for productivity)
5. Select your Prometheus data source
6. Click **Import**

### Option 2: Grafana API (Automated)

```bash
# Set your Grafana Cloud details
GRAFANA_URL="https://your-instance.grafana.net"
GRAFANA_API_KEY="your-api-key"

# Import operational dashboard
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @gpwk-metrics.json

# Import productivity dashboard
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @gpwk-productivity.json
```

---

## Running the System

### 1. Start Metrics Collector (Required for Productivity Metrics)

```bash
# Start in foreground (for testing)
gpwk/bin/gpwk-metrics-collector 60

# Start in background (production)
nohup gpwk/bin/gpwk-metrics-collector 60 > /tmp/gpwk-metrics.log 2>&1 &

# Save PID
echo $! > /tmp/gpwk-metrics-collector.pid
```

### 2. Use GPWK Commands

```bash
# All commands now send operational metrics automatically
gpwk/bin/gpwk-capture "Buy groceries ~quick"
gpwk/bin/gpwk-triage #123 today
gpwk/bin/gpwk-delegate --list
gpwk/bin/gpwk-review
gpwk/bin/gpwk-plan today

# Operational metrics → sent immediately (push)
# Productivity metrics → collected on next poll by metrics_collector (pull, within 60s)
```

---

## Benefits of Hybrid Architecture

| Aspect | Benefit |
|--------|---------|
| **Accuracy** | Productivity metrics always reflect GitHub truth |
| **Real-time** | Operational metrics provide immediate performance feedback |
| **Resilience** | If operations fail, productivity metrics still correct |
| **External edits** | Manual GitHub UI changes are tracked in productivity metrics |
| **Recovery** | If telemetry is down, next poll catches up |
| **Separation** | Operational vs productivity concerns cleanly separated |
| **Debugging** | Can compare push vs pull to detect discrepancies |

---

## Example Grafana Queries

### Operational Metrics (gpwk-metrics.json)

```promql
# Capture success rate
sum(rate(gpwk_capture_total{status="success"}[5m]))
/
sum(rate(gpwk_capture_total[5m])) * 100

# All operations success rate
sum(rate(gpwk_capture_total{status="success"}[5m]))
+ sum(rate(gpwk_triage_operations_total{status="success"}[5m]))
+ sum(rate(gpwk_delegate_operations_total{status="success"}[5m]))
+ sum(rate(gpwk_review_operations_total{status="success"}[5m]))
+ sum(rate(gpwk_plan_operations_total{status="success"}[5m]))

# API latency p95
histogram_quantile(0.95, sum(rate(gpwk_github_api_latency_bucket[5m])) by (le, operation))
```

### Productivity Metrics (gpwk-productivity.json)

```promql
# Issues created today
gpwk_productivity_issues_created_today

# Completion rate
gpwk_productivity_completion_rate_percent

# Work time tracked
gpwk_productivity_work_time_minutes

# Open issues by type
sum(gpwk_productivity_issues_by_type) by (type)

# Backlog age
gpwk_productivity_backlog_age_days
```

---

## Customization

You can customize the dashboards by:

1. **Time Range**: Use the time picker in the top-right
2. **Refresh Rate**: Default is 10 seconds, adjust as needed
3. **Data Source**: Select your Prometheus data source
4. **Thresholds**: Edit panel thresholds to match your SLOs
5. **Alerts**: Add alert rules to panels for proactive monitoring

---

## Tips

### For Operations Dashboard
- **Percentiles**: p50 = median, p95 = 95th percentile, p99 = 99th percentile
  - If p99 latency is high, 1% of requests are slow
  - If p50 is close to p99, latency is consistent
  - Large gap indicates variance

- **Success Rate**: Should be close to 100%
  - Green: 95%+
  - Yellow: 90-95%
  - Red: Below 90%

- **Retry Counts**: Higher retries indicate GitHub API timing issues
  - Monitor if retry counts increase over time

### For Productivity Dashboard
- **Completion Rate**: Track daily to identify productivity patterns
  - 100%+ = Closing more than creating (clearing backlog)
  - 50-100% = Normal pace
  - <50% = Backlog growing

- **Work Time**: Compare tracked time vs actual calendar time
- **Backlog Age**: Monitor to prevent tasks from getting stale

---

## Next Steps

1. **Set up Alerts**: Create alert rules for high error rates or latency
2. **Create SLOs**: Define service level objectives based on baseline metrics
3. **Monitor Trends**: Watch productivity metrics to identify work patterns
4. **Correlate Data**: Use operational metrics to debug productivity anomalies

---

## Support

For issues or questions:
- Check GPWK documentation: `gpwk/docs/metrics-separation.md`
- Review OpenTelemetry metrics configuration: `gpwk/config/alloy/README.md`
- Grafana Cloud documentation: https://grafana.com/docs/grafana-cloud/
