# GPWK Plan

Create a daily or weekly plan by pulling tasks from GitHub and generating a local log.

## Arguments
- `$ARGUMENTS` - `today`, `tomorrow`, `week`, or a specific date (YYYY-MM-DD)

## Instructions

You are creating a plan that combines GitHub issues with a local daily log (hybrid approach).

### Step 1: Read Configuration

Read `gpwk/memory/github-config.md` to get repository and project details.
Read `gpwk/memory/principles.md` to understand user's work preferences:
- Daily task limit
- Deep work windows
- Energy matching preferences

### Step 2: Determine Date Range

Parse `$ARGUMENTS`:
- `today` or empty → today's date
- `tomorrow` → tomorrow's date
- `week` → today through next 7 days
- `YYYY-MM-DD` → specific date

### Step 3: Fetch Issues from GitHub

Get issues assigned to the planned timeframe:

```bash
# Get issues in "Today" column (for today planning)
gh project item-list <project-number> --owner @me --format json | \
  jq '.items[] | select(.status == "Today")'

# Get all open issues for overview
gh issue list --repo <owner>/<repo> --state open --json number,title,labels,createdAt --limit 100

# Get issues by carryover status
gh issue list --repo <owner>/<repo> --label "pwk:c1,pwk:c2,pwk:c3" --json number,title,labels
```

### Step 4: Analyze and Categorize

Group issues by:
1. **Already in Today**: Issues with Status = "Today"
2. **Carryover candidates**: Issues with `pwk:c1`, `pwk:c2`, `pwk:c3` labels
3. **High priority**: Issues with `priority:high`
4. **AI-delegatable**: Issues with `pwk:ai` label
5. **Quick wins**: Issues with `energy:quick`

### Step 5: Generate Daily Plan

Apply principles to suggest a balanced day:
- Respect daily task limit (e.g., max 6 significant tasks)
- Match energy levels (deep work in morning if that's the preference)
- Flag carryover issues that need attention

### Step 6: Create Local Log File

Create or update `gpwk/logs/YYYY-MM-DD.md`:

```markdown
# Daily Log: YYYY-MM-DD

## Carryover from Yesterday
<!-- Issues with pwk:c1+ labels -->
- [ ] #123 - Task description [c2]
- [ ] #124 - Another task [c1]

## Today's Plan
<!-- Generated from project "Today" column + suggestions -->

### Deep Work Block (suggested: 9:00-11:00)
- [ ] #125 - Complex feature implementation [P] ~deep

### Shallow Work
- [ ] #126 - Review PR comments [P] ~shallow
- [ ] #127 - Research caching strategies [AI] ~shallow

### Quick Wins
- [ ] #128 - Fix typo in docs [P] ~quick

## AI Delegation Queue
<!-- Issues with pwk:ai label -->
- [ ] #127 - Research caching strategies
- [ ] #129 - Generate API documentation

## Activity Stream
<!-- Updated throughout the day by /gpwk.capture -->

## Blockers
<!-- Note any blockers encountered -->

## End of Day
<!-- Filled by /gpwk.review -->
- Completed:
- Remaining:
- Reflections:
```

### Step 7: Display Summary

Show the plan to the user:

```
📅 Plan for YYYY-MM-DD

From GitHub Project:
  • 3 tasks in "Today" column
  • 2 carryover items (1 at c2 - consider breakdown)
  • 2 AI-delegatable tasks ready

Suggested Schedule:
  09:00-11:00  Deep work: #125 Complex feature
  11:00-12:00  Shallow: #126 Review PR, #127 Research
  14:00-14:30  Quick wins: #128 Fix docs

AI Queue:
  • #127 Research caching strategies
  • #129 Generate API docs
  Run /gpwk.delegate to execute

Local log created: logs/YYYY-MM-DD.md

Tips:
  • #123 has been carried over 2 days - consider /gpwk.breakdown
  • Run /gpwk.triage to move Inbox items to Today
```

## Weekly Planning

If `$ARGUMENTS` is `week`:

1. Show all issues by Status column
2. Identify issues due this week
3. Highlight overdue or heavily-carried-over items
4. Suggest redistribution if any day is overloaded
5. Create a weekly overview file `gpwk/logs/YYYY-WXX-week.md`

## Error Handling

- If no issues in "Today": Suggest running `/gpwk.triage` first
- If log file exists: Ask whether to overwrite or merge
- If principles not configured: Use sensible defaults

## Integration Points

- References `gpwk/memory/principles.md` for work preferences
- Creates files in `gpwk/logs/` directory
- Works with GitHub Project "Today" column
- Feeds into `/gpwk.delegate` for AI task execution
