# GPWK Triage

Move issues between project columns (Inbox → Today/This Week/Backlog) with full telemetry.

## Arguments
- None required - Interactive triage session

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable for an interactive triage session. The Python backend handles:
- ✅ Fetching all Inbox issues
- ✅ Presenting issues for review with full context
- ✅ Moving issues to appropriate columns
- ✅ Updating project field statuses
- ✅ Respecting daily task limits from principles
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-triage
```

That's it! The Python backend provides an interactive triage interface.

## Triage Workflow

The triage session works through Inbox items:

1. **Fetch Inbox Items** - Gets all issues with Status = "Inbox"
2. **Present Each Issue** - Shows:
   - Issue number and title
   - Labels (type, priority, energy)
   - Creation date
   - Body preview
3. **Prompt for Decision** - Options:
   - `t` - Move to Today
   - `w` - Move to This Week
   - `b` - Move to Backlog
   - `s` - Skip (keep in Inbox)
   - `q` - Quit triage session
4. **Apply Move** - Updates project status field
5. **Respect Limits** - Warns if Today column exceeds daily task limit

## Features

### Python Backend Benefits
- **Interactive prompts**: Clear decision flow
- **Context display**: See full issue details before deciding
- **Limit enforcement**: Warns about overcommitment
- **Bulk operations**: Triage multiple issues efficiently
- **Full telemetry**: Track triage patterns and decision times

### Telemetry Collected
- **Traces**: Complete triage session flow in Grafana Tempo
- **Metrics**: Issues triaged, time per decision, column distribution
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Session duration, decisions made, warnings issued

### Smart Features

- **Daily limit warnings**: Alerts when Today column gets too full
- **Priority highlighting**: High priority issues shown prominently
- **Energy matching**: Suggests columns based on energy labels
- **Carryover awareness**: Flags issues already carried over multiple days

## Project Columns

- **Inbox** - New captures needing triage
- **Today** - Tasks for today (limited by principles)
- **This Week** - Tasks for this week
- **Backlog** - Future tasks, nice-to-haves
- **Done** - Completed (managed by /gpwk.capture and /gpwk.review)

## Example Session

```bash
/gpwk.triage
```

Output:
```
🗂️  GPWK Triage Session

Inbox: 7 items

[1/7] Issue #46: Testing Python telemetry to Grafana Alloy
  Labels: pwk:capture
  Created: 2025-12-20

  Move to: (t)oday, (w)eek, (b)acklog, (s)kip, (q)uit? b
  ✓ Moved to Backlog

[2/7] Issue #47: Test with parentheses (My Dog) and 'quotes' works!
  Labels: pwk:capture
  Created: 2025-12-20

  Move to: (t)oday, (w)eek, (b)acklog, (s)kip, (q)uit? b
  ✓ Moved to Backlog

[3/7] Issue #27: Create PowerPoint with Grafana implementation details
  Labels: pwk:personal, priority:medium
  Created: 2025-12-17
  Due: 2025-12-22 (Monday)

  Move to: (t)oday, (w)eek, (b)acklog, (s)kip, (q)uit? w
  ✓ Moved to This Week

⚠️  Today column now has 4 tasks (limit: 4-6)
  Consider using This Week for lower priority items

Triage complete!
  • Processed: 7 items
  • Today: 1
  • This Week: 1
  • Backlog: 5
  • Duration: 2m 15s
```

## Best Practices

### When to Triage
- **Morning**: Before running `/gpwk.plan`
- **Throughout day**: When new captures accumulate
- **End of day**: During `/gpwk.review` if needed

### Decision Guidelines
- **Today**: Must be done today, aligns with today's priorities
- **This Week**: Important but can wait 1-7 days
- **Backlog**: Good idea but no urgency
- **Skip**: Needs more info or waiting on dependency

### Limit Management
Your principles define daily task limits (default: 4-6 significant tasks)
- Triage warns when approaching limit
- Quick wins (~quick) don't count toward limit
- Consider energy levels when filling Today column

## Integration Points

- **Reads**: `gpwk/memory/principles.md` for task limits
- **Updates**: GitHub Project Status field
- **Feeds**: `/gpwk.plan` (creates plan from Today column)
- **Called by**: `/gpwk.review` (end-of-day cleanup)

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

**No items in Inbox:**
Run `/gpwk.capture` to create tasks first.

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_triage`)
- Metrics: Grafana Prometheus (`gpwk.triage.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)
