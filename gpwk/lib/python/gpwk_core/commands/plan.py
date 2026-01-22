"""GPWK Plan command - Generate daily/weekly plans with telemetry."""

import time
import subprocess
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import PlanResult
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Operational Metrics (how plan performs)
plan_operations = meter.create_counter(
    "gpwk.plan.operations.total",
    description="Total plan operations",
    unit="1"
)

plan_duration = meter.create_histogram(
    "gpwk.plan.duration",
    description="Plan operation duration",
    unit="ms"
)

plan_errors = meter.create_counter(
    "gpwk.plan.errors",
    description="Failed plan operations",
    unit="1"
)


class PlanCommand:
    """Plan command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize plan command."""
        self.config = config

    @tracer.start_as_current_span("plan")
    def plan(
        self,
        plan_date: Optional[date] = None,
        mode: str = "today"
    ) -> PlanResult:
        """
        Generate daily or weekly plan.

        Args:
            plan_date: Date to plan for (defaults to today)
            mode: "today", "tomorrow", or "week"

        Returns:
            PlanResult with plan details
        """
        start_time = time.time()
        span = trace.get_current_span()

        if not plan_date:
            if mode == "tomorrow":
                plan_date = date.today() + timedelta(days=1)
            else:
                plan_date = date.today()

        span.set_attribute("plan.date", str(plan_date))
        span.set_attribute("plan.mode", mode)

        logger.info(
            "plan_started",
            plan_date=str(plan_date),
            mode=mode
        )

        try:
            # Fetch issues from GitHub
            today_issues = self._get_today_issues()
            carryover_issues = self._get_carryover_issues()
            high_priority_issues = self._get_high_priority_issues()
            ai_issues = self._get_ai_issues()

            # Generate daily log
            log_path = self._generate_daily_log(
                plan_date,
                today_issues,
                carryover_issues,
                high_priority_issues,
                ai_issues
            )

            duration_ms = (time.time() - start_time) * 1000

            plan_operations.add(1, {"status": "success", "mode": mode})
            plan_duration.record(duration_ms, {"status": "success"})

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("plan.duration_ms", duration_ms)
            span.set_attribute("plan.today_count", len(today_issues))
            span.set_attribute("plan.carryover_count", len(carryover_issues))

            logger.info(
                "plan_completed",
                duration_ms=duration_ms,
                today_count=len(today_issues),
                carryover_count=len(carryover_issues),
                log_path=str(log_path),
                success=True
            )

            return PlanResult(
                success=True,
                plan_date=plan_date,
                log_path=str(log_path),
                today_issues=today_issues,
                carryover_issues=carryover_issues,
                high_priority_issues=high_priority_issues,
                ai_issues=ai_issues,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            plan_errors.add(1, {"error_type": type(e).__name__})
            plan_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "plan_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                exc_info=True
            )

            return PlanResult(
                success=False,
                plan_date=plan_date,
                error=str(e),
                duration_ms=duration_ms
            )

    @tracer.start_as_current_span("get_today_issues")
    def _get_today_issues(self) -> List[Dict]:
        """Get issues in Today column."""
        result = subprocess.run(
            [
                "gh", "project", "item-list",
                str(self.config.github_project_number),
                "--owner", "@me",
                "--format", "json",
                "--limit", "1000"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        data = json.loads(result.stdout)
        items = data.get("items", [])

        # Filter for "Today" status
        from ..status_utils import compare_status
        today = [i for i in items if compare_status(i.get("status"), "today")]

        logger.info("today_issues_fetched", count=len(today))
        return today

    @tracer.start_as_current_span("get_carryover_issues")
    def _get_carryover_issues(self) -> List[Dict]:
        """Get issues with carryover labels."""
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--label", "pwk:c1,pwk:c2,pwk:c3",
                "--state", "open",
                "--json", "number,title,labels",
                "--limit", "100"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        issues = json.loads(result.stdout)
        logger.info("carryover_issues_fetched", count=len(issues))
        return issues

    @tracer.start_as_current_span("get_high_priority_issues")
    def _get_high_priority_issues(self) -> List[Dict]:
        """Get high priority issues."""
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--label", "priority:high",
                "--state", "open",
                "--json", "number,title,labels",
                "--limit", "50"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        issues = json.loads(result.stdout)
        logger.info("high_priority_issues_fetched", count=len(issues))
        return issues

    @tracer.start_as_current_span("get_ai_issues")
    def _get_ai_issues(self) -> List[Dict]:
        """Get AI-delegatable issues."""
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--label", "pwk:ai",
                "--state", "open",
                "--json", "number,title,labels",
                "--limit", "50"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        issues = json.loads(result.stdout)
        logger.info("ai_issues_fetched", count=len(issues))
        return issues

    @tracer.start_as_current_span("generate_daily_log")
    def _generate_daily_log(
        self,
        plan_date: date,
        today_issues: List[Dict],
        carryover_issues: List[Dict],
        high_priority_issues: List[Dict],
        ai_issues: List[Dict]
    ) -> Path:
        """Generate or update daily log file."""
        logs_dir = Path(self.config.logs_dir)
        logs_dir.mkdir(parents=True, exist_ok=True)

        log_file = logs_dir / f"{plan_date}.md"

        # Check if log already exists
        if log_file.exists():
            logger.info("daily_log_exists", log_file=str(log_file))
            return log_file

        # Generate log content
        content = self._build_log_content(
            plan_date,
            today_issues,
            carryover_issues,
            high_priority_issues,
            ai_issues
        )

        # Write log file
        log_file.write_text(content)

        logger.info("daily_log_created", log_file=str(log_file), size=len(content))
        return log_file

    def _build_log_content(
        self,
        plan_date: date,
        today_issues: List[Dict],
        carryover_issues: List[Dict],
        high_priority_issues: List[Dict],
        ai_issues: List[Dict]
    ) -> str:
        """Build daily log content."""
        content = f"# Daily Log: {plan_date}\n\n"

        # Carryover section
        if carryover_issues:
            content += "## Carryover from Yesterday\n"
            content += "<!-- Issues with pwk:c1+ labels -->\n"
            for issue in carryover_issues:
                number = issue.get("number", "?")
                title = issue.get("title", "Untitled")
                labels = issue.get("labels", [])
                label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                             for label in labels]
                carryover_label = next((l for l in label_names if l.startswith("pwk:c")), "")
                content += f"- [ ] #{number} - {title} [{carryover_label}]\n"
            content += "\n"

        # Today's plan
        content += "## Today's Plan\n"
        content += "<!-- Generated from project 'Today' column + suggestions -->\n\n"

        # Group by energy level
        deep_work = []
        shallow_work = []
        quick_wins = []
        other = []

        for item in today_issues:
            energy = item.get("energy", "")
            if energy == "deep":
                deep_work.append(item)
            elif energy in ["shallow", "quick"]:
                if energy == "quick":
                    quick_wins.append(item)
                else:
                    shallow_work.append(item)
            else:
                other.append(item)

        if deep_work:
            content += "### Deep Work Block\n"
            for item in deep_work:
                content += self._format_task_item(item)
            content += "\n"

        if shallow_work or other:
            content += "### Shallow Work\n"
            for item in shallow_work + other:
                content += self._format_task_item(item)
            content += "\n"

        if quick_wins:
            content += "### Quick Wins\n"
            for item in quick_wins:
                content += self._format_task_item(item)
            content += "\n"

        # AI delegation queue
        if ai_issues:
            content += "## AI Delegation Queue\n"
            content += "<!-- Issues with pwk:ai label -->\n"
            for issue in ai_issues:
                number = issue.get("number", "?")
                title = issue.get("title", "Untitled")
                content += f"- [ ] #{number} - {title}\n"
            content += "\n"

        # Activity stream
        content += "## Activity Stream\n"
        content += "<!-- Updated throughout the day by /gpwk.capture -->\n\n"

        # Blockers
        content += "## Blockers\n"
        content += "<!-- Note any blockers encountered -->\n\n"

        # End of day
        content += "## End of Day\n"
        content += "<!-- Filled by /gpwk.review -->\n"
        content += "- Completed:\n"
        content += "- Remaining:\n"
        content += "- Reflections:\n"

        return content

    def _format_task_item(self, item: Dict) -> str:
        """Format a task item for the log."""
        content = item.get("content", {})
        number = content.get("number", item.get("number", "?"))
        title = content.get("title", item.get("title", "Untitled"))

        # Get labels
        labels = item.get("labels", [])
        label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                     for label in labels]

        # Determine type marker
        type_marker = "P"
        if "pwk:ai" in label_names:
            type_marker = "AI"

        # Get energy marker
        energy = item.get("energy", "")
        energy_marker = f" ~{energy}" if energy else ""

        return f"- [ ] #{number} - {title} [{type_marker}]{energy_marker}\n"
