"""GPWK Optimize command - Analyze work patterns and suggest system optimizations."""

import os
import re
import time
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import structlog

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode

from ..config import GPWKConfig
from ..telemetry import get_tracer, get_meter

logger = structlog.get_logger(__name__)
tracer = get_tracer(__name__)
meter = get_meter(__name__)

# Metrics
optimize_runs = meter.create_counter(
    "gpwk.optimize.runs.total",
    description="Total optimize runs",
    unit="1"
)

optimize_duration = meter.create_histogram(
    "gpwk.optimize.duration",
    description="Optimize operation duration",
    unit="ms"
)

optimizations_applied = meter.create_counter(
    "gpwk.optimize.applied.total",
    description="Number of optimizations applied",
    unit="1"
)


@dataclass
class DailyMetrics:
    """Metrics for a single day."""

    date: date
    planned_count: int = 0
    completed_count: int = 0
    completion_rate: float = 0.0
    carryover_count: int = 0
    deep_work_minutes: int = 0
    activities: List[Tuple[str, str]] = field(default_factory=list)  # (time, activity)
    completed_tasks: List[str] = field(default_factory=list)
    remaining_tasks: List[str] = field(default_factory=list)
    reflections: Dict[str, str] = field(default_factory=dict)  # {"went_well": "...", "could_improve": "..."}


@dataclass
class OptimizationRecommendation:
    """A single optimization recommendation."""

    priority: str  # "high", "medium", "low"
    title: str
    current: str
    recommended: str
    data: Dict[str, any]
    rationale: str
    impact: str
    category: str  # "task_limits", "deep_work", "carryover", etc.


@dataclass
class OptimizeResult:
    """Result of an optimize operation."""

    success: bool
    days_analyzed: int = 0
    date_range: Tuple[date, date] = None
    avg_completion_rate: float = 0.0
    avg_carryover: float = 0.0
    recommendations: List[OptimizationRecommendation] = field(default_factory=list)
    applied_changes: List[str] = field(default_factory=list)
    report_path: Optional[str] = None
    tracking_issue: Optional[int] = None
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


