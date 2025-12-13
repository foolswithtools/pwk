# GPWK Capture

Quick capture of activities, tasks, or thoughts to GitHub Issues.

## Arguments
- `$ARGUMENTS` - The activity or task to capture

## Instructions

You are capturing an activity or task to GitHub. Parse the input and create an appropriate issue.

### Step 1: Read Configuration

Read `gpwk/memory/github-config.md` to get:
- Repository name and owner
- Project number
- Field IDs

If not configured, prompt user to run `/gpwk.setup` first.

### Step 2: Parse Input

Parse `$ARGUMENTS` to extract:

1. **Task type** (from brackets):
   - `[AI]` → label `pwk:ai`, Type field = `ai-task`
   - `[P]` → label `pwk:personal`, Type field = `task`
   - No bracket → label `pwk:capture`, Type field = `capture`

2. **Priority** (from keywords):
   - `!high` or `!urgent` → label `priority:high`, Priority field = `high`
   - `!medium` → label `priority:medium`, Priority field = `medium`
   - `!low` → label `priority:low`, Priority field = `low`

3. **Energy** (from keywords):
   - `~deep` → label `energy:deep`, Energy field = `deep`
   - `~shallow` → label `energy:shallow`, Energy field = `shallow`
   - `~quick` → label `energy:quick`, Energy field = `quick`

4. **Title**: Everything else after removing type/priority/energy markers

### Step 3: Create Issue

```bash
gh issue create \
  --repo <owner>/<repo> \
  --title "<parsed-title>" \
  --label "<labels>" \
  --body "$(cat <<'EOF'
## Captured
- **Date**: <current-date-time>
- **Source**: GPWK Capture

## Context
<any additional context parsed from input>

## Notes
(Add notes as you work on this)
EOF
)"
```

### Step 4: Add to Project

Get the issue URL/number from the create output, then add to project:

```bash
# Add issue to project
gh project item-add <project-number> --owner @me --url <issue-url>

# Get the item ID
ITEM_ID=$(gh project item-list <project-number> --owner @me --format json | jq -r '.items[] | select(.content.url == "<issue-url>") | .id')

# Set Status to Inbox
gh project item-edit --project-id <project-number> --id $ITEM_ID --field-id <status-field-id> --single-select-option-id <inbox-option-id>

# Set Type field
gh project item-edit --project-id <project-number> --id $ITEM_ID --field-id <type-field-id> --single-select-option-id <type-option-id>

# Set Priority if specified
# Set Energy if specified
```

### Step 5: Update Local Log (Hybrid)

Also append to today's local log file `gpwk/logs/YYYY-MM-DD.md`:

```markdown
- HH:MM - Captured #<issue-number>: <title> [<type>]
```

If the log file doesn't exist, create it from template first.

### Step 6: Confirm

Display confirmation:

```
✓ Captured: <title>
  Issue: #<number> (<url>)
  Labels: <labels>
  Status: Inbox

  Run /gpwk.triage to move to Today/This Week
```

## Examples

**Input**: `research best practices for API rate limiting [AI]`
**Result**:
- Issue: "research best practices for API rate limiting"
- Labels: `pwk:ai`
- Type: `ai-task`
- Status: Inbox

**Input**: `fix login bug !high ~deep [P]`
**Result**:
- Issue: "fix login bug"
- Labels: `pwk:personal`, `priority:high`, `energy:deep`
- Type: `task`
- Priority: high
- Energy: deep

**Input**: `remember to call John about project timeline`
**Result**:
- Issue: "remember to call John about project timeline"
- Labels: `pwk:capture`
- Type: `capture`
- Status: Inbox

## Error Handling

- If gh CLI not authenticated: Prompt for `gh auth login`
- If repo not found: Suggest running `/gpwk.setup`
- If project not found: Suggest running `/gpwk.setup`
- On success: Always show issue number and URL
