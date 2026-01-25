#!/usr/bin/env python3
"""CLI entry point for gpwk-triage command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.triage import TriageCommand


def main():
    """Main entry point for gpwk-triage command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        issue_number = None
        target_status = None
        auto = False
        close_mode = False
        review_mode = False
        issue_numbers = []

        args = sys.argv[1:]

        if "--auto" in args:
            auto = True
        elif "--review" in args:
            # Format: --review 42,56 or --review 42-56 or --review 42 56
            review_mode = True
            review_idx = args.index("--review")

            if review_idx + 1 < len(args):
                review_args = args[review_idx + 1:]

                # Parse issue numbers (same logic as --close)
                for arg in review_args:
                    if "-" in arg and arg.replace("-", "").isdigit():
                        parts = arg.split("-")
                        if len(parts) == 2:
                            start = int(parts[0])
                            end = int(parts[1])
                            issue_numbers.extend(range(start, end + 1))
                    elif "," in arg:
                        issue_numbers.extend([int(n.strip()) for n in arg.split(",")])
                    else:
                        try:
                            issue_numbers.append(int(arg.strip("#")))
                        except ValueError:
                            print(f"✗ Invalid issue number: {arg}", file=sys.stderr)
                            shutdown_telemetry()
                            sys.exit(1)

            if not issue_numbers:
                print("✗ No issue numbers provided after --review", file=sys.stderr)
                print("  Usage: gpwk-triage --review 42,56", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        elif "--close" in args:
            # Format: --close 49-54 or --close 49,50,51 or --close 49 50 51
            close_mode = True
            close_idx = args.index("--close")

            if close_idx + 1 < len(args):
                # Get remaining args after --close
                close_args = args[close_idx + 1:]

                # Parse issue numbers
                for arg in close_args:
                    # Range: 49-54
                    if "-" in arg and arg.replace("-", "").isdigit():
                        parts = arg.split("-")
                        if len(parts) == 2:
                            start = int(parts[0])
                            end = int(parts[1])
                            issue_numbers.extend(range(start, end + 1))
                    # Comma-separated: 49,50,51
                    elif "," in arg:
                        issue_numbers.extend([int(n.strip()) for n in arg.split(",")])
                    # Single number: 49
                    else:
                        try:
                            issue_numbers.append(int(arg.strip("#")))
                        except ValueError:
                            print(f"✗ Invalid issue number: {arg}", file=sys.stderr)
                            shutdown_telemetry()
                            sys.exit(1)

            if not issue_numbers:
                print("✗ No issue numbers provided after --close", file=sys.stderr)
                print("  Usage: gpwk-triage --close 49-54", file=sys.stderr)
                print("  Usage: gpwk-triage --close 49,50,51,52", file=sys.stderr)
                print("  Usage: gpwk-triage --close 49 50 51 52", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        elif len(args) >= 2:
            # Format: #123 today
            issue_arg = args[0]
            target_status = args[1]

            # Parse issue number
            if issue_arg.startswith("#"):
                try:
                    issue_number = int(issue_arg[1:])
                except ValueError:
                    print(f"✗ Invalid issue number: {issue_arg}", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)
            else:
                try:
                    issue_number = int(issue_arg)
                except ValueError:
                    print(f"✗ Invalid issue number: {issue_arg}", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)

        # Run triage command
        triage = TriageCommand(config)

        if review_mode:
            # Review issues and provide recommendations
            result = triage.review_issues(issue_numbers)
        elif close_mode:
            # Review and close issues
            result = triage.review_and_close_issues(issue_numbers)
        else:
            # Regular triage
            result = triage.triage(
                issue_number=issue_number,
                target_status=target_status,
                auto=auto
            )

        # Display result
        if result.success:
            if result.recommendations:
                # Display review recommendations
                print(f"🔍 Issue Review Complete")
                print()
                print(f"Reviewed {len(result.recommendations)} issues:")
                print("═" * 70)

                for rec in result.recommendations:
                    num = rec.get("number")
                    title = rec.get("title", "")
                    action = rec.get("action", "review")
                    recommendation = rec.get("recommendation", "")
                    is_test = rec.get("is_test", False)
                    status = rec.get("status", "")

                    # Action icon
                    if action == "close":
                        icon = "❌"
                        action_text = "CLOSE"
                    elif action == "keep":
                        icon = "✅"
                        action_text = "KEEP"
                    elif action == "skip":
                        icon = "⏭️ "
                        action_text = "SKIP"
                    else:
                        icon = "🔍"
                        action_text = "REVIEW"

                    print(f"{icon} #{num} [{action_text}]")
                    if title:
                        print(f"   {title}")
                    print(f"   → {recommendation}")
                    if is_test:
                        print(f"   💡 Test issue detected")
                    if status == "CLOSED":
                        print(f"   ℹ️  Already closed")
                    print()

                print("═" * 70)

                # Summary by action
                close_count = sum(1 for r in result.recommendations if r.get("action") == "close")
                keep_count = sum(1 for r in result.recommendations if r.get("action") == "keep")
                review_count = sum(1 for r in result.recommendations if r.get("action") == "review")

                print()
                print("Summary:")
                if close_count:
                    print(f"  ❌ Close: {close_count} issues")
                if keep_count:
                    print(f"  ✅ Keep: {keep_count} issues")
                if review_count:
                    print(f"  🔍 Manual review: {review_count} issues")

                if result.duration_ms:
                    print()
                    print(f"Duration: {result.duration_ms:.0f}ms | Full telemetry captured 📊")

                # Suggest next action
                if close_count:
                    close_numbers = [r["number"] for r in result.recommendations if r.get("action") == "close"]
                    print()
                    print("Next step:")
                    if len(close_numbers) <= 3:
                        print(f"  gpwk/bin/gpwk-triage --close {','.join(map(str, close_numbers))}")
                    else:
                        print(f"  gpwk/bin/gpwk-triage --close {close_numbers[0]}-{close_numbers[-1]}")

            elif result.closed_issues:
                # Display closed issues
                print(f"✓ Issue Review & Closure Complete")
                print()
                print(f"Closed {len(result.closed_issues)} issues:")
                print("─" * 60)
                for issue in result.closed_issues:
                    print(f"  ✓ #{issue['number']} - {issue['title']}")
                print("─" * 60)

                if result.failed_issues:
                    print()
                    print(f"⚠️  Failed to close {len(result.failed_issues)} issues:")
                    for issue_num, error in result.failed_issues:
                        print(f"  ✗ #{issue_num} - {error}")

                if result.duration_ms:
                    print()
                    print(f"Duration: {result.duration_ms:.0f}ms")
                    print(f"Trace ID in telemetry for observability")

                print()
                print("All closures include comments and full telemetry 🎯")

            elif result.inbox_items:
                # Show inbox
                print(f"📥 Inbox Triage")
                print()
                print(f"INBOX ({len(result.inbox_items)} items)")
                print("─" * 60)

                for item in result.inbox_items:
                    # item is a dict from gh project item-list
                    if isinstance(item, dict):
                        content = item.get("content", {})
                        if isinstance(content, dict):
                            number = content.get("number", "?")
                            title = content.get("title", "Untitled")
                        else:
                            number = "?"
                            title = str(item.get("title", "Untitled"))

                        # Get labels from content
                        labels_list = []
                        if isinstance(content, dict):
                            labels_data = content.get("labels", [])
                            if isinstance(labels_data, list):
                                labels_list = [label.get("name", "") if isinstance(label, dict) else str(label)
                                             for label in labels_data]

                        # Extract metadata
                        priority = next((l.split(":")[1] for l in labels_list if isinstance(l, str) and l.startswith("priority:")), "-")
                        energy = next((l.split(":")[1] for l in labels_list if isinstance(l, str) and l.startswith("energy:")), "-")
                        type_label = next((l for l in labels_list if isinstance(l, str) and l.startswith("pwk:")), "")

                        print(f"#{number} [{type_label}] {title}")
                        print(f"     Priority: {priority} | Energy: {energy}")
                        print()

                print("─" * 60)
                print()
                print("Commands:")
                print("  gpwk-triage #123 today     Move to Today")
                print("  gpwk-triage #123 week      Move to This Week")
                print("  gpwk-triage #123 backlog   Move to Backlog")
                print("  gpwk-triage --auto         Auto-triage all")

            elif result.items_moved > 0:
                print(f"✓ {result.message}")
                if result.duration_ms:
                    print(f"  Duration: {result.duration_ms:.0f}ms")
                print()
                print("  Run /gpwk.plan today to see updated plan")
            else:
                print(f"✓ {result.message}")

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Triage failed: {result.error}", file=sys.stderr)
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
