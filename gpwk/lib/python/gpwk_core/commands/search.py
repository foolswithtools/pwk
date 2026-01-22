"""GPWK Search command - fully instrumented with OpenTelemetry."""

import time
import json
import subprocess
from typing import List
from datetime import datetime
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import SearchFilter, SearchResult, GithubIssue
from ..github_ops import GithubOperations
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
search_counter = meter.create_counter(
    "gpwk.search.total",
    description="Total search operations",
    unit="1"
)

search_duration = meter.create_histogram(
    "gpwk.search.duration",
    description="Search operation duration",
    unit="ms"
)

search_errors = meter.create_counter(
    "gpwk.search.errors",
    description="Failed search operations",
    unit="1"
)

search_results_count = meter.create_histogram(
    "gpwk.search.results_count",
    description="Number of search results returned",
    unit="1"
)


@tracer.start_as_current_span("gpwk_search")
def search_command(
    filter: SearchFilter,
    json_output: bool = False,
    config: GPWKConfig = None
) -> SearchResult:
    """
    Search for issues matching filter criteria with full instrumentation.

    This function:
    1. Builds label list from filter shortcuts
    2. Queries GitHub using gh CLI
    3. Filters by project status (if specified)
    4. Formats results (human-readable or JSON)
    5. Records metrics

    All operations are instrumented with OpenTelemetry for observability.

    Args:
        filter: SearchFilter with query criteria
        json_output: If True, format as JSON
        config: GPWK configuration

    Returns:
        SearchResult with matching issues and formatted output

    Raises:
        Exception: If critical operation fails
    """
    start_time = time.time()
    span = trace.get_current_span()

    # Add filter to span
    span.set_attribute("search.has_query", bool(filter.query))
    span.set_attribute("search.has_status", bool(filter.status))
    span.set_attribute("search.label_count", len(filter.labels))
    span.set_attribute("search.state", filter.state)
    span.set_attribute("search.limit", filter.limit)
    span.set_attribute("search.json_output", json_output)

    logger.info(
        "search_started",
        query=filter.query,
        status=filter.status,
        labels=filter.labels,
        state=filter.state,
        limit=filter.limit
    )

    try:
        # Step 1: Build label list from shortcuts
        with tracer.start_as_current_span("build_labels") as label_span:
            labels = _build_label_list(filter)

            label_span.set_attribute("search.final_label_count", len(labels))

            logger.info(
                "labels_built",
                labels=labels
            )

        # Step 2: Query GitHub
        with tracer.start_as_current_span("query_github") as query_span:
            issues = _query_issues(filter, labels, config)

            query_span.set_attribute("search.raw_result_count", len(issues))

            logger.info(
                "github_queried",
                result_count=len(issues)
            )

        # Step 3: Filter by project status (if specified)
        if filter.status:
            with tracer.start_as_current_span("filter_by_status") as status_span:
                issues = _filter_by_status(issues, filter.status, config)

                status_span.set_attribute("search.filtered_result_count", len(issues))

                logger.info(
                    "filtered_by_status",
                    status=filter.status,
                    result_count=len(issues)
                )

        # Step 4: Format output
        with tracer.start_as_current_span("format_output") as format_span:
            formatted_output = _format_output(issues, json_output)

            format_span.set_attribute("search.output_length", len(formatted_output))

            logger.info(
                "output_formatted",
                output_length=len(formatted_output),
                json_output=json_output
            )

        # Success!
        duration_ms = (time.time() - start_time) * 1000

        search_counter.add(1, {
            "status": "success",
            "has_query": str(bool(filter.query)),
            "has_status": str(bool(filter.status))
        })
        search_duration.record(duration_ms, {"status": "success"})
        search_results_count.record(len(issues), {})

        span.set_status(Status(StatusCode.OK))
        span.set_attribute("search.duration_ms", duration_ms)
        span.set_attribute("search.success", True)
        span.set_attribute("search.result_count", len(issues))

        logger.info(
            "search_completed",
            result_count=len(issues),
            duration_ms=duration_ms,
            success=True
        )

        return SearchResult(
            success=True,
            issues=issues,
            count=len(issues),
            duration_ms=duration_ms,
            filter_used=filter,
            formatted_output=formatted_output
        )

    except Exception as e:
        # Record error
        duration_ms = (time.time() - start_time) * 1000

        search_errors.add(1, {
            "error_type": type(e).__name__
        })
        search_duration.record(duration_ms, {"status": "error"})

        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        span.set_attribute("search.success", False)
        span.set_attribute("search.error_type", type(e).__name__)

        logger.error(
            "search_failed",
            error=str(e),
            error_type=type(e).__name__,
            duration_ms=duration_ms,
            exc_info=True
        )

        return SearchResult(
            success=False,
            issues=[],
            count=0,
            duration_ms=duration_ms,
            filter_used=filter,
            error=str(e)
        )


