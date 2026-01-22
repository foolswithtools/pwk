"""GPWK Core - Python library for GitHub Personal Work Kit."""

from .config import load_config
from .models import (
    GPWKConfig,
    ParsedCapture,
    GithubIssue,
    ProjectItem,
    CaptureResult,
    TriageResult,
    DelegateResult,
    ReviewResult,
    PlanResult,
    CompleteResult,
    SearchFilter,
    SearchResult
)
from .parser import GPWKParser
from .github_ops import GithubOperations
from .telemetry import setup_telemetry, get_tracer, get_meter, shutdown_telemetry

__version__ = "1.0.0"

__all__ = [
    "load_config",
    "GPWKConfig",
    "ParsedCapture",
    "GithubIssue",
    "ProjectItem",
    "CaptureResult",
    "TriageResult",
    "DelegateResult",
    "ReviewResult",
    "PlanResult",
    "CompleteResult",
    "SearchFilter",
    "SearchResult",
    "GPWKParser",
    "GithubOperations",
    "setup_telemetry",
    "shutdown_telemetry",
    "get_tracer",
    "get_meter",
]
