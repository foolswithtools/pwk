"""GPWK Complete command - fully instrumented with OpenTelemetry."""

import time
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import CompleteResult
from ..github_ops import GithubOperations
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
complete_counter = meter.create_counter(
    "gpwk.complete.total",
    description="Total complete operations",
    unit="1"
)

complete_duration = meter.create_histogram(
    "gpwk.complete.duration",
    description="Complete operation duration",
    unit="ms"
)

complete_errors = meter.create_counter(
    "gpwk.complete.errors",
    description="Failed complete operations",
    unit="1"
)


@tracer.start_as_current_span("gpwk_complete")
def complete_command(
    issue_number: int,
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    comment: Optional[str] = None,
    config: GPWKConfig = None
) -> CompleteResult:
    """
    Mark a task as complete with full instrumentation.

    This function:
    1. Validates the issue exists
    2. Parses and normalizes time range (if provided)
    3. Closes the GitHub issue with completion comment
    4. Updates project status to "done"
    5. Updates the daily log Activity Stream
    6. Records metrics

    All operations are instrumented with OpenTelemetry for observability.

    Args:
        issue_number: GitHub issue number to complete
        time_from: Start time (optional, e.g., "10:30 PM", "22:30")
        time_to: End time (optional, e.g., "11:00 PM", "23:00")
        comment: Additional completion comment (optional)
        config: GPWK configuration

    Returns:
        CompleteResult with success status and completion details

    Raises:
        Exception: If critical operation fails
    """
    start_time = time.time()
    span = trace.get_current_span()

    # Add input to span
    span.set_attribute("complete.issue_number", issue_number)
    span.set_attribute("complete.has_time_range", bool(time_from and time_to))
    span.set_attribute("complete.has_comment", bool(comment))

    logger.info(
        "complete_started",
        issue_number=issue_number,
        has_time_range=bool(time_from and time_to),
        has_comment=bool(comment)
    )

    time_range = None
    log_updated = False
    project_updated = False

    try:
        github = GithubOperations(config)

        # Step 1: Validate issue exists
        with tracer.start_as_current_span("validate_issue") as validate_span:
            issue = github.get_issue(issue_number)

            validate_span.set_attribute("github.issue_title", issue.title)
            validate_span.set_attribute("github.issue_url", issue.url)
            span.set_attribute("github.issue_title", issue.title)

            logger.info(
                "issue_validated",
                issue_number=issue_number,
                title=issue.title,
                url=issue.url
            )

        # Step 2: Parse and normalize time range
        if time_from and time_to:
            with tracer.start_as_current_span("parse_time") as time_span:
                time_from_normalized = _normalize_time(time_from)
                time_to_normalized = _normalize_time(time_to)
                time_range = (time_from_normalized, time_to_normalized)

                time_span.set_attribute("time.from", time_from_normalized)
                time_span.set_attribute("time.to", time_to_normalized)
                span.set_attribute("time.from", time_from_normalized)
                span.set_attribute("time.to", time_to_normalized)

                logger.info(
                    "time_parsed",
                    time_from=time_from_normalized,
                    time_to=time_to_normalized
                )

        # Step 3: Build completion comment
        with tracer.start_as_current_span("build_comment") as comment_span:
            completion_comment = _build_completion_comment(
                time_range=time_range,
                custom_comment=comment
            )

            comment_span.set_attribute("comment.length", len(completion_comment))

            logger.info(
                "comment_built",
                comment_length=len(completion_comment)
            )

        # Step 4: Close issue with comment
        with tracer.start_as_current_span("close_issue") as close_span:
            github.close_issue(
                issue_number=issue_number,
                comment=completion_comment
            )

            close_span.set_attribute("github.closed", True)
            span.set_attribute("github.closed", True)

            logger.info(
                "issue_closed",
                issue_number=issue_number
            )

        # Step 5: Update project status to "done"
        with tracer.start_as_current_span("update_project") as project_span:
            # Get project item for this issue
            project_items = github.get_project_items()
            project_item = None

            for item in project_items:
                if item.get("content", {}).get("number") == issue_number:
                    project_item = item
                    break

            if project_item:
                github.set_project_fields(
                    item_id=project_item["id"],
                    status="done"
                )

                project_span.set_attribute("project.item_id", project_item["id"])
                project_span.set_attribute("project.status", "done")
                span.set_attribute("project.updated", True)

                project_updated = True

                logger.info(
                    "project_updated",
                    item_id=project_item["id"],
                    status="done"
                )
            else:
                logger.warning(
                    "project_item_not_found",
                    issue_number=issue_number,
                    message="Issue not in project, skipping status update"
                )

        # Step 6: Update daily log
        with tracer.start_as_current_span("update_log") as log_span:
            log_entry = _create_log_entry(
                issue_number=issue_number,
                title=issue.title,
                time_range=time_range
            )

            _append_to_daily_log(
                config=config,
                entry=log_entry
            )

            log_span.set_attribute("log.date", str(datetime.now().date()))
            log_span.set_attribute("log.entry_length", len(log_entry))

            log_updated = True

            logger.info("daily_log_updated")

        # Success!
        duration_ms = (time.time() - start_time) * 1000

        complete_counter.add(1, {
            "status": "success",
            "has_time_range": str(bool(time_range))
        })
        complete_duration.record(duration_ms, {"status": "success"})

        span.set_status(Status(StatusCode.OK))
        span.set_attribute("complete.duration_ms", duration_ms)
        span.set_attribute("complete.success", True)
        span.set_attribute("complete.log_updated", log_updated)
        span.set_attribute("complete.project_updated", project_updated)

        logger.info(
            "complete_completed",
            issue_number=issue_number,
            duration_ms=duration_ms,
            success=True,
            log_updated=log_updated,
            project_updated=project_updated
        )

        return CompleteResult(
            success=True,
            issue_number=issue_number,
            duration_ms=duration_ms,
            time_range=time_range,
            log_updated=log_updated,
            project_updated=project_updated
        )

    except Exception as e:
        # Record error
        duration_ms = (time.time() - start_time) * 1000

        complete_errors.add(1, {
            "error_type": type(e).__name__
        })
        complete_duration.record(duration_ms, {"status": "error"})

        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.set_attribute("complete.success", False)
        span.set_attribute("complete.error_type", type(e).__name__)

        logger.error(
            "complete_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=duration_ms,
            exc_info=True
        )

        return CompleteResult(
            success=False,
            issue_number=issue_number,
            duration_ms=duration_ms,
            error=str(e),
            log_updated=log_updated,
            project_updated=project_updated
        )


