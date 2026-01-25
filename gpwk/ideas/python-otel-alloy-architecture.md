# GPWK with Python + OpenTelemetry + Grafana Alloy

**Date**: 2025-12-20
**Proposal**: Reimplement GPWK core in Python with full observability instrumentation

## Executive Summary

Replace shell-based GPWK implementation with Python + OpenTelemetry, using Grafana Alloy to collect telemetry. This enables:
- **Better reliability** (proper error handling, retries, typing)
- **Full observability** (metrics, logs, traces for every operation)
- **Self-optimization** (data-driven insights from your own productivity patterns)
- **Troubleshooting** (distributed traces show exactly where failures occur)

## Python vs Shell Scripts: Advantages

### 1. Reliability & Error Handling

**Shell Scripts**:
```bash
# Shell escaping nightmare
ITEM_ID=$(gh project item-list 1 --owner @me --format json | jq -r '.items[] | select(.content.url == "https://...") | .id')
# Error: (eval):1: parse error near '('
```

**Python**:
```python
from github import Github
import requests

def get_project_item_id(issue_number: int, max_retries: int = 5) -> Optional[str]:
    """Get project item ID with automatic retry and proper error handling."""
    with tracer.start_as_current_span("get_project_item_id") as span:
        span.set_attribute("github.issue_number", issue_number)

        for attempt in range(max_retries):
            try:
                response = requests.get(
                    f"https://api.github.com/projects/{PROJECT_ID}/items",
                    headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
                )
                response.raise_for_status()

                items = response.json()
                for item in items:
                    if item.get("content", {}).get("number") == issue_number:
                        item_id = item["id"]
                        span.set_attribute("github.item_id", item_id)
                        return item_id

                # Not found yet, retry with exponential backoff
                time.sleep(2 ** attempt)

            except requests.RequestException as e:
                span.record_exception(e)
                logger.error(f"GitHub API error (attempt {attempt + 1}): {e}")

        return None
```

**Advantages**:
- ✅ No shell escaping issues
- ✅ Type hints catch errors before runtime
- ✅ Native exception handling
- ✅ Automatic retry with exponential backoff
- ✅ Clean error messages
- ✅ Every error captured in traces

### 2. Better Data Structures

**Shell Scripts**:
```bash
# Complex jq parsing
gh issue list --json number,title,labels | \
  jq '.[] | select(.labels[] | .name == "pwk:c2")'
```

**Python**:
```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class GithubIssue:
    number: int
    title: str
    labels: List[str]
    url: str
    created_at: datetime

    @property
    def carryover_level(self) -> Optional[int]:
        """Extract carryover level from labels."""
        for label in self.labels:
            if label.startswith("pwk:c"):
                return int(label[-1])
        return None

    @property
    def is_ai_delegatable(self) -> bool:
        return "pwk:ai" in self.labels

# Clean iteration
for issue in github.get_issues():
    if issue.carryover_level == 2:
        print(f"Warning: Issue #{issue.number} carried over 2 days")
```

**Advantages**:
- ✅ Type safety
- ✅ Clean object-oriented design
- ✅ IDE autocomplete
- ✅ Self-documenting code
- ✅ Easier testing

### 3. Testing

**Shell Scripts**: Hard to test, requires mocking `gh` command

**Python**:
```python
import pytest
from unittest.mock import Mock, patch

def test_parse_capture_completed_activity():
    """Test that completed activities are detected."""
    parser = GPWKParser()

    result = parser.parse_capture(
        "I took Mr. Noodles for a walk between 9-10 AM. This is complete."
    )

    assert result.is_completed == True
    assert result.title == "Took Mr. Noodles for a walk (9:00 AM - 10:00 AM)"
    assert result.time_range == ("09:00", "10:00")
    assert "energy:quick" in result.labels

@pytest.mark.parametrize("title,should_escape", [
    ("Bug in login (critical)", True),
    ("Review 'code' changes", True),
    ("Simple task", False),
])
def test_special_character_handling(title, should_escape):
    """Test that special characters are handled correctly."""
    github_ops = GithubOperations()

    with patch('github.Github') as mock_gh:
        github_ops.create_issue(title)
        # Assert no escaping errors occurred
        mock_gh.create_issue.assert_called_once()
```

**Advantages**:
- ✅ Unit tests with pytest
- ✅ Mocking and fixtures
- ✅ Parameterized tests
- ✅ Coverage reports
- ✅ CI/CD integration

