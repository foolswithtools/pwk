#!/usr/bin/env python3
"""CLI entry point for gpwk-capture command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import (
    load_config,
    setup_telemetry,
    shutdown_telemetry,
    GPWKParser,
    GithubOperations
)
from gpwk_core.commands.capture import capture_command


def main():
    """Main entry point for gpwk-capture command."""
    # Get capture text from command line arguments or stdin
    if len(sys.argv) < 2:
        # Check if stdin was provided
        stdin_content = os.environ.get("GPWK_STDIN_CONTENT", "").strip()
        if stdin_content:
            capture_text = stdin_content
        else:
            print("Usage: gpwk-capture <capture_text>", file=sys.stderr)
            print("Examples:", file=sys.stderr)
            print("  gpwk-capture 'I took the dog for a walk 9-10 AM'", file=sys.stderr)
            print("  echo 'Research API patterns [AI] !high' | gpwk-capture", file=sys.stderr)
            shutdown_telemetry()
            sys.exit(1)
    else:
        capture_text = " ".join(sys.argv[1:])

    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Run capture command
        result = capture_command(capture_text, config)

        # Display result
        if result.success:
            print(f"✓ Captured: {capture_text[:50]}...")
            print(f"  Issue: #{result.issue_number} ({result.issue_url})")
            print(f"  Duration: {result.duration_ms:.0f}ms")
            print()
            print("  Run /gpwk.triage to move to Today/This Week")
            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Capture failed: {result.error}", file=sys.stderr)
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
