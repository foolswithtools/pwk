# GPWK Triage

Move issues between project columns (Inbox → Today/This Week/Backlog).

## Arguments
- `$ARGUMENTS` - Optional: `--inbox` to show inbox, `#123 today` to move specific issue

## Instructions

You are triaging issues in the GitHub Project, moving them from Inbox to appropriate time horizons.

### Step 1: Read Configuration

Read `memory/github-config.md` for project and field IDs.
Read `memory/principles.md` for:
- Daily task limit
- Preferred work balance

### Step 2: Parse Arguments

- Empty or `--inbox` → Show Inbox and prompt for triage
- `#123 today` → Move issue #123 to Today
- `#123 week` → Move issue #123 to This Week
- `#123 backlog` → Move issue #123 to Backlog
- `--auto` → Auto-triage based on priority and age

### Step 3: Fetch Inbox Items

```bash
gh project item-list <project-number> --owner @me --format json | \
  jq '.items[] | select(.status == "Inbox")'
```

Also get current Today column count for capacity planning.

### Step 4: Display Inbox

```
📥 Inbox Triage

Current Today: 4 tasks (limit: 6)
Capacity: 2 more tasks

INBOX (5 items)
────────────────────────────────────────
#201 [AI] Research authentication patterns
     Created: 2 days ago | Priority: - | Energy: -
     Suggested: Today (AI task, can run in background)

#202 [P] Fix navigation bug
     Created: 1 day ago | Priority: high | Energy: shallow
     Suggested: Today (high priority)

#203 [P] Refactor database layer
     Created: 3 days ago | Priority: medium | Energy: deep
     Suggested: This Week (needs deep focus block)

#204 [capture] Call with stakeholder about timeline
     Created: today | Priority: - | Energy: -
     Suggested: Convert to task or calendar event

#205 [P] Update README with new features
     Created: 1 week ago | Priority: low | Energy: quick
     Suggested: Backlog or quick win slot

────────────────────────────────────────

Commands:
  /gpwk.triage #201 today     Move to Today
  /gpwk.triage #203 week      Move to This Week
  /gpwk.triage #205 backlog   Move to Backlog
  /gpwk.triage --auto         Auto-triage all
```

### Step 5: Move Issue (if specific issue provided)

```bash
# Get the project item ID for this issue
ITEM_ID=$(gh project item-list <project-number> --owner @me --format json | \
  jq -r '.items[] | select(.content.number == <issue-number>) | .id')

# Get the option ID for the target status
# (This requires knowing the field and option IDs from setup)

# Update the status
gh project item-edit \
  --project-id <project-id> \
  --id $ITEM_ID \
  --field-id <status-field-id> \
  --single-select-option-id <target-status-option-id>
```

### Step 6: Handle Captures

For items with `pwk:capture` label, offer options:

```
#204 is a capture, not a task yet.

Options:
  1. Convert to task [P] - Keep as personal task
  2. Convert to task [AI] - Mark as AI-delegatable
  3. Move to calendar - This is an event, not a task
  4. Delete - No longer relevant
  5. Keep in Inbox - Need more info

Choice:
```

If converting to task:
```bash
gh issue edit <number> --remove-label "pwk:capture" --add-label "pwk:personal"
```

### Step 7: Auto-Triage (--auto)

Apply these rules:

1. **High priority** → Today (if capacity allows)
2. **AI tasks** → Today (they run in background)
3. **Quick wins** → Today (good for energy management)
4. **Deep work** → This Week (need to schedule properly)
5. **Low priority / old captures** → Backlog
6. **Over capacity** → This Week

```
🤖 Auto-Triage Results

Moved to Today:
  ✓ #201 - Research auth patterns [AI]
  ✓ #202 - Fix navigation bug [high priority]

Moved to This Week:
  ✓ #203 - Refactor database layer [deep work]

Moved to Backlog:
  ✓ #205 - Update README [low priority]

Needs Manual Decision:
  ⚠ #204 - Capture needs conversion

Today is now at: 6/6 tasks (full)
```

### Step 8: Capacity Warnings

If Today is at or over capacity:

```
⚠️ Today is at capacity (6/6 tasks)

Options:
  1. Move something from Today to This Week
  2. Proceed anyway (may cause carryover)
  3. Cancel this triage

Current Today tasks:
  #198 - Implement login flow [P] ~deep
  #199 - Review PR comments [P] ~shallow
  ...
```

### Step 9: Update Local Log

If changes were made, note in today's log:

```markdown
## Triage Log
- HH:MM - Moved #201 to Today
- HH:MM - Moved #203 to This Week
- HH:MM - Converted #204 from capture to task
```

### Step 10: Confirm

```
✓ Triage Complete

Changes:
  → Today: +2 (now 6 tasks)
  → This Week: +1
  → Backlog: +1

Inbox remaining: 1 item (needs manual decision)

Run /gpwk.plan today to see updated daily plan
```

## Best Practices

- Triage inbox at least once daily (morning recommended)
- Keep Today at or under your daily limit
- Don't over-schedule deep work
- AI tasks are "free" capacity-wise (run in background)
- Convert captures promptly to maintain inbox zero

## Error Handling

- If issue not in project: Add it first, then move
- If field IDs invalid: Prompt to re-run /gpwk.setup
- If capacity exceeded: Warn but allow override
