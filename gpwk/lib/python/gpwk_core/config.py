"""Configuration management for GPWK."""

import os
import re
from pathlib import Path
from typing import Optional

from .models import GPWKConfig


def load_config(config_file: Optional[str] = None) -> GPWKConfig:
    """
    Load GPWK configuration from github-config.md file.

    Args:
        config_file: Path to config file, defaults to gpwk/memory/github-config.md

    Returns:
        GPWKConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required fields are missing
    """
    if config_file is None:
        # Find git root directory
        import subprocess
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=True
            )
            git_root = Path(result.stdout.strip())
            config_file = str(git_root / "gpwk" / "memory" / "github-config.md")
        except (subprocess.CalledProcessError, FileNotFoundError):
            config_file = "gpwk/memory/github-config.md"

    config_path = Path(config_file)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_file}\n"
            "Run /gpwk.setup first to create configuration."
        )

    content = config_path.read_text()

    # Parse repository info
    repo_match = re.search(r"- \*\*Name\*\*: (.+)", content)
    owner_match = re.search(r"- \*\*Owner\*\*: (.+)", content)

    if not repo_match or not owner_match:
        raise ValueError("Could not parse repository name/owner from config")

    repo_name = repo_match.group(1).strip()
    owner = owner_match.group(1).strip()
    github_repo = f"{owner}/{repo_name}"

    # Parse project info
    project_number_match = re.search(r"- \*\*Number\*\*: (\d+)", content)
    project_id_match = re.search(r"- \*\*ID\*\*: (.+)", content)

    if not project_number_match or not project_id_match:
        raise ValueError("Could not parse project number/ID from config")

    project_number = int(project_number_match.group(1))
    project_id = project_id_match.group(1).strip()

    # Parse field IDs
    status_field_match = re.search(r"- \*\*Status\*\*: (.+)", content)
    type_field_match = re.search(r"- \*\*Type\*\*: (.+)", content)
    priority_field_match = re.search(r"- \*\*Priority\*\*: (.+)", content)
    energy_field_match = re.search(r"- \*\*Energy\*\*: (.+)", content)

    if not all([status_field_match, type_field_match, priority_field_match, energy_field_match]):
        raise ValueError("Could not parse field IDs from config")

    status_field_id = status_field_match.group(1).strip()
    type_field_id = type_field_match.group(1).strip()
    priority_field_id = priority_field_match.group(1).strip()
    energy_field_id = energy_field_match.group(1).strip()

    # Parse field options
    def parse_options(section_name: str) -> dict:
        """Parse option IDs from a field section."""
        options = {}
        # Find the section
        section_match = re.search(
            rf"- \*\*{section_name}\*\*:.*?\n((?:  - Options:.*?\n)*)",
            content,
            re.MULTILINE | re.DOTALL
        )
        if section_match:
            options_text = section_match.group(1)
            # Parse "name (id)" format - handles hyphens in names like "ai-task", "work-item"
            for match in re.finditer(r"([\w-]+)\s*\((\w+)\)", options_text):
                option_name = match.group(1)
                option_id = match.group(2)
                options[option_name.lower()] = option_id

        return options

    status_options = parse_options("Status")
    type_options = parse_options("Type")
    priority_options = parse_options("Priority")
    energy_options = parse_options("Energy")

    # Map status options to expected names (lowercase keys)
    status_mapping = {
        "inbox": "inbox",
        "today": "today",
        "this week": "week",      # Maps "This Week" to canonical "week"
        "thisweek": "week",        # Support "thisweek" variant
        "backlog": "backlog",
        "review": "review",
        "done": "done",
        # Legacy mappings
        "todo": "inbox",
        "in progress": "today"     # Legacy: map "in progress" to "today"
    }
    mapped_status_options = {}
    for k, v in status_options.items():
        mapped_key = status_mapping.get(k, k)
        mapped_status_options[mapped_key] = v

    # Map type options
    type_mapping = {
        "task": "task",
        "ai-task": "ai-task",
        "aitask": "ai-task",
        "work-item": "work-item",
        "workitem": "work-item",
        "capture": "capture"
    }
    mapped_type_options = {}
    for k, v in type_options.items():
        mapped_key = type_mapping.get(k, k)
        mapped_type_options[mapped_key] = v

    # Get GitHub token from environment
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        # Try to get from gh CLI
        import subprocess
        try:
            result = subprocess.run(
                ["gh", "auth", "token"],
                capture_output=True,
                text=True,
                check=True
            )
            github_token = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise ValueError(
                "GitHub token not found. Set GITHUB_TOKEN environment variable "
                "or authenticate with `gh auth login`"
            )

    # Get OTLP endpoint from environment or use default
    otlp_endpoint = os.environ.get("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

    # Set logs directory to absolute path
    logs_dir = str(config_path.parent.parent / "logs")

    return GPWKConfig(
        github_token=github_token,
        github_repo=github_repo,
        github_project_id=project_id,
        github_project_number=project_number,
        status_field_id=status_field_id,
        type_field_id=type_field_id,
        priority_field_id=priority_field_id,
        energy_field_id=energy_field_id,
        status_options=mapped_status_options,
        type_options=mapped_type_options,
        priority_options=priority_options,
        energy_options=energy_options,
        otlp_endpoint=otlp_endpoint,
        logs_dir=logs_dir,
    )
