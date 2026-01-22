#!/usr/bin/env python3
"""CLI entry point for gpwk-plan command."""

import sys
import os
from datetime import date, datetime, timedelta

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.plan import PlanCommand


def main():
    """Main entry point for gpwk-plan command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        plan_date = None
        mode = "today"

        args = sys.argv[1:]

        if not args or args[0] == "today":
            mode = "today"
            plan_date = date.today()
        elif args[0] == "tomorrow":
            mode = "tomorrow"
            plan_date = date.today() + timedelta(days=1)
        elif args[0] == "week":
            mode = "week"
            plan_date = date.today()
        else:
            # Try to parse as date
            try:
                plan_date = datetime.strptime(args[0], "%Y-%m-%d").date()
                mode = "specific"
            except ValueError:
                print(f"✗ Invalid argument: {args[0]}", file=sys.stderr)
                print("  Usage: gpwk-plan [today|tomorrow|week|YYYY-MM-DD]", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        # Run plan command
        plan = PlanCommand(config)
        result = plan.plan(
            plan_date=plan_date,
            mode=mode
        )

        # Display result
        if result.success:
            print(f"📅 Daily Plan: {result.plan_date}")
            print()

            # Show carryover items
            if result.carryover_issues:
                print(f"⚠️  Carryover from Yesterday ({len(result.carryover_issues)} items)")
                for issue in result.carryover_issues[:5]:
                    number = issue.get("number", "?")
                    title = issue.get("title", "Untitled")
                    labels = issue.get("labels", [])
                    label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                                 for label in labels]
                    carryover_label = next((l for l in label_names if l.startswith("pwk:c")), "")
                    print(f"  • #{number} - {title} [{carryover_label}]")
                if len(result.carryover_issues) > 5:
                    print(f"  ... and {len(result.carryover_issues) - 5} more")
                print()

            # Show today's plan
            if result.today_issues:
                print(f"📋 Today's Plan ({len(result.today_issues)} tasks)")

                # Group by energy
                deep_work = [i for i in result.today_issues if i.get("energy") == "deep"]
                quick_wins = [i for i in result.today_issues if i.get("energy") == "quick"]
                other = [i for i in result.today_issues if i.get("energy") not in ["deep", "quick"]]

                if deep_work:
                    print("  Deep Work:")
                    for item in deep_work:
                        content = item.get("content", {})
                        number = content.get("number", item.get("number", "?"))
                        title = content.get("title", item.get("title", "Untitled"))
                        print(f"    • #{number} - {title}")

                if other:
                    print("  Regular Tasks:")
                    for item in other[:5]:
                        content = item.get("content", {})
                        number = content.get("number", item.get("number", "?"))
                        title = content.get("title", item.get("title", "Untitled"))
                        print(f"    • #{number} - {title}")
                    if len(other) > 5:
                        print(f"    ... and {len(other) - 5} more")

                if quick_wins:
                    print("  Quick Wins:")
                    for item in quick_wins:
                        content = item.get("content", {})
                        number = content.get("number", item.get("number", "?"))
                        title = content.get("title", item.get("title", "Untitled"))
                        print(f"    • #{number} - {title}")
                print()
            else:
                print("📋 Today's Plan")
                print("  No tasks planned yet. Run /gpwk.triage to move tasks to Today")
                print()

            # Show AI delegation queue
            if result.ai_issues:
                print(f"🤖 AI Delegation Queue ({len(result.ai_issues)} tasks)")
                for issue in result.ai_issues[:3]:
                    number = issue.get("number", "?")
                    title = issue.get("title", "Untitled")
                    print(f"  • #{number} - {title}")
                if len(result.ai_issues) > 3:
                    print(f"  ... and {len(result.ai_issues) - 3} more")
                print()

            # Show log path
            print("─" * 60)
            print()
            if result.log_path:
                print(f"✓ Daily log created: {result.log_path}")
            else:
                print(f"✓ Plan generated")

            if result.duration_ms:
                print(f"  Duration: {result.duration_ms:.0f}ms")
            print()

            # Suggestions
            print("Next steps:")
            if result.ai_issues:
                print("  • Run /gpwk.delegate to execute AI tasks")
            if result.carryover_issues:
                print("  • Consider /gpwk.breakdown for c2+ carryover items")
            print("  • Use /gpwk.capture to track activities throughout the day")
            print()

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Plan failed: {result.error}", file=sys.stderr)
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
