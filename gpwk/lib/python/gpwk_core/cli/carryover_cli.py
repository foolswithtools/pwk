#!/usr/bin/env python3
"""CLI entry point for gpwk-carryover command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.carryover import CarryoverCommand


def main():
    """Main entry point for gpwk-carryover command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        args = sys.argv[1:]
        dry_run = "--dry-run" in args or "-n" in args

        # Run carryover command
        carryover = CarryoverCommand(config)
        result = carryover.carryover(dry_run=dry_run)

        # Display result
        if result.get("success"):
            updates = result.get("updates", [])
            needs_breakdown = result.get("needs_breakdown", [])
            is_dry_run = result.get("dry_run", False)

            if is_dry_run:
                print("🔍 Carryover Preview (Dry Run)")
            else:
                print("✓ Carryover Complete")
            print()

            if not updates:
                print("No incomplete issues to carry over")
                print()
                if result.get("duration_ms"):
                    print(f"Duration: {result.get('duration_ms'):.0f}ms | Full telemetry captured 📊")
                shutdown_telemetry()
                sys.exit(0)

            # Display updates
            print(f"{'Preview:' if is_dry_run else 'Updated:'} {len(updates)} issues")
            print("─" * 70)

            # Group by action
            new_c1 = [u for u in updates if u["action"] == "add_c1"]
            c1_to_c2 = [u for u in updates if u["action"] == "c1_to_c2"]
            c2_to_c3 = [u for u in updates if u["action"] == "c2_to_c3"]
            keep_c3 = [u for u in updates if u["action"] == "keep_c3"]

            if new_c1:
                print()
                print("NEW CARRYOVER (first time)")
                for u in new_c1:
                    print(f"  #{u['issue_number']} - {u['title']}")
                    print(f"         Labels: + {u['new_label']}")

            if c1_to_c2:
                print()
                print("CARRYOVER DAY 2")
                for u in c1_to_c2:
                    print(f"  #{u['issue_number']} - {u['title']}")
                    print(f"         Labels: {u['current_label']} → {u['new_label']}")
                    print(f"         ⚠️  One more carryover triggers breakdown")

            if c2_to_c3:
                print()
                print("CARRYOVER DAY 3+ (Needs Attention)")
                for u in c2_to_c3:
                    print(f"  #{u['issue_number']} - {u['title']}")
                    print(f"         Labels: {u['current_label']} → {u['new_label']}")
                    print(f"         🚨 BREAKDOWN RECOMMENDED")
                    print(f"         Consider: /gpwk.breakdown #{u['issue_number']}")

            if keep_c3:
                print()
                print("ALREADY AT C3 (Still Stuck)")
                for u in keep_c3:
                    print(f"  #{u['issue_number']} - {u['title']}")
                    print(f"         Labels: {u['current_label']} (unchanged)")
                    print(f"         🚨 STILL NEEDS BREAKDOWN")

            print()
            print("─" * 70)
            print()
            print("Summary:")
            if new_c1:
                print(f"  • {len(new_c1)} new carryovers")
            if c1_to_c2:
                print(f"  • {len(c1_to_c2)} at c2 (warning threshold)")
            if c2_to_c3:
                print(f"  • {len(c2_to_c3)} upgraded to c3 (breakdown needed)")
            if keep_c3:
                print(f"  • {len(keep_c3)} stuck at c3 (overdue for breakdown)")

            if needs_breakdown:
                print()
                print("⚠️  Action Required:")
                for issue_num in needs_breakdown:
                    issue = next((u for u in updates if u["issue_number"] == issue_num), None)
                    if issue:
                        print(f"  /gpwk.breakdown #{issue_num}  # {issue['title']}")

            print()
            if result.get("duration_ms"):
                print(f"Duration: {result.get('duration_ms'):.0f}ms | Full telemetry captured 📊")

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Carryover failed: {result.get('error')}", file=sys.stderr)
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
