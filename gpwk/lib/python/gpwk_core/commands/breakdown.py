"""GPWK Breakdown command - Break down complex work with telemetry."""

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
breakdown_operations = meter.create_counter(
    "gpwk.breakdown.operations.total",
    description="Total breakdown operations",
    unit="1"
)

breakdown_duration = meter.create_histogram(
    "gpwk.breakdown.duration",
    description="Breakdown operation duration",
    unit="ms"
)

sub_issues_created = meter.create_counter(
    "gpwk.breakdown.sub_issues.total",
    description="Total sub-issues created",
    unit="1"
)


class BreakdownCommand:
    """Breakdown command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize breakdown command."""
        self.config = config

    @tracer.start_as_current_span("breakdown")
    def breakdown(self, work_description: str) -> Dict:
        """
        Break down work into parent issue with sub-issues.

        Args:
            work_description: Description of work or existing issue number

        Returns:
            Result dictionary with parent and sub-issue details
        """
        start_time = time.time()
        span = trace.get_current_span()

        logger.info("breakdown_started", work_description=work_description)

        try:
            from ..github_ops import GithubOperations
            github_ops = GithubOperations(self.config)

            # 1. Determine if breaking down existing issue or creating new
            is_existing = work_description.strip().startswith("#")

            if is_existing:
                # Extract issue number
                issue_num_str = work_description.strip()[1:]
                try:
                    parent_issue_number = int(issue_num_str)
                except ValueError:
                    return {
                        "success": False,
                        "error": f"Invalid issue number: {work_description}"
                    }

                # Fetch existing issue
                parent_issue = github_ops.get_issue(parent_issue_number)
                parent_title = parent_issue.title
                parent_body = parent_issue.body or ""
                span.set_attribute("breakdown.existing_issue", True)
                span.set_attribute("breakdown.parent_issue_number", parent_issue_number)

                logger.info("breaking_down_existing_issue", issue_number=parent_issue_number, title=parent_title)
            else:
                # Create new parent issue
                parent_title = f"[Work Item] {work_description}"
                parent_body = f"""## Overview
{work_description}

## Scope
**In Scope:**
- TBD (sub-issues defined below)

**Out of Scope:**
- TBD

## Success Criteria
- [ ] All sub-issues completed
- [ ] Solution tested and validated

## Phases
<!-- Sub-issues will be linked below -->

## Progress
- **Started**: {time.strftime("%Y-%m-%d")}
- **Status**: Planning

## Related
Links to relevant code, docs, or other issues
"""

                parent_issue = github_ops.create_issue(
                    title=parent_title,
                    labels=["pwk:work-item"],
                    body=parent_body
                )

                parent_issue_number = parent_issue.number
                span.set_attribute("breakdown.existing_issue", False)
                span.set_attribute("breakdown.parent_issue_number", parent_issue_number)

                logger.info("parent_issue_created", issue_number=parent_issue_number, title=parent_title)

            # 2. Generate breakdown structure
            # For now, use a simple breakdown structure
            # In future, this could use AI to analyze the work and suggest tasks
            breakdown_plan = {
                "phases": [
                    {
                        "name": "Phase 1: Research & Planning",
                        "tasks": [
                            {"title": "Research existing solutions", "type": "[AI]", "energy": "~deep"},
                            {"title": "Document requirements", "type": "[P]", "energy": "~shallow"},
                            {"title": "Create implementation plan", "type": "[P]", "energy": "~deep"}
                        ]
                    },
                    {
                        "name": "Phase 2: Implementation",
                        "tasks": [
                            {"title": "Set up project structure", "type": "[P]", "energy": "~shallow"},
                            {"title": "Implement core functionality", "type": "[P]", "energy": "~deep"},
                            {"title": "Add error handling", "type": "[P]", "energy": "~shallow"}
                        ]
                    },
                    {
                        "name": "Phase 3: Testing & Documentation",
                        "tasks": [
                            {"title": "Write tests", "type": "[AI]", "energy": "~shallow"},
                            {"title": "Manual testing", "type": "[P]", "energy": "~shallow"},
                            {"title": "Write documentation", "type": "[AI]", "energy": "~shallow"}
                        ]
                    }
                ]
            }

            span.set_attribute("breakdown.phases_count", len(breakdown_plan["phases"]))

            # 3. Create sub-issues
            sub_issues = []
            total_tasks = sum(len(phase["tasks"]) for phase in breakdown_plan["phases"])

            span.set_attribute("breakdown.total_tasks", total_tasks)

            for phase_idx, phase in enumerate(breakdown_plan["phases"], 1):
                for task_idx, task in enumerate(phase["tasks"], 1):
                    # Determine labels
                    task_type = task["type"]
                    if task_type == "[AI]":
                        labels = ["pwk:ai"]
                    else:
                        labels = ["pwk:personal"]

                    # Add energy label if specified
                    energy = task.get("energy", "").replace("~", "")
                    if energy in ["deep", "shallow", "quick"]:
                        labels.append(f"energy:{energy}")

                    # Create sub-issue
                    sub_body = f"""## Parent Work Item
Part of #{parent_issue_number}: {parent_title}

## Task
{task["title"]}

## Phase
{phase["name"]} (Task {task_idx} of {len(phase["tasks"])})

## Acceptance Criteria
- [ ] Task completed as described
- [ ] Code/documentation updated if needed
- [ ] Testing completed

## Notes
(Add notes as you work)
"""

                    with tracer.start_as_current_span(f"create_sub_issue_{phase_idx}_{task_idx}") as sub_span:
                        sub_issue = github_ops.create_issue(
                            title=f"{task['title']} {task_type}",
                            labels=labels,
                            body=sub_body
                        )

                        sub_span.set_attribute("sub_issue_number", sub_issue.number)
                        sub_span.set_attribute("phase", phase["name"])

                        # Add to project
                        try:
                            project_item = github_ops.add_to_project_with_retry(sub_issue.url)

                            # Set to Backlog status
                            github_ops.set_project_fields(
                                project_item.id,
                                status="backlog"
                            )

                            sub_span.add_event("Added to project")
                        except Exception as e:
                            logger.warning("add_to_project_failed", issue_number=sub_issue.number, error=str(e))
                            sub_span.add_event(f"Failed to add to project: {str(e)}")

                        sub_issues.append({
                            "number": sub_issue.number,
                            "title": task["title"],
                            "type": task_type,
                            "phase": phase["name"],
                            "url": sub_issue.url
                        })

                        sub_issues_created.add(1, {"type": task_type.strip("[]").lower()})

                        logger.info("sub_issue_created", issue_number=sub_issue.number, phase=phase["name"])

            # 4. Update parent issue with sub-issue links
            updated_body = parent_body + "\n\n## Sub-Issues\n\n"

            for phase in breakdown_plan["phases"]:
                updated_body += f"\n### {phase['name']}\n\n"
                phase_issues = [si for si in sub_issues if si["phase"] == phase["name"]]

                for sub_issue in phase_issues:
                    updated_body += f"- [ ] #{sub_issue['number']} - {sub_issue['title']} {sub_issue['type']}\n"

            github_ops.update_issue(parent_issue_number, body=updated_body)

            logger.info("parent_issue_updated", issue_number=parent_issue_number, sub_issues_count=len(sub_issues))

            # 5. Build result
            result = {
                "success": True,
                "message": f"Breakdown complete: {len(sub_issues)} sub-issues created",
                "parent_issue": {
                    "number": parent_issue_number,
                    "title": parent_title,
                    "url": f"https://github.com/{self.config.github_repo}/issues/{parent_issue_number}"
                },
                "sub_issues": sub_issues,
                "phases": [phase["name"] for phase in breakdown_plan["phases"]],
                "total_tasks": len(sub_issues)
            }

            duration_ms = (time.time() - start_time) * 1000

            breakdown_operations.add(1, {"status": "success"})
            breakdown_duration.record(duration_ms)

            span.set_status(Status(StatusCode.OK))
            logger.info(
                "breakdown_completed",
                parent_issue=parent_issue_number,
                sub_issues_count=len(sub_issues),
                duration_ms=duration_ms
            )

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            breakdown_operations.add(1, {"status": "error"})
            breakdown_duration.record(duration_ms, {"status": "error"})

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error("breakdown_failed", error=str(e), exc_info=True)

            return {
                "success": False,
                "error": str(e),
                "duration_ms": duration_ms
            }
