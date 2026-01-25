# GPWK Metrics: Clean Separation of Concerns

## Philosophy

**Operational metrics** = How the system performs (push)
**Productivity metrics** = What you accomplished (pull from GitHub)

## Metric Categories

### 1. Operational Metrics (Push-Based)

**Purpose**: Monitor GPWK system health and performance
**Source**: Inline instrumentation in Python code
**When**: Recorded immediately during operations
**Namespace**: `gpwk.capture.*`, `gpwk.github.*`

| Metric | Type | Description | Where |
|--------|------|-------------|-------|
| `gpwk.capture.total` | Counter | Capture command executions | capture.py |
| `gpwk.capture.duration` | Histogram | Capture command latency | capture.py |
| `gpwk.capture.errors` | Counter | Failed capture operations | capture.py |
| `gpwk.github.api_calls.total` | Counter | GitHub API requests | github_ops.py |
| `gpwk.github.api_latency` | Histogram | GitHub API response time | github_ops.py |
| `gpwk.github.api_errors.total` | Counter | GitHub API failures | github_ops.py |
| `gpwk.github.retry_count` | Histogram | Retry attempts needed | github_ops.py |

**Use Cases:**
- Is GPWK running slow?
- Are GitHub API calls failing?
- Do we need more retries?
- System performance dashboards

---

### 2. Productivity Metrics (Pull-Based)

**Purpose**: Track actual work accomplished
**Source**: Periodic queries to GitHub API and daily logs
**When**: Collected every 60 seconds by metrics collector daemon
**Namespace**: `gpwk.productivity.*`

| Metric | Type | Description | Source |
|--------|------|-------------|--------|
| `gpwk.productivity.issues_open` | Histogram | Current open issues count | GitHub API |
| `gpwk.productivity.issues_by_type{type}` | Histogram | Open issues by type | GitHub API |
| `gpwk.productivity.issues_by_priority{priority}` | Histogram | Open issues by priority | GitHub API |
| `gpwk.productivity.issues_by_energy{energy}` | Histogram | Open issues by energy | GitHub API |
| `gpwk.productivity.issues_created_today` | Histogram | Issues created today | GitHub API |
| `gpwk.productivity.issues_closed_today` | Histogram | Issues closed today | GitHub API |
| `gpwk.productivity.completion_rate_percent` | Histogram | Today's completion rate | GitHub API |
| `gpwk.productivity.work_time_minutes` | Histogram | Total time tracked today | Daily log |
| `gpwk.productivity.backlog_age_days` | Histogram | Oldest issue age | GitHub API |

**Use Cases:**
- How many tasks did I complete today?
- What's my backlog size?
- Am I closing as many as I create?
- Productivity dashboards

---

## Why This Separation?

### Operational Metrics (Push)
```
/gpwk.capture → [API Call] → Record latency immediately
```
**Must be push-based because:**
- Need real-time performance monitoring
- Track transient events (retries, errors)
- Measure duration of operations in progress

