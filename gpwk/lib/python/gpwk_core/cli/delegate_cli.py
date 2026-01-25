#!/usr/bin/env python3
"""CLI entry point for gpwk-delegate command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.commands.delegate import DelegateCommand


def main():
    """Main entry point for gpwk-delegate command."""
    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Parse arguments
        issue_number = None
        execute_all = False
        list_only = True  # Default to list
        sync_status = False
        post_result_mode = False
        mark_complete_mode = False
        result_body = None

        args = sys.argv[1:]

        if "--post-result" in args:
            # Post AI result to issue: --post-result #123 "result body"
            post_result_mode = True
            list_only = False
            try:
                idx = args.index("--post-result")
                if idx + 2 < len(args):
                    issue_arg = args[idx + 1]
                    result_body = args[idx + 2]

                    # Parse issue number
                    if issue_arg.startswith("#"):
                        issue_number = int(issue_arg[1:])
                    else:
                        issue_number = int(issue_arg)
                else:
                    print("✗ Usage: gpwk-delegate --post-result #123 \"result body\"", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)
            except (ValueError, IndexError) as e:
                print(f"✗ Invalid --post-result arguments: {e}", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        elif "--mark-complete" in args:
            # Mark issue as AI complete: --mark-complete #123
            mark_complete_mode = True
            list_only = False
            try:
                idx = args.index("--mark-complete")
                if idx + 1 < len(args):
                    issue_arg = args[idx + 1]

                    # Parse issue number
                    if issue_arg.startswith("#"):
                        issue_number = int(issue_arg[1:])
                    else:
                        issue_number = int(issue_arg)
                else:
                    print("✗ Usage: gpwk-delegate --mark-complete #123", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)
            except (ValueError, IndexError) as e:
                print(f"✗ Invalid --mark-complete argument: {e}", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        elif "--sync-status" in args:
            sync_status = True
            list_only = False

        elif "--execute" in args:
            execute_all = True
            list_only = False
            # Check if there's an issue number after --execute
            try:
                exec_idx = args.index("--execute")
                if exec_idx + 1 < len(args):
                    next_arg = args[exec_idx + 1]
                    if next_arg.startswith("#"):
                        issue_number = int(next_arg[1:])
                    else:
                        try:
                            issue_number = int(next_arg)
                        except ValueError:
                            pass
                    if issue_number:
                        execute_all = False
            except (ValueError, IndexError):
                pass

        elif "--list" in args:
            list_only = True

        elif len(args) > 0:
            # Try to parse as issue number
            issue_arg = args[0]
            if issue_arg.startswith("#"):
                try:
                    issue_number = int(issue_arg[1:])
                    list_only = False
                except ValueError:
                    print(f"✗ Invalid issue number: {issue_arg}", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)
            else:
                try:
                    issue_number = int(issue_arg)
                    list_only = False
                except ValueError:
                    print(f"✗ Invalid argument: {issue_arg}", file=sys.stderr)
                    shutdown_telemetry()
                    sys.exit(1)

        # Run delegate command
        delegate = DelegateCommand(config)

        # Handle different operation modes
        if post_result_mode:
            # Post AI result to issue
            success = delegate.post_ai_result(
                issue_number=issue_number,
                result_body=result_body,
                add_ai_complete_label=True
            )
            if success:
                print(f"✓ AI result posted to issue #{issue_number}")
                print(f"  Label added: status:ai-complete")
                shutdown_telemetry()
                sys.exit(0)
            else:
                print(f"✗ Failed to post AI result to issue #{issue_number}", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        elif mark_complete_mode:
            # Mark issue as AI complete
            success = delegate.mark_ai_complete(issue_number)
            if success:
                print(f"✓ Issue #{issue_number} marked as AI complete")
                print(f"  Label added: status:ai-complete")
                shutdown_telemetry()
                sys.exit(0)
            else:
                print(f"✗ Failed to mark issue #{issue_number} as AI complete", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)

        else:
            # Standard delegate workflow
            result = delegate.delegate(
                issue_number=issue_number,
                execute_all=execute_all,
                list_only=list_only,
                sync_status=sync_status
            )

        # Display result (only for standard delegate workflow)
        if result.success:
            if result.ai_tasks:
                # Show AI tasks list
                print("🤖 AI-Delegatable Tasks")
                print()
                print(f"Ready to Execute ({len(result.ai_tasks)} tasks):")
                print("─" * 60)

                for task in result.ai_tasks:
                    number = task.get("number", "?")
                    title = task.get("title", "Untitled")
                    labels = task.get("labels", [])

                    # Extract metadata
                    label_names = [label.get("name", "") if isinstance(label, dict) else str(label)
                                 for label in labels]
                    priority = next((l.split(":")[1] for l in label_names if l.startswith("priority:")), "-")

                    print(f"  #{number} - {title}")
                    print(f"         Priority: {priority}")
                    print()

                print("─" * 60)
                print()
                print("Commands:")
                print("  gpwk-delegate --execute        Execute all tasks")
                print("  gpwk-delegate #123             Execute specific task")
                print("  gpwk-delegate --execute #123   Execute specific task")
                print("  gpwk-delegate --sync-status    Sync AI-complete tasks to Review")
                print()
                print("Helper Commands (called by GitHub Action):")
                print("  gpwk-delegate --post-result #123 \"body\"    Post AI result as comment")
                print("  gpwk-delegate --mark-complete #123         Add ai-complete label")

            elif result.tasks_executed > 0 or result.tasks_failed > 0:
                print(f"✓ {result.message}")
                if result.duration_ms:
                    print(f"  Duration: {result.duration_ms:.0f}ms")
                if result.tasks_executed > 0:
                    print(f"  Tasks executed: {result.tasks_executed}")
                if result.tasks_failed > 0:
                    print(f"  Tasks failed: {result.tasks_failed}")
            else:
                print(f"✓ {result.message}")

            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Delegate failed: {result.error}", file=sys.stderr)
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
