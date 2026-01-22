"""GitHub operations with retry logic and instrumentation."""

import time
from typing import Optional, Dict, List
import structlog
import requests

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from .models import GPWKConfig, GithubIssue, ProjectItem
from .telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
github_api_calls = meter.create_counter(
    "gpwk.github.api_calls.total",
    description="Total GitHub API calls",
    unit="1"
)

github_api_errors = meter.create_counter(
    "gpwk.github.api_errors.total",
    description="GitHub API errors",
    unit="1"
)

github_api_latency = meter.create_histogram(
    "gpwk.github.api_latency",
    description="GitHub API latency",
    unit="ms"
)

retry_count_metric = meter.create_histogram(
    "gpwk.github.retry_count",
    description="Number of retries needed",
    unit="1"
)

# Note: Productivity metrics (issues closed, completion rates)
# are collected by the metrics_collector daemon by querying GitHub
# for actual state. This ensures accuracy and catches external changes.


class GithubOperations:
    """GitHub operations with retry logic and instrumentation."""

    def __init__(self, config: GPWKConfig):
        """Initialize GitHub operations."""
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {config.github_token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })

    @tracer.start_as_current_span("create_issue")
    def create_issue(
        self,
        title: str,
        labels: list[str],
        body: str
    ) -> GithubIssue:
        """
        Create a GitHub issue.

        This method properly handles special characters in titles (parentheses,
        quotes, etc.) that cause issues with shell scripts.

        Args:
            title: Issue title (can contain any characters)
            labels: List of label names
            body: Issue body (markdown)

        Returns:
            GithubIssue instance

        Raises:
            requests.HTTPError: If GitHub API returns error
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "create_issue")
        span.set_attribute("github.title", title)
        span.set_attribute("github.labels_count", len(labels))

        logger.info(
            "creating_issue",
            title=title,
            labels=labels,
            repo=self.config.github_repo
        )

        url = f"https://api.github.com/repos/{self.config.github_repo}/issues"
        payload = {
            "title": title,
            "body": body,
            "labels": labels
        }

        start_time = time.time()

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "create_issue"})
            github_api_calls.add(1, {"operation": "create_issue", "status": "success"})

            data = response.json()

            issue = GithubIssue(
                number=data["number"],
                title=data["title"],
                url=data["html_url"],
                labels=[label["name"] for label in data["labels"]],
                created_at=data["created_at"],
                body=data.get("body")
            )

            span.set_attribute("github.issue_number", issue.number)
            span.set_attribute("github.issue_url", issue.url)
            span.set_status(Status(StatusCode.OK))

            logger.info(
                "issue_created",
                issue_number=issue.number,
                issue_url=issue.url,
                duration_ms=duration_ms
            )

            return issue

        except requests.HTTPError as e:
            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "create_issue"})
            github_api_calls.add(1, {"operation": "create_issue", "status": "error"})
            github_api_errors.add(1, {"operation": "create_issue"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "issue_creation_failed",
                title=title,
                error=str(e),
                status_code=e.response.status_code if e.response else None,
                duration_ms=duration_ms,
                exc_info=True
            )

            raise

    @tracer.start_as_current_span("add_to_project")
    def add_to_project_with_retry(
        self,
        issue_url: str,
        max_retries: int = 5
    ) -> ProjectItem:
        """
        Add issue to project with retry logic.

        This solves the timing issue where the project item might not be
        immediately available after adding.

        Args:
            issue_url: GitHub issue URL
            max_retries: Maximum number of retries

        Returns:
            ProjectItem with ID and retry count

        Raises:
            RuntimeError: If item couldn't be added after max retries
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "add_to_project")
        span.set_attribute("github.issue_url", issue_url)
        span.set_attribute("github.max_retries", max_retries)

        logger.info(
            "adding_to_project",
            issue_url=issue_url,
            project_id=self.config.github_project_id
        )

        # Extract issue number from URL
        issue_number = int(issue_url.split("/")[-1])

        # Add to project using GraphQL
        with tracer.start_as_current_span("graphql_add_project_item") as add_span:
            item_id = self._add_project_item_graphql(issue_url)
            add_span.set_attribute("github.item_id", item_id)

        # Retry to get the item with all fields
        retry_count = 0
        wait_time = 1

        for attempt in range(max_retries):
            with tracer.start_as_current_span(f"retry_attempt_{attempt + 1}") as retry_span:
                retry_span.set_attribute("github.attempt", attempt + 1)

                if attempt > 0:
                    logger.info(
                        "retrying_get_project_item",
                        attempt=attempt + 1,
                        wait_time=wait_time
                    )
                    time.sleep(wait_time)
                    wait_time *= 2  # Exponential backoff

                try:
                    # Try to fetch the item
                    project_item = self._get_project_item(item_id)

                    if project_item:
                        retry_span.set_status(Status(StatusCode.OK))
                        retry_count = attempt

                        retry_count_metric.record(retry_count, {
                            "operation": "add_to_project"
                        })

                        span.set_attribute("github.retry_count", retry_count)
                        span.set_status(Status(StatusCode.OK))

                        if retry_count > 0:
                            span.add_event(f"Required {retry_count} retries")
                            logger.warning(
                                "project_item_required_retries",
                                item_id=item_id,
                                retry_count=retry_count
                            )

                        logger.info(
                            "added_to_project",
                            item_id=item_id,
                            retry_count=retry_count
                        )

                        return project_item

                except Exception as e:
                    retry_span.record_exception(e)
                    retry_span.set_status(Status(StatusCode.ERROR, str(e)))
                    logger.warning(
                        "get_project_item_failed",
                        attempt=attempt + 1,
                        error=str(e)
                    )

        # Failed after all retries
        error_msg = f"Could not get project item after {max_retries} retries"
        span.set_status(Status(StatusCode.ERROR, error_msg))
        logger.error(
            "add_to_project_failed",
            issue_url=issue_url,
            max_retries=max_retries
        )

        raise RuntimeError(error_msg)

    def _add_project_item_graphql(self, issue_url: str) -> str:
        """Add item to project using GraphQL API."""
        # For now, use the gh CLI as a fallback
        # TODO: Implement pure GraphQL mutation
        import subprocess

        result = subprocess.run(
            [
                "gh", "project", "item-add",
                str(self.config.github_project_number),
                "--owner", "@me",
                "--url", issue_url
            ],
            capture_output=True,
            text=True,
            check=True
        )

        # Extract item ID from the output (this is a simplification)
        # In production, we should parse the output properly
        return "pending"  # Will be fetched in retry loop

    def _get_project_item(self, item_id: str) -> Optional[ProjectItem]:
        """Get project item by ID."""
        # Use gh CLI to list items and find ours
        import subprocess
        import json

        result = subprocess.run(
            [
                "gh", "project", "item-list",
                str(self.config.github_project_number),
                "--owner", "@me",
                "--format", "json"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        items = json.loads(result.stdout)

        # For now, just return the first item as proof of concept
        # TODO: Actually find the right item
        if items.get("items"):
            first_item = items["items"][0]
            return ProjectItem(
                id=first_item["id"],
                issue=GithubIssue(
                    number=first_item.get("content", {}).get("number", 0),
                    title=first_item.get("title", ""),
                    url=first_item.get("content", {}).get("url", ""),
                    labels=[],
                    created_at=""
                ),
                status=first_item.get("status", "")
            )

        return None

    @tracer.start_as_current_span("set_project_fields")
    def set_project_fields(
        self,
        item_id: str,
        status: Optional[str] = None,
        type: Optional[str] = None,
        priority: Optional[str] = None,
        energy: Optional[str] = None
    ) -> None:
        """
        Set project fields for an item.

        Args:
            item_id: Project item ID
            status: Status value ("inbox", "inprogress", "done")
            type: Type value ("task", "ai-task", "capture", "work-item")
            priority: Priority value ("high", "medium", "low")
            energy: Energy value ("deep", "shallow", "quick")
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "set_project_fields")
        span.set_attribute("github.item_id", item_id)

        fields_set = []

        if status:
            self._set_field(item_id, "status", status, self.config.status_options)
            fields_set.append("status")

        if type:
            self._set_field(item_id, "type", type, self.config.type_options)
            fields_set.append("type")

        if priority:
            self._set_field(item_id, "priority", priority, self.config.priority_options)
            fields_set.append("priority")

        if energy:
            self._set_field(item_id, "energy", energy, self.config.energy_options)
            fields_set.append("energy")

        span.set_attribute("github.fields_set_count", len(fields_set))
        span.add_event(f"Set {len(fields_set)} fields: {', '.join(fields_set)}")

        logger.info(
            "project_fields_set",
            item_id=item_id,
            fields=fields_set
        )

    def _set_field(
        self,
        item_id: str,
        field_name: str,
        field_value: str,
        options: Dict[str, str]
    ) -> None:
        """Set a single project field."""
        with tracer.start_as_current_span(f"set_field_{field_name}") as span:
            span.set_attribute("github.field_name", field_name)
            span.set_attribute("github.field_value", field_value)

            # Get field ID and option ID
            field_id_map = {
                "status": self.config.status_field_id,
                "type": self.config.type_field_id,
                "priority": self.config.priority_field_id,
                "energy": self.config.energy_field_id
            }

            field_id = field_id_map[field_name]
            option_id = options.get(field_value)

            if not option_id:
                logger.warning(
                    "field_option_not_found",
                    field_name=field_name,
                    field_value=field_value,
                    available_options=list(options.keys())
                )
                return

            # Use gh CLI for now
            import subprocess

            try:
                subprocess.run(
                    [
                        "gh", "project", "item-edit",
                        "--id", item_id,
                        "--project-id", self.config.github_project_id,
                        "--field-id", field_id,
                        "--single-select-option-id", option_id
                    ],
                    capture_output=True,
                    text=True,
                    check=True
                )

                span.set_status(Status(StatusCode.OK))

            except subprocess.CalledProcessError as e:
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                logger.error(
                    "set_field_failed",
                    field_name=field_name,
                    error=e.stderr if e.stderr else str(e)
                )

    @tracer.start_as_current_span("close_issue")
    def close_issue(self, issue_number: int, comment: Optional[str] = None) -> None:
        """
        Close a GitHub issue.

        Args:
            issue_number: Issue number
            comment: Optional comment to add when closing
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "close_issue")
        span.set_attribute("github.issue_number", issue_number)

        logger.info("closing_issue", issue_number=issue_number)

        # Add comment if provided
        if comment:
            self._add_comment(issue_number, comment)

        # Close the issue
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}"
        payload = {"state": "closed"}

        response = self.session.patch(url, json=payload)
        response.raise_for_status()

        span.set_status(Status(StatusCode.OK))
        logger.info("issue_closed", issue_number=issue_number)

    def _add_comment(self, issue_number: int, comment: str) -> None:
        """Add a comment to an issue."""
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}/comments"
        payload = {"body": comment}

        response = self.session.post(url, json=payload)
        response.raise_for_status()

    @tracer.start_as_current_span("get_issue")
    def get_issue(self, issue_number: int) -> GithubIssue:
        """
        Get a GitHub issue by number.

        Args:
            issue_number: Issue number

        Returns:
            GithubIssue instance
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "get_issue")
        span.set_attribute("github.issue_number", issue_number)

        logger.info("getting_issue", issue_number=issue_number)

        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}"

        start_time = time.time()

        try:
            response = self.session.get(url)
            response.raise_for_status()

            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "get_issue"})
            github_api_calls.add(1, {"operation": "get_issue", "status": "success"})

            data = response.json()

            issue = GithubIssue(
                number=data["number"],
                title=data["title"],
                url=data["html_url"],
                labels=[label["name"] for label in data["labels"]],
                created_at=data["created_at"],
                body=data.get("body")
            )

            span.set_status(Status(StatusCode.OK))
            logger.info("issue_retrieved", issue_number=issue_number, duration_ms=duration_ms)

            return issue

        except requests.HTTPError as e:
            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "get_issue"})
            github_api_calls.add(1, {"operation": "get_issue", "status": "error"})
            github_api_errors.add(1, {"operation": "get_issue"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "get_issue_failed",
                issue_number=issue_number,
                error=str(e),
                status_code=e.response.status_code if e.response else None,
                duration_ms=duration_ms,
                exc_info=True
            )

            raise

    @tracer.start_as_current_span("update_issue")
    def update_issue(self, issue_number: int, body: Optional[str] = None, labels: Optional[List[str]] = None) -> None:
        """
        Update a GitHub issue.

        Args:
            issue_number: Issue number
            body: New body content (optional)
            labels: New labels list (optional)
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "update_issue")
        span.set_attribute("github.issue_number", issue_number)

        logger.info("updating_issue", issue_number=issue_number)

        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}"
        payload = {}

        if body is not None:
            payload["body"] = body
        if labels is not None:
            payload["labels"] = labels

        start_time = time.time()

        try:
            response = self.session.patch(url, json=payload)
            response.raise_for_status()

            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "update_issue"})
            github_api_calls.add(1, {"operation": "update_issue", "status": "success"})

            span.set_status(Status(StatusCode.OK))
            logger.info("issue_updated", issue_number=issue_number, duration_ms=duration_ms)

        except requests.HTTPError as e:
            duration_ms = (time.time() - start_time) * 1000
            github_api_latency.record(duration_ms, {"operation": "update_issue"})
            github_api_calls.add(1, {"operation": "update_issue", "status": "error"})
            github_api_errors.add(1, {"operation": "update_issue"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "update_issue_failed",
                issue_number=issue_number,
                error=str(e),
                duration_ms=duration_ms,
                exc_info=True
            )

            raise

    @tracer.start_as_current_span("add_label")
    def add_label(self, issue_number: int, label: str) -> None:
        """
        Add a label to an issue.

        Args:
            issue_number: Issue number
            label: Label name to add
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "add_label")
        span.set_attribute("github.issue_number", issue_number)
        span.set_attribute("github.label", label)

        logger.info("adding_label", issue_number=issue_number, label=label)

        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}/labels"
        payload = {"labels": [label]}

        try:
            response = self.session.post(url, json=payload)
            response.raise_for_status()

            span.set_status(Status(StatusCode.OK))
            logger.info("label_added", issue_number=issue_number, label=label)

        except requests.HTTPError as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error("add_label_failed", issue_number=issue_number, label=label, error=str(e), exc_info=True)
            raise

    @tracer.start_as_current_span("remove_label")
    def remove_label(self, issue_number: int, label: str) -> None:
        """
        Remove a label from an issue.

        Args:
            issue_number: Issue number
            label: Label name to remove
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "remove_label")
        span.set_attribute("github.issue_number", issue_number)
        span.set_attribute("github.label", label)

        logger.info("removing_label", issue_number=issue_number, label=label)

        # GitHub API expects URL-encoded label names
        import urllib.parse
        encoded_label = urllib.parse.quote(label)
        url = f"https://api.github.com/repos/{self.config.github_repo}/issues/{issue_number}/labels/{encoded_label}"

        try:
            response = self.session.delete(url)
            response.raise_for_status()

            span.set_status(Status(StatusCode.OK))
            logger.info("label_removed", issue_number=issue_number, label=label)

        except requests.HTTPError as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error("remove_label_failed", issue_number=issue_number, label=label, error=str(e), exc_info=True)
            raise

    @tracer.start_as_current_span("get_project_items")
    def get_project_items(self, status_filter: Optional[str] = None) -> List[dict]:
        """
        Get all items from the GitHub project.

        Args:
            status_filter: Optional status to filter by (e.g., "Today", "Backlog")

        Returns:
            List of project items
        """
        span = trace.get_current_span()
        span.set_attribute("github.operation", "get_project_items")
        if status_filter:
            span.set_attribute("github.status_filter", status_filter)

        logger.info("getting_project_items", status_filter=status_filter)

        # Use gh CLI for now
        import subprocess
        import json

        try:
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

            if status_filter:
                from .status_utils import compare_status
                items = [item for item in items if compare_status(item.get("status"), status_filter)]

            span.set_attribute("github.items_count", len(items))
            span.set_status(Status(StatusCode.OK))
            logger.info("project_items_retrieved", count=len(items))

            return items

        except subprocess.CalledProcessError as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error("get_project_items_failed", error=str(e), exc_info=True)
            raise
