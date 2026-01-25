"""GPWK Carryover command - Update carryover labels with telemetry."""

import time
import subprocess
import json
from typing import List, Dict, Optional
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
carryover_operations = meter.create_counter(
    "gpwk.carryover.operations.total",
    description="Total carryover operations",
    unit="1"
)

carryover_duration = meter.create_histogram(
    "gpwk.carryover.duration",
    description="Carryover operation duration",
    unit="ms"
)

issues_carried = meter.create_counter(
    "gpwk.carryover.issues.total",
    description="Total issues carried over",
    unit="1"
)


class CarryoverCommand:
    """Carryover command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize carryover command."""
        self.config = config

    @tracer.start_as_current_span("carryover")
    def carryover(self, dry_run: bool = False) -> Dict:
        """
        Update carryover labels on incomplete tasks.

        Args:
            dry_run: Preview changes without applying

        Returns:
            Result dictionary with carryover details
        """
        start_time = time.time()
        span = trace.get_current_span()
        span.set_attribute("carryover.dry_run", dry_run)

        logger.info("carryover_started", dry_run=dry_run)

        try:
            from ..github_ops import GithubOperations
            github_ops = GithubOperations(self.config)

            # 1. Find today's incomplete issues
            today_items = github_ops.get_project_items(status_filter="Today")

            # Filter for open issues only
            incomplete_issues = [
                item for item in today_items
                if item.get("content", {}).get("state") == "OPEN"
            ]

            span.set_attribute("carryover.incomplete_count", len(incomplete_issues))
            logger.info("incomplete_issues_found", count=len(incomplete_issues))

            if not incomplete_issues:
                result = {
                    "success": True,
                    "message": "No incomplete issues to carry over",
                    "dry_run": dry_run,
                    "updates": []
                }

                duration_ms = (time.time() - start_time) * 1000
                carryover_operations.add(1, {"status": "success"})
                carryover_duration.record(duration_ms)
                span.set_status(Status(StatusCode.OK))

                return result

            # 2. Calculate label transitions
            updates = []
            needs_breakdown = []

            for item in incomplete_issues:
                content = item.get("content", {})
                issue_number = content.get("number")
                title = content.get("title", "")

                if not issue_number:
                    continue

                # Get current labels
                labels = [label.get("name") for label in content.get("labels", [])]

                # Determine current carryover state and next action
                current_label = None
                new_label = None
                action = None

                if "pwk:c3" in labels:
                    action = "keep_c3"
                    current_label = "pwk:c3"
                    new_label = "pwk:c3"
                    needs_breakdown.append(issue_number)
                elif "pwk:c2" in labels:
                    action = "c2_to_c3"
                    current_label = "pwk:c2"
                    new_label = "pwk:c3"
                    needs_breakdown.append(issue_number)
                elif "pwk:c1" in labels:
                    action = "c1_to_c2"
                    current_label = "pwk:c1"
                    new_label = "pwk:c2"
                else:
                    action = "add_c1"
                    current_label = None
                    new_label = "pwk:c1"

                updates.append({
                    "issue_number": issue_number,
                    "title": title,
                    "action": action,
                    "current_label": current_label,
                    "new_label": new_label,
                    "needs_breakdown": issue_number in needs_breakdown
                })

            span.set_attribute("carryover.updates_count", len(updates))
            span.set_attribute("carryover.needs_breakdown_count", len(needs_breakdown))

            # 3. If dry run, return preview
            if dry_run:
                result = {
                    "success": True,
                    "message": f"Dry run: {len(updates)} issues would be updated",
                    "dry_run": True,
                    "updates": updates,
                    "needs_breakdown": needs_breakdown
                }

                duration_ms = (time.time() - start_time) * 1000
                carryover_operations.add(1, {"status": "success", "dry_run": "true"})
                carryover_duration.record(duration_ms)
                span.set_status(Status(StatusCode.OK))

                logger.info("carryover_dry_run_completed", updates_count=len(updates), duration_ms=duration_ms)

                return result

            # 4. Apply label updates
            failed_updates = []

            for update in updates:
                issue_num = update["issue_number"]

                try:
                    with tracer.start_as_current_span(f"update_issue_{issue_num}") as update_span:
                        update_span.set_attribute("issue_number", issue_num)
                        update_span.set_attribute("action", update["action"])

                        # Remove old label if exists
                        if update["current_label"] and update["current_label"] != update["new_label"]:
                            github_ops.remove_label(issue_num, update["current_label"])
                            logger.info("label_removed", issue_number=issue_num, label=update["current_label"])

                        # Add new label
                        github_ops.add_label(issue_num, update["new_label"])
                        logger.info("label_added", issue_number=issue_num, label=update["new_label"])

                        # 5. Add tracking comment
                        carryover_level = update["new_label"][-1]  # Extract '1', '2', or '3' from 'pwk:c1'

                        comment = f"""📅 **Carryover Notice**

This task was carried over from today.
Current carryover count: **{carryover_level}**

"""
                        if update["needs_breakdown"]:
                            comment += """⚠️ **Action Needed**: This task has been carried over multiple times.
Consider running `/gpwk.breakdown #{issue_num}` to break it into smaller tasks.

"""

                        comment += "*Logged by GPWK*"

                        github_ops._add_comment(issue_num, comment)
                        logger.info("carryover_comment_added", issue_number=issue_num)

                        update_span.set_status(Status(StatusCode.OK))
                        issues_carried.add(1, {"carryover_level": carryover_level})

                except Exception as e:
                    logger.error("carryover_update_failed", issue_number=issue_num, error=str(e), exc_info=True)
                    failed_updates.append((issue_num, str(e)))

            # 6. Build result
            successful_updates = len(updates) - len(failed_updates)

            result = {
                "success": True,
                "message": f"Carryover complete: {successful_updates} issues updated",
                "dry_run": False,
                "updates": updates,
                "successful_updates": successful_updates,
                "failed_updates": failed_updates,
                "needs_breakdown": needs_breakdown
            }

            duration_ms = (time.time() - start_time) * 1000

            carryover_operations.add(1, {"status": "success"})
            carryover_duration.record(duration_ms)

            span.set_status(Status(StatusCode.OK))
            logger.info(
                "carryover_completed",
                successful_updates=successful_updates,
                failed_updates=len(failed_updates),
                duration_ms=duration_ms
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            carryover_operations.add(1, {"status": "error"})
            carryover_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error("carryover_failed", error=str(e), exc_info=True)

            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms
            }
