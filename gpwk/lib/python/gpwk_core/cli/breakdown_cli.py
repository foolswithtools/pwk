#!/usr/bin/env python3
"""CLI entry point for gpwk-breakdown command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.breakdown import BreakdownCommand


def main():
    """Main entry point for gpwk-breakdown command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        args = sys.argv[1:]

        if not args:
            # Check if stdin was provided
            stdin_content = os.environ.get("GPWK_STDIN_CONTENT", "").strip()
            if stdin_content:
                work_description = stdin_content
            else:
                print("✗ No work description provided", file=sys.stderr)
                print("", file=sys.stderr)
                print("Usage:", file=sys.stderr)
                print("  gpwk-breakdown \"work description\"", file=sys.stderr)
                print("  gpwk-breakdown #123  # breakdown existing issue", file=sys.stderr)
                print("", file=sys.stderr)
                print("Examples:", file=sys.stderr)
                print("  gpwk-breakdown \"Implement authentication system\"", file=sys.stderr)
                print("  cat requirements.md | gpwk-breakdown", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)
        else:
            # Get work description (join all args)
            work_description = " ".join(args)

        # Run breakdown command
        breakdown = BreakdownCommand(config)
        result = breakdown.breakdown(work_description)

        # Display result
        if result.get("success"):
            parent = result.get("parent_issue", {})
            sub_issues = result.get("sub_issues", [])
            phases = result.get("phases", [])

            print("✓ Work Item Breakdown Complete")
            print()
            print(f"Parent Issue: #{parent['number']} - {parent['title']}")
            print(f"URL: {parent['url']}")
            print()
            print(f"Created {len(sub_issues)} sub-issues across {len(phases)} phases:")
            print("─" * 70)

            # Group by phase
            for phase_name in phases:
                phase_issues = [si for si in sub_issues if si["phase"] == phase_name]
                print()
                print(f"  {phase_name}")

                for si in phase_issues:
                    print(f"    #{si['number']} - {si['title']} {si['type']}")

            print()
            print("─" * 70)
            print()
            print("Summary:")
            ai_count = sum(1 for si in sub_issues if si["type"] == "[AI]")
            personal_count = sum(1 for si in sub_issues if si["type"] == "[P]")
            print(f"  • {len(sub_issues)} total tasks")
            print(f"  • {ai_count} AI-delegatable tasks")
            print(f"  • {personal_count} personal tasks")
            print()
            print("Next steps:")
            print(f"  • Run /gpwk.triage to schedule tasks")
            print(f"  • Run /gpwk.delegate to execute AI tasks")
            print()

            if result.get("duration_ms"):
                print(f"Duration: {result.get('duration_ms'):.0f}ms | Full telemetry captured 📊")

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Breakdown failed: {result.get('error')}", file=sys.stderr)
            if result.get("duration_ms"):
                print(f"  Duration: {result.get('duration_ms'):.0f}ms", file=sys.stderr)
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
