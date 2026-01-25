# GPWK Complete

Mark tasks as complete with time tracking, automatic log updates, and full telemetry.

## Arguments
- `ISSUE_NUMBER` - The GitHub issue number to mark as complete (required)
- `--from TIME` - Start time of work (optional, format: "HH:MM" or "HH:MM AM/PM")
- `--to TIME` - End time of work (optional, format: "HH:MM" or "HH:MM AM/PM")
- `--comment TEXT` - Additional completion comment (optional)

## Instructions

**IMPORTANT**: This command uses the Python backend with OpenTelemetry instrumentation.

### How It Works

The Python backend handles task completion consistently:
- ✅ Closes GitHub issue with completion comment
- ✅ Updates project status to "Done"
- ✅ Appends entry to daily log Activity Stream
- ✅ Supports flexible time formats (12h/24h)
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Parse arguments
ISSUE_NUMBER="${1:?Error: Issue number required}"
shift

# Call Python backend with all arguments
gpwk/bin/gpwk-complete "$ISSUE_NUMBER" "$@"
```

## Usage Examples

**Basic completion (no time tracking):**
```bash
/gpwk.complete 113
```
Result: Issue #113 closed, added to log, moved to Done

**With time range (12-hour format):**
```bash
/gpwk.complete 114 --from "10:45 PM" --to "11:00 PM"
```
Result: Issue #114 closed with time range 22:45-23:00 in log

**With time range (24-hour format):**
```bash
/gpwk.complete 115 --from "22:00" --to "23:00"
```
Result: Issue #115 closed with time range in log

**With completion comment:**
```bash
/gpwk.complete 116 --comment "Fixed authentication bug and added tests"
```
Result: Issue #116 closed with custom comment

**With both time and comment:**
```bash
/gpwk.complete 117 --from "14:30" --to "16:00" --comment "Completed PowerPoint presentation"
```
Result: Issue #117 closed with time 14:30-16:00 and custom comment

## What Gets Updated

### 1. GitHub Issue
- **State**: Changed to "closed"
- **Comment**: Posted with completion details
  - Timestamp
  - Time range (if provided)
  - Custom comment (if provided)

### 2. GitHub Project
- **Status Field**: Moved to "Done" column
- Issue remains in project for tracking

### 3. Daily Log
Appends to Activity Stream in `gpwk/logs/YYYY-MM-DD.md`:

```markdown
- HH:MM-HH:MM - Completed #ISSUE: Title ✓
  - Description
  - Task completed
```

If no time range provided:
```markdown
- Completed #ISSUE: Title ✓
  - Description
  - Task completed
```

## Time Format Support

The command intelligently parses various time formats:

| Input | Parsed As | Notes |
|-------|-----------|-------|
| `10:30 PM` | `22:30` | 12-hour with AM/PM |
| `10:30 AM` | `10:30` | Morning time |
| `22:30` | `22:30` | 24-hour format |
| `10:30` | `10:30` | Assumes 24-hour if no AM/PM |
| `2:15 PM` | `14:15` | Single-digit hour OK |

## Error Handling

The command handles edge cases gracefully:

- **Issue not found**: Displays error, suggests checking issue number
- **Issue already closed**: Warns but still updates log
- **Daily log missing**: Warns to run `/gpwk.plan` first, doesn't fail
- **Invalid time format**: Displays error with format examples
- **No time range**: Completes without time tracking (valid)

## Integration Points

- **Reads**: GitHub issue data via GitHub API
- **Writes**: GitHub issue state, project fields, daily log
- **Triggers**: Can be followed by `/gpwk.review` for end-of-day summary
- **Telemetry**: Traces exported to Grafana Tempo, metrics to Prometheus

## Performance

Typical operation: ~500-1000ms
- Fetch issue: ~100-200ms
- Close issue: ~200-300ms
- Update project: ~100-200ms
- Update log: ~50-100ms
- Telemetry overhead: ~50ms

## Telemetry Collected

- **Traces**: Complete operation flow in Grafana Tempo
- **Metrics**: Completion count, duration, error rate
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Issue number, time range, has_comment, duration

## Troubleshooting

**Error: Virtual environment not found**
```bash
cd gpwk/lib/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error: Configuration not found**
Run `/gpwk.setup` first to create GitHub configuration.

**Daily log not updated:**
Check that `gpwk/logs/YYYY-MM-DD.md` exists. Run `/gpwk.plan today` to create it.

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_complete`)
- Metrics: Grafana Prometheus (`gpwk.complete.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)

## Comparison with Manual Approach

**Before (manual):**
```bash
gh issue close 113 --comment "Completed"
# Manually edit daily log
# Manually update project status
# No telemetry
```

**After (gpwk-complete):**
```bash
/gpwk.complete 113 --from "10:30 PM" --to "11:45 PM"
# Everything automated with full observability
```

## See Also

- `/gpwk.capture` - Create tasks
- `/gpwk.review` - End-of-day reflection
- `/gpwk.triage` - Move tasks between columns
- `/gpwk.search` - Find tasks
