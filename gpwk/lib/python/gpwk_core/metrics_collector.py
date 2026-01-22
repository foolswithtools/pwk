"""Pull-based metrics collector for GPWK.

This module periodically queries GitHub and local state to record
metrics based on ACTUAL state, not assumed state from operations.

Benefits:
- Metrics reflect reality, not assumptions
- Catches external changes (manual edits via GitHub UI)
- Can recover from telemetry downtime
- Source of truth is GitHub/logs, not our code
"""

import time
from datetime import datetime, date, timezone
from pathlib import Path
from typing import Dict, List, Callable
import structlog
import subprocess
import json

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import Observation

from .models import GPWKConfig
from .telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)


class MetricsCollector:
    """Periodic metrics collector that queries actual state."""

    def __init__(self, config: GPWKConfig):
        """Initialize metrics collector."""
        self.config = config

        # Current metric values (updated by collection, read by callbacks)
        self.issues_open = 0
        self.issues_by_type: Dict[str, int] = {}
        self.issues_by_priority: Dict[str, int] = {}
        self.issues_by_energy: Dict[str, int] = {}
        self.issues_created_today = 0
        self.issues_closed_today = 0
        self.completion_rate_percent = 0
        self.work_time_minutes = 0
        self.backlog_age_days = 0

        # Register observable gauges with callbacks
        self._register_observable_gauges()

    def _register_observable_gauges(self):
        """Register all observable gauge metrics with their callbacks."""

        # Total open issues
        meter.create_observable_gauge(
            "gpwk.productivity.issues_open",
            callbacks=[lambda options: [Observation(self.issues_open)]],
            description="Current number of open issues (from GitHub)",
            unit="1"
        )

        # Issues by type
        meter.create_observable_gauge(
            "gpwk.productivity.issues_by_type",
            callbacks=[self._observe_issues_by_type],
            description="Current number of issues by type (from GitHub)",
            unit="1"
        )

        # Issues by priority
        meter.create_observable_gauge(
            "gpwk.productivity.issues_by_priority",
            callbacks=[self._observe_issues_by_priority],
            description="Current number of issues by priority (from GitHub)",
            unit="1"
        )

        # Issues by energy
        meter.create_observable_gauge(
            "gpwk.productivity.issues_by_energy",
            callbacks=[self._observe_issues_by_energy],
            description="Current number of issues by energy (from GitHub)",
            unit="1"
        )

        # Issues created today
        meter.create_observable_gauge(
            "gpwk.productivity.issues_created_today",
            callbacks=[lambda options: [Observation(self.issues_created_today)]],
            description="Issues created today (from GitHub)",
            unit="1"
        )

        # Issues closed today
        meter.create_observable_gauge(
            "gpwk.productivity.issues_closed_today",
            callbacks=[lambda options: [Observation(self.issues_closed_today)]],
            description="Issues closed today (from GitHub)",
            unit="1"
        )

        # Completion rate
        meter.create_observable_gauge(
            "gpwk.productivity.completion_rate_percent",
            callbacks=[lambda options: [Observation(self.completion_rate_percent)]],
            description="Completion rate for today: closed/created * 100 (from GitHub)",
            unit="percent"
        )

        # Work time
        meter.create_observable_gauge(
            "gpwk.productivity.work_time_minutes",
            callbacks=[lambda options: [Observation(self.work_time_minutes)]],
            description="Total work time tracked today (from daily log)",
            unit="minutes"
        )

        # Backlog age
        meter.create_observable_gauge(
            "gpwk.productivity.backlog_age_days",
            callbacks=[lambda options: [Observation(self.backlog_age_days)]],
            description="Age of oldest open issue (from GitHub)",
            unit="days"
        )

    def _observe_issues_by_type(self, options) -> List[Observation]:
        """Callback for issues_by_type gauge."""
        return [Observation(count, {"type": issue_type})
                for issue_type, count in self.issues_by_type.items()]

    def _observe_issues_by_priority(self, options) -> List[Observation]:
        """Callback for issues_by_priority gauge."""
        return [Observation(count, {"priority": priority})
                for priority, count in self.issues_by_priority.items()]

    def _observe_issues_by_energy(self, options) -> List[Observation]:
        """Callback for issues_by_energy gauge."""
        return [Observation(count, {"energy": energy})
                for energy, count in self.issues_by_energy.items()]

    @tracer.start_as_current_span("collect_all_metrics")
    def collect_all_metrics(self):
        """Collect all productivity metrics from GitHub and logs."""
        self._collect_github_metrics()
        self._collect_log_metrics()
        logger.info("metrics_collected")

    @tracer.start_as_current_span("collect_github_metrics")
    def _collect_github_metrics(self):
        """Query GitHub for actual issue state and update metric values."""

        # Query GitHub GraphQL API for all issues
        query = """
        query {
          repository(owner: "clostaunau", name: "personal-work") {
            issues(first: 100, states: [OPEN, CLOSED], orderBy: {field: UPDATED_AT, direction: DESC}) {
              nodes {
                number
                title
                state
                createdAt
                closedAt
                labels(first: 20) {
                  nodes {
                    name
                  }
                }
              }
            }
          }
        }
        """

        result = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={query}"],
            capture_output=True,
            text=True,
            check=True
        )

        issues = json.loads(result.stdout)["data"]["repository"]["issues"]["nodes"]

        # Count open issues
        open_issues = [i for i in issues if i["state"] == "OPEN"]
        self.issues_open = len(open_issues)

        # Count by type
        self.issues_by_type = self._count_by_label_prefix(open_issues, "pwk:")

        # Count by priority
        self.issues_by_priority = self._count_by_label_prefix(open_issues, "priority:")

        # Count by energy
        self.issues_by_energy = self._count_by_label_prefix(open_issues, "energy:")

        # Calculate backlog age (oldest open issue)
        if open_issues:
            oldest = min(open_issues, key=lambda x: x["createdAt"])
            created = datetime.fromisoformat(oldest["createdAt"].replace("Z", "+00:00"))
            age_days = (datetime.now(created.tzinfo) - created).days
            self.backlog_age_days = age_days

        # Calculate today's metrics (use UTC date to match GitHub API timestamps)
        today_utc = datetime.now(timezone.utc).date().isoformat()
        created_today = [i for i in issues if i.get("createdAt", "").startswith(today_utc)]
        closed_today = [i for i in issues if i.get("closedAt") and i.get("closedAt", "").startswith(today_utc)]

        # Update daily counts
        self.issues_created_today = len(created_today)
        self.issues_closed_today = len(closed_today)

        # Calculate completion rate
        if created_today:
            self.completion_rate_percent = int((len(closed_today) / len(created_today)) * 100)
        else:
            self.completion_rate_percent = 0

        logger.info(
            "github_metrics_collected",
            open_issues=len(open_issues),
            created_today=len(created_today),
            closed_today=len(closed_today)
        )

    @tracer.start_as_current_span("collect_log_metrics")
    def _collect_log_metrics(self):
        """Parse today's daily log for work time tracking."""

        today = date.today()
        log_path = Path(self.config.logs_dir) / f"{today.isoformat()}.md"

        if not log_path.exists():
            self.work_time_minutes = 0
            logger.info("log_metrics_collected", work_time_minutes=0)
            return

        content = log_path.read_text()

        # Parse work sessions from ## Work Time section
        total_minutes = 0
        in_work_time_section = False

        for line in content.split("\n"):
            if line.startswith("## Work Time"):
                in_work_time_section = True
                continue
            elif line.startswith("##") and in_work_time_section:
                break
            elif in_work_time_section and "-" in line and ":" in line:
                # Parse time range like "09:00 - 10:30"
                try:
                    parts = line.split("-")
                    if len(parts) == 2:
                        start_time = parts[0].strip().split(":")
                        end_time = parts[1].strip().split(":")
                        start_hour, start_min = int(start_time[0]), int(start_time[1])
                        end_hour, end_min = int(end_time[0]), int(end_time[1])
                        start_minutes = start_hour * 60 + start_min
                        end_minutes = end_hour * 60 + end_min
                        duration = end_minutes - start_minutes
                        if duration > 0:  # Sanity check
                            total_minutes += duration
                except (ValueError, IndexError):
                    continue

        self.work_time_minutes = total_minutes

        logger.info(
            "log_metrics_collected",
            work_time_minutes=total_minutes
        )

    def _count_by_label_prefix(self, issues: List[Dict], prefix: str) -> Dict[str, int]:
        """Count issues by label prefix (e.g., 'pwk:' for types)."""
        counts = {}
        for issue in issues:
            labels = [label["name"] for label in issue.get("labels", {}).get("nodes", [])]
            for label in labels:
                if label.startswith(prefix):
                    label_value = label[len(prefix):]
                    counts[label_value] = counts.get(label_value, 0) + 1
        return counts

    def run(self, interval_seconds: int = 60):
        """Run metrics collection loop."""
        logger.info("metrics_collector_started", interval_seconds=interval_seconds)

        while True:
            try:
                self.collect_all_metrics()
            except Exception as e:
                logger.error("metrics_collection_failed", error=str(e))

            time.sleep(interval_seconds)


def run_collector_loop(config: GPWKConfig, interval_seconds: int = 60):
    """Run metrics collector daemon loop."""
    collector = MetricsCollector(config)
    collector.run(interval_seconds)
