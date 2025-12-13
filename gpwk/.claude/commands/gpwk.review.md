# GPWK Review

End-of-day reflection and metrics summary.

## Arguments
- `$ARGUMENTS` - Optional: `--quick` for brief summary, `--full` for detailed review, or a date (YYYY-MM-DD)

## Instructions

You are conducting an end-of-day review that combines GitHub issue data with local log reflection.

### Step 1: Read Configuration

Read `gpwk/memory/github-config.md` for repository details.
Read `gpwk/memory/principles.md` for review preferences.

### Step 2: Determine Date and Mode

Parse `$ARGUMENTS`:
- `--quick` → Brief metrics only
- `--full` or empty → Full review with reflection prompts
- `YYYY-MM-DD` → Review a specific past date

### Step 3: Gather Data from GitHub

```bash
# Issues closed today
gh issue list \
  --repo <owner>/<repo> \
  --state closed \
  --search "closed:YYYY-MM-DD" \
  --json number,title,labels,closedAt

# Issues still open that were planned for today
# (Issues in "Today" column of project)
gh project item-list <project-number> --owner @me --format json | \
  jq '.items[] | select(.status == "Today" and .content.state == "OPEN")'

# Issues with carryover labels
gh issue list \
  --repo <owner>/<repo> \
  --label "pwk:c1,pwk:c2,pwk:c3" \
  --state open \
  --json number,title,labels

# AI tasks executed today (have comments from today)
gh issue list \
  --repo <owner>/<repo> \
  --label "pwk:ai" \
  --json number,title,updatedAt,comments
```

### Step 4: Read Local Log

Read `gpwk/logs/YYYY-MM-DD.md` if it exists:
- Activity Stream entries
- Blockers noted
- Any manual notes

### Step 5: Calculate Metrics

Compute:
- **Completion rate**: closed / (closed + remaining in Today)
- **AI delegation rate**: AI tasks executed / total AI tasks
- **Carryover count**: Issues that will need carryover labels
- **Deep work blocks**: Count of deep work activities logged
- **Interruptions**: Count of context switches (if tracked)

### Step 6: Generate Review

#### Quick Review (--quick)

```
📊 Daily Summary: YYYY-MM-DD

Completed: 6 tasks
  ✓ #123 - Fix login bug
  ✓ #124 - Update documentation
  ✓ #125 - Research caching [AI]
  ...

Remaining: 2 tasks
  → #126 - Complex refactoring (will carryover)
  → #127 - API integration

Metrics:
  • Completion: 75% (6/8)
  • AI tasks: 2 executed
  • Carryover: 2 items

Run /gpwk.review --full for detailed reflection
```

#### Full Review (--full)

```
📊 Daily Review: YYYY-MM-DD

═══════════════════════════════════════

COMPLETED (6)
  ✓ #123 - Fix login bug [P]
  ✓ #124 - Update documentation [P]
  ✓ #125 - Research caching strategies [AI]
  ✓ #126 - Generate test cases [AI]
  ✓ #127 - Review PR feedback [P]
  ✓ #128 - Quick typo fix [P]

NOT COMPLETED (2)
  → #129 - Complex refactoring [P] ~deep
    Reason: Underestimated complexity, needs breakdown

  → #130 - API integration [P]
    Reason: Blocked by external dependency

AI DELEGATION
  • 2 tasks executed
  • Results quality: Good
  • #125 research was particularly useful

METRICS
  ┌────────────────────────────┐
  │ Completion Rate    75%    │
  │ Planned Tasks      8      │
  │ Completed          6      │
  │ Carried Over       2      │
  │ AI Tasks Run       2      │
  │ Deep Work Blocks   2      │
  └────────────────────────────┘

PATTERNS NOTICED
  • Strong afternoon productivity
  • Morning deep work block was effective
  • #129 has been stuck - consider breakdown

═══════════════════════════════════════
```

Then prompt for reflection:

```
REFLECTION PROMPTS

1. What went well today?
   > [wait for user input]

2. What could have gone better?
   > [wait for user input]

3. What did you learn?
   > [wait for user input]

4. What's the most important thing for tomorrow?
   > [wait for user input]
```

### Step 7: Update Local Log

Append reflections to `gpwk/logs/YYYY-MM-DD.md`:

```markdown
## End of Day Review

### Metrics
- Completed: 6/8 (75%)
- AI Tasks: 2 executed
- Deep Work: 2 blocks

### Completed
- #123 - Fix login bug
- #124 - Update documentation
...

### Carried Over
- #129 - Complex refactoring → needs breakdown
- #130 - API integration → blocked

### Reflections
**What went well:** <user input>
**Could improve:** <user input>
**Learned:** <user input>
**Tomorrow's priority:** <user input>

### Review completed at HH:MM
```

### Step 8: Prepare Carryover

Identify issues that need carryover labels updated:

```bash
# For issues still open that were in Today:
# - Add pwk:c1 if no carryover label
# - Upgrade pwk:c1 → pwk:c2
# - Upgrade pwk:c2 → pwk:c3
# - Keep pwk:c3 but flag for breakdown
```

Display carryover preparation:

```
CARRYOVER PREPARATION

These issues will be carried to tomorrow:
  #129 - Complex refactoring [c1 → c2]
  #130 - API integration [new → c1]

⚠️ Warning: #129 will be at c2. One more carryover triggers breakdown suggestion.

Run /gpwk.carryover to apply labels and move to tomorrow.
```

### Step 9: Closing

```
✓ Review Complete

Log updated: logs/YYYY-MM-DD.md
Carryover ready: 2 items

Suggested next actions:
  • Run /gpwk.carryover to process carryover
  • Consider /gpwk.breakdown #129 before it hits c3

Good work today. Rest well! 🌙
```

## Weekly Review Mode

If reviewing on Sunday or `--weekly`:
- Aggregate metrics across the week
- Show completion trend
- Identify recurring carryover items
- Review work items progress
- Set intentions for next week

## Error Handling

- If no log file exists: Generate from GitHub data only
- If no issues closed: Note this and prompt for reflection
- If GitHub API fails: Fall back to local log only