## Grafana Alloy Integration: The Game Changer

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│ GPWK Python Library (gpwk_core)                              │
│                                                               │
│  ├── github_ops.py   ← Instrumented with OpenTelemetry      │
│  ├── parser.py       ← Spans for each parse operation        │
│  ├── log_ops.py      ← Metrics on log updates               │
│  └── telemetry.py    ← OTLP export configuration            │
│                                                               │
│  All operations emit:                                        │
│  • Traces (distributed tracing)                             │
│  • Metrics (counters, histograms, gauges)                   │
│  • Logs (structured logging with context)                   │
└───────────────────────────┬──────────────────────────────────┘
                            │ OTLP (gRPC/HTTP)
                            │
┌───────────────────────────▼──────────────────────────────────┐
│ Grafana Alloy Agent (localhost:4317)                         │
│                                                               │
│  otelcol.receiver.otlp "gpwk" {                              │
│    grpc { endpoint = "0.0.0.0:4317" }                        │
│    http { endpoint = "0.0.0.0:4318" }                        │
│    output {                                                  │
│      traces = [otelcol.exporter.otlp.tempo.input]           │
│      metrics = [prometheus.remote_write.mimir.receiver]     │
│      logs = [loki.write.cloud.receiver]                     │
│    }                                                         │
│  }                                                           │
└───────────────────────────┬──────────────────────────────────┘
                            │
┌───────────────────────────▼──────────────────────────────────┐
│ Grafana Cloud (or local Grafana stack)                       │
│  • Tempo (traces)                                            │
│  • Mimir (metrics)                                           │
│  • Loki (logs)                                               │
│  • Grafana (dashboards & alerts)                            │
└──────────────────────────────────────────────────────────────┘
```

### What Gets Instrumented

#### 1. Traces (Distributed Tracing)

Every GPWK operation becomes a trace with spans:

```python
from opentelemetry import trace

tracer = trace.get_tracer("gpwk.capture", version="1.0.0")

@tracer.start_as_current_span("gpwk.capture")
def capture_activity(text: str) -> CaptureResult:
    """Capture an activity or task to GitHub."""

    with tracer.start_as_current_span("parse_notation") as span:
        parsed = parser.parse_capture_notation(text)
        span.set_attribute("capture.type", parsed.type)
        span.set_attribute("capture.is_completed", parsed.is_completed)
        span.set_attribute("capture.has_priority", parsed.priority is not None)

    with tracer.start_as_current_span("create_github_issue") as span:
        issue = github_ops.create_issue(
            title=parsed.title,
            labels=parsed.labels,
            body=parsed.body
        )
        span.set_attribute("github.issue_number", issue.number)
        span.set_attribute("github.issue_url", issue.url)

    with tracer.start_as_current_span("add_to_project") as span:
        project_item = github_ops.add_to_project(
            issue_url=issue.url,
            status="done" if parsed.is_completed else "inbox"
        )
        span.set_attribute("github.project_item_id", project_item.id)

    with tracer.start_as_current_span("set_project_fields") as span:
        for field_name, field_value in parsed.project_fields.items():
            github_ops.set_project_field(
                item_id=project_item.id,
                field=field_name,
                value=field_value
            )
            span.add_event(f"Set {field_name} = {field_value}")

    with tracer.start_as_current_span("update_daily_log") as span:
        log_ops.append_to_activity_stream(
            date=datetime.now().date(),
            issue=issue,
            time_range=parsed.time_range
        )

    return CaptureResult(success=True, issue=issue)
```

**What you see in Grafana Tempo**:
```
Trace: gpwk.capture (543ms total)
  ├─ parse_notation (12ms)
  ├─ create_github_issue (234ms)
  │   └─ github_api_request (228ms)
  ├─ add_to_project (89ms)
  │   ├─ github_api_request (45ms)
  │   └─ retry_get_item_id (42ms)  ← Shows retry happened!
  │       ├─ attempt_1 (15ms) FAILED
  │       └─ attempt_2 (15ms) SUCCESS
  ├─ set_project_fields (156ms)
  │   ├─ set_status (52ms)
  │   ├─ set_type (51ms)
  │   └─ set_energy (51ms)
  └─ update_daily_log (52ms)
      └─ file_write (48ms)
