# GPWK Carryover

Update carryover labels on incomplete issues and prepare for the next day.

## Arguments
- `$ARGUMENTS` - Optional: `--dry-run` to preview without applying, `--force` to skip confirmations

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable to process carryover labels. The Python backend handles:
- ✅ Fetching incomplete issues from Today column
- ✅ Calculating label updates (c1 → c2 → c3)
- ✅ Identifying issues needing breakdown (at c3)
- ✅ Applying label changes to GitHub issues
- ✅ Preview mode with --dry-run
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-carryover $ARGUMENTS
```

That's it! The Python backend handles the entire carryover workflow.

---

## What Carryover Does

You are processing end-of-day carryover, updating labels to track how many days issues have been carried forward.

### Step 3: Calculate Label Updates

For each incomplete issue in Today:

| Current Label | Action | New Label |
|---------------|--------|-----------|
| (none) | Add c1 | pwk:c1 |
| pwk:c1 | Remove c1, Add c2 | pwk:c2 |
| pwk:c2 | Remove c2, Add c3 | pwk:c3 |
| pwk:c3 | Keep c3, Flag for breakdown | pwk:c3 + needs-breakdown |

### Step 4: Preview Changes (or --dry-run)

```
🔄 Carryover Preview

Issues being carried over from today:

NEW CARRYOVER (first time)
  #201 - Implement user auth [P]
         Status: Today → stays in Today
         Labels: + pwk:c1

CARRYOVER DAY 2
  #198 - Refactor API layer [P]
         Status: Today → stays in Today
         Labels: pwk:c1 → pwk:c2
         ⚠️ One more carryover triggers breakdown

CARRYOVER DAY 3+ (Needs Attention)
  #195 - Complex migration task [P]
         Status: Today → stays in Today
         Labels: pwk:c2 → pwk:c3
         🚨 BREAKDOWN RECOMMENDED
         This task has been carried 3 times.
         Consider running: /gpwk.breakdown #195

ALREADY AT C3 (Still stuck)
  #190 - Legacy system update [P]
         Labels: pwk:c3 (unchanged)
         🚨 STILL NEEDS BREAKDOWN
         Has been at c3 for 2 days.

Summary:
  • 1 new carryover
  • 1 at c2 (warning threshold)
  • 1 upgraded to c3 (breakdown needed)
  • 1 stuck at c3 (overdue for breakdown)

Proceed with carryover? (y/n)
```

### Step 5: Apply Label Updates

```bash
# Remove old label, add new label
gh issue edit <number> \
  --repo <owner>/<repo> \
  --remove-label "pwk:c1" \
  --add-label "pwk:c2"

# For new carryovers (no existing label)
gh issue edit <number> \
  --repo <owner>/<repo> \
  --add-label "pwk:c1"

# For c3 issues that need breakdown flag
gh issue edit <number> \
  --repo <owner>/<repo> \
  --add-label "needs-breakdown"
```

### Step 6: Add Carryover Comment

For visibility, add a comment to each carried issue:

```bash
gh issue comment <number> --repo <owner>/<repo> --body "$(cat <<'EOF'
📅 **Carryover Notice**

This task was carried over from YYYY-MM-DD.
Current carryover count: **c2**

If this task continues to be carried over, consider:
- Breaking it into smaller subtasks
- Identifying blockers
- Re-evaluating priority

*Logged by GPWK at HH:MM*
EOF
)"
```

### Step 7: Track Metrics

Record carryover metrics for trend analysis:

```bash
# Append to a carryover tracking issue or local file
# Track: date, count of c1/c2/c3, issues by ID
```

Update local log `gpwk/logs/YYYY-MM-DD.md`:

```markdown
## Carryover Applied

| Issue | Title | Previous | New |
|-------|-------|----------|-----|
| #201 | Implement user auth | (new) | c1 |
| #198 | Refactor API layer | c1 | c2 |
| #195 | Complex migration | c2 | c3 |

### Breakdown Needed
- #195 - Complex migration task (at c3)
- #190 - Legacy system update (stuck at c3)
```

### Step 8: Suggest Actions

```
✓ Carryover Complete

Applied:
  • 4 issues updated with carryover labels
  • Comments added for tracking

⚠️ Attention Needed:

  #195 - Complex migration task
         Now at c3. Breakdown strongly recommended.
         Run: /gpwk.breakdown #195

  #190 - Legacy system update
         Stuck at c3 for 2 days.
         Options:
           - /gpwk.breakdown #190
           - Close as won't-do
           - Reassign or delegate

Metrics updated in gpwk/logs/YYYY-MM-DD.md

Tomorrow's starting point:
  • 4 carryover items
  • 2 need immediate attention
  • Run /gpwk.plan tomorrow to incorporate
```

## Carryover Analytics

Track patterns over time:

```
📊 Carryover Trends (Last 7 Days)

Day       | c1 | c2 | c3 | Completed
----------|----|----|----|-----------
Mon 12/09 |  2 |  1 |  0 |     6
Tue 12/10 |  1 |  2 |  0 |     7
Wed 12/11 |  3 |  1 |  1 |     5
Thu 12/12 |  2 |  2 |  1 |     6

Patterns:
  • Average completion: 6 tasks/day
  • Average carryover: 2.5 tasks/day
  • Chronic carryover: #190 (5 days)

Recommendation:
  Consider reducing daily task load from 8 to 6
  to reduce carryover rate.
```

## Error Handling

- If label operation fails: Log error, continue with others
- If issue not found: Skip and report
- If already processed today: Skip duplicate processing

## Integration

- Run automatically as part of `/gpwk.review --full`
- Or run standalone before `/gpwk.plan tomorrow`
- Works with GitHub Issues and Projects