def _normalize_time(time_str: str) -> str:
    """
    Normalize time to 24-hour format (HH:MM).

    Supports:
    - "10:30 PM" -> "22:30"
    - "10:30 AM" -> "10:30"
    - "22:30" -> "22:30"
    - "2:15 PM" -> "14:15"

    Args:
        time_str: Time string in various formats

    Returns:
        Normalized time string in HH:MM format

    Raises:
        ValueError: If time format is invalid
    """
    time_str = time_str.strip()

    # Pattern: "HH:MM AM/PM"
    match = re.match(r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?", time_str, re.IGNORECASE)

    if not match:
        raise ValueError(f"Invalid time format: '{time_str}'. Use 'HH:MM' or 'HH:MM AM/PM'")

    hour_str, minute_str, period = match.groups()
    hour = int(hour_str)
    minute = int(minute_str)

    # Validate minute
    if minute >= 60:
        raise ValueError(f"Invalid minute value: {minute}")

    # Convert to 24-hour format if period is specified
    if period:
        period = period.upper()
        if period == "PM" and hour != 12:
            hour += 12
        elif period == "AM" and hour == 12:
            hour = 0

    # Validate hour
    if hour >= 24:
        raise ValueError(f"Invalid hour value: {hour}")

    return f"{hour:02d}:{minute:02d}"


def _build_completion_comment(
    time_range: Optional[Tuple[str, str]],
    custom_comment: Optional[str]
) -> str:
    """Build completion comment for GitHub issue."""
    now = datetime.now()
    parts = ["✅ Completed"]

    if time_range:
        parts.append(f"\n\n**Time**: {time_range[0]} - {time_range[1]}")

    parts.append(f"\n**Date**: {now.strftime('%Y-%m-%d')}")

    if custom_comment:
        parts.append(f"\n\n{custom_comment}")

    return "".join(parts)


def _create_log_entry(
    issue_number: int,
    title: str,
    time_range: Optional[Tuple[str, str]]
) -> str:
    """Create a log entry for the daily log."""
    if time_range:
        time_str = f"{time_range[0]}-{time_range[1]}"
    else:
        time_str = datetime.now().strftime("%H:%M")

    entry = f"- {time_str} - Completed #{issue_number}: {title} ✓\n"
    entry += f"  - {title}\n"
    entry += f"  - Task completed\n"

    return entry


def _append_to_daily_log(config: GPWKConfig, entry: str) -> None:
    """Append entry to today's daily log."""
    today = datetime.now().date()
    log_file = Path(config.logs_dir) / f"{today}.md"

    if not log_file.exists():
        logger.warning(
            "daily_log_not_found",
            log_file=str(log_file),
            message="Run /gpwk.plan first to create today's log"
        )
        # Don't fail, just log warning
        return

    content = log_file.read_text()

    # Find the Activity Stream section
    activity_section = "## Activity Stream"

    if activity_section in content:
        # Insert after the Activity Stream header
        insert_pos = content.find(activity_section)
        # Skip to end of section line
        insert_pos = content.find("\n", insert_pos) + 1
        # Skip comment line if present
        if "<!--" in content[insert_pos:insert_pos + 100]:
            insert_pos = content.find("\n", insert_pos) + 1

        # Insert the entry
        new_content = (
            content[:insert_pos] +
            entry +
            content[insert_pos:]
        )

        log_file.write_text(new_content)

        logger.info(
            "log_entry_appended",
            log_file=str(log_file),
            entry_length=len(entry)
        )
    else:
        logger.warning(
            "activity_stream_section_not_found",
            log_file=str(log_file)
        )
