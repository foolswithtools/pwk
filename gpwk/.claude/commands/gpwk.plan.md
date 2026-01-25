# GPWK Plan

Create a daily or weekly plan by pulling tasks from GitHub and generating a local log with full telemetry.

## Arguments
- `$ARGUMENTS` - `today`, `tomorrow`, `week`, or a specific date (YYYY-MM-DD). Defaults to `today` if empty.

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable with the plan mode. The Python backend handles:
- ✅ Fetching issues from GitHub project
- ✅ Categorizing by status, priority, energy, carryover
- ✅ Applying work principles (daily limits, deep work windows, energy matching)
- ✅ Generating daily log file from template
- ✅ Providing balanced schedule suggestions
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GPWK_ROOT="$SCRIPT_DIR/../.."

# Default to today if no argument provided
MODE="${ARGUMENTS:-today}"

# Call Python backend
"$GPWK_ROOT/bin/gpwk-plan" "$MODE"
```

That's it! The Python backend handles everything automatically.

## Plan Modes

### Daily Planning

**Today (default):**
```bash
/gpwk.plan
# or
/gpwk.plan today
```
Generates plan for today, creates `gpwk/logs/YYYY-MM-DD.md`

**Tomorrow:**
```bash
/gpwk.plan tomorrow
```
Generates plan for tomorrow

**Specific Date:**
```bash
/gpwk.plan 2025-12-25
```
Generates plan for specific date

### Weekly Planning

```bash
/gpwk.plan week
```
Generates weekly overview covering next 7 days, creates `gpwk/logs/YYYY-WXX-week.md`

## What Gets Analyzed

The Python backend fetches and categorizes:

1. **Today Column Issues** - Tasks already scheduled for today
2. **Carryover Issues** - Tasks with `pwk:c1`, `pwk:c2`, `pwk:c3` labels
3. **High Priority Issues** - Tasks with `priority:high` label
4. **AI-Delegatable Issues** - Tasks with `pwk:ai` label
5. **Quick Wins** - Tasks with `energy:quick` label

## Daily Log Structure

The generated log includes:

```markdown
# Daily Log: YYYY-MM-DD

## Carryover from Yesterday
<!-- Issues with pwk:c1+ labels -->

## Today's Plan
### Deep Work Block (suggested: 9:00-11:00)
<!-- Deep focus tasks (~deep energy) -->

### Shallow Work
<!-- Low cognitive load tasks (~shallow) -->

### Quick Wins
<!-- Under 15 min tasks (~quick) -->

## AI Delegation Queue
<!-- Tasks with pwk:ai label -->

## Activity Stream
<!-- Updated throughout the day by /gpwk.capture -->

## Blockers
<!-- Note any blockers -->

## End of Day
<!-- Filled by /gpwk.review -->
```

## Work Principles Applied

The plan respects your configured principles from `gpwk/memory/principles.md`:

- **Daily task limits** (default: 4-6 significant tasks)
- **Deep work windows** (default: morning 9:00-12:00)
- **Energy matching** (deep work in high-energy periods)
- **Carryover warnings** (c2+ tasks flagged for attention)
- **Context switch limits** (max 3 per day)

## Features

### Python Backend Benefits
- **Intelligent scheduling**: Matches task energy to your chronotype
- **Carryover detection**: Warns about stuck tasks
- **Balanced planning**: Prevents overcommitment
- **Full telemetry**: Track planning patterns over time

### Telemetry Collected
- **Traces**: Complete planning flow in Grafana Tempo
- **Metrics**: Plan generation time, task counts, carryover rates
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Date, mode, task counts by category, duration

### Planning Intelligence

The system analyzes:
- How many tasks are in each status column
- Which tasks have been carried over multiple days
- Your recent completion patterns
- Your configured work preferences

And suggests:
- Optimal task ordering (deep work first)
- Warning about overcommitment
- Specific carryover tasks needing breakdown
- AI delegation opportunities

## Examples

**Morning Planning:**
```bash
/gpwk.plan
```
Output:
```
📅 Plan for 2025-12-21

From GitHub Project:
  • 3 tasks in "Today" column
  • 2 carryover items (1 at c2 - consider breakdown)
  • 2 AI-delegatable tasks ready

Suggested Schedule:
  09:00-11:00  Deep work: #27 PowerPoint presentation
  11:00-12:00  Shallow: #23 Contact training team
  14:00-14:30  Quick wins: #39 Update calendar

AI Queue:
  • #18 Research AWS Batch
  • #17 Review Claude Code materials
  Run /gpwk.delegate to execute

Local log created: logs/2025-12-21.md

Tips:
  • #22 has been carried over 2 days - consider /gpwk.breakdown
  • Run /gpwk.triage to move Inbox items to Today
```

**Weekly Planning:**
```bash
/gpwk.plan week
```
Shows all issues across project columns, highlights overdue items, suggests redistribution.

## Integration Points

- **Reads**: `gpwk/memory/principles.md` for work preferences
- **Reads**: `gpwk/memory/goals.md` for long-term objectives
- **Creates**: `gpwk/logs/YYYY-MM-DD.md` daily log files
- **Updates**: GitHub Project status (view only)
- **Feeds**: `/gpwk.delegate` for AI task execution

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

**No issues in "Today" column:**
Run `/gpwk.triage` first to move tasks from Inbox.

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_plan`)
- Metrics: Grafana Prometheus (`gpwk.plan.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)
