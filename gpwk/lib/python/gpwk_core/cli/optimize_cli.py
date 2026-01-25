#!/usr/bin/env python3
"""CLI entry point for gpwk-optimize command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.optimize import OptimizeCommand


def main():
    """Main entry point for gpwk-optimize command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        weeks = 2
        dry_run = False
        auto_apply = False

        args = sys.argv[1:]

        for arg in args:
            if arg == "--dry-run":
                dry_run = True
            elif arg == "--apply":
                auto_apply = True
            elif arg.startswith("--weeks"):
                if "=" in arg:
                    weeks = int(arg.split("=")[1])
                else:
                    # Next arg should be the number
                    idx = args.index(arg)
                    if idx + 1 < len(args):
                        weeks = int(args[idx + 1])

        # Run optimize command
        optimize = OptimizeCommand(config)
        result = optimize.optimize(
            weeks=weeks,
            dry_run=dry_run,
            auto_apply=auto_apply
        )

        # Display result
        if result.success:
            print(f"📊 GPWK Optimization Analysis")
            print()
            print("=" * 70)
            print()

            if result.date_range:
                start_date, end_date = result.date_range
                print(f"Data Period: {start_date} to {end_date} ({result.days_analyzed} days)")
            else:
                print(f"Days Analyzed: {result.days_analyzed}")

            print()
            print(f"Average Completion Rate: {result.avg_completion_rate * 100:.0f}%")
            print(f"Average Carryover: {result.avg_carryover:.1f} tasks/day")
            print()

            if result.recommendations:
                print(f"RECOMMENDATIONS ({len(result.recommendations)})")
                print("-" * 70)

                for i, rec in enumerate(result.recommendations, 1):
                    priority_emoji = "⚠️" if rec.priority == "high" else "📌" if rec.priority == "medium" else "💡"
                    print(f"\n{priority_emoji} {rec.priority.upper()}: {rec.title}")
                    print(f"   Current: {rec.current}")
                    print(f"   Recommended: {rec.recommended}")
                    print(f"   Impact: {rec.impact}")

                print()
                print("-" * 70)

            if result.report_path:
                print(f"\n📄 Full report saved: {result.report_path}")

            if result.applied_changes:
                print(f"\n✅ Applied {len(result.applied_changes)} changes:")
                for change in result.applied_changes:
                    print(f"   • {change}")

                if result.tracking_issue:
                    print(f"\n📋 Tracking issue: #{result.tracking_issue}")

            if dry_run:
                print("\n💡 DRY RUN MODE - No changes applied")
                print("   Remove --dry-run to apply recommendations")

            print()
            print(f"⏱️  Analysis completed in {result.duration_ms:.0f}ms")
            print()

            # Telemetry info
            print("✅ Operation complete with full telemetry")
            print("   View in Grafana: Tempo (traces), Prometheus (metrics), Loki (logs)")

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Optimization failed: {result.error}", file=sys.stderr)
            shutdown_telemetry()
            sys.exit(1)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        shutdown_telemetry()
        sys.exit(1)


if __name__ == "__main__":
    main()
