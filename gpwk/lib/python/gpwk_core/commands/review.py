"""GPWK Review command - End-of-day reflection with telemetry."""

import time
import subprocess
import json
from datetime import datetime, date, timezone
from pathlib import Path
from typing import List, Dict, Optional
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import ReviewResult
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Operational Metrics (how review performs)
review_operations = meter.create_counter(
    "gpwk.review.operations.total",
    description="Total review operations",
    unit="1"
)

review_duration = meter.create_histogram(
    "gpwk.review.duration",
    description="Review operation duration",
    unit="ms"
)

review_errors = meter.create_counter(
    "gpwk.review.errors",
    description="Failed review operations",
    unit="1"
)


class ReviewCommand:
    """Review command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize review command."""
        self.config = config

    @tracer.start_as_current_span("review")
    def review(
        self,
        review_date: Optional[date] = None,
        quick: bool = False,
        full: bool = True
    ) -> ReviewResult:
        """
        Generate end-of-day review.

        Args:
            review_date: Date to review (defaults to today)
            quick: Brief metrics only
            full: Full review with details

        Returns:
            ReviewResult with metrics and summary
        """
        start_time = time.time()
        span = trace.get_current_span()

        if not review_date:
            review_date = date.today()

        span.set_attribute("review.date", str(review_date))
        span.set_attribute("review.quick", quick)
        span.set_attribute("review.full", full)

        logger.info(
            "review_started",
            review_date=str(review_date),
            quick=quick,
            full=full
        )

        try:
            # Gather data from GitHub
            closed_issues = self._get_closed_issues(review_date)
            remaining_issues = self._get_remaining_today_issues()
            carryover_issues = self._get_carryover_issues()

            # Calculate metrics
            completed_count = len(closed_issues)
            remaining_count = len(remaining_issues)
            total_planned = completed_count + remaining_count
            completion_rate = (completed_count / total_planned * 100) if total_planned > 0 else 0

            # Collect reflections (only in full mode, not quick)
            reflections = None
            if full and not quick:
                reflections = self._collect_reflections()

            # Update daily log with review data
            self._update_daily_log(
                review_date,
                closed_issues,
                remaining_issues,
                carryover_issues,
                completed_count,
                remaining_count,
                completion_rate,
                reflections
            )

            duration_ms = (time.time() - start_time) * 1000

            review_operations.add(1, {"status": "success", "mode": "quick" if quick else "full"})
            review_duration.record(duration_ms, {"status": "success"})

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("review.duration_ms", duration_ms)
            span.set_attribute("review.completed_count", completed_count)
            span.set_attribute("review.remaining_count", remaining_count)
            span.set_attribute("review.completion_rate", completion_rate)

            logger.info(
                "review_completed",
                duration_ms=duration_ms,
                completed=completed_count,
                remaining=remaining_count,
                completion_rate=completion_rate,
                success=True
            )

            return ReviewResult(
                success=True,
                review_date=review_date,
                completed_issues=closed_issues,
                remaining_issues=remaining_issues,
                carryover_issues=carryover_issues,
                completed_count=completed_count,
                remaining_count=remaining_count,
                completion_rate=completion_rate,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            review_errors.add(1, {"error_type": type(e).__name__})
            review_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "review_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                exc_info=True
            )

            return ReviewResult(
                success=False,
                review_date=review_date,
                error=str(e),
                duration_ms=duration_ms
            )

    @tracer.start_as_current_span("get_closed_issues")
    def _get_closed_issues(self, review_date: date) -> List[Dict]:
        """Get issues closed on the review date (in local time)."""
        # Get closed issues from review_date and the next day (UTC)
        # This accounts for timezone differences where an issue closed late on
        # review_date in local time might be early next day in UTC
        from datetime import timedelta
        next_day = review_date + timedelta(days=1)

        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--state", "closed",
                "--search", f"closed:{review_date.isoformat()}..{next_day.isoformat()}",
                "--json", "number,title,labels,closedAt",
                "--limit", "100"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        all_issues = json.loads(result.stdout)

        # Filter to only issues closed on the exact review_date (in local time)
        # This handles timezone differences by converting UTC to local time
        filtered_issues = []
        for issue in all_issues:
            closed_at = issue.get("closedAt")
            if closed_at:
                try:
                    # Parse ISO timestamp (GitHub returns UTC with 'Z' suffix)
                    closed_datetime_utc = datetime.fromisoformat(closed_at.replace('Z', '+00:00'))

                    # Convert to local timezone
                    closed_datetime_local = closed_datetime_utc.astimezone()

                    # Extract local date for comparison
                    closed_date_local = closed_datetime_local.date()

                    if closed_date_local == review_date:
                        filtered_issues.append(issue)
                except (ValueError, AttributeError) as e:
                    logger.warning(
                        "failed_to_parse_closed_date",
                        issue_number=issue.get("number"),
                        closed_at=closed_at,
                        error=str(e)
                    )
                    # Include issue if we can't parse the date (fail open)
                    filtered_issues.append(issue)

        logger.info(
            "closed_issues_fetched",
            count=len(filtered_issues),
            total_fetched=len(all_issues),
            date=str(review_date)
        )

        return filtered_issues

    @tracer.start_as_current_span("get_remaining_today_issues")
    def _get_remaining_today_issues(self) -> List[Dict]:
        """Get issues still open in Today column."""
        # Get all project items
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

        # Filter for "Today" status and open state
        from ..status_utils import compare_status

        remaining = []
        for item in items:
            if compare_status(item.get("status"), "today"):
                content = item.get("content", {})
                if content.get("type") == "Issue":
                    # Only include issues that are actually open (not closed)
                    if content.get("state") == "OPEN":
                        remaining.append(item)

        logger.info("remaining_today_issues_fetched", count=len(remaining))
        return remaining

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

    @tracer.start_as_current_span("collect_reflections")
    def _collect_reflections(self) -> Dict[str, str]:
        """Collect interactive reflections from user."""
        import sys

        reflections = {}

        print()
        print("=" * 60)
        print("REFLECTIONS")
        print("=" * 60)
        print()

        prompts = [
            ("went_well", "What went well today?"),
            ("could_improve", "What could be improved?"),
            ("learned", "What did you learn?"),
            ("tomorrow_priority", "What's your top priority for tomorrow?")
        ]

        for key, prompt in prompts:
            print(f"{prompt}")
            print("> ", end="", flush=True)
            try:
                response = input().strip()
                reflections[key] = response if response else "(No response)"
            except (EOFError, KeyboardInterrupt):
                reflections[key] = "(Skipped)"
            print()

        logger.info("reflections_collected", reflection_count=len(reflections))
        return reflections

    @tracer.start_as_current_span("update_daily_log")
    def _update_daily_log(
        self,
        review_date: date,
        completed_issues: List[Dict],
        remaining_issues: List[Dict],
        carryover_issues: List[Dict],
        completed_count: int,
        remaining_count: int,
        completion_rate: float,
        reflections: Optional[Dict[str, str]] = None
    ) -> None:
        """Update daily log file with review data."""
        logs_dir = Path(self.config.logs_dir)
        log_file = logs_dir / f"{review_date}.md"

        if not log_file.exists():
            logger.warning("daily_log_not_found", log_file=str(log_file))
            print(f"\n⚠ Daily log not found: {log_file}")
            print("  Run /gpwk.plan first to create today's log file")
            return

        # Read existing log
        content = log_file.read_text()

        # Build review section
        review_section = self._build_review_section(
            completed_issues,
            remaining_issues,
            carryover_issues,
            completed_count,
            remaining_count,
            completion_rate,
            reflections
        )

        # Replace "End of Day" section
        import re

        # Try multiple patterns to find existing End of Day section
        # Pattern 1: Empty placeholder
        placeholder_pattern = r'## End of Day\n<!-- Filled by /gpwk\.review -->\n- Completed:\n- Remaining:\n- Reflections:\n'

        # Pattern 2: Existing "End of Day Review" section (replace everything until end of file or next ## heading)
        existing_review_pattern = r'## End of Day[^\n]*\n(?:(?!^## ).*\n?)*'

        if re.search(placeholder_pattern, content):
            # Replace empty placeholder
            updated_content = re.sub(placeholder_pattern, review_section, content)
        elif re.search(existing_review_pattern, content, re.MULTILINE):
            # Replace existing review section
            updated_content = re.sub(existing_review_pattern, review_section.rstrip() + "\n", content, flags=re.MULTILINE)
        else:
            # Append to end if section doesn't exist
            updated_content = content.rstrip() + "\n\n" + review_section

        # Write updated content
        log_file.write_text(updated_content)

        logger.info("daily_log_updated", log_file=str(log_file), size=len(updated_content))

    def _build_review_section(
        self,
        completed_issues: List[Dict],
        remaining_issues: List[Dict],
        carryover_issues: List[Dict],
        completed_count: int,
        remaining_count: int,
        completion_rate: float,
        reflections: Optional[Dict[str, str]] = None
    ) -> str:
        """Build the End of Day review section content."""
        from datetime import datetime

        section = "## End of Day Review\n\n"

        # Metrics
        section += "### Metrics\n"
        section += f"- Completed: {completed_count}/{completed_count + remaining_count}"
        if completed_count + remaining_count > 0:
            section += f" ({completion_rate:.0f}%)"
        section += "\n"
        section += f"- Remaining: {remaining_count} tasks\n"

        # Add task type breakdown
        if completed_issues:
            personal = sum(1 for i in completed_issues if any(
                (l.get("name") if isinstance(l, dict) else l) == "pwk:personal"
                for l in i.get("labels", [])
            ))
            ai = sum(1 for i in completed_issues if any(
                (l.get("name") if isinstance(l, dict) else l) == "pwk:ai"
                for l in i.get("labels", [])
            ))
            if personal > 0 or ai > 0:
                section += f"- Personal tasks: {personal}, AI tasks: {ai}\n"

        section += "\n"

        # Completed issues
        section += "### Completed\n"
        if completed_issues:
            for issue in completed_issues:
                number = issue.get("number", "?")
                title = issue.get("title", "Untitled")
                section += f"- #{number} - {title}\n"
        else:
            section += "- (None)\n"
        section += "\n"

        # Remaining/Carryover
        if remaining_issues or carryover_issues:
            section += "### Remaining (Carryover Candidates)\n"
            # Combine and deduplicate
            all_remaining = {}
            for item in remaining_issues:
                content = item.get("content", {})
                number = content.get("number")
                if number:
                    all_remaining[number] = content.get("title", "Untitled")

            for issue in carryover_issues:
                number = issue.get("number")
                if number and number not in all_remaining:
                    all_remaining[number] = issue.get("title", "Untitled")

            for number, title in all_remaining.items():
                section += f"- #{number} - {title}\n"
            section += "\n"

        # Reflections
        if reflections:
            section += "### Reflections\n\n"
            section += f"**What went well:** {reflections.get('went_well', '(No response)')}\n\n"
            section += f"**Could improve:** {reflections.get('could_improve', '(No response)')}\n\n"
            section += f"**Learned:** {reflections.get('learned', '(No response)')}\n\n"
            section += f"**Tomorrow's priority:** {reflections.get('tomorrow_priority', '(No response)')}\n\n"

        # Timestamp
        now = datetime.now()
        section += f"### Review completed at {now.strftime('%I:%M %p')}\n"

        return section