```

**Benefits**:
- 🔍 **See exactly where time is spent**
- 🔍 **Identify slow operations** (GitHub API latency)
- 🔍 **Debug failures** (which span failed and why)
- 🔍 **Retry visibility** (see that retry logic worked)

#### 2. Metrics (Time-Series Data)

```python
from opentelemetry import metrics

meter = metrics.get_meter("gpwk")

# Counters
capture_total = meter.create_counter(
    "gpwk.capture.total",
    description="Total capture operations",
    unit="1"
)

capture_errors = meter.create_counter(
    "gpwk.capture.errors",
    description="Failed capture operations",
    unit="1"
)

github_api_calls = meter.create_counter(
    "gpwk.github.api_calls.total",
    description="GitHub API calls made",
    unit="1"
)

# Histograms
capture_duration = meter.create_histogram(
    "gpwk.capture.duration",
    description="Capture operation duration",
    unit="ms"
)

github_api_latency = meter.create_histogram(
    "gpwk.github.api_latency",
    description="GitHub API request latency",
    unit="ms"
)

# Gauges
tasks_today = meter.create_up_down_counter(
    "gpwk.tasks.today",
    description="Number of tasks planned for today",
    unit="1"
)

carryover_count = meter.create_up_down_counter(
    "gpwk.carryover.count",
    description="Number of carried over tasks",
    unit="1"
)

# Usage
def capture_activity(text: str):
    start_time = time.time()

    try:
        # ... operation ...

        capture_total.add(1, {
            "status": "success",
            "type": parsed.type,
            "completed": str(parsed.is_completed)
        })

    except Exception as e:
        capture_errors.add(1, {"error_type": type(e).__name__})
        raise

    finally:
        duration_ms = (time.time() - start_time) * 1000
        capture_duration.record(duration_ms, {
            "operation": "capture",
            "type": parsed.type
        })
```

**Metrics You Get**:
- `gpwk_capture_total` - How many captures per day
- `gpwk_capture_duration_bucket` - p50, p95, p99 latency
- `gpwk_github_api_calls_total` - API usage tracking
- `gpwk_github_api_latency_bucket` - API performance
- `gpwk_tasks_today` - Current task count
- `gpwk_carryover_count` - How many tasks carried over
- `gpwk_completion_rate` - Task completion percentage
- `gpwk_energy_distribution` - Distribution of deep/shallow/quick tasks

#### 3. Structured Logs

```python
import structlog

logger = structlog.get_logger("gpwk")

def create_issue(title: str, labels: List[str]):
    logger.info(
        "creating_github_issue",
        title=title,
        labels=labels,
        repo=REPO_NAME
    )

    try:
        issue = gh.create_issue(title, labels)
        logger.info(
            "github_issue_created",
            issue_number=issue.number,
            issue_url=issue.url,
            duration_ms=elapsed
        )
        return issue

    except GithubException as e:
        logger.error(
            "github_issue_creation_failed",
            title=title,
            error=str(e),
            status_code=e.status,
            exc_info=True
        )
        raise
