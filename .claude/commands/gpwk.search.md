# GPWK Search

Search and query GitHub issues with flexible filtering and full telemetry.

## Arguments
- `QUERY` - Text search in title/body (optional)
- `--status <value>` - Filter by project column (inbox|today|thisweek|backlog|done|review)
- `--label <value>` - Filter by label (comma-separated for OR logic)
- `--priority <value>` - Filter by priority (high|medium|low)
- `--energy <value>` - Filter by energy level (deep|shallow|quick)
- `--type <value>` - Filter by type (task|ai-task|personal|capture)
- `--state <value>` - Filter by issue state (open|closed|all, default: open)
- `--limit <N>` - Maximum results (default: 50)
- `--json` - Output as JSON for piping to other tools

## Instructions

**IMPORTANT**: This command uses the Python backend with OpenTelemetry instrumentation.

### How It Works

The Python backend provides unified search capabilities:
- ✅ Flexible filtering (status, labels, priority, energy, type)
- ✅ Text search in titles and bodies
- ✅ Multiple output formats (human-readable, JSON)
- ✅ Sub-second query performance
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Parse arguments and call Python backend
gpwk/bin/gpwk-search "$@"
```

## Usage Examples

**Find high-priority tasks:**
```bash
/gpwk.search --priority high
```
Result: All open issues with `priority:high` label

**Find AI-delegatable tasks:**
```bash
/gpwk.search --label "pwk:ai"
```
Result: All open issues with `pwk:ai` label

**Find today's tasks:**
```bash
/gpwk.search --status today
```
Result: All issues in the "Today" project column

**Text search:**
```bash
/gpwk.search "rivian"
```
Result: All open issues with "rivian" in title or body

**Find blocked tasks:**
```bash
/gpwk.search --label "status:blocked"
```
Result: All open issues with `status:blocked` label

**Complex query (priority + energy):**
```bash
/gpwk.search --priority high --energy deep
```
Result: High-priority deep work tasks

**JSON output for scripting:**
```bash
/gpwk.search --label "pwk:ai" --json | jq '.[] | .number'
```
Result: Issue numbers of AI tasks in JSON format

**Find carryover tasks:**
```bash
/gpwk.search --label "pwk:c1,pwk:c2,pwk:c3"
```
Result: All tasks that have been carried over

**Search with text + filters:**
```bash
/gpwk.search "consulting" --priority high
```
Result: High-priority issues mentioning "consulting"

**Find closed issues:**
```bash
/gpwk.search --state closed --limit 10
```
Result: Last 10 closed issues

## Common Query Patterns

### By Priority
```bash
/gpwk.search --priority high          # High priority
/gpwk.search --priority medium        # Medium priority
/gpwk.search --priority low           # Low priority
```

### By Energy Level
```bash
/gpwk.search --energy deep            # Deep work
/gpwk.search --energy shallow         # Shallow work
/gpwk.search --energy quick           # Quick wins
```

### By Type
```bash
/gpwk.search --type ai-task           # AI-delegatable
/gpwk.search --type task              # Personal tasks
/gpwk.search --type capture           # Quick captures
```

### By Project Status
```bash
/gpwk.search --status inbox           # Needs triage
/gpwk.search --status today           # Scheduled for today
/gpwk.search --status thisweek        # This week's tasks
/gpwk.search --status backlog         # Backlog
/gpwk.search --status done            # Completed
/gpwk.search --status review          # Needs review
```

### By Special Labels
```bash
/gpwk.search --label "status:blocked"  # Blocked tasks
/gpwk.search --label "status:waiting"  # Waiting on others
/gpwk.search --label "status:ai-complete"  # AI tasks done
```

## Output Formats

### Human-Readable (Default)
```
Found 3 issue(s):

#113 - Place 2026 California registration sticker on Rivian
  Labels: pwk:personal
  URL: https://github.com/user/repo/issues/113

#114 - Place 2026 California registration sticker on Nissan Leaf
  Labels: pwk:personal
  URL: https://github.com/user/repo/issues/114

#96 - Research existing solutions
  Labels: pwk:ai, priority:high, energy:deep
  URL: https://github.com/user/repo/issues/96
```

### JSON Format
```json
[
  {
    "number": 113,
    "title": "Place 2026 California registration sticker on Rivian",
    "url": "https://github.com/user/repo/issues/113",
    "labels": ["pwk:personal"],
    "state": "open"
  },
  {
    "number": 114,
    "title": "Place 2026 California registration sticker on Nissan Leaf",
    "url": "https://github.com/user/repo/issues/114",
    "labels": ["pwk:personal"],
    "state": "open"
  }
]
```

## Query Logic

### Label Filters (OR Logic)
Comma-separated labels use OR logic:
```bash
# Finds issues with c1 OR c2 OR c3
/gpwk.search --label "pwk:c1,pwk:c2,pwk:c3"
```

### Multiple Filters (AND Logic)
Multiple filter types use AND logic:
```bash
# Finds issues with (priority:high AND energy:deep)
/gpwk.search --priority high --energy deep
```

### Text Search
GitHub's search syntax applies:
- Searches title and body
- Case-insensitive
- Partial word matching

## Performance

Typical search: ~200-500ms
- Query GitHub: ~100-300ms
- Parse results: ~50-100ms
- Format output: ~50-100ms
- Telemetry overhead: ~50ms

Complex filters (with project status): ~500-1000ms
- Additional project API call: ~200-400ms

## Telemetry Collected

- **Traces**: Complete search flow in Grafana Tempo
- **Metrics**: Search count, duration, result count, error rate
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Query text, filters used, result count, duration

## Error Handling

The command handles edge cases gracefully:

- **No results**: Displays "Found 0 issue(s)"
- **Invalid filter value**: Displays error with valid options
- **GitHub API error**: Displays error with retry suggestion
- **Invalid limit**: Displays error with valid range

## Integration Points

- **Reads**: GitHub issues via REST API and `gh` CLI
- **Reads**: GitHub Project data for status filtering
- **No Writes**: Read-only operation
- **Output**: stdout (text or JSON)
- **Telemetry**: Traces exported to Grafana Tempo, metrics to Prometheus

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

**No results found:**
- Check filter values (e.g., "pwk:ai" not "ai")
- Try broader search (remove filters)
- Check issue state (default is "open" only)

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_search`)
- Metrics: Grafana Prometheus (`gpwk.search.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)

## Use Cases

### Daily Planning
```bash
# What's on my plate today?
/gpwk.search --status today

# What needs triage?
/gpwk.search --status inbox

# What's high priority?
/gpwk.search --priority high
```

### Finding Specific Tasks
```bash
# Did I capture a task about X?
/gpwk.search "registration sticker"

# What AI tasks are ready?
/gpwk.search --label "pwk:ai" --state open

# What's blocked?
/gpwk.search --label "status:blocked"
```

### Scripting & Automation
```bash
# Get issue numbers for bulk operations
/gpwk.search --priority high --json | jq '.[].number'

# Count tasks by type
/gpwk.search --type ai-task --json | jq 'length'

# Export for analysis
/gpwk.search --state closed --limit 100 --json > completed.json
```

### Carryover Analysis
```bash
# Level 1 carryover (1 day)
/gpwk.search --label "pwk:c1"

# Level 2 carryover (2 days) - needs attention
/gpwk.search --label "pwk:c2"

# Level 3 carryover (3+ days) - needs breakdown
/gpwk.search --label "pwk:c3"
```

## See Also

- `/gpwk.capture` - Create tasks
- `/gpwk.complete` - Mark tasks complete
- `/gpwk.triage` - Move tasks between columns
- `/gpwk.plan` - Generate daily plans
