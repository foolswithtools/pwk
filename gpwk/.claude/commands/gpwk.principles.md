# GPWK Principles

View or edit your personal work principles that govern GPWK behavior.

## Arguments
- `$ARGUMENTS` - Optional: `--edit` to modify principles, specific section name to view

## Instructions

You are managing the user's work principles stored in `memory/principles.md`.

### Step 1: Read Current Principles

Read `memory/principles.md` to get current configuration.

### Step 2: Determine Action

Parse `$ARGUMENTS`:
- Empty → Display all principles
- `--edit` → Interactive editing mode
- Section name (e.g., `delegation`, `time`, `energy`) → Show specific section

### Step 3: Display Principles

Format principles for easy reading:

```
📋 Your Work Principles

TIME MANAGEMENT
  Deep Work:
    • Minimum block: 2 hours
    • Preferred time: Morning (9:00-12:00)
    • Max per day: 2 blocks

  Meeting Boundaries:
    • No meetings before: 10:00 AM
    • No meetings after: 4:00 PM

  Breaks:
    • Pomodoro: 25 min work / 5 min break
    • Long break: 15-30 min after 4 pomodoros

TASK MANAGEMENT
  Daily Limits:
    • Maximum significant tasks: 6
    • Quick wins don't count toward limit

  Carryover Rules:
    • c1: Track normally
    • c2: Warning, check for blockers
    • c3: Mandatory breakdown consideration

AI DELEGATION
  Safe to Delegate:
    ✓ Research and information gathering
    ✓ Summarization and synthesis
    ✓ First drafts of documentation
    ✓ Boilerplate code generation

  Keep Personal:
    ✗ Decisions with significant impact
    ✗ Relationship-dependent communication
    ✗ Creative direction and vision

ENERGY MANAGEMENT
  Task Matching:
    • Morning: Deep work, creative tasks
    • Afternoon: Meetings, collaboration
    • Late day: Admin, quick wins

Run /gpwk.principles --edit to modify
```

### Step 4: Edit Mode (--edit)

If `--edit` is specified, offer interactive editing:

```
📋 Edit Principles

Which section would you like to edit?
  1. Time Management
  2. Task Management
  3. AI Delegation
  4. Energy Management
  5. Weekly Rhythm
  6. Review Rituals

Enter number or section name:
```

Then for each section, show current values and ask for changes:

```
TIME MANAGEMENT - Deep Work

Current values:
  • Minimum block: 2 hours
  • Preferred time: Morning (9:00-12:00)
  • Max per day: 2 blocks

What would you like to change?
(Enter new values or press Enter to keep current)

Minimum block (current: 2 hours):
Preferred time (current: Morning 9:00-12:00):
Max per day (current: 2 blocks):
```

### Step 5: Save Changes

If changes were made, update `memory/principles.md`:

```bash
# Use the Edit tool to update the file
# Preserve markdown structure
# Add "Last updated" timestamp
```

Confirm:

```
✓ Principles Updated

Changes saved to memory/principles.md

Modified:
  • Deep Work minimum block: 2 hours → 90 minutes
  • Daily task limit: 6 → 5

These changes will apply to future GPWK commands.
```

### Step 6: Specific Section View

If a section name is provided, show only that section:

```
/gpwk.principles delegation

📋 AI Delegation Principles

SAFE TO DELEGATE
  ✓ Research and information gathering
  ✓ Summarization and synthesis
  ✓ First drafts of documentation
  ✓ Boilerplate code generation
  ✓ Test case generation
  ✓ Data formatting and cleanup

KEEP PERSONAL
  ✗ Decisions with significant impact
  ✗ Relationship-dependent communication
  ✗ Creative direction and vision
  ✗ Anything requiring institutional knowledge
  ✗ Final reviews and approvals

DELEGATION REVIEW
  • Always review AI results before acting
  • AI work products need human polish

Run /gpwk.principles --edit to modify
```

## Principle Categories

Available sections:
- `time` - Time management (deep work, meetings, breaks)
- `tasks` - Task management (limits, carryover rules)
- `delegation` - AI delegation (safe/unsafe categories)
- `energy` - Energy management (task matching)
- `weekly` - Weekly rhythm (day-specific rituals)
- `review` - Review rituals (daily, weekly)

## How Principles Affect Commands

| Principle | Affects |
|-----------|---------|
| Daily task limit | `/gpwk.plan`, `/gpwk.triage` |
| Deep work windows | `/gpwk.plan` scheduling |
| Carryover thresholds | `/gpwk.carryover` warnings |
| Delegation criteria | `/gpwk.delegate` safety checks |
| Energy matching | `/gpwk.plan`, `/gpwk.triage` suggestions |

## Error Handling

- If principles file missing: Create from template
- If section not found: Suggest valid sections
- If invalid values: Prompt for correction