```

**Logs Sent to Loki**:
```json
{
  "timestamp": "2025-12-20T10:05:23.456Z",
  "level": "info",
  "event": "github_issue_created",
  "issue_number": 45,
  "issue_url": "https://github.com/...",
  "duration_ms": 234,
  "trace_id": "abc123...",
  "span_id": "def456..."
}
```

**Benefits**:
- 📊 **Query logs** by trace_id to see all logs for one operation
- 📊 **Correlate** logs with traces and metrics
- 📊 **Search** for specific errors or patterns
- 📊 **Alert** on error rate spikes

## Dashboards You Could Build

### 1. Personal Productivity Dashboard

**Panels**:
- **Task Completion Rate** (daily, weekly, monthly)
  - Query: `rate(gpwk_tasks_completed_total[1d]) / rate(gpwk_tasks_planned_total[1d])`
- **Energy Level Distribution** (deep vs shallow vs quick)
  - Pie chart of task types
- **Best Performing Time Windows**
  - Heatmap: completion rate by hour of day
- **Carryover Trends**
  - Graph: tasks with c1, c2, c3 labels over time
- **AI Delegation Success Rate**
  - `rate(gpwk_ai_tasks_success[7d]) / rate(gpwk_ai_tasks_total[7d])`

### 2. GPWK System Health Dashboard

**Panels**:
- **Command Execution Rate** (captures, plans, triages per day)
- **GitHub API Latency** (p50, p95, p99)
- **Error Rate by Command**
- **Retry Count** (how often retries are needed)
- **Operation Duration** (slow operations highlighted)

### 3. Weekly Review Dashboard

Automated insights for `/gpwk.review`:
- **Completion rate this week**: 78% (down from 85% last week)
- **Most productive day**: Tuesday (92% completion)
- **Carryover problem**: 3 tasks at c3 level
- **AI delegation**: 12 tasks delegated, 95% success rate
- **Deep work blocks**: Average 1.8 per day (target: 2)

## Self-Optimizing Features

### 1. Data-Driven `/gpwk.optimize`

**Current**: Analyzes text logs manually

**With Metrics**: Query Grafana for actual data!

```python
def optimize_analyze_productivity() -> OptimizationReport:
    """Query Grafana to get actual productivity metrics."""

    # Query Grafana for completion rates by time of day
    query = """
    rate(gpwk_tasks_completed_total{time_of_day=~".*"}[7d])
    /
    rate(gpwk_tasks_planned_total{time_of_day=~".*"}[7d])
    """
    results = grafana.query_prometheus(query)

    # Find best performing time windows
    best_times = sorted(results, key=lambda x: x.value, reverse=True)[:3]

    return OptimizationReport(
        best_deep_work_times=best_times,
        recommendation="Schedule deep work at 9-11 AM (92% completion rate)"
    )
```

**Insights**:
- "You complete deep work tasks 85% faster in mornings vs afternoons"
- "Tasks labeled ~quick have 98% completion rate, ~deep have 67%"
- "You carry over 3x more tasks on Fridays (reduce Friday planning)"
- "AI-delegated research tasks save you avg 45 minutes each"

### 2. Predictive Carryover

```python
# Train simple ML model on historical data
from sklearn.linear_model import LogisticRegression

def predict_carryover_risk(task: Task) -> float:
    """Predict likelihood of task carrying over based on features."""

    # Features from metrics
    features = [
        task.energy_level,  # deep=3, shallow=2, quick=1
        task.priority,      # high=3, medium=2, low=1
        task.day_of_week,   # Monday=1, ..., Friday=5
        task.time_planned,  # Hour of day (9, 10, 11, etc.)
        historical_completion_rate_for_similar_tasks
    ]

    risk = model.predict_proba([features])[0][1]

    if risk > 0.7:
        logger.warning(
            "high_carryover_risk",
            task_number=task.number,
            risk=risk,
            recommendation="Consider breaking down or rescheduling"
        )

    return risk
```

### 3. Alerting

**Grafana Alerts**:
```yaml
alert: HighCarryoverRate
expr: |
  (
    count(gpwk_tasks{label=~"pwk:c[23]"})
    /
    count(gpwk_tasks{status="today"})
  ) > 0.3
for: 1h
annotations:
  summary: "30%+ of today's tasks are carryovers"
  description: "Consider running /gpwk.triage to reassess priorities"
```

```yaml
alert: GitHubAPIErrors
expr: |
  rate(gpwk_github_api_errors_total[5m]) > 0.1
for: 5m
annotations:
  summary: "GitHub API error rate elevated"
  description: "Check GitHub status or authentication"
```

## Implementation Plan

### Phase 1: Foundation (Week 1)

**Deliverables**:
- [ ] Create `gpwk/lib/python/gpwk_core/` Python package
- [ ] Setup OpenTelemetry SDK with OTLP exporter
- [ ] Configure Grafana Alloy to receive OTLP
- [ ] Basic instrumentation for one command (`/gpwk.capture`)
- [ ] Verify traces/metrics/logs in Grafana

**Structure**:
```
gpwk/
├── lib/
│   └── python/
│       └── gpwk_core/
│           ├── __init__.py
│           ├── telemetry.py       # OpenTelemetry setup
│           ├── config.py          # Configuration management
│           ├── github_ops.py      # GitHub operations
│           ├── parser.py          # GPWK notation parser
│           ├── log_ops.py         # Daily log operations
│           └── models.py          # Data models
├── bin/
│   └── gpwk                       # Python CLI entry point
├── config/
│   └── alloy/
│       └── gpwk.alloy            # Alloy configuration
└── tests/
    └── test_*.py                 # Pytest tests
