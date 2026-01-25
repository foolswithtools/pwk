# GPWK Capture

Quick capture of activities, tasks, or thoughts to GitHub Issues with full telemetry.

## Arguments
- `$ARGUMENTS` - The activity or task to capture

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable with the capture text. The Python backend handles:
- ✅ Parsing GPWK notation ([AI], [P], !high, ~deep, etc.)
- ✅ Completion detection (past tense, time ranges)
- ✅ GitHub issue creation (no shell escaping issues!)
- ✅ Project field management with retry logic
- ✅ Daily log updates
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-capture "$ARGUMENTS"
```

That's it! The Python backend handles everything automatically.

## Notation Reference

### Task Type
- `[AI]` → AI-delegatable task (label: `pwk:ai`, Type: `ai-task`)
- `[P]` → Personal/human-only task (label: `pwk:personal`, Type: `task`)
- No bracket → Quick capture needing triage (label: `pwk:capture`, Type: `capture`)

### Priority
- `!high` or `!urgent` → High priority
- `!medium` → Medium priority
- `!low` → Low priority

### Energy
- `~deep` → Requires deep focus
- `~shallow` → Shallow work, low cognitive load
- `~quick` → Quick win, under 15 minutes

### Completion Detection (Automatic)
The Python backend automatically detects completed activities:
- **Past tense verbs**: "I took...", "completed...", "finished..."
- **Time ranges**: "between 9-10 AM", "from 2-3 PM"
- **Explicit markers**: "this is complete", "done"

Completed activities are automatically closed and marked as done.

## Examples

**Simple capture:**
```bash
/gpwk.capture "remember to call John about project timeline"
```
Result: Issue created with `pwk:capture` label, Status: Inbox

**AI task with priority and energy:**
```bash
/gpwk.capture "research best practices for API rate limiting [AI] !high ~deep"
```
Result: Issue with `pwk:ai`, `priority:high`, `energy:deep`, Type: ai-task

**Personal task:**
```bash
/gpwk.capture "fix login bug !high ~deep [P]"
```
Result: Issue with `pwk:personal`, `priority:high`, `energy:deep`, Type: task

**Completed activity (auto-detected):**
```bash
/gpwk.capture "I took Mr. Noodles for a walk between 9-10 AM"
```
Result: Issue created, automatically closed, Status: Done, added to Activity Stream

**Special characters (no escaping needed!):**
```bash
/gpwk.capture "Test with (parentheses) and 'quotes' works!"
```
Result: Works perfectly - Python backend handles all special characters

**Knowledge capture task:**
```bash
/gpwk.capture "Research GraphQL federation patterns and best practices [AI]"
# Then add pwk:knowledge label to trigger automated research workflow
gh issue edit {ISSUE_NUMBER} --add-label "pwk:knowledge"
```
Result: Issue with `pwk:ai` label created. When `pwk:knowledge` label is added, the GPWK Knowledge Capture workflow automatically:
- Performs internet research using WebSearch/WebFetch
- Creates comprehensive documentation in `knowledge/{topic}/`
- Generates README.md, technical-reference.md, and sources.md
- Commits directly to repository
- Posts results back to issue
- Adds `status:ai-complete` label

## Features

### Python Backend Benefits
- **No shell escaping issues**: Handles parentheses, quotes, special characters
- **Automatic retry logic**: Fixes GitHub API timing issues
- **Completion detection**: Past tense and time ranges detected automatically
- **Full telemetry**: Every operation instrumented with OpenTelemetry

### Telemetry Collected
- **Traces**: See complete operation flow in Grafana Tempo
- **Metrics**: Capture count, duration, error rate
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Type, priority, energy, completion status, duration

### Performance
Typical operation: ~500-700ms
- Parse: ~10-20ms
- Create issue: ~200-300ms
- Add to project: ~50-100ms (+ retries if needed)
- Set fields: ~150-200ms
- Update log: ~50ms

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

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_capture`)
- Metrics: Grafana Prometheus (`gpwk.capture.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)