### Productivity Metrics (Pull)
```
Every 60s: Query GitHub → Count actual state → Record metrics
```
**Must be pull-based because:**
- ✅ **Accuracy**: Reflects actual GitHub state, not assumptions
- ✅ **Resilience**: Works even if operations fail
- ✅ **External changes**: Detects manual edits via GitHub UI
- ✅ **Recovery**: Catches up if telemetry was down
- ✅ **Simplicity**: No inline instrumentation needed
- ✅ **Source of truth**: GitHub is authoritative

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GPWK Commands                         │
│  (/gpwk.capture, /gpwk.triage, /gpwk.delegate)         │
└────────────┬────────────────────────────┬───────────────┘
             │                            │
    ┌────────▼─────────┐        ┌────────▼──────────┐
    │ Operational      │        │ GitHub Operations │
    │ Metrics (Push)   │        │                   │
    │                  │        │ • Create issues   │
    │ • Latency       │        │ • Close issues    │
    │ • Errors        │        │ • Update project  │
    │ • Retries       │        └───────────────────┘
    └──────────────────┘                 │
             │                            │
             │                            ▼
             │                   ┌────────────────────┐
             │                   │   GitHub (Truth)   │
             │                   │                    │
             │                   │ • Issues           │
             │                   │ • Labels           │
             │                   │ • Status           │
             │                   └─────────┬──────────┘
             │                             │
             │                   ┌─────────▼──────────┐
             │                   │ Metrics Collector  │
             │                   │ (Every 60s)        │
             │                   │                    │
             │                   │ • Query GitHub     │
             │                   │ • Parse logs       │
             │                   │ • Record metrics   │
             │                   └─────────┬──────────┘
             │                             │
             │                   ┌─────────▼──────────┐
             │                   │ Productivity       │
             │                   │ Metrics (Pull)     │
             │                   │                    │
             │                   │ • Open count       │
             │                   │ • Created/closed   │
             │                   │ • Work time        │
             │                   └────────────────────┘
             │                             │
             └─────────────────────────────┘
                                 │
                                 ▼
                      ┌────────────────────┐
                      │  Grafana Cloud     │
                      │                    │
                      │  Two dashboards:   │
                      │  1. Operations     │
                      │  2. Productivity   │
                      └────────────────────┘
```

---

## Dashboard Design

### Dashboard 1: GPWK Operations (Technical)

**Audience**: System administrators, debugging
**Metrics**: Push-based (operational)

Panels:
- Capture command success rate
- API latency percentiles (p50, p95, p99)
- Error rate over time
- Retry count distribution

**Queries:**
```promql
# Capture success rate
sum(rate(gpwk_capture_total{status="success"}[5m]))
/
sum(rate(gpwk_capture_total[5m])) * 100

# API latency p95
histogram_quantile(0.95, sum(rate(gpwk_github_api_latency_bucket[5m])) by (le))
```

---

### Dashboard 2: GPWK Productivity (User-Facing)

**Audience**: You (the user), productivity tracking
**Metrics**: Pull-based (from GitHub/logs)

Panels:
- Issues created today
- Issues closed today
- Completion rate %
- Open issues by type/priority/energy
- Total work time tracked
- Backlog age

**Queries:**
```promql
# Issues created today
gpwk_productivity_issues_created_today

# Completion rate
gpwk_productivity_completion_rate_percent

# Work time
gpwk_productivity_work_time_minutes

# Open issues by type
sum(gpwk_productivity_issues_by_type) by (type)
```

---

## Running the System

### Start Metrics Collector (Required for Productivity Metrics)

```bash
# Start in foreground
gpwk/bin/gpwk-metrics-collector

# Run in background
nohup gpwk/bin/gpwk-metrics-collector > /dev/null 2>&1 &
```

### Use GPWK Normally

```bash
/gpwk.capture "Buy groceries ~quick"
# → Operational metrics sent immediately (push)
# → Productivity metrics collected on next poll (pull, within 60s)
```

---

## Benefits of This Approach

| Aspect | Benefit |
|--------|---------|
| **Accuracy** | Productivity metrics always reflect GitHub truth |
| **Simplicity** | Capture command doesn't need productivity instrumentation |
| **Resilience** | If capture fails, productivity metrics still correct |
| **External edits** | Manual GitHub UI changes are tracked |
| **Recovery** | If telemetry down, next poll catches up |
| **Separation** | Operational vs productivity concerns cleanly separated |
| **Debugging** | Can compare push vs pull to detect issues |

---

## Example: Detecting Issues

### Scenario: Capture command fails silently

**Operational metrics (push):**
```
gpwk_capture_total{status="error"} = 1
gpwk_capture_errors = 1
```
Shows the command failed ✅

**Productivity metrics (pull):**
```
gpwk_productivity_issues_created_today = 0
```
Shows no issue was actually created ✅

**Result**: Both dashboards tell the full story!

---

## Summary

**Operational = Push** → Real-time system health
**Productivity = Pull** → Truth from GitHub/logs

This clean separation ensures:
- Operational metrics are fast and real-time
- Productivity metrics are accurate and resilient
- Each metric serves its purpose optimally