```

### Phase 2: Migration (Week 2)

**Deliverables**:
- [ ] Migrate `/gpwk.capture` to use Python backend
- [ ] Migrate `/gpwk.plan` to use Python backend
- [ ] Add comprehensive metrics and traces
- [ ] Build first Grafana dashboard

### Phase 3: Advanced Features (Week 3)

**Deliverables**:
- [ ] Build productivity analytics dashboard
- [ ] Implement `/gpwk.optimize` with Grafana queries
- [ ] Setup alerts for errors and carryover
- [ ] Add predictive carryover risk

### Phase 4: Self-Optimization (Week 4)

**Deliverables**:
- [ ] ML model for task completion prediction
- [ ] Automated recommendations in `/gpwk.plan`
- [ ] Weekly insights dashboard
- [ ] Export/share productivity reports

## Sample Code: Instrumented Capture

```python
# gpwk_core/commands/capture.py

from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
import structlog

tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)
logger = structlog.get_logger(__name__)

# Metrics
capture_counter = meter.create_counter("gpwk.capture.total")
capture_duration = meter.create_histogram("gpwk.capture.duration_ms")
capture_errors = meter.create_counter("gpwk.capture.errors")

@tracer.start_as_current_span("gpwk_capture")
def capture(text: str, config: GPWKConfig) -> CaptureResult:
    """
    Capture an activity or task to GitHub with full instrumentation.

    This function creates a GitHub issue, adds it to the project,
    sets all metadata fields, and updates the daily log file.

    All operations are instrumented with OpenTelemetry for observability.
    """
    start_time = time.time()
    span = trace.get_current_span()

    # Add input to span
    span.set_attribute("capture.input_text", text)

    logger.info("capture_started", input_length=len(text))

    try:
        # Parse input
        with tracer.start_as_current_span("parse") as parse_span:
            parser = GPWKParser()
            parsed = parser.parse_capture_notation(text)

            # Add attributes
            parse_span.set_attribute("capture.type", parsed.type)
            parse_span.set_attribute("capture.is_completed", parsed.is_completed)
            parse_span.set_attribute("capture.priority", parsed.priority or "none")
            parse_span.set_attribute("capture.energy", parsed.energy or "none")

            logger.info(
                "parsed_capture",
                type=parsed.type,
                completed=parsed.is_completed,
                title=parsed.title
            )

        # Create GitHub issue
        with tracer.start_as_current_span("create_issue") as issue_span:
            github = GithubOperations(config)
            issue = github.create_issue(
                title=parsed.title,
                labels=parsed.labels,
                body=parsed.body
            )

            issue_span.set_attribute("github.issue_number", issue.number)
            issue_span.set_attribute("github.issue_url", issue.url)

            logger.info(
                "issue_created",
                issue_number=issue.number,
                issue_url=issue.url
            )

        # Add to project (with retry)
        with tracer.start_as_current_span("add_to_project") as project_span:
            project_item = github.add_to_project_with_retry(
                issue_url=issue.url,
                max_retries=5
            )

            project_span.set_attribute("github.project_item_id", project_item.id)
            project_span.set_attribute("github.retry_count", project_item.retry_count)

            if project_item.retry_count > 0:
                project_span.add_event(
                    f"Required {project_item.retry_count} retries"
                )
                logger.warning(
                    "project_add_required_retries",
                    retries=project_item.retry_count
                )

        # Set fields
        with tracer.start_as_current_span("set_fields") as fields_span:
            status = "done" if parsed.is_completed else "inbox"

            github.set_project_fields(
                item_id=project_item.id,
                status=status,
                type=parsed.type,
                priority=parsed.priority,
                energy=parsed.energy
            )

            fields_span.set_attribute("project.status", status)
            fields_span.add_event(f"Set {len(parsed.project_fields)} fields")

        # Update daily log
        with tracer.start_as_current_span("update_log") as log_span:
            log_ops = LogOperations(config)
            log_ops.append_to_activity_stream(
                date=datetime.now().date(),
                issue_number=issue.number,
                title=parsed.title,
                time_range=parsed.time_range,
                completed=parsed.is_completed
            )

            log_span.set_attribute("log.date", str(datetime.now().date()))

        # Success!
        duration_ms = (time.time() - start_time) * 1000

        capture_counter.add(1, {
            "status": "success",
            "type": parsed.type,
            "completed": str(parsed.is_completed)
        })
        capture_duration.record(duration_ms, {"status": "success"})

        span.set_status(Status(StatusCode.OK))
        span.set_attribute("capture.duration_ms", duration_ms)

        logger.info(
            "capture_completed",
            issue_number=issue.number,
            duration_ms=duration_ms
        )

        return CaptureResult(
            success=True,
            issue_number=issue.number,
            issue_url=issue.url,
            duration_ms=duration_ms
        )

    except Exception as e:
        # Record error
        duration_ms = (time.time() - start_time) * 1000

        capture_errors.add(1, {
            "error_type": type(e).__name__,
            "type": parsed.type if 'parsed' in locals() else "unknown"
        })
        capture_duration.record(duration_ms, {"status": "error"})

        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))

        logger.error(
            "capture_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=duration_ms,
            exc_info=True
        )

        raise
