# GPWK Breakdown

Decompose complex work into a parent issue with linked sub-issues.

## Arguments
- `$ARGUMENTS` - The work item to break down, or an existing issue number (#123)

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable to break down complex work. The Python backend handles:
- ✅ Fetching existing issue details from GitHub
- ✅ Analyzing work and generating structured breakdown
- ✅ Creating parent work item issue
- ✅ Creating linked sub-issues with proper labels
- ✅ Setting up parent-child relationships
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-breakdown "$ARGUMENTS"
```

That's it! The Python backend handles the entire breakdown workflow.

---

## What the Breakdown Does

You are breaking down complex work into manageable sub-issues. This creates a parent "work item" issue with linked child issues for each task.

### Step 3: Gather Context

If creating new, ask user for:
1. **Work item title**: What is this work about?
2. **Context**: Why is this work needed? What problem does it solve?
3. **Scope**: What's in scope? What's explicitly out of scope?
4. **Success criteria**: How do we know when this is done?

If breaking down existing issue, extract this from the issue body/comments.

### Step 4: Generate Breakdown

Analyze the work and break it into phases and tasks. Consider:
- Logical ordering and dependencies
- Mix of `[AI]` and `[P]` tasks where appropriate
- Appropriate granularity (each task should be completable in one session)

Create a structured breakdown:

```markdown
## Phase 1: Research & Discovery
- [AI] Research existing solutions and patterns
- [AI] Document current implementation
- [P] Review research and make architectural decisions

## Phase 2: Implementation
- [P] Set up project structure
- [P] Implement core functionality
- [AI] Generate unit tests for core functions

## Phase 3: Integration & Testing
- [P] Integrate with existing codebase
- [P] Manual testing and edge cases
- [AI] Generate integration tests

## Phase 4: Documentation & Cleanup
- [AI] Generate API documentation
- [P] Review and polish documentation
- [P] Final review and merge
```

### Step 5: Create Parent Issue

```bash
gh issue create \
  --repo <owner>/<repo> \
  --title "[Work Item] <title>" \
  --label "pwk:work-item" \
  --body "$(cat <<'EOF'
## Overview
<context and description>

## Scope
**In Scope:**
- <item>

**Out of Scope:**
- <item>

## Success Criteria
- [ ] <criterion>

## Phases
<!-- Sub-issues linked below -->

### Phase 1: Research & Discovery
- [ ] #TBD - Research existing solutions [AI]
- [ ] #TBD - Document current implementation [AI]
- [ ] #TBD - Review and decide architecture [P]

### Phase 2: Implementation
...

## Progress
- **Started**: <date>
- **Target**: <date if known>
- **Status**: In Progress

## Related
- Links to relevant code, docs, or other issues
EOF
)"
```

Capture the parent issue number.

### Step 6: Create Sub-Issues

For each task in the breakdown, create a linked sub-issue:

```bash
gh issue create \
  --repo <owner>/<repo> \
  --title "<task title>" \
  --label "<pwk:ai or pwk:personal>,<energy label>" \
  --body "$(cat <<'EOF'
## Parent Work Item
Part of #<parent-number>: <parent-title>

## Task
<description of what needs to be done>

## Phase
<phase name> (X of Y tasks in this phase)

## Acceptance Criteria
- [ ] <specific criterion>

## Notes
(Add notes as you work)
EOF
)"
```

### Step 7: Add Issues to Project

Add parent and all sub-issues to the project:

```bash
# Add parent issue
gh project item-add <project-number> --owner @me --url <parent-url>

# Set Type to work-item
gh project item-edit --project-id <project-number> --id <item-id> --field-id <type-field-id> --single-select-option-id <work-item-option-id>

# Add each sub-issue
for issue_url in <sub-issue-urls>; do
  gh project item-add <project-number> --owner @me --url $issue_url
  # Set Status to Backlog initially
  # Set Type based on [AI] or [P]
done
```

### Step 8: Update Parent with Links

Edit the parent issue to include actual sub-issue numbers:

```bash
gh issue edit <parent-number> --body "<updated body with real issue numbers>"
```

### Step 9: Confirm

Display summary:

```
✓ Work Item Created: #<parent-number>

<title>
https://github.com/<owner>/<repo>/issues/<parent-number>

Sub-issues created:
  Phase 1: Research & Discovery
    #201 - Research existing solutions [AI]
    #202 - Document current implementation [AI]
    #203 - Review and decide architecture [P]

  Phase 2: Implementation
    #204 - Set up project structure [P]
    #205 - Implement core functionality [P]
    #206 - Generate unit tests [AI]

  ...

Total: 12 sub-issues (4 AI-delegatable, 8 personal)

Next steps:
  • Run /gpwk.triage to schedule Phase 1 tasks
  • Run /gpwk.delegate to execute AI tasks
```

## Breaking Down Carried-Over Issues

When an issue has `pwk:c3` label (carried over 3+ times), suggest automatic breakdown:

```
⚠️ Issue #123 has been carried over 3 times.
This usually means it's too large for a single session.

Would you like to break it down into smaller tasks?
Run: /gpwk.breakdown #123
```

## Error Handling

- If parent issue creation fails: Report error, don't create orphan sub-issues
- If sub-issue creation fails: Log which ones succeeded, allow retry
- If project operations fail: Issues still created, manual project add needed

## Design Principles

- Each sub-issue should be completable in one work session
- First sub-issue in each phase should be independently startable
- AI tasks should come before decision points (research before decide)
- Dependencies are implicit through phase ordering
