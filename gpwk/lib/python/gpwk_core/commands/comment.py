"""GPWK Comment command - Add comments to GitHub issues with telemetry."""

import time
import requests
from typing import List, Optional
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import CommentResult
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Operational Metrics
comment_operations = meter.create_counter(
    "gpwk.comment.operations.total",
    description="Total comment operations",
    unit="1"
)

comment_duration = meter.create_histogram(
    "gpwk.comment.duration",
    description="Comment operation duration",
    unit="ms"
)

comment_errors = meter.create_counter(
    "gpwk.comment.errors",
    description="Failed comment operations",
    unit="1"
)

comment_body_length = meter.create_histogram(
    "gpwk.comment.body_length",
    description="Character count in comments",
    unit="1"
)


class CommentCommand:
    """Comment command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize comment command."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

    @tracer.start_as_current_span("comment")
    def comment(
        self,
        issue_number: int,
        body: str,
        close: bool = False,
        labels: Optional[List[str]] = None
    ) -> CommentResult:
        """
        Add a comment to a GitHub issue.

        Args:
            issue_number: Issue number to comment on
            body: Comment body text
            close: Whether to close the issue after commenting
            labels: Optional labels to add to the issue

        Returns:
            CommentResult with success status and details
        """
        start_time = time.time()
        span = trace.get_current_span()

        span.set_attribute("comment.issue_number", issue_number)
        span.set_attribute("comment.body_length", len(body))
        span.set_attribute("comment.has_close_flag", close)
        span.set_attribute("comment.has_labels", bool(labels))
        span.set_attribute("comment.labels_count", len(labels) if labels else 0)

        logger.info(
            "comment_started",
            issue_number=issue_number,
            body_length=len(body),
            close=close,
            labels=labels
        )

        try:
            # Add comment to issue
            comment_data = self._add_comment(issue_number, body)
            comment_id = comment_data.get("id")
            comment_url = comment_data.get("html_url")

            logger.info(
                "comment_added",
                issue_number=issue_number,
                comment_id=comment_id,
                comment_url=comment_url
            )

            # Add labels if provided
            labels_added = []
            if labels:
                for label in labels:
                    with tracer.start_as_current_span("add_label") as label_span:
                        label_span.set_attribute("label", label)
                        self._add_label(issue_number, label)
                        labels_added.append(label)

                logger.info(
                    "labels_added",
                    issue_number=issue_number,
                    labels=labels_added
                )

            # Close issue if flag set
            closed = False
            if close:
                with tracer.start_as_current_span("close_issue"):
                    self._close_issue(issue_number)
                    closed = True

                logger.info(
                    "issue_closed",
                    issue_number=issue_number
                )

            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            comment_operations.add(1, {
                "status": "success",
                "has_close": str(close),
                "has_labels": str(bool(labels))
            })
            comment_duration.record(duration_ms, {"status": "success"})
            comment_body_length.record(len(body))

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("comment.duration_ms", duration_ms)
            span.set_attribute("comment.success", True)

            logger.info(
                "comment_completed",
                issue_number=issue_number,
                duration_ms=duration_ms,
                success=True
            )

            return CommentResult(
                success=True,
                comment_id=str(comment_id),
                comment_url=comment_url,
                issue_number=issue_number,
                closed=closed,
                labels_added=labels_added if labels_added else None,
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            comment_errors.add(1, {"error_type": type(e).__name__})
            comment_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "comment_failed",
                issue_number=issue_number,
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                exc_info=True
            )

            return CommentResult(
                success=False,
                issue_number=issue_number,
                error=str(e),
                duration_ms=duration_ms
            )

    def _add_comment(self, issue_number: int, body: str) -> dict:
        """
        Add a comment to an issue.

        Args:
            issue_number: Issue number
            body: Comment body text

        Returns:
            Comment data from GitHub API
        """
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}/comments"
        payload = {"body": body}

        start_time = time.time()

        with tracer.start_as_current_span("github_api.add_comment") as span:
            span.set_attribute("github.operation", "add_comment")
            span.set_attribute("github.issue_number", issue_number)

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            duration_ms = (time.time() - start_time) * 1000

            data = response.json()

            span.set_attribute("github.comment_id", data.get("id"))
            span.set_attribute("github.api_latency_ms", duration_ms)
            span.set_status(Status(StatusCode.OK))

            return data

    def _add_label(self, issue_number: int, label: str) -> None:
        """
        Add a label to an issue.

        Args:
            issue_number: Issue number
            label: Label name
        """
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}/labels"
        payload = {"labels": [label]}

        with tracer.start_as_current_span("github_api.add_label") as span:
            span.set_attribute("github.operation", "add_label")
            span.set_attribute("github.issue_number", issue_number)
            span.set_attribute("github.label", label)

            response = self.session.post(url, json=payload)
            response.raise_for_status()

            span.set_status(Status(StatusCode.OK))

    def _close_issue(self, issue_number: int) -> None:
        """
        Close an issue.

        Args:
            issue_number: Issue number
        """
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}"
        payload = {"state": "closed"}

        with tracer.start_as_current_span("github_api.close_issue") as span:
            span.set_attribute("github.operation", "close_issue")
            span.set_attribute("github.issue_number", issue_number)

            response = self.session.patch(url, json=payload)
            response.raise_for_status()

            span.set_status(Status(StatusCode.OK))
