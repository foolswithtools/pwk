"""GPWK Triage command - Move issues between project columns with telemetry."""

import time
import subprocess
import json
from typing import List, Dict, Optional, Tuple
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import TriageResult, ProjectItem
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Operational Metrics (how triage performs)
triage_operations = meter.create_counter(
    "gpwk.triage.operations.total",
    description="Total triage operations",
    unit="1"
)

triage_duration = meter.create_histogram(
    "gpwk.triage.duration",
    description="Triage operation duration",
    unit="ms"
)

items_moved = meter.create_counter(
    "gpwk.triage.items_moved.total",
    description="Number of items moved between columns",
    unit="1"
)

triage_errors = meter.create_counter(
    "gpwk.triage.errors",
    description="Failed triage operations",
    unit="1"
)

state_mismatches = meter.create_counter(
    "gpwk.triage.state_mismatches.total",
    description="Closed issues found in project columns (state mismatches)",
    unit="1"
)


class TriageCommand:
    """Triage command with telemetry."""

    # Status field option names (from GitHub config)
    # These should match what's in the parsed config
    STATUS_INBOX = "inbox"
    STATUS_INPROGRESS = "progress"
    STATUS_DONE = "done"

    def __init__(self, config: GPWKConfig):
        """Initialize triage command."""
        self.config = config

    @tracer.start_as_current_span("triage")
    def triage(
        self,
        issue_number: Optional[int] = None,
        target_status: Optional[str] = None,
        auto: bool = False
    ) -> TriageResult:
        """
        Triage issues in the project.

        Args:
            issue_number: Specific issue to move
            target_status: Target column (today/week/backlog)
            auto: Auto-triage all inbox items

        Returns:
            TriageResult with success status and details
        """
        start_time = time.time()
        span = trace.get_current_span()

        span.set_attribute("triage.issue_number", issue_number or "all")
        span.set_attribute("triage.target_status", target_status or "auto")
        span.set_attribute("triage.auto", auto)

        logger.info(
            "triage_started",
            issue_number=issue_number,
            target_status=target_status,
            auto=auto
        )

        try:
            if issue_number and target_status:
                # Move specific issue
                result = self._move_issue(issue_number, target_status)
            elif auto:
                # Auto-triage all inbox items
                result = self._auto_triage()
            else:
                # Show inbox for manual triage
                result = self._show_inbox()

            duration_ms = (time.time() - start_time) * 1000

            triage_operations.add(1, {"status": "success", "mode": "auto" if auto else "manual"})
            triage_duration.record(duration_ms, {"status": "success"})

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("triage.duration_ms", duration_ms)

            logger.info(
                "triage_completed",
                duration_ms=duration_ms,
                success=True
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            triage_errors.add(1, {"error_type": type(e).__name__})
            triage_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "triage_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                exc_info=True
            )

            return TriageResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    @tracer.start_as_current_span("move_issue")
    def _move_issue(self, issue_number: int, target_status: str) -> TriageResult:
        """Move a specific issue to a target status."""
        start_time = time.time()
        span = trace.get_current_span()
        span.set_attribute("issue_number", issue_number)
        span.set_attribute("target_status", target_status)

        logger.info("moving_issue", issue_number=issue_number, target_status=target_status)

        # Check issue state before moving (detect state mismatches)
        issue_details = self._get_issue_details(issue_number)
        if issue_details:
            issue_state = issue_details.get("state", "UNKNOWN")
            span.set_attribute("issue_state", issue_state)

            # Detect state mismatch: closed issue still in project
            if issue_state == "CLOSED":
                state_mismatches.add(1, {
                    "issue_number": str(issue_number),
                    "target_status": target_status
                })
                logger.warning(
                    "state_mismatch_detected",
                    issue_number=issue_number,
                    github_state="CLOSED",
                    project_action="moving",
                    target_status=target_status,
                    message="Closed issue found in project - this indicates stale project data"
                )

        # Get project item ID for this issue
        item_id = self._get_item_id_for_issue(issue_number)
        if not item_id:
            raise ValueError(f"Issue #{issue_number} not found in project")

        # Normalize user input to canonical status key
        from ..status_utils import normalize_status_input, is_backward_move, normalize_github_status

        canonical_status = normalize_status_input(target_status)
        if not canonical_status:
            valid_statuses = ', '.join(sorted(self.config.status_options.keys()))
            raise ValueError(
                f"Unknown target status: '{target_status}'. "
                f"Valid options: {valid_statuses}"
            )

        # Check if this is a backward move (e.g., Done → Today)
        current_item = self._get_item_by_id(item_id)
        if current_item and current_item.get("status"):
            current_status = current_item.get("status")
            current_canonical = normalize_github_status(current_status)

            if is_backward_move(current_status, target_status):
                logger.warning(
                    "backward_move_attempted",
                    issue_number=issue_number,
                    from_status=current_status,
                    to_status=target_status,
                    message="Moving task backwards in workflow - this may affect metrics"
                )

            # Special warning for moving Done tasks
            if current_canonical == "done" and canonical_status != "done":
                logger.warning(
                    "moving_completed_task",
                    issue_number=issue_number,
                    from_status="Done",
                    to_status=target_status,
                    message="Reopening a completed task - consider creating a new task instead"
                )

        # Get option ID from config using canonical status key
        option_id = self.config.status_options.get(canonical_status)
        if not option_id:
            raise ValueError(f"Status option not found in config: {canonical_status}")

        # Update status field
        subprocess.run(
            [
                "gh", "project", "item-edit",
                "--project-id", self.config.github_project_id,
                "--id", item_id,
                "--field-id", self.config.status_field_id,
                "--single-select-option-id", option_id
            ],
            capture_output=True,
            text=True,
            check=True
        )

        duration_ms = (time.time() - start_time) * 1000

        items_moved.add(1, {
            "from": "inbox",
            "to": target_status
        })

        span.set_status(Status(StatusCode.OK))
        logger.info("issue_moved", issue_number=issue_number, target=target_status, duration_ms=duration_ms)

        return TriageResult(
            success=True,
            items_moved=1,
            target_status=target_status,
            message=f"Moved #{issue_number} to {target_status}",
            duration_ms=duration_ms
        )

    @tracer.start_as_current_span("show_inbox")
    def _show_inbox(self) -> TriageResult:
        """Show inbox items for manual triage."""
        # Get all inbox items
        inbox_items = self._get_inbox_items()

        logger.info("inbox_fetched", count=len(inbox_items))

        return TriageResult(
            success=True,
            inbox_items=inbox_items,
            message=f"Inbox has {len(inbox_items)} items"
        )

    @tracer.start_as_current_span("auto_triage")
    def _auto_triage(self) -> TriageResult:
        """Auto-triage inbox items based on rules."""
        inbox_items = self._get_inbox_items()

        moved_count = 0

        for item in inbox_items:
            # Auto-triage logic
            target = self._suggest_target(item)
            if target:
                try:
                    issue_number = item.get("content", {}).get("number")
                    self._move_issue(issue_number, target)
                    moved_count += 1
                except Exception as e:
                    logger.warning(
                        "auto_triage_item_failed",
                        item=item.get("id"),
                        error=str(e)
                    )

        return TriageResult(
            success=True,
            items_moved=moved_count,
            message=f"Auto-triaged {moved_count} items"
        )

    def _get_inbox_items(self) -> List[Dict]:
        """Get all items in inbox status."""
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

        # Filter for Inbox status and detect state mismatches
        from ..status_utils import compare_status

        inbox = []
        for item in items:
            if item.get("status") is None or compare_status(item.get("status"), "inbox"):
                # Check for state mismatches: closed issues in inbox
                content = item.get("content", {})
                if content.get("type") == "Issue":
                    issue_state = content.get("state", "UNKNOWN")
                    issue_number = content.get("number")

                    if issue_state == "CLOSED":
                        state_mismatches.add(1, {
                            "issue_number": str(issue_number),
                            "location": "inbox"
                        })
                        logger.warning(
                            "state_mismatch_in_inbox",
                            issue_number=issue_number,
                            github_state="CLOSED",
                            project_status=item.get("status"),
                            message="Closed issue found in inbox - should be in Done or removed"
                        )

                inbox.append(item)

        return inbox

    def _get_item_id_for_issue(self, issue_number: int) -> Optional[str]:
        """Get project item ID for a given issue number."""
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

        for item in items:
            if item.get("content", {}).get("number") == issue_number:
                return item.get("id")

        return None

    def _get_item_by_id(self, item_id: str) -> Optional[Dict]:
        """Get project item details by item ID."""
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

        for item in items:
            if item.get("id") == item_id:
                return item

        return None

    def _suggest_target(self, item: Dict) -> Optional[str]:
        """Suggest target column for an item based on labels/priority."""
        labels = [label.get("name", "") for label in item.get("labels", [])]

        # High priority → today
        if "priority:high" in labels:
            return "today"

        # AI tasks → today (background work)
        if "pwk:ai" in labels:
            return "today"

        # Quick wins → today
        if "energy:quick" in labels:
            return "today"

        # Deep work → week
        if "energy:deep" in labels:
            return "week"

        # Default → backlog
        return "backlog"

    @tracer.start_as_current_span("review_and_close")
    def review_and_close_issues(
        self,
        issue_numbers: List[int],
        reason: str = "Test completed"
    ) -> TriageResult:
        """
        Review and close multiple issues (e.g., test issues).

        Args:
            issue_numbers: List of issue numbers to review and close
            reason: Reason for closing

        Returns:
            TriageResult with closure details
        """
        start_time = time.time()
        span = trace.get_current_span()
        span.set_attribute("review.issue_count", len(issue_numbers))
        span.set_attribute("review.reason", reason)

        logger.info(
            "review_and_close_started",
            issue_count=len(issue_numbers),
            reason=reason
        )

        closed_issues = []
        failed_issues = []

        for issue_number in issue_numbers:
            try:
                # Get issue details first
                issue_data = self._get_issue_details(issue_number)

                if not issue_data:
                    logger.warning(
                        "issue_not_found",
                        issue_number=issue_number
                    )
                    failed_issues.append((issue_number, "Not found"))
                    continue

                # Determine closure comment based on issue type
                title = issue_data.get("title", "")
                labels = [label.get("name", "") for label in issue_data.get("labels", [])]

                # Build closure comment
                comment = self._build_closure_comment(title, labels, reason)

                # Close the issue with comment
                self._close_issue_with_comment(issue_number, comment)

                closed_issues.append({
                    "number": issue_number,
                    "title": title
                })

                logger.info(
                    "issue_closed",
                    issue_number=issue_number,
                    title=title
                )

            except Exception as e:
                logger.error(
                    "close_issue_failed",
                    issue_number=issue_number,
                    error=str(e),
                    exc_info=True
                )
                failed_issues.append((issue_number, str(e)))

        duration_ms = (time.time() - start_time) * 1000

        # Record metrics
        items_moved.add(len(closed_issues), {
            "from": "open",
            "to": "closed"
        })

        span.set_attribute("review.closed_count", len(closed_issues))
        span.set_attribute("review.failed_count", len(failed_issues))
        span.set_status(Status(StatusCode.OK))

        logger.info(
            "review_and_close_completed",
            closed=len(closed_issues),
            failed=len(failed_issues),
            duration_ms=duration_ms
        )

        return TriageResult(
            success=True,
            items_moved=len(closed_issues),
            closed_issues=closed_issues,
            failed_issues=failed_issues,
            message=f"Closed {len(closed_issues)} issues",
            duration_ms=duration_ms
        )

    def _get_issue_details(self, issue_number: int) -> Optional[Dict]:
        """Get issue details from GitHub."""
        try:
            result = subprocess.run(
                [
                    "gh", "issue", "view",
                    str(issue_number),
                    "--repo", self.config.github_repo,
                    "--json", "number,title,body,labels,state,createdAt"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError:
            return None

    def _build_closure_comment(
        self,
        title: str,
        labels: List[str],
        reason: str
    ) -> str:
        """Build appropriate closure comment based on issue type."""
        is_test = any(
            keyword in title.lower()
            for keyword in ["test", "testing", "final test", "success"]
        )
        is_capture = "pwk:capture" in labels

        if is_test:
            # Test issue
            test_type = "telemetry test" if "telemetry" in title.lower() else "test"
            return (
                f"{reason}. {test_type.capitalize()} completed successfully. "
                f"Closing test capture.\n\n"
                f"🤖 Closed via GPWK Python triage with telemetry"
            )
        elif is_capture:
            # Regular capture
            return (
                f"{reason}. Activity/capture completed. "
                f"Closing issue.\n\n"
                f"🤖 Closed via GPWK Python triage with telemetry"
            )
        else:
            # Regular task
            return (
                f"{reason}.\n\n"
                f"🤖 Closed via GPWK Python triage with telemetry"
            )

    def _close_issue_with_comment(self, issue_number: int, comment: str) -> None:
        """Close issue with a comment."""
        # Post comment
        subprocess.run(
            [
                "gh", "issue", "comment",
                str(issue_number),
                "--repo", self.config.github_repo,
                "--body", comment
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Close issue
        subprocess.run(
            [
                "gh", "issue", "close",
                str(issue_number),
                "--repo", self.config.github_repo
            ],
            capture_output=True,
            text=True,
            check=True
        )

    @tracer.start_as_current_span("review_issues")
    def review_issues(
        self,
        issue_numbers: List[int]
    ) -> TriageResult:
        """
        Review issues and provide recommendations (keep vs close).

        Args:
            issue_numbers: List of issue numbers to review

        Returns:
            TriageResult with recommendations
        """
        start_time = time.time()
        span = trace.get_current_span()
        span.set_attribute("review.issue_count", len(issue_numbers))

        logger.info(
            "review_issues_started",
            issue_count=len(issue_numbers)
        )

        recommendations = []

        for issue_number in issue_numbers:
            try:
                # Get issue details
                issue_data = self._get_issue_details(issue_number)

                if not issue_data:
                    recommendations.append({
                        "number": issue_number,
                        "status": "not_found",
                        "recommendation": "Issue not found",
                        "action": "skip"
                    })
                    continue

                # Analyze issue
                title = issue_data.get("title", "")
                labels = [label.get("name", "") for label in issue_data.get("labels", [])]
                body = issue_data.get("body", "")
                state = issue_data.get("state", "OPEN")
                created_at = issue_data.get("createdAt", "")

                # Determine if test issue
                is_test = self._is_test_issue(title, labels, body)
                is_capture = "pwk:capture" in labels
                is_real_task = "pwk:task" in labels or "pwk:personal" in labels

                # Make recommendation
                if state == "CLOSED":
                    recommendation = "Already closed"
                    action = "skip"
                elif is_test:
                    recommendation = "Test issue - safe to close"
                    action = "close"
                    reason = "Test completed"
                elif is_capture and not is_real_task:
                    recommendation = "Capture needing triage - review body"
                    action = "review"
                    reason = "Needs classification"
                elif is_real_task:
                    recommendation = "Real task - keep open"
                    action = "keep"
                    reason = "Active task"
                else:
                    recommendation = "Unclear - manual review needed"
                    action = "review"
                    reason = "Unable to classify"

                recommendations.append({
                    "number": issue_number,
                    "title": title,
                    "status": state,
                    "labels": labels,
                    "is_test": is_test,
                    "is_capture": is_capture,
                    "is_real_task": is_real_task,
                    "recommendation": recommendation,
                    "action": action
                })

                logger.info(
                    "issue_reviewed",
                    issue_number=issue_number,
                    action=action,
                    is_test=is_test
                )

            except Exception as e:
                logger.error(
                    "review_issue_failed",
                    issue_number=issue_number,
                    error=str(e),
                    exc_info=True
                )
                recommendations.append({
                    "number": issue_number,
                    "status": "error",
                    "recommendation": f"Error: {str(e)}",
                    "action": "skip"
                })

        duration_ms = (time.time() - start_time) * 1000

        span.set_attribute("review.reviewed_count", len(recommendations))
        span.set_status(Status(StatusCode.OK))

        logger.info(
            "review_issues_completed",
            reviewed=len(recommendations),
            duration_ms=duration_ms
        )

        return TriageResult(
            success=True,
            message=f"Reviewed {len(recommendations)} issues",
            recommendations=recommendations,
            duration_ms=duration_ms
        )

    def _is_test_issue(self, title: str, labels: List[str], body: str) -> bool:
        """Determine if an issue is a test issue."""
        test_keywords = [
            "test", "testing", "final test", "success",
            "otlp", "telemetry", "grafana", "alloy",
            "tls configuration", "cumulative temporality"
        ]

        title_lower = title.lower()
        body_lower = body.lower() if body else ""

        # Check title
        title_has_test = any(keyword in title_lower for keyword in test_keywords)

        # Check if it's a capture with test language
        is_capture = "pwk:capture" in labels
        body_has_test = any(keyword in body_lower for keyword in test_keywords)

        return title_has_test or (is_capture and body_has_test)