class OptimizeCommand:
    """Optimize command with telemetry."""

    def __init__(self, config: GPWKConfig):
        """Initialize optimize command."""
        self.config = config

    @tracer.start_as_current_span("optimize")
    def optimize(
        self,
        weeks: int = 2,
        dry_run: bool = False,
        auto_apply: bool = False
    ) -> OptimizeResult:
        """
        Analyze work patterns and suggest optimizations.

        Args:
            weeks: Number of weeks to analyze (default: 2)
            dry_run: Preview only, don't apply changes
            auto_apply: Automatically apply all recommendations

        Returns:
            OptimizeResult with analysis and recommendations
        """
        start_time = time.time()
        span = trace.get_current_span()

        span.set_attribute("optimize.weeks", weeks)
        span.set_attribute("optimize.dry_run", dry_run)
        span.set_attribute("optimize.auto_apply", auto_apply)

        logger.info(
            "optimize_started",
            weeks=weeks,
            dry_run=dry_run,
            auto_apply=auto_apply
        )

        try:
            # Step 1: Collect historical data
            with tracer.start_as_current_span("collect_data"):
                daily_metrics = self._collect_historical_data(weeks)

            if not daily_metrics:
                return OptimizeResult(
                    success=False,
                    error="No log data found. Run /gpwk.review to create daily logs first.",
                    duration_ms=(time.time() - start_time) * 1000
                )

            # Step 2: Calculate aggregate metrics
            with tracer.start_as_current_span("calculate_metrics"):
                agg_metrics = self._calculate_aggregate_metrics(daily_metrics)

            # Step 3: Read current principles
            with tracer.start_as_current_span("read_principles"):
                current_principles = self._read_current_principles()

            # Step 4: Generate recommendations
            with tracer.start_as_current_span("generate_recommendations"):
                recommendations = self._generate_recommendations(agg_metrics, current_principles)

            # Step 5: Create report
            with tracer.start_as_current_span("create_report"):
                report_path = self._create_report(daily_metrics, agg_metrics, recommendations, dry_run)

            # Step 6: Interactive approval (unless dry_run or auto_apply)
            applied_changes = []
            tracking_issue = None

            if not dry_run:
                if auto_apply:
                    # Apply all recommendations
                    applied_changes = self._apply_recommendations(recommendations)
                    tracking_issue = self._create_tracking_issue(recommendations, applied_changes)
                else:
                    # Interactive approval
                    approved = self._get_user_approval(recommendations)
                    if approved:
                        applied_changes = self._apply_recommendations(approved)
                        tracking_issue = self._create_tracking_issue(approved, applied_changes)

            duration_ms = (time.time() - start_time) * 1000

            # Record metrics
            optimize_runs.add(1, {"dry_run": dry_run})
            optimize_duration.record(duration_ms)
            if applied_changes:
                optimizations_applied.add(len(applied_changes), {"auto": auto_apply})

            span.set_attribute("optimize.days_analyzed", len(daily_metrics))
            span.set_attribute("optimize.recommendations", len(recommendations))
            span.set_attribute("optimize.applied", len(applied_changes))
            span.set_status(Status(StatusCode.OK))

            logger.info(
                "optimize_completed",
                days_analyzed=len(daily_metrics),
                recommendations=len(recommendations),
                applied=len(applied_changes),
                duration_ms=duration_ms
            )

            return OptimizeResult(
                success=True,
                days_analyzed=len(daily_metrics),
                date_range=(daily_metrics[0].date, daily_metrics[-1].date) if daily_metrics else None,
                avg_completion_rate=agg_metrics.get("avg_completion_rate", 0),
                avg_carryover=agg_metrics.get("avg_carryover", 0),
                recommendations=recommendations,
                applied_changes=applied_changes,
                report_path=report_path,
                tracking_issue=tracking_issue,
                message=f"Analyzed {len(daily_metrics)} days, generated {len(recommendations)} recommendations",
                duration_ms=duration_ms
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            span.record_exception(e)
            span.set_status(Status(StatusCode.ERROR, str(e)))

            logger.error(
                "optimize_failed",
                error=str(e),
                duration_ms=duration_ms,
                exc_info=True
            )

            return OptimizeResult(
                success=False,
                error=str(e),
                duration_ms=duration_ms
            )

    def _collect_historical_data(self, weeks: int) -> List[DailyMetrics]:
        """Collect historical data from daily logs."""
        logs_dir = Path(self.config.logs_dir)

        if not logs_dir.exists():
            logger.warning("logs_directory_not_found", path=str(logs_dir))
            return []

        # Get log files from last N weeks
        cutoff_date = date.today() - timedelta(weeks=weeks)
        log_files = sorted(logs_dir.glob("*.md"))

        daily_metrics = []

        for log_file in log_files:
            # Extract date from filename (YYYY-MM-DD.md)
            match = re.match(r"(\d{4}-\d{2}-\d{2})\.md", log_file.name)
            if not match:
                continue

            log_date = datetime.strptime(match.group(1), "%Y-%m-%d").date()

            if log_date < cutoff_date:
                continue

            # Parse the log file
            metrics = self._parse_log_file(log_file, log_date)
            if metrics:
                daily_metrics.append(metrics)

        logger.info("historical_data_collected", days=len(daily_metrics), weeks=weeks)
        return daily_metrics

    def _parse_log_file(self, log_file: Path, log_date: date) -> Optional[DailyMetrics]:
        """Parse a single log file to extract metrics."""
        try:
            content = log_file.read_text()

            metrics = DailyMetrics(date=log_date)

            # Extract completed tasks
            completed_section = re.search(r"## Completed.*?\n(.*?)\n##", content, re.DOTALL)
            if completed_section:
                tasks = re.findall(r"- (.+)", completed_section.group(1))
                metrics.completed_tasks = tasks
                metrics.completed_count = len(tasks)

            # Extract remaining tasks
            remaining_section = re.search(r"## Not Completed.*?\n(.*?)\n##", content, re.DOTALL)
            if remaining_section:
                tasks = re.findall(r"- (.+)", remaining_section.group(1))
                metrics.remaining_tasks = tasks

            # Calculate planned count
            metrics.planned_count = metrics.completed_count + len(metrics.remaining_tasks)

            # Calculate completion rate
            if metrics.planned_count > 0:
                metrics.completion_rate = metrics.completed_count / metrics.planned_count

            # Extract carryover count (mentions of pwk:c labels)
            carryover_matches = re.findall(r"pwk:c[123]", content)
            metrics.carryover_count = len(set(carryover_matches))

            # Extract reflections
            went_well = re.search(r"### What went well\?\s*\n(.+)", content)
            if went_well:
                metrics.reflections["went_well"] = went_well.group(1).strip()

            could_improve = re.search(r"### What could be improved\?\s*\n(.+)", content)
            if could_improve:
                metrics.reflections["could_improve"] = could_improve.group(1).strip()

            learned = re.search(r"### What did you learn\?\s*\n(.+)", content)
            if learned:
                metrics.reflections["learned"] = learned.group(1).strip()

            return metrics

        except Exception as e:
            logger.warning("log_parse_failed", file=str(log_file), error=str(e))
            return None

    def _calculate_aggregate_metrics(self, daily_metrics: List[DailyMetrics]) -> Dict:
        """Calculate aggregate metrics across all days."""
        if not daily_metrics:
            return {}

        total_planned = sum(m.planned_count for m in daily_metrics)
        total_completed = sum(m.completed_count for m in daily_metrics)
        total_carryover = sum(m.carryover_count for m in daily_metrics)

        completion_rates = [m.completion_rate for m in daily_metrics if m.planned_count > 0]

        # Aggregate reflections
        could_improve_themes = defaultdict(int)
        for m in daily_metrics:
            if "could_improve" in m.reflections:
                text = m.reflections["could_improve"].lower()
                # Simple keyword extraction
                if "start earlier" in text or "started late" in text:
                    could_improve_themes["start_earlier"] += 1
                if "time estimate" in text or "took longer" in text:
                    could_improve_themes["time_estimates"] += 1
                if "health" in text or "exercise" in text:
                    could_improve_themes["health"] += 1
                if "backlog" in text:
                    could_improve_themes["backlog"] += 1

        return {
            "days_analyzed": len(daily_metrics),
            "avg_planned": total_planned / len(daily_metrics),
            "avg_completed": total_completed / len(daily_metrics),
            "avg_completion_rate": sum(completion_rates) / len(completion_rates) if completion_rates else 0,
            "avg_carryover": total_carryover / len(daily_metrics),
            "total_planned": total_planned,
            "total_completed": total_completed,
            "could_improve_themes": dict(could_improve_themes)
        }

    def _read_current_principles(self) -> Dict:
        """Read current principles from memory file."""
        principles_path = Path("gpwk/memory/principles.md")

        if not principles_path.exists():
            logger.warning("principles_file_not_found")
            return {}

        content = principles_path.read_text()

        principles = {}

        # Extract daily task limit
        limit_match = re.search(r"Maximum significant tasks[:\s]+(\d+)", content, re.IGNORECASE)
        if limit_match:
            principles["max_tasks"] = int(limit_match.group(1))

        # Extract deep work window
        deep_work_match = re.search(r"Preferred time[:\s]+(.+)", content, re.IGNORECASE)
        if deep_work_match:
            principles["deep_work_time"] = deep_work_match.group(1).strip()

        return principles

    def _generate_recommendations(
        self,
        agg_metrics: Dict,
        current_principles: Dict
    ) -> List[OptimizationRecommendation]:
        """Generate optimization recommendations based on data."""
        recommendations = []

        # Recommendation 1: Adjust daily task limit
        avg_completed = agg_metrics.get("avg_completed", 0)
        avg_planned = agg_metrics.get("avg_planned", 0)
        completion_rate = agg_metrics.get("avg_completion_rate", 0)
        current_max = current_principles.get("max_tasks", 6)

        # If completion rate is low and avg_planned is high, suggest reducing limit
        if completion_rate < 0.85 and avg_planned > avg_completed:
            recommended_max = max(3, int(avg_completed + 0.5))  # Round up completed + buffer
            projected_rate = min(0.95, completion_rate * (current_max / recommended_max))

            recommendations.append(OptimizationRecommendation(
                priority="high",
                title="Adjust Daily Task Limit",
                current=f"Maximum significant tasks: {current_max}",
                recommended=f"Maximum significant tasks: {recommended_max}",
                data={
                    "avg_planned": round(avg_planned, 1),
                    "avg_completed": round(avg_completed, 1),
                    "current_rate": round(completion_rate * 100, 1),
                    "projected_rate": round(projected_rate * 100, 1)
                },
                rationale=f"You consistently plan {avg_planned:.1f} tasks but complete {avg_completed:.1f} " +
                         f"({completion_rate*100:.0f}% success). Lowering to {recommended_max} would give " +
                         f"{projected_rate*100:.0f}% success rate and build momentum.",
                impact="High - Improves daily satisfaction and reduces carryover",
                category="task_limits"
            ))

        # Recommendation 2: Address carryover patterns
        avg_carryover = agg_metrics.get("avg_carryover", 0)

        if avg_carryover > 0.5:
            recommendations.append(OptimizationRecommendation(
                priority="medium",
                title="Add c2 Breakdown Trigger",
                current="c3 threshold: Mandatory action",
                recommended="c2 threshold: Suggest breakdown",
                data={
                    "avg_carryover": round(avg_carryover, 1),
                    "days_analyzed": agg_metrics.get("days_analyzed", 0)
                },
                rationale=f"Average {avg_carryover:.1f} carryover tasks per day. " +
                         "Tasks at c2 often become chronic. Earlier intervention prevents this pattern.",
                impact="Medium - Reduces chronic carryover",
                category="carryover"
            ))

        # Recommendation 3: Reflection themes
        themes = agg_metrics.get("could_improve_themes", {})

        if themes.get("start_earlier", 0) >= 3:
            recommendations.append(OptimizationRecommendation(
                priority="high",
                title="Address Over-Planning Pattern",
                current=f"Planning {avg_planned:.1f} tasks per day",
                recommended=f"Reduce to {int(avg_completed + 1)} tasks per day",
                data={
                    "mentions": themes["start_earlier"],
                    "theme": "Repeatedly mentions starting earlier"
                },
                rationale=f"You mentioned 'could start earlier' {themes['start_earlier']} times. " +
                         "This suggests over-planning. Reduce daily load to match actual capacity.",
                impact="High - Reduces stress and improves execution",
                category="planning"
            ))

        if themes.get("health", 0) >= 3:
            recommendations.append(OptimizationRecommendation(
                priority="medium",
                title="Add Health Task to Daily Plan",
                current="No dedicated health time",
                recommended="Add 1 health task to morning planning",
                data={
                    "mentions": themes["health"],
                    "theme": "Health tasks mentioned but not scheduled"
                },
                rationale=f"Health mentioned {themes['health']} times in reflections but rarely scheduled. " +
                         "Add explicit health task to make it a priority.",
                impact="Medium - Improves well-being",
                category="health"
            ))

        return recommendations

    def _create_report(
        self,
        daily_metrics: List[DailyMetrics],
        agg_metrics: Dict,
        recommendations: List[OptimizationRecommendation],
        dry_run: bool
    ) -> str:
        """Create optimization report."""
        report_dir = Path("ideas")
        report_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        report_path = report_dir / f"optimization-report-{timestamp}.md"

        # Build report content
        content = f"""# GPWK Optimization Report

**Generated**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Data Period**: {daily_metrics[0].date} to {daily_metrics[-1].date} ({len(daily_metrics)} days)
**Logs Analyzed**: {len(daily_metrics)} files

## Executive Summary

Based on {len(daily_metrics)} days of work data, your system is performing at {agg_metrics['avg_completion_rate']*100:.0f}% completion rate.

**Key Metrics**:
- Average tasks planned: {agg_metrics['avg_planned']:.1f}/day
- Average tasks completed: {agg_metrics['avg_completed']:.1f}/day
- Average completion rate: {agg_metrics['avg_completion_rate']*100:.0f}%
- Average carryover: {agg_metrics['avg_carryover']:.1f}/day

## Recommended Changes

"""

        # Group recommendations by priority
        high_priority = [r for r in recommendations if r.priority == "high"]
        medium_priority = [r for r in recommendations if r.priority == "medium"]
        low_priority = [r for r in recommendations if r.priority == "low"]

        for priority_group, priority_label in [(high_priority, "HIGH PRIORITY ⚠️"),
                                                (medium_priority, "MEDIUM PRIORITY"),
                                                (low_priority, "LOW PRIORITY")]:
            if priority_group:
                content += f"\n### {priority_label}\n\n"

                for i, rec in enumerate(priority_group, 1):
                    content += f"""#### {i}. {rec.title}

**Current**: {rec.current}
**Recommended**: {rec.recommended}

**Data**:
{chr(10).join(f"- {k}: {v}" for k, v in rec.data.items())}

**Rationale**:
{rec.rationale}

**Impact**: {rec.impact}

---

"""

        if dry_run:
            content += "\n## Dry Run Mode\n\nNo changes were applied. Review recommendations above.\n"
        else:
            content += "\n## Next Steps\n\n"
            content += "Review recommendations and approve changes to update your principles.\n"

        # Write report
        report_path.write_text(content)
        logger.info("report_created", path=str(report_path))

        return str(report_path)

    def _get_user_approval(self, recommendations: List[OptimizationRecommendation]) -> List[OptimizationRecommendation]:
        """Get interactive user approval for recommendations."""
        # This would be interactive in a real implementation
        # For now, return high priority recommendations
        return [r for r in recommendations if r.priority == "high"]

    def _apply_recommendations(self, recommendations: List[OptimizationRecommendation]) -> List[str]:
        """Apply approved recommendations to principles file."""
        if not recommendations:
            return []

        principles_path = Path("gpwk/memory/principles.md")

        if not principles_path.exists():
            logger.error("principles_file_not_found")
            return []

        content = principles_path.read_text()
        applied = []

        for rec in recommendations:
            if rec.category == "task_limits":
                # Update task limit
                new_limit = rec.data.get("recommended_max") or int(re.search(r"\d+", rec.recommended).group())
                content = re.sub(
                    r"(Maximum significant tasks[:\s]+)\d+",
                    f"\\g<1>{new_limit}",
                    content,
                    flags=re.IGNORECASE
                )
                applied.append(f"Updated task limit to {new_limit}")

        # Add update note
        update_note = f"\n\n> Updated by /gpwk.optimize on {date.today()} based on {len(recommendations)} recommendations\n"
        content += update_note

        # Write back
        principles_path.write_text(content)
        logger.info("principles_updated", changes=len(applied))

        return applied

    def _create_tracking_issue(
        self,
        recommendations: List[OptimizationRecommendation],
        applied_changes: List[str]
    ) -> Optional[int]:
        """Create GitHub issue to track optimization experiment."""
        # This would use gh CLI or GitHub API
        # For now, just log it
        logger.info("tracking_issue_needed", recommendations=len(recommendations), changes=len(applied_changes))
        return None