def _build_label_list(filter: SearchFilter) -> List[str]:
    """Convert shortcuts to label list."""
    labels = list(filter.labels)  # Start with explicit labels

    # Map type shortcuts to labels
    if filter.type:
        type_map = {
            "task": "pwk:personal",
            "ai-task": "pwk:ai",
            "personal": "pwk:personal",
            "capture": "pwk:capture",
            "work-item": "pwk:work-item"
        }
        labels.append(type_map.get(filter.type, f"pwk:{filter.type}"))

    # Add priority label
    if filter.priority:
        labels.append(f"priority:{filter.priority}")

    # Add energy label
    if filter.energy:
        labels.append(f"energy:{filter.energy}")

    return labels


def _query_issues(
    filter: SearchFilter,
    labels: List[str],
    config: GPWKConfig
) -> List[GithubIssue]:
    """Query GitHub using gh CLI."""
    cmd = [
        "gh", "issue", "list",
        "--repo", config.github_repo,
        "--state", filter.state,
        "--limit", str(filter.limit),
        "--json", "number,title,labels,state,createdAt,body,url"
    ]

    # Add label filter if specified
    if labels:
        cmd.extend(["--label", ",".join(labels)])

    # Add text search if specified
    if filter.query:
        cmd.extend(["--search", filter.query])

    logger.info("executing_gh_command", command=" ".join(cmd))

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )

    issues_data = json.loads(result.stdout)

    # Parse into GithubIssue objects
    issues = []
    for data in issues_data:
        issue = GithubIssue(
            number=data["number"],
            title=data["title"],
            url=data["url"],
            labels=[label["name"] for label in data.get("labels", [])],
            created_at=datetime.fromisoformat(data["createdAt"].replace("Z", "+00:00")),
            body=data.get("body")
        )
        issues.append(issue)

    return issues


def _filter_by_status(
    issues: List[GithubIssue],
    status: str,
    config: GPWKConfig
) -> List[GithubIssue]:
    """Filter issues by project status."""
    # Get project items with status filter
    github = GithubOperations(config)
    project_items = github.get_project_items(status_filter=status)

    # Build set of issue numbers in this status
    item_numbers = {item["content"]["number"] for item in project_items}

    # Filter issues
    filtered = [issue for issue in issues if issue.number in item_numbers]

    return filtered


def _format_output(issues: List[GithubIssue], json_output: bool) -> str:
    """Format search results."""
    if json_output:
        # JSON format
        return json.dumps([{
            "number": issue.number,
            "title": issue.title,
            "url": issue.url,
            "labels": issue.labels,
            "state": "open",  # We queried by state, so all will have same state
            "created_at": issue.created_at.isoformat()
        } for issue in issues], indent=2)

    # Human-readable format
    if not issues:
        return "Found 0 issue(s)"

    output = [f"Found {len(issues)} issue(s):\n"]

    for issue in issues:
        labels_str = ", ".join(issue.labels) if issue.labels else "none"
        output.append(f"#{issue.number} - {issue.title}")
        output.append(f"  Labels: {labels_str}")
        output.append(f"  URL: {issue.url}\n")

    return "\n".join(output)
