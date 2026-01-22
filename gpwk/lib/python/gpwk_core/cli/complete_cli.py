#!/usr/bin/env python3
"""CLI entry point for gpwk-complete command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import (
    load_config,
    setup_telemetry,
    shutdown_telemetry
)
from gpwk_core.commands.complete import complete_command


def main():
    """Main entry point for gpwk-complete command."""
    # Parse arguments
    if len(sys.argv) < 2:
        print("Usage: gpwk-complete ISSUE_NUMBER [--from TIME] [--to TIME] [--comment TEXT]", file=sys.stderr)
        print("\nExamples:", file=sys.stderr)
        print("  gpwk-complete 113", file=sys.stderr)
        print("  gpwk-complete 114 --from '10:45 PM' --to '11:00 PM'", file=sys.stderr)
        print("  gpwk-complete 115 --from '22:00' --to '23:00'", file=sys.stderr)
        print("  gpwk-complete 116 --comment 'Fixed authentication bug'", file=sys.stderr)
        print("  gpwk-complete 117 --from '14:30' --to '16:00' --comment 'Completed task'", file=sys.stderr)
        shutdown_telemetry()
        sys.exit(1)

    # Parse issue number
    try:
        issue_number = int(sys.argv[1])
    except ValueError:
        print(f"✗ Error: Invalid issue number '{sys.argv[1]}'", file=sys.stderr)
        print("  Issue number must be an integer", file=sys.stderr)
        shutdown_telemetry()
        sys.exit(1)

    # Parse optional flags
    time_from = None
    time_to = None
    comment = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--from" and i + 1 < len(sys.argv):
            time_from = sys.argv[i + 1]
            i += 2
        elif arg == "--to" and i + 1 < len(sys.argv):
            time_to = sys.argv[i + 1]
            i += 2
        elif arg == "--comment" and i + 1 < len(sys.argv):
            comment = sys.argv[i + 1]
            i += 2
        else:
            print(f"✗ Error: Unknown argument '{arg}'", file=sys.stderr)
            shutdown_telemetry()
            sys.exit(1)

    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Run complete command
        result = complete_command(
            issue_number=issue_number,
            time_from=time_from,
            time_to=time_to,
            comment=comment,
            config=config
        )

        # Display result
        if result.success:
            print(f"✓ Completed: #{result.issue_number}")
            print(f"  Duration: {result.duration_ms:.0f}ms")
            if result.time_range:
                print(f"  Time: {result.time_range[0]} - {result.time_range[1]}")
            if result.log_updated:
                print(f"  ✓ Daily log updated")
            if result.project_updated:
                print(f"  ✓ Project status updated to Done")
            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Complete failed: {result.error}", file=sys.stderr)
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
