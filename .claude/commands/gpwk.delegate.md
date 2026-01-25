# GPWK Delegate

Execute AI-delegatable tasks automatically with Claude, posting results as issue comments with full telemetry.

## Arguments
- None required - Processes all `pwk:ai` labeled tasks
- Optional: `#123` - Delegate specific issue number only

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

**GPWK uses a split architecture for AI delegation:**

**Python Backend (Infrastructure)**:
- ✅ Lists AI-delegatable tasks (`pwk:ai` label)
- ✅ Updates project statuses (Inbox → Today → Review)
- ✅ Provides helper methods for result posting
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)
- ❌ Does NOT directly execute AI tasks via Anthropic API

**GitHub Action (Execution)**:
- ✅ Executes tasks using Claude Code environment
- ✅ Reads issue body and generates comprehensive results
- ✅ Calls Python helpers to post results as comments
- ✅ Adds `status:ai-complete` label for review
- ✅ Scheduled: Every 4 hours on weekdays
- ✅ Manual trigger: `gh workflow run claude-gpwk.yml -f action_type=delegate`

**Why This Split?**
- Secure API key management (GitHub Secrets)
- Reliable Claude Code execution environment
- Separation of concerns (infrastructure vs execution)
- Proven working: See issues #96, #104 for successful examples

### Execute Command

```bash
# Call Python backend from workspace root
if [ -n "$ARGUMENTS" ]; then
  gpwk/bin/gpwk-delegate "$ARGUMENTS"
else
  gpwk/bin/gpwk-delegate
fi
```

That's it! The Python backend executes AI tasks autonomously.

## Delegation Workflow

**Complete Execution Flow**:

1. **List AI Tasks** (Python: `gpwk-delegate --list`)
   - Fetches all open issues with `pwk:ai` label
   - Shows priority, energy, and task details

2. **Prepare Infrastructure** (Python: `gpwk-delegate #123`)
   - Validates issue has `pwk:ai` label
   - Moves issue to "Today" status
   - Returns: "Infrastructure prepared, awaiting GitHub Action"

3. **Execute Task** (GitHub Action: `claude-gpwk.yml`)
   - Reads issue title and body
   - Executes with Claude Code environment
   - Generates comprehensive result
   - Posts result via: `gpwk-delegate --post-result #123 "body"`
   - Adds label via: `gpwk-delegate --mark-complete #123`

4. **Sync to Review** (Python: `gpwk-delegate --sync-status`)
   - Finds all issues with `status:ai-complete` label
   - Moves them to "Review" status in project
   - Ready for human review

5. **Human Review**
   - Read AI results in issue comments
   - Validate quality and completeness
   - Close issue or request follow-up

## Architecture Deep Dive

### Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          User Actions                            │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ Python Backend (Infrastructure)                                 │
│ ─────────────────────────────────────────────────────────────── │
│ • List AI tasks:      gpwk-delegate --list                      │
│ • Prepare task:       gpwk-delegate #123                        │
│ • Sync to Review:     gpwk-delegate --sync-status               │
│ • Helper - Post:      gpwk-delegate --post-result #123 "body"   │
│ • Helper - Complete:  gpwk-delegate --mark-complete #123        │
│                                                                  │
│ Updates: GitHub Project status (Today, Review)                  │
│ Telemetry: Full OpenTelemetry instrumentation                   │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Action (AI Execution)                                    │
│ ─────────────────────────────────────────────────────────────── │
│ Workflow: .github/workflows/claude-gpwk.yml                     │
│ Trigger:  Scheduled (4hr cron) OR manual                        │
│ Command:  gh workflow run claude-gpwk.yml -f action_type=delegate│
│                                                                  │
│ Execution Environment: Claude Code                              │
│ - Reads issue body                                              │
│ - Executes with full Claude Code capabilities                   │
│ - Generates comprehensive result                                │
│ - Calls Python helpers to post result                           │
│                                                                  │
│ Posts: Issue comments, labels                                   │
└───────────────┬─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│ GitHub Issues (Results)                                         │
│ ─────────────────────────────────────────────────────────────── │
│ • AI result posted as comment                                   │
│ • status:ai-complete label added                                │
│ • Status moved to Review                                        │
│ • Ready for human validation                                    │
└─────────────────────────────────────────────────────────────────┘
```

### Helper Methods

The Python backend provides these helper methods for GitHub Action integration:

**1. Post AI Result**
```bash
gpwk-delegate --post-result #96 "## AI Delegation Result\n\n[Comprehensive analysis]..."
```
Called by GitHub Action to post execution results as issue comments.
- Posts markdown-formatted result as comment
- Optionally adds `status:ai-complete` label
- Full OpenTelemetry instrumentation
- Returns: Success boolean

**2. Mark AI Complete**
```bash
gpwk-delegate --mark-complete #96
```
Simple helper to add `status:ai-complete` label.
- Adds label to signal task needs review
- Full telemetry support
- Returns: Success boolean

**3. Sync AI Complete to Review**
```bash
gpwk-delegate --sync-status
```
Batch operation to move all AI-complete tasks to Review status.
- Finds all issues with `status:ai-complete` label
- Gets project item ID for each issue
- Moves to "Review" status in project
- Reports: synced count, failed count

### Proven Working Examples

**Issue #96**: Research task successfully executed via GitHub Action
- Python prepared infrastructure
- GitHub Action executed with Claude Code
- Result posted as comment
- Label added for review

**Issue #104**: Documentation task successfully executed
- Same workflow as #96
- Comprehensive result generated
- Awaiting human review in "Review" status

These examples demonstrate the architecture works end-to-end.

## Safe to Delegate

From your principles, these tasks are safe for AI:

✅ **Research and Information Gathering**
- Aggregating information from multiple sources
- Literature reviews
- Technology comparisons
- Best practices research

✅ **Summarization and Synthesis**
- Meeting notes structuring
- Documentation summaries
- Code review summaries (not decisions)

✅ **Content Generation**
- First drafts of documentation
- Boilerplate code generation
- Test case generation
- API documentation
- Data formatting and cleanup

✅ **Analysis**
- Bug reproduction steps
- Performance analysis reports
- Dependency audits

## Keep Personal

❌ **DO NOT delegate:**
- Decisions with significant impact
- Relationship-dependent communication
- Creative direction and vision
- Anything requiring institutional knowledge
- Final reviews and approvals
- Customer-facing communication
- Research requiring judgment calls

## Features

### Python Backend Benefits
- **Autonomous execution**: Runs without supervision
- **Quality results**: Uses Claude's latest capabilities
- **Safety checks**: Validates delegation appropriateness
- **Result tracking**: Comments preserve full audit trail
- **Full telemetry**: Track AI task patterns and ROI

### Telemetry Collected
- **Traces**: Complete delegation flow in Grafana Tempo
- **Metrics**: Tasks delegated, completion time, token usage, success rate
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Task type, complexity, duration, quality score

### AI Execution (GitHub Action)

When the GitHub Action executes each task:
- Reads full context from issue body
- Uses Claude Code environment with Claude Sonnet 4.5
- Generates comprehensive, actionable results
- Posts result via `--post-result` helper
- Adds `status:ai-complete` label via `--mark-complete` helper
- Tracks execution in GitHub Action logs

## Example Session

**List AI Tasks:**
```bash
/gpwk.delegate --list
```

Output:
```
🤖 AI-Delegatable Tasks

