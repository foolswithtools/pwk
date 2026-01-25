"""Data models for GPWK."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import List, Optional, Tuple


@dataclass
class ParsedCapture:
    """Result of parsing a capture notation."""

    title: str
    type: str  # "task", "ai-task", "capture"
    labels: List[str]
    body: str
    is_completed: bool = False
    priority: Optional[str] = None  # "high", "medium", "low"
    energy: Optional[str] = None  # "deep", "shallow", "quick"
    time_range: Optional[Tuple[str, str]] = None  # ("09:00", "10:00")
    markers: List[str] = field(default_factory=list)

    @property
    def project_fields(self) -> dict:
        """Get project fields as a dict."""
        fields = {"type": self.type}
        if self.priority:
            fields["priority"] = self.priority
        if self.energy:
            fields["energy"] = self.energy
        return fields


@dataclass
class GithubIssue:
    """GitHub issue representation."""

    number: int
    title: str
    url: str
    labels: List[str]
    created_at: datetime
    body: Optional[str] = None

    @property
    def carryover_level(self) -> Optional[int]:
        """Extract carryover level from labels."""
        for label in self.labels:
            if label.startswith("pwk:c"):
                try:
                    return int(label[-1])
                except ValueError:
                    pass
        return None

    @property
    def is_ai_delegatable(self) -> bool:
        """Check if issue is AI-delegatable."""
        return "pwk:ai" in self.labels


@dataclass
class ProjectItem:
    """GitHub project item representation."""

    id: str
    issue: GithubIssue
    status: str
    retry_count: int = 0


@dataclass
class CaptureResult:
    """Result of a capture operation."""

    success: bool
    issue_number: Optional[int] = None
    issue_url: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class TriageResult:
    """Result of a triage operation."""

    success: bool
    items_moved: int = 0
    inbox_items: List[dict] = field(default_factory=list)
    closed_issues: List[dict] = field(default_factory=list)
    failed_issues: List[tuple] = field(default_factory=list)
    recommendations: List[dict] = field(default_factory=list)
    target_status: Optional[str] = None
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class DelegateResult:
    """Result of a delegate operation."""

    success: bool
    tasks_executed: int = 0
    tasks_failed: int = 0
    ai_tasks: List[dict] = field(default_factory=list)
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ReviewResult:
    """Result of a review operation."""

    success: bool
    review_date: datetime.date
    completed_issues: List[dict] = field(default_factory=list)
    remaining_issues: List[dict] = field(default_factory=list)
    carryover_issues: List[dict] = field(default_factory=list)
    completed_count: int = 0
    remaining_count: int = 0
    completion_rate: float = 0.0
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class PlanResult:
    """Result of a plan operation."""

    success: bool
    plan_date: datetime.date
    log_path: Optional[str] = None
    today_issues: List[dict] = field(default_factory=list)
    carryover_issues: List[dict] = field(default_factory=list)
    high_priority_issues: List[dict] = field(default_factory=list)
    ai_issues: List[dict] = field(default_factory=list)
    message: Optional[str] = None
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class CommentResult:
    """Result of a comment operation."""

    success: bool
    comment_id: Optional[str] = None  # GitHub comment ID
    comment_url: Optional[str] = None  # HTML URL to comment
    issue_number: Optional[int] = None
    closed: Optional[bool] = None  # True if issue was closed
    labels_added: Optional[List[str]] = None  # Labels that were added
    duration_ms: Optional[float] = None
    error: Optional[str] = None


@dataclass
class CompleteResult:
    """Result of a complete operation."""

    success: bool
    issue_number: int
    duration_ms: float
    time_range: Optional[Tuple[str, str]] = None
    error: Optional[str] = None
    log_updated: bool = False
    project_updated: bool = False


@dataclass
class SearchFilter:
    """Search filter specification."""

    query: Optional[str] = None
    status: Optional[str] = None  # Project column
    labels: List[str] = field(default_factory=list)
    priority: Optional[str] = None
    energy: Optional[str] = None
    type: Optional[str] = None
    state: str = "open"  # open, closed, all
    limit: int = 50


@dataclass
class SearchResult:
    """Result of a search operation."""

    success: bool
    issues: List[GithubIssue]
    count: int
    duration_ms: float
    filter_used: SearchFilter
    formatted_output: str = ""
    error: Optional[str] = None


@dataclass
class GPWKConfig:
    """GPWK configuration."""

    # GitHub
    github_token: str
    github_repo: str  # "owner/repo"
    github_project_id: str
    github_project_number: int

    # Field IDs
    status_field_id: str
    type_field_id: str
    priority_field_id: str
    energy_field_id: str

    # Field option IDs
    status_options: dict  # {"inbox": "f75ad846", "inprogress": "47fc9ee4", "done": "98236657"}
    type_options: dict  # {"task": "d7fb4fc4", "ai-task": "24aa72b8", ...}
    priority_options: dict  # {"high": "ee378458", "medium": "1561cb05", "low": "15ce78d1"}
    energy_options: dict  # {"deep": "00040b3d", "shallow": "5b207a17", "quick": "d211b9ba"}

    # OpenTelemetry
    otlp_endpoint: str = "http://localhost:4317"
    service_name: str = "gpwk"

    # Paths
    logs_dir: str = "gpwk/logs"
    config_file: str = "gpwk/memory/github-config.md"
