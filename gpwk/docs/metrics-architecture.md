# GPWK Metrics Architecture

## Two Types of Metrics

GPWK uses a **hybrid approach** combining push-based and pull-based metrics for comprehensive observability.

### 1. Push-Based Metrics (Inline Instrumentation)

**When**: Recorded during operations (when things happen)
**Source**: Python code inline in capture.py, github_ops.py
**Best for**: Operational metrics, latency, errors

**Examples:**
```python
# In capture.py
github_api_calls.add(1, {"operation": "create_issue", "status": "success"})
github_api_latency.record(duration_ms, {"operation": "create_issue"})
capture_duration.record(duration_ms, {"status": "success"})
```

**Metrics:**
- `gpwk.capture.total` - Capture operations count
- `gpwk.capture.duration` - How long capture took
- `gpwk.capture.errors` - Failed operations
- `gpwk.github.api_calls.total` - API requests
- `gpwk.github.api_latency` - API response time
- `gpwk.github.retry_count` - Retries needed

**Pros:**
✅ Real-time (immediate)
✅ Low latency
✅ Can track attempts/retries
✅ Captures operational details

**Cons:**
❌ Based on assumptions (what we think happened)
❌ Inaccurate if operations fail
❌ Misses external changes
❌ Can't recover if telemetry was down

---

### 2. Pull-Based Metrics (Periodic State Collection)

**When**: Periodically (e.g., every 60 seconds)
**Source**: Queries GitHub API and local log files
**Best for**: State metrics, current counts, truth verification

**Examples:**
```python
# In metrics_collector.py
# Query GitHub for actual state
issues = gh_api.list_issues()
open_count = len([i for i in issues if i.state == "OPEN"])
issues_open_counter.add(open_count, {"source": "github_api"})
```

**Metrics:**
- `gpwk.state.issues_open` - Current open issues count
- `gpwk.state.issues_by_type{type}` - Issues by type (task, ai-task, etc.)
- `gpwk.state.backlog_age_days` - Age of oldest issue
- `gpwk.state.completion_rate` - Today's completion rate (%)
- `gpwk.state.work_time_minutes` - Total time tracked today

**Pros:**
✅ **Accurate** - Based on actual state, not assumptions
✅ **Resilient** - Works even if some operations fail
✅ **External changes** - Catches manual edits via GitHub UI
✅ **Can recover** - If telemetry was down, next query catches up
✅ **Source of truth** - GitHub/logs are the truth

**Cons:**
❌ Delayed (depends on polling interval)
❌ Higher load on GitHub API
❌ Can't track attempts/retries (only final state)

---

## How It Works

### Push-Based (Inline)
```
User runs: /gpwk.capture "task"
    ↓
Create issue → GitHub API call succeeds
    ↓
Record metric: gpwk.issues.created.total +1
    ↓
Send to Grafana Cloud IMMEDIATELY
```

If GitHub API fails, metric is still recorded (incorrect!).

### Pull-Based (Periodic)
```
Every 60 seconds:
    ↓
Query GitHub API: GET /repos/{repo}/issues
    ↓
Count actual state: 15 issues open
    ↓
Record metric: gpwk.state.issues_open = 15
    ↓
Send to Grafana Cloud
```

Always reflects actual truth from GitHub.

---

## Running the Metrics Collector

### Start the Collector Daemon

```bash
# Run in foreground (default: every 60 seconds)
gpwk/bin/gpwk-metrics-collector

# Custom interval (every 30 seconds)
gpwk/bin/gpwk-metrics-collector 30

# Run in background
gpwk/bin/gpwk-metrics-collector > /dev/null 2>&1 &
```

### What It Does

Every interval (60s by default):
1. **Query GitHub** - Get all issues via `gh issue list`
2. **Count state**:
   - Open issues count
   - Issues by type (task, ai-task, personal, etc.)
   - Backlog age (oldest issue)
   - Today's completion rate
3. **Query daily log** - Parse time ranges to calculate work time
4. **Record metrics** - Send to Grafana Cloud via OTLP

### Logs Output

```
Starting GPWK metrics collector (interval: 60s)
Querying: OWNER/REPO
Logs: /path/to/repo/gpwk/logs
Press Ctrl+C to stop

[info] github_metrics_collected open_issues=17 created_today=3 closed_today=2
[info] log_metrics_collected work_time_minutes=150
[info] metrics_collected
```

---

## Dashboard Queries

### Pull-Based State Metrics

**Current Open Issues:**
```promql
gpwk_state_issues_open{source="github_api"}
```

**Issues by Type (Right Now):**
```promql
sum(gpwk_state_issues_by_type{source="github_api"}) by (type)
```

**Backlog Health:**
```promql
gpwk_state_backlog_age_days{source="github_api"}
```

**Today's Completion Rate:**
```promql
gpwk_state_completion_rate{source="github_api"}
```

**Total Work Time Today:**
```promql
gpwk_state_work_time_minutes{source="daily_log"}
```

### Push-Based Operational Metrics

**Capture Success Rate:**
```promql
sum(rate(gpwk_capture_total{status="success"}[5m]))
/
sum(rate(gpwk_capture_total[5m])) * 100
```

**API Latency Percentiles:**
```promql
histogram_quantile(0.95, sum(rate(gpwk_github_api_latency_bucket[5m])) by (le))
```

---

## Benefits of Hybrid Approach

| Metric Type | Push-Based | Pull-Based | Best For |
|-------------|-----------|-----------|----------|
| **Latency** | ✅ Real-time | ❌ Delayed | Operational monitoring |
| **Accuracy** | ❌ Assumptions | ✅ Truth | State verification |
| **Retries** | ✅ Tracked | ❌ Not visible | Debugging |
| **External changes** | ❌ Missed | ✅ Detected | Audit |
| **Recovery** | ❌ Lost if down | ✅ Catches up | Reliability |
| **API load** | ✅ Low | ⚠️ Periodic | Cost |

**Recommendation**: Use BOTH!
- **Push-based** for real-time operations monitoring
- **Pull-based** for truth verification and state tracking

---

## Example: Detecting Discrepancies

### Scenario: GitHub API fails silently

**Push-based says:**
```
gpwk_issues_created_total = 100  (we think we created 100)
```

**Pull-based says:**
```
gpwk_state_issues_open = 95  (only 95 actually exist)
```

**Alert**: Discrepancy detected! 5 issues were lost due to API failures.

### Scenario: Manual edit via GitHub UI

Someone manually closes an issue via GitHub.com:

**Push-based:**
- Doesn't know (no capture command was run)
- `gpwk_issues_closed_total` = incorrect

**Pull-based:**
- Detects change on next poll (60s)
- `gpwk_state_issues_open` decreases by 1
- Truth is maintained!

---

## Next Steps

1. **Start the collector**:
   ```bash
   gpwk/bin/gpwk-metrics-collector &
   ```

2. **Update dashboards** to include pull-based metrics

3. **Set up alerts** for discrepancies between push/pull metrics

4. **Add more pull-based metrics** as needed (e.g., carryover counts, blocked tasks)
