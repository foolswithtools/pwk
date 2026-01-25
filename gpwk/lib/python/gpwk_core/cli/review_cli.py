#!/usr/bin/env python3
"""CLI entry point for gpwk-review command."""

import sys
import os
from datetime import date, datetime

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.review import ReviewCommand


def main():
    """Main entry point for gpwk-review command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        review_date = None
        quick = False
        full = True

        args = sys.argv[1:]

        if "--quick" in args:
            quick = True
            full = False
        elif "--full" in args:
            full = True
            quick = False

        # Check for date argument
        for arg in args:
            if arg not in ["--quick", "--full"]:
                # Try to parse as date
                try:
                    review_date = datetime.strptime(arg, "%Y-%m-%d").date()
                except ValueError:
                    print(f"✗ Invalid date format: {arg} (expected YYYY-MM-DD)", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)

        # Run review command
        review = ReviewCommand(config)
        result = review.review(
            review_date=review_date,
            quick=quick,
            full=full
        )

        # Display result
        if result.success:
            print(f"📊 Daily Review: {result.review_date}")
            print()
            print("═" * 60)
            print()

            # Show completed tasks
            if result.completed_issues:
                print(f"COMPLETED ({result.completed_count})")
                for issue in result.completed_issues:
                    number = issue.get("number", "?")
                    title = issue.get("title", "Untitled")
                    labels = issue.get("labels", [])
                    label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                                 for label in labels]

                    # Identify type
                    type_marker = "P"
                    if "pwk:ai" in label_names:
                        type_marker = "AI"
                    elif "pwk:capture" in label_names:
                        type_marker = "C"

                    print(f"  ✓ #{number} - {title} [{type_marker}]")
                print()
            else:
                print("COMPLETED (0)")
                print("  No issues closed today")
                print()

            # Show remaining tasks
            if result.remaining_issues:
                print(f"NOT COMPLETED ({result.remaining_count})")
                for item in result.remaining_issues[:5]:  # Limit to first 5
                    content = item.get("content", {})
                    number = content.get("number", "?")
                    title = content.get("title", "Untitled")
                    print(f"  → #{number} - {title}")
                if result.remaining_count > 5:
                    print(f"  ... and {result.remaining_count - 5} more")
                print()
            else:
                print("NOT COMPLETED (0)")
                print("  All planned tasks completed!")
                print()

            # Show metrics
            print("METRICS")
            print("  ┌" + "─" * 34 + "┐")
            print(f"  │ Completion Rate    {result.completion_rate:5.1f}%     │")
            print(f"  │ Planned Tasks      {result.completed_count + result.remaining_count:5d}      │")
            print(f"  │ Completed          {result.completed_count:5d}      │")
            print(f"  │ Remaining          {result.remaining_count:5d}      │")
            if result.carryover_issues:
                print(f"  │ Carryover Items    {len(result.carryover_issues):5d}      │")
            print("  └" + "─" * 34 + "┘")
            print()

            # Show carryover warning if needed
            if result.carryover_issues:
                print("CARRYOVER ISSUES")
                for issue in result.carryover_issues:
                    number = issue.get("number", "?")
                    title = issue.get("title", "Untitled")
                    labels = issue.get("labels", [])
                    label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                                 for label in labels]

                    carryover_label = next((l for l in label_names if l.startswith("pwk:c")), "new")
                    print(f"  ⚠ #{number} - {title} [{carryover_label}]")
                print()
                print("  Run /gpwk.carryover to update carryover labels")
                print()

            print("═" * 60)
            print()
            print("✓ Review Complete")
            if result.duration_ms:
                print(f"  Duration: {result.duration_ms:.0f}ms")
            print()

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Review failed: {result.error}", file=sys.stderr)
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