Ready to Execute (2 tasks):
────────────────────────────────────────────────────────────

  #96 - Research AWS Batch for AI long-running jobs
         Priority: high

  #104 - Document Claude Code setup for team
         Priority: medium

────────────────────────────────────────────────────────────

Commands:
  gpwk-delegate --execute        Execute all tasks
  gpwk-delegate #123             Execute specific task
  gpwk-delegate --execute #123   Execute specific task
  gpwk-delegate --sync-status    Sync AI-complete tasks to Review

Helper Commands (called by GitHub Action):
  gpwk-delegate --post-result #123 "body"    Post AI result as comment
  gpwk-delegate --mark-complete #123         Add ai-complete label
```

**Prepare Specific Task:**
```bash
/gpwk.delegate #96
```

Output:
```
✓ Infrastructure prepared for #96: Research AWS Batch for AI long-running jobs. Awaiting GitHub Action execution.
  Duration: 234ms
```

**Sync Completed Tasks to Review:**
```bash
/gpwk.delegate --sync-status
```

Output:
```
✓ Synced 2 AI-complete tasks to Review status (0 failed)
  Duration: 567ms
  Tasks executed: 2
```

## Result Format

AI results are posted as comments with this structure:

```markdown
## 🤖 AI Delegation Result

**Task**: Review Claude Code materials from Todd

**Executed**: 2025-12-21 10:30 AM
**Duration**: 45 seconds
**Model**: Claude Sonnet 4.5

### Summary

[Executive summary of findings]

### Key Points

1. [Main finding 1]
2. [Main finding 2]
3. [Main finding 3]

### Detailed Analysis

[Comprehensive analysis]

### Resources

- [Link 1]
- [Link 2]

### Recommendations

1. [Action item 1]
2. [Action item 2]

---
*Generated by GPWK AI Delegation* | [View Telemetry](link to trace)
```

## Review Process

After delegation:

1. **Read AI results** - Review comment on each issue
2. **Validate quality** - Ensure results meet your standards
3. **Take action** - Use results to inform decisions
4. **Close or iterate** - Close if complete, or add follow-up tasks
5. **Remove label** - Remove `status:ai-complete` after review

## Quality Standards

AI results always include:
- Clear executive summary
- Detailed analysis with evidence
- Actionable recommendations
- Source citations where applicable
- Limitations and caveats

Results you can trust because:
- Claude Sonnet 4.5 (latest, most capable)
- Full context from issue body
- Structured output format
- Telemetry for quality tracking

## Best Practices

### When to Delegate
- **After /gpwk.triage**: Delegate new AI tasks from Inbox
- **During /gpwk.plan**: Execute AI queue while doing deep work
- **Before decisions**: Get research done before meetings
- **Batch processing**: Run delegation for multiple tasks at once

### Delegation Criteria
Ask: "Would this help me make a better decision?"
- Research: YES - delegate fact-finding
- Decision: NO - keep personal
- Draft: YES - delegate first pass
- Final: NO - review personally

### Time Savings
Average AI task: 45-90 seconds
Equivalent human work: 30-90 minutes
ROI: ~30-60x time savings on delegatable tasks

## Integration Points

- **Reads**: Issues with `pwk:ai` label
- **Updates**: Adds `status:ai-complete` label
- **Creates**: Issue comments with results
- **Called from**: `/gpwk.plan` (suggested in AI queue)
- **Feeds**: Your decision-making process

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

**No AI tasks found:**
Label tasks with `pwk:ai` using `/gpwk.capture "task [AI]"` or manually.

**AI tasks not executing:**
- Check GitHub Action runs: `gh run list --workflow=claude-gpwk.yml`
- Trigger manually: `gh workflow run claude-gpwk.yml -f action_type=delegate`
- Verify ANTHROPIC_API_KEY is set in GitHub Secrets

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_delegate`)
- Metrics: Grafana Prometheus (`gpwk.delegate.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)
