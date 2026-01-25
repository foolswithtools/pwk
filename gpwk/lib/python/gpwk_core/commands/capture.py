"""GPWK Capture command - fully instrumented with OpenTelemetry."""

import time
from datetime import datetime
from pathlib import Path
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import CaptureResult
from ..parser import GPWKParser
from ..github_ops import GithubOperations
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
capture_counter = meter.create_counter(
    "gpwk.capture.total",
    description="Total capture operations",
    unit="1"
)

capture_duration = meter.create_histogram(
    "gpwk.capture.duration",
    description="Capture operation duration",
    unit="ms"
)

capture_errors = meter.create_counter(
    "gpwk.capture.errors",
    description="Failed capture operations",
    unit="1"
)

# Note: Productivity metrics (issues created, tasks completed, work time)
# are collected by the metrics_collector daemon by querying GitHub/logs
# for actual state. This ensures accuracy and catches external changes.


@tracer.start_as_current_span("gpwk_capture")
def capture_command(text: str, config: GPWKConfig) -> CaptureResult:
    """
    Capture an activity or task to GitHub with full instrumentation.

    This function:
    1. Parses the input text for GPWK notation
    2. Detects if it's a completed activity
    3. Creates a GitHub issue (handles special characters properly)
    4. Adds to project with retry logic (fixes timing issues)
    5. Sets all metadata fields
    6. Updates the daily log file
    7. Closes issue if completed

    All operations are instrumented with OpenTelemetry for observability.

    Args:
        text: Raw capture text (e.g., "I took the dog for a walk 9-10 AM")
        config: GPWK configuration

    Returns:
        CaptureResult with success status and issue details

    Raises:
        Exception: If critical operation fails
    """
    start_time = time.time()
    span = trace.get_current_span()

    # Add input to span
    span.set_attribute("capture.input_text", text)
    span.set_attribute("capture.input_length", len(text))

    logger.info("capture_started", input_length=len(text))

    parsed = None  # Initialize for error handling

    try:
        # Step 1: Parse input
        with tracer.start_as_current_span("parse") as parse_span:
            parser = GPWKParser()
            parsed = parser.parse_capture_notation(text)

            # Add attributes
            parse_span.set_attribute("capture.type", parsed.type)
            parse_span.set_attribute("capture.is_completed", parsed.is_completed)
            parse_span.set_attribute("capture.priority", parsed.priority or "none")
            parse_span.set_attribute("capture.energy", parsed.energy or "none")
            parse_span.set_attribute("capture.title", parsed.title)

            # Add to parent span
            span.set_attribute("capture.type", parsed.type)
            span.set_attribute("capture.is_completed", parsed.is_completed)

            logger.info(
                "parsed_capture",
                type=parsed.type,
                completed=parsed.is_completed,
                title=parsed.title,
                labels=parsed.labels
            )

        # Step 2: Create GitHub issue
        with tracer.start_as_current_span("create_issue") as issue_span:
            github = GithubOperations(config)
            issue = github.create_issue(
                title=parsed.title,
                labels=parsed.labels,
                body=parsed.body
            )

            issue_span.set_attribute("github.issue_number", issue.number)
            issue_span.set_attribute("github.issue_url", issue.url)

            # Add to parent span
            span.set_attribute("github.issue_number", issue.number)
            span.set_attribute("github.issue_url", issue.url)

            logger.info(
                "issue_created",
                issue_number=issue.number,
                issue_url=issue.url
            )

        # Step 3: Add to project (with retry logic)
        with tracer.start_as_current_span("add_to_project") as project_span:
            project_item = github.add_to_project_with_retry(
                issue_url=issue.url,
                max_retries=5
            )

            project_span.set_attribute("github.project_item_id", project_item.id)
            project_span.set_attribute("github.retry_count", project_item.retry_count)

            # Add to parent span
            span.set_attribute("github.project_item_id", project_item.id)
            span.set_attribute("github.retry_count", project_item.retry_count)

            if project_item.retry_count > 0:
                project_span.add_event(
                    f"Required {project_item.retry_count} retries to get project item"
                )
                span.add_event(
                    f"Project add required {project_item.retry_count} retries"
                )
                logger.warning(
                    "project_add_required_retries",
                    retries=project_item.retry_count
                )

        # Step 4: Set project fields
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
            fields_span.add_event(f"Set {len(parsed.project_fields) + 1} fields")

            logger.info(
                "project_fields_set",
                status=status,
                fields=list(parsed.project_fields.keys())
            )

        # Step 5: Close issue if completed
        if parsed.is_completed:
            with tracer.start_as_current_span("close_issue") as close_span:
                github.close_issue(
                    issue_number=issue.number,
                    comment="Activity completed. Closing as done."
                )

                close_span.set_attribute("github.closed", True)
                span.set_attribute("github.closed", True)

                logger.info(
                    "issue_closed",
                    issue_number=issue.number
                )

        # Step 6: Update daily log
        with tracer.start_as_current_span("update_log") as log_span:
            log_entry = _create_log_entry(
                issue_number=issue.number,
                title=parsed.title,
                time_range=parsed.time_range,
                is_completed=parsed.is_completed,
                labels=parsed.labels
            )

            _append_to_daily_log(
                config=config,
                entry=log_entry,
                is_completed=parsed.is_completed
            )

            log_span.set_attribute("log.date", str(datetime.now().date()))
            log_span.set_attribute("log.entry_length", len(log_entry))

            logger.info("daily_log_updated")

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
        span.set_attribute("capture.success", True)

        logger.info(
            "capture_completed",
            issue_number=issue.number,
            duration_ms=duration_ms,
            success=True
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
            "type": parsed.type if parsed else "unknown"
        })
        capture_duration.record(duration_ms, {"status": "error"})

        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.set_attribute("capture.success", False)
        span.set_attribute("capture.error_type", type(e).__name__)

        logger.error(
            "capture_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=duration_ms,
            exc_info=True
        )

        return CaptureResult(
            success=False,
            error=str(e),
            duration_ms=duration_ms
        )


def _create_log_entry(
    issue_number: int,
    title: str,
    time_range: tuple,
    is_completed: bool,
    labels: list
) -> str:
    """Create a log entry for the daily log."""
    now = datetime.now()

    if time_range:
        time_str = f"{time_range[0]}-{time_range[1]}"
    else:
        time_str = now.strftime("%H:%M")

    # Extract energy tag
    energy_tag = ""
    for label in labels:
        if label.startswith("energy:"):
            energy_tag = f" ~{label.split(':')[1]}"
            break

    status_marker = "✓" if is_completed else ""

    entry = f"- {time_str} - {'Completed' if is_completed else 'Captured'} #{issue_number}: {title} {status_marker}\n"

    if is_completed and time_range:
        entry += f"  - {title}\n"
        entry += f"  - {'Personal routine/self-care' if 'quick' in labels else 'Activity'}{energy_tag}\n"
    else:
        entry += f"  - Captured for triage{energy_tag}\n"

    return entry


def _append_to_daily_log(
    config: GPWKConfig,
    entry: str,
    is_completed: bool
) -> None:
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
        # Skip to end of comment line
        insert_pos = content.find("\n", insert_pos) + 1
        # Skip comment line
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