```

## Grafana Alloy Configuration

```alloy
// gpwk/config/alloy/gpwk.alloy

// Receive OTLP from GPWK Python library
otelcol.receiver.otlp "gpwk" {
  grpc {
    endpoint = "127.0.0.1:4317"
  }

  http {
    endpoint = "127.0.0.1:4318"
  }

  output {
    metrics = [otelcol.processor.batch.default.input]
    logs    = [otelcol.processor.batch.default.input]
    traces  = [otelcol.processor.batch.default.input]
  }
}

// Batch for efficiency
otelcol.processor.batch "default" {
  output {
    metrics = [otelcol.exporter.otlp.grafana_cloud.input]
    logs    = [otelcol.exporter.otlp.grafana_cloud.input]
    traces  = [otelcol.exporter.otlp.grafana_cloud.input]
  }
}

// Export to Grafana Cloud
otelcol.exporter.otlp "grafana_cloud" {
  client {
    endpoint = env("GRAFANA_CLOUD_OTLP_ENDPOINT")

    auth = otelcol.auth.basic.grafana_cloud.handler
  }
}

otelcol.auth.basic "grafana_cloud" {
  username = env("GRAFANA_CLOUD_INSTANCE_ID")
  password = env("GRAFANA_CLOUD_API_KEY")
}

// Meta-monitoring: Monitor Alloy itself
prometheus.exporter.self "alloy" { }

prometheus.scrape "alloy_metrics" {
  targets    = prometheus.exporter.self.alloy.targets
  forward_to = [prometheus.remote_write.grafana_cloud.receiver]
}

prometheus.remote_write "grafana_cloud" {
  endpoint {
    url = env("GRAFANA_CLOUD_PROMETHEUS_URL")

    basic_auth {
      username = env("GRAFANA_CLOUD_INSTANCE_ID")
      password = env("GRAFANA_CLOUD_API_KEY")
    }
  }
}
```

## Benefits Summary

### For Reliability
- ✅ No shell escaping issues
- ✅ Automatic retry with exponential backoff
- ✅ Type safety catches errors early
- ✅ Comprehensive error handling
- ✅ Unit tests for all functionality

### For Observability
- 📊 **Traces**: See exactly where failures occur
- 📊 **Metrics**: Track productivity patterns over time
- 📊 **Logs**: Structured, searchable, correlated
- 📊 **Dashboards**: Visualize your productivity data
- 📊 **Alerts**: Get notified of issues proactively

### For Self-Optimization
- 🎯 Data-driven insights from actual metrics
- 🎯 Predictive analytics for carryover risk
- 🎯 ML-based recommendations
- 🎯 Automated weekly reports
- 🎯 Continuous improvement based on real data

### For Developer Experience
- 💻 Python is more maintainable than shell scripts
- 💻 IDE support (autocomplete, type checking)
- 💻 Easy to test and debug
- 💻 Rich ecosystem of libraries
- 💻 Better collaboration (clear code structure)

## Next Steps

1. **Validate Grafana Alloy setup**: Ensure Alloy is running and can receive OTLP
2. **Build proof of concept**: Implement instrumented `/gpwk.capture` in Python
3. **Deploy to Grafana Cloud**: Send telemetry and build first dashboard
4. **Iterate**: Add more commands, refine instrumentation
5. **Analyze**: Use the data to optimize GPWK and your productivity

This transforms GPWK from a simple task tracker into a **data-driven productivity platform**!

---
*Proposal created: 2025-12-20*
