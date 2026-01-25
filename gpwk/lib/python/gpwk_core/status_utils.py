"""Status normalization utilities for GPWK.

This module provides bidirectional normalization between:
- User input (any case: "today", "Today", "TODAY")
- GitHub API values (capitalized: "Today", "Inbox", "Done")
- Canonical keys (lowercase: "today", "inbox", "done")

The normalization layer ensures case-insensitive status handling throughout GPWK.
"""

from typing import Optional

# Canonical status names (lowercase, match config keys)
CANONICAL_STATUS_NAMES = {
    "inbox": "inbox",
    "today": "today",
    "week": "week",  # Maps to GitHub's "This Week"
    "backlog": "backlog",
    "review": "review",
    "done": "done",
}

# Map GitHub display names to canonical keys
# GitHub returns these exact strings (with capitalization/spacing)
GITHUB_TO_CANONICAL = {
    "Inbox": "inbox",
    "Today": "today",
    "This Week": "week",
    "Backlog": "backlog",
    "Review": "review",
    "Done": "done",
}

# Map canonical keys to GitHub display names
CANONICAL_TO_GITHUB = {v: k for k, v in GITHUB_TO_CANONICAL.items()}

# User input aliases (all lowercase)
# These provide flexibility in what users can type
STATUS_ALIASES = {
    "inbox": "inbox",
    "today": "today",
    "week": "week",
    "thisweek": "week",       # "thisweek" → "week"
    "this week": "week",      # "this week" → "week"
    "backlog": "backlog",
    "review": "review",
    "done": "done",
    "progress": "today",      # Legacy alias
    "inprogress": "today",    # Legacy alias
    "in progress": "today",   # Legacy alias
}


def normalize_status_input(user_input: str) -> Optional[str]:
    """
    Normalize user input to canonical status key.

    Handles case variations and aliases, converting user-friendly
    input into the canonical lowercase key used throughout GPWK.

    Args:
        user_input: Status from user (e.g., "TODAY", "This Week", "thisweek")

    Returns:
        Canonical key (e.g., "today", "week") or None if invalid

    Examples:
        >>> normalize_status_input("TODAY")
        "today"
        >>> normalize_status_input("This Week")
        "week"
        >>> normalize_status_input("thisweek")
        "week"
        >>> normalize_status_input("progress")
        "today"
        >>> normalize_status_input("invalid")
        None
    """
    if not user_input:
        return None

    normalized = user_input.lower().strip()
    return STATUS_ALIASES.get(normalized)


def normalize_github_status(github_status: str) -> Optional[str]:
    """
    Normalize GitHub API status to canonical key.

    Converts GitHub's capitalized status names (e.g., "Today", "This Week")
    into canonical lowercase keys (e.g., "today", "week").

    Args:
        github_status: Status from GitHub API (e.g., "Today", "This Week")

    Returns:
        Canonical key (e.g., "today", "week") or None if unknown

    Examples:
        >>> normalize_github_status("Today")
        "today"
        >>> normalize_github_status("This Week")
        "week"
        >>> normalize_github_status("Done")
        "done"
        >>> normalize_github_status("Unknown")
        None
    """
    if not github_status:
        return None

    return GITHUB_TO_CANONICAL.get(github_status)


def get_display_name(canonical_key: str) -> Optional[str]:
    """
    Get GitHub display name from canonical key.

    Args:
        canonical_key: Canonical status key (e.g., "today", "week")

    Returns:
        GitHub display name (e.g., "Today", "This Week") or None

    Examples:
        >>> get_display_name("today")
        "Today"
        >>> get_display_name("week")
        "This Week"
        >>> get_display_name("invalid")
        None
    """
    return CANONICAL_TO_GITHUB.get(canonical_key)


def compare_status(github_status: str, user_filter: str) -> bool:
    """
    Case-insensitive status comparison.

    Compares a status from GitHub (capitalized) with a user's filter input
    (any case) by normalizing both to canonical keys.

    Args:
        github_status: Status from GitHub API (e.g., "Today", "Inbox")
        user_filter: User's filter input (e.g., "today", "inbox", "TODAY")

    Returns:
        True if they represent the same status, False otherwise

    Examples:
        >>> compare_status("Today", "today")
        True
        >>> compare_status("Inbox", "INBOX")
        True
        >>> compare_status("This Week", "thisweek")
        True
        >>> compare_status("Today", "done")
        False
    """
    if not github_status or not user_filter:
        return False

    github_canonical = normalize_github_status(github_status)
    user_canonical = normalize_status_input(user_filter)

    return github_canonical == user_canonical and github_canonical is not None


def is_backward_move(from_status: str, to_status: str) -> bool:
    """
    Check if moving from_status to to_status is a backward move.

    Determines if a status transition moves backwards in the workflow,
    which may indicate an unintended action (e.g., moving a Done task back to Today).

    Workflow order: Inbox → Today → This Week → Backlog → Review → Done

    Args:
        from_status: Current status (GitHub format or canonical)
        to_status: Target status (user input format or canonical)

    Returns:
        True if moving backwards in workflow, False otherwise

    Examples:
        >>> is_backward_move("Done", "today")
        True
        >>> is_backward_move("Today", "done")
        False
        >>> is_backward_move("Review", "backlog")
        True
        >>> is_backward_move("Inbox", "today")
        False
    """
    # Define workflow order (lower index = earlier in workflow)
    workflow_order = ["inbox", "today", "week", "backlog", "review", "done"]

    # Normalize both statuses to canonical keys
    from_canonical = normalize_github_status(from_status) or normalize_status_input(from_status)
    to_canonical = normalize_status_input(to_status)

    if not from_canonical or not to_canonical:
        return False

    try:
        from_idx = workflow_order.index(from_canonical)
        to_idx = workflow_order.index(to_canonical)
        return to_idx < from_idx
    except ValueError:
        # Status not in workflow order, can't determine
        return False
