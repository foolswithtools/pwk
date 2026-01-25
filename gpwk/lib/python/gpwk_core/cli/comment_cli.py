#!/usr/bin/env python3
"""CLI entry point for gpwk-comment command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import (
    load_config,
    setup_telemetry,
    shutdown_telemetry
)
from gpwk_core.commands import CommentCommand


def parse_arguments():
    """Parse command line arguments."""
    args = sys.argv[1:]

    if not args:
        print("Usage: gpwk-comment <issue-number> [body] [--close] [--label <label>]", file=sys.stderr)
        print("", file=sys.stderr)
        print("Examples:", file=sys.stderr)
        print("  gpwk-comment 92 'This is a comment'", file=sys.stderr)
        print("  echo 'Comment from stdin' | gpwk-comment 92", file=sys.stderr)
        print("  gpwk-comment 92 'Done!' --close", file=sys.stderr)
        print("  gpwk-comment 92 'Complete' --label status:ai-complete --close", file=sys.stderr)
        return None

    try:
        issue_number = int(args[0])
    except ValueError:
        print(f"Error: Invalid issue number: {args[0]}", file=sys.stderr)
        return None

    labels = []
    close_issue = False
    body = None

    i = 1
    while i < len(args):
        if args[i] == "--close":
            close_issue = True
            i += 1
        elif args[i] == "--label":
            if i + 1 < len(args):
                labels.append(args[i + 1])
                i += 2
            else:
                print("Error: --label requires a value", file=sys.stderr)
                return None
        elif body is None:
            body = args[i]
            i += 1
        else:
            print(f"Error: unexpected argument: {args[i]}", file=sys.stderr)
            return None

    # If no body provided via args, check for stdin content
    if body is None:
        # Check if stdin was captured by bash wrapper
        stdin_content = os.environ.get("GPWK_STDIN_CONTENT", "").strip()
        if stdin_content:
            body = stdin_content
        else:
            print("Error: comment body required (provide as argument or via stdin)", file=sys.stderr)
            return None

    return {
        "issue_number": issue_number,
        "body": body,
        "close": close_issue,
        "labels": labels if labels else None
    }


def main():
    """Main entry point for gpwk-comment command."""
    # Parse arguments
    parsed = parse_arguments()
    if parsed is None:
        shutdown_telemetry()
        sys.exit(1)

    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Create command instance
        comment_cmd = CommentCommand(config)

        # Execute comment command
        result = comment_cmd.comment(
            issue_number=parsed["issue_number"],
            body=parsed["body"],
            close=parsed["close"],
            labels=parsed["labels"]
        )

        # Display result
        if result.success:
            print(f"✓ Comment added to issue #{result.issue_number}")
            print(f"  Comment ID: {result.comment_id}")
            print(f"  URL: {result.comment_url}")

            if result.labels_added:
                print(f"  Labels added: {', '.join(result.labels_added)}")

            if result.closed:
                print(f"  Issue closed: Yes")

            if result.duration_ms:
                print(f"  Duration: {result.duration_ms:.0f}ms")

            print()
            print("✅ Full telemetry captured 📊")
            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Comment failed: {result.error}", file=sys.stderr)
            shutdown_telemetry()
            sys.exit(1)

    except FileNotFoundError as e:
        print(f"✗ Configuration error: {e}", file=sys.stderr)
        print("  Run /gpwk.setup first to configure GPWK", file=sys.stderr)
        shutdown_telemetry()
        sys.exit(1)

    except Exception as e:
        print(f"✗ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        shutdown_telemetry()
        sys.exit(1)


if __name__ == "__main__":
    main()
