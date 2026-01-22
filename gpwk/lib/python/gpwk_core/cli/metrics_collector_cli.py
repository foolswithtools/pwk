#!/usr/bin/env python3
"""CLI entry point for gpwk-metrics-collector command."""

import sys
import os

# Add parent directory to path to import gpwk_core
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lib", "python"))

from gpwk_core import load_config, setup_telemetry, shutdown_telemetry
from gpwk_core.metrics_collector import run_collector_loop


def main():
    """Run metrics collector daemon."""
    # Parse interval argument
    interval = 60  # Default: 60 seconds
    if len(sys.argv) > 1:
        try:
            interval = int(sys.argv[1])
        except ValueError:
            print(f"Usage: gpwk-metrics-collector [interval_seconds]", file=sys.stderr)
            print(f"Example: gpwk-metrics-collector 60  # Collect every 60 seconds", file=sys.stderr)
            shutdown_telemetry()
            sys.exit(1)

    try:
        # Load configuration
        config = load_config()

        # Setup OpenTelemetry
        setup_telemetry(config)

        print(f"Starting GPWK metrics collector (interval: {interval}s)")
        print(f"Querying: {config.github_repo}")
        print(f"Logs: {config.logs_dir}")
        print(f"Press Ctrl+C to stop")
        print()

        # Run collector loop
        run_collector_loop(config, interval_seconds=interval)

    except KeyboardInterrupt:
        print("\nStopped by user")
        shutdown_telemetry()
        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        shutdown_telemetry()
        sys.exit(1)


if __name__ == "__main__":
    main()
