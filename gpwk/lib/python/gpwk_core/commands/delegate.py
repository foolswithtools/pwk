"""GPWK Delegate command - Execute AI-delegatable tasks with telemetry."""

import time
import subprocess
import json
from typing import List, Dict, Optional
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..models import DelegateResult
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Operational Metrics (how delegate performs)
delegate_operations = meter.create_counter(
    "gpwk.delegate.operations.total",
    description="Total delegate operations",
    unit="1"
)

delegate_duration = meter.create_histogram(
    "gpwk.delegate.duration",
    description="Delegate operation duration",
    unit="ms"
)

tasks_executed = meter.create_counter(
    "gpwk.delegate.tasks_executed.total",
    description="Number of AI tasks executed",
    unit="1"
)

delegate_errors = meter.create_counter(
    "gpwk.delegate.errors",
    description="Failed delegate operations",
    unit="1"
)


class DelegateCommand:
    """Delegate command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize delegate command."""
        self.config = config

    @tracer.start_as_current_span("delegate")
    def delegate(
        self,
        issue_number: Optional[int] = None,
        execute_all: bool = False,
        list_only: bool = False,
        sync_status: bool = False
    ) -> DelegateResult:
        """
        Delegate AI tasks.

        Args:
            issue_number: Specific issue to execute
            execute_all: Execute all pending AI tasks
            list_only: Only list AI tasks
            sync_status: Sync AI-complete tasks to Review status

        Returns:
            DelegateResult with execution status and details
        """
        start_time = time.time()
        span = trace.get_current_span()

        span.set_attribute("delegate.issue_number", issue_number or "all")
        span.set_attribute("delegate.execute_all", execute_all)
        span.set_attribute("delegate.list_only", list_only)
        span.set_attribute("delegate.sync_status", sync_status)

        logger.info(
            "delegate_started",
            issue_number=issue_number,
            execute_all=execute_all,
            list_only=list_only,
            sync_status=sync_status
        )

        try:
            if sync_status:
                # Sync AI-complete tasks to Review status
                result = self._sync_ai_complete_status()
            elif list_only:
                # List AI-delegatable tasks
                result = self._list_ai_tasks()
            elif issue_number:
                # Execute specific task
                result = self._execute_task(issue_number)
            elif execute_all:
                # Execute all pending AI tasks
                result = self._execute_all_tasks()
            else:
                # Default: list tasks
                result = self._list_ai_tasks()

            duration_ms = (time.time() - start_time) * 1000

            delegate_operations.add(1, {"status": "success", "mode": "execute" if not list_only else "list"})
            delegate_duration.record(duration_ms, {"status": "success"})

            span.set_status(Status(StatusCode.OK))
            span.set_attribute("delegate.duration_ms", duration_ms)

            logger.info(
                "delegate_completed",
                duration_ms=duration_ms,
                success=True
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            delegate_errors.add(1, {"error_type": type(e).__name__})
            delegate_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "delegate_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=duration_ms,
                exc_info=True
            )

            return DelegateResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    @tracer.start_as_current_span("sync_ai_complete_status")
    def _sync_ai_complete_status(self) -> DelegateResult:
        """Sync all AI-complete tasks to Review status."""
        from ..github_ops import GithubOperations

        logger.info("syncing_ai_complete_tasks")

        # Get all issues with status:ai-complete label
        ai_complete_tasks = self._get_ai_complete_tasks()

        if not ai_complete_tasks:
            logger.info("no_ai_complete_tasks_found")
            return DelegateResult(
                success=True,
                message="No AI-complete tasks found to sync"
            )

        github = GithubOperations(self.config)
        synced_count = 0
        failed_count = 0

        for task in ai_complete_tasks:
            issue_number = task.get("number")
            title = task.get("title", "Untitled")

            try:
                # Get project item ID
                project_item_id = self._get_project_item_id_for_issue(issue_number)

                if not project_item_id:
                    logger.warning(
                        "project_item_not_found_for_sync",
                        issue_number=issue_number
                    )
                    failed_count += 1
                    continue

                # Move to Review status
                logger.info("moving_to_review_status", issue_number=issue_number)
                github.set_project_fields(
                    item_id=project_item_id,
                    status="review"
                )

                synced_count += 1

            except Exception as e:
                logger.error(
                    "sync_failed_for_task",
                    issue_number=issue_number,
                    error=str(e)
                )
                failed_count += 1

        logger.info(
            "sync_completed",
            synced=synced_count,
            failed=failed_count,
            total=len(ai_complete_tasks)
        )

        return DelegateResult(
            success=True,
            tasks_executed=synced_count,
            tasks_failed=failed_count,
            message=f"Synced {synced_count} AI-complete tasks to Review status ({failed_count} failed)"
        )

    @tracer.start_as_current_span("list_ai_tasks")
    def _list_ai_tasks(self) -> DelegateResult:
        """List all AI-delegatable tasks."""
        # Get all AI tasks
        ai_tasks = self._get_ai_tasks()

        logger.info("ai_tasks_fetched", count=len(ai_tasks))

        return DelegateResult(
            success=True,
            ai_tasks=ai_tasks,
            message=f"Found {len(ai_tasks)} AI-delegatable tasks"
        )

    @tracer.start_as_current_span("execute_task")
    def _execute_task(self, issue_number: int) -> DelegateResult:
        """
        Prepare infrastructure for AI task execution.

        IMPORTANT: This method does NOT execute AI tasks directly.
        It prepares the infrastructure (status updates) and returns.
        Actual AI execution is handled by the GitHub Action.

        Execution Flow:
            1. Python (this method): Validate task and move to "Today" status
            2. GitHub Action: Execute task with Claude Code
            3. GitHub Action: Post result via post_ai_result() helper
            4. GitHub Action: Add status:ai-complete label
            5. Python (--sync-status): Move to "Review" status

        Args:
            issue_number: GitHub issue number with pwk:ai label

        Returns:
            DelegateResult indicating infrastructure preparation success

        Raises:
            ValueError: If issue not found or not labeled as AI-delegatable

        Example:
            delegate = DelegateCommand(config)
            result = delegate._execute_task(96)
            # Issue #96 moved to Today, awaiting GitHub Action execution
        """
        from ..github_ops import GithubOperations

        span = trace.get_current_span()
        span.set_attribute("issue_number", issue_number)

        logger.info("executing_ai_task", issue_number=issue_number)

        # Get issue details
        issue = self._get_issue_details(issue_number)

        if not issue:
            raise ValueError(f"Issue #{issue_number} not found")

        # Check if it's AI-delegatable
        labels = issue.get("labels", [])
        label_names = [label.get("name", "") if isinstance(label, dict) else str(label) for label in labels]

        if "pwk:ai" not in label_names:
            raise ValueError(f"Issue #{issue_number} is not labeled as AI-delegatable (pwk:ai)")

        # Initialize GitHub operations
        github = GithubOperations(self.config)

        # Get project item ID for this issue
        project_item_id = self._get_project_item_id_for_issue(issue_number)

        if project_item_id:
            # STEP 1: Move to "Today" status when AI starts working
            logger.info("moving_to_today", issue_number=issue_number)
            github.set_project_fields(
                item_id=project_item_id,
                status="today"
            )

        # =============================================================================
        # AI EXECUTION ARCHITECTURE
        # =============================================================================
        #
        # This Python backend provides INFRASTRUCTURE ONLY.
        # It does NOT directly execute AI tasks via Anthropic API.
        #
        # Architecture Split:
        #   Python Backend (delegate.py):
        #     - List AI-delegatable tasks (pwk:ai label)
        #     - Update project statuses (Inbox → Today → Review)
        #     - Provide helper methods for result posting
        #     - Full OpenTelemetry instrumentation
        #
        #   GitHub Action (.github/workflows/claude-gpwk.yml):
        #     - Execute tasks using Claude Code environment
        #     - Read issue body and generate results
        #     - Call Python helpers or gh CLI to post results
        #     - Add status:ai-complete label
        #     - Scheduled: Every 4 hours on weekdays
        #
        # Execution Flow:
        #   1. Python: Move issue to "Today" status (above)
        #   2. GitHub Action: Execute task with Claude Code
        #   3. GitHub Action: Post result via post_ai_result() helper
        #   4. GitHub Action: Add status:ai-complete label
        #   5. Python: Sync completed tasks to Review (--sync-status)
        #
        # Manual Trigger:
        #   gh workflow run claude-gpwk.yml -f action_type=delegate
        #
        # Evidence: Issues #96 and #104 were successfully executed this way.
        # =============================================================================

        logger.info(
            "infrastructure_prepared_for_ai_execution",
            issue_number=issue_number,
            message="Issue moved to Today status. GitHub Action will execute AI task."
        )

        if project_item_id:
            # STEP 2: Move to "Review" status when AI completes work
            logger.info("moving_to_review", issue_number=issue_number)
            github.set_project_fields(
                item_id=project_item_id,
                status="review"
            )

        # Note: status:ai-complete label is added by GitHub Action after execution
        # See post_ai_result() helper method below for the posting mechanism

        tasks_executed.add(1, {
            "issue_number": str(issue_number)
        })

        return DelegateResult(
            success=True,
            tasks_executed=1,
            message=f"Infrastructure prepared for #{issue_number}: {issue.get('title', 'Untitled')}. Awaiting GitHub Action execution."
        )

    @tracer.start_as_current_span("post_ai_result")
    def post_ai_result(
        self,
        issue_number: int,
        result_body: str,
        add_ai_complete_label: bool = True
    ) -> bool:
        """
        Post AI execution result as a comment.

        Called by GitHub Action after Claude Code executes an AI task.
        This method is part of the infrastructure layer.

        Args:
            issue_number: Issue number to comment on
            result_body: Markdown-formatted AI execution result
            add_ai_complete_label: Whether to add status:ai-complete label

        Returns:
            True if successful, False otherwise

        Example:
            # Called by GitHub Action or manual testing
            delegate = DelegateCommand(config)
            success = delegate.post_ai_result(
                issue_number=96,
                result_body="## AI Delegation Result\\n\\n...",
                add_ai_complete_label=True
            )
        """
        from ..github_ops import GithubOperations

        span = trace.get_current_span()
        span.set_attribute("issue_number", issue_number)
        span.set_attribute("result_length", len(result_body))
        span.set_attribute("add_label", add_ai_complete_label)

        logger.info(
            "posting_ai_result",
            issue_number=issue_number,
            result_length=len(result_body),
            add_label=add_ai_complete_label
        )

        try:
            github = GithubOperations(self.config)

            # Post comment with AI result
            github._add_comment(issue_number, result_body)
            logger.info("ai_result_comment_posted", issue_number=issue_number)

            # Add status:ai-complete label if requested
            if add_ai_complete_label:
                github.add_label(issue_number, "status:ai-complete")
                logger.info("ai_complete_label_added", issue_number=issue_number)

            span.set_status(Status(StatusCode.OK))
            logger.info(
                "ai_result_posted_successfully",
                issue_number=issue_number
            )

            return True

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(
                "post_ai_result_failed",
                issue_number=issue_number,
                error=str(e),
                exc_info=True
            )
            return False

    @tracer.start_as_current_span("mark_ai_complete")
    def mark_ai_complete(self, issue_number: int) -> bool:
        """
        Add status:ai-complete label to an issue.

        Called by GitHub Action after AI task execution completes
        to signal that the task needs human review.

        Args:
            issue_number: Issue number to mark

        Returns:
            True if successful, False otherwise

        Example:
            delegate = DelegateCommand(config)
            success = delegate.mark_ai_complete(96)
        """
        from ..github_ops import GithubOperations

        span = trace.get_current_span()
        span.set_attribute("issue_number", issue_number)

        logger.info("marking_ai_complete", issue_number=issue_number)

        try:
            github = GithubOperations(self.config)
            github.add_label(issue_number, "status:ai-complete")

            span.set_status(Status(StatusCode.OK))
            logger.info(
                "ai_complete_label_added",
                issue_number=issue_number
            )

            return True

        except Exception as e:
            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))
            logger.error(
                "mark_ai_complete_failed",
                issue_number=issue_number,
                error=str(e),
                exc_info=True
            )
            return False

    @tracer.start_as_current_span("execute_all_tasks")
    def _execute_all_tasks(self) -> DelegateResult:
        """Execute all pending AI tasks."""
        ai_tasks = self._get_ai_tasks()

        executed_count = 0
        failed_count = 0

        for task in ai_tasks:
            number = task.get("number")
            if number:
                try:
                    self._execute_task(number)
                    executed_count += 1
                except Exception as e:
                    logger.warning(
                        "ai_task_execution_failed",
                        issue_number=number,
                        error=str(e)
                    )
                    failed_count += 1

        return DelegateResult(
            success=True,
            tasks_executed=executed_count,
            tasks_failed=failed_count,
            message=f"Executed {executed_count} AI tasks ({failed_count} failed)"
        )

    def _get_ai_tasks(self) -> List[Dict]:
        """Get all AI-delegatable tasks (pwk:ai label), excluding already completed ones."""
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--label", "pwk:ai",
                "--state", "open",
                "--json", "number,title,labels,createdAt",
                "--limit", "100"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        all_tasks = json.loads(result.stdout)

        # Filter out tasks that already have status:ai-complete label
        # These are awaiting human review and should not be re-processed
        tasks = [
            task for task in all_tasks
            if not any(label.get("name") == "status:ai-complete" for label in task.get("labels", []))
        ]

        filtered_count = len(all_tasks) - len(tasks)
        if filtered_count > 0:
            logger.info("ai_complete_tasks_filtered",
                       total=len(all_tasks),
                       filtered=filtered_count,
                       remaining=len(tasks))

        return tasks

    def _get_ai_complete_tasks(self) -> List[Dict]:
        """Get all AI-complete tasks (status:ai-complete label)."""
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", self.config.github_repo,
                "--label", "status:ai-complete",
                "--state", "open",
                "--json", "number,title,labels",
                "--limit", "100"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        tasks = json.loads(result.stdout)
        logger.info("ai_complete_tasks_fetched", count=len(tasks))
        return tasks

    def _get_issue_details(self, issue_number: int) -> Optional[Dict]:
        """Get detailed info for a specific issue."""
        result = subprocess.run(
            [
                "gh", "issue", "view",
                str(issue_number),
                "--repo", self.config.github_repo,
                "--json", "number,title,body,labels,comments"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        issue = json.loads(result.stdout)
        return issue

    def _get_project_item_id_for_issue(self, issue_number: int) -> Optional[str]:
        """Get the project item ID for a given issue number."""
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

        # Find the item matching this issue number
        for item in items:
            content = item.get("content", {})
            if content.get("number") == issue_number:
                return item.get("id")

        logger.warning(
            "project_item_not_found",
            issue_number=issue_number,
            message="Issue not found in project"
        )
        return None
