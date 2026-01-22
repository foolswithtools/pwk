#!/usr/bin/env python3
"""CLI entry point for gpwk-search command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import (
    load_config,
    setup_telemetry,
    shutdown_telemetry
)
from gpwk_core.commands.search import search_command, SearchFilter


def main():
    """Main entry point for gpwk-search command."""
    # Parse arguments
    query = None
    status = None
    labels = []
    priority = None
    energy = None
    task_type = None
    state = "open"
    limit = 50
    json_output = False

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--status" and i + 1 < len(sys.argv):
            status = sys.argv[i + 1]
            i += 2
        elif arg == "--label" and i + 1 < len(sys.argv):
            # Split comma-separated labels
            labels.extend(sys.argv[i + 1].split(","))
            i += 2
        elif arg == "--priority" and i + 1 < len(sys.argv):
            priority = sys.argv[i + 1]
            i += 2
        elif arg == "--energy" and i + 1 < len(sys.argv):
            energy = sys.argv[i + 1]
            i += 2
        elif arg == "--type" and i + 1 < len(sys.argv):
            task_type = sys.argv[i + 1]
            i += 2
        elif arg == "--state" and i + 1 < len(sys.argv):
            state = sys.argv[i + 1]
            i += 2
        elif arg == "--limit" and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                print(f"✗ Error: Invalid limit value '{sys.argv[i + 1]}'", file=sys.stderr)
                shutdown_telemetry()
                sys.exit(1)
            i += 2
        elif arg == "--json":
            json_output = True
            i += 1
        elif arg in ["-h", "--help"]:
            print("Usage: gpwk-search [QUERY] [OPTIONS]")
            print("\nOptions:")
            print("  --status <value>      Filter by project column (inbox|today|thisweek|backlog|done|review)")
            print("  --label <value>       Filter by label (comma-separated for OR logic)")
            print("  --priority <value>    Filter by priority (high|medium|low)")
            print("  --energy <value>      Filter by energy (deep|shallow|quick)")
            print("  --type <value>        Filter by type (task|ai-task|personal|capture)")
            print("  --state <value>       Filter by state (open|closed|all, default: open)")
            print("  --limit <N>           Maximum results (default: 50)")
            print("  --json                Output as JSON")
            print("\nExamples:")
            print("  gpwk-search --priority high")
            print("  gpwk-search --label 'pwk:ai'")
            print("  gpwk-search --status today")
            print("  gpwk-search 'rivian'")
            print("  gpwk-search --priority high --energy deep")
            print("  gpwk-search --label 'pwk:ai' --json | jq '.[] | .number'")
            shutdown_telemetry()
            sys.exit(0)
        else:
            # Assume it's a query text
            if query is None:
                query = arg
            else:
                # Concatenate multiple words
                query += " " + arg
            i += 1

    # Create search filter
    search_filter = SearchFilter(
        query=query,
        status=status,
        labels=labels,
        priority=priority,
        energy=energy,
        type=task_type,
        state=state,
        limit=limit
    )

    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        # Run search command
        result = search_command(
            filter=search_filter,
            json_output=json_output,
            config=config
        )

        # Display result
        if result.success:
            print(result.formatted_output)
            shutdown_telemetry()
            sys.exit(0)
        else:
            print(f"✗ Search failed: {result.error}", file=sys.stderr)
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
