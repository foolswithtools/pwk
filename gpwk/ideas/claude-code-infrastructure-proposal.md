# Claude Code Infrastructure for GPWK

**Proposal Date**: 2025-12-20
**Purpose**: Build specialized Claude Code agents and skills to make GPWK commands more robust

## Overview

Current GPWK commands are implemented as individual slash commands that execute bash directly. This leads to:
- Shell escaping issues
- No retry logic for API timing issues
- Verbose error handling in every command
- Duplication across commands

**Solution**: Build reusable Claude Code infrastructure

## Proposed Architecture

```
┌─────────────────────────────────────────────────────┐
│ User Commands (/gpwk.capture, /gpwk.plan, etc.)   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ GPWK Command Layer (.claude/commands/*.md)         │
│ - Parse user input                                  │
│ - Validate arguments                                │
│ - Call agents/skills                                │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ GPWK Skills Layer (.claude/skills/)                │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ gpwk.github-ops                             │   │
│ │ - Create issues with retry                  │   │
│ │ - Add to project atomically                 │   │
│ │ - Update project fields                     │   │
│ │ - Handle completed activities               │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ gpwk.log-ops                                │   │
│ │ - Update daily logs                         │   │
│ │ - Create log files from templates           │   │
│ │ - Parse log sections                        │   │
│ └─────────────────────────────────────────────┘   │
│                                                     │
│ ┌─────────────────────────────────────────────┐   │
│ │ gpwk.parser                                 │   │
│ │ - Parse capture notation ([AI], !high, etc.)│   │
│ │ - Detect completion status                  │   │
│ │ - Extract metadata                          │   │
│ └─────────────────────────────────────────────┘   │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│ Helper Library (gpwk/lib/github-helpers.sh)        │
│ - Shell functions with retry logic                 │
│ - Environment variable management                  │
│ - Utility functions                                │
└─────────────────────────────────────────────────────┘
```

## Component Specifications

### 1. Skill: `gpwk.github-ops`

**File**: `.claude/skills/gpwk.github-ops.md`

**Purpose**: Handle all GitHub Issue and Project operations

**Functions**:

#### `create_issue_and_setup_project()`
- Create GitHub issue with proper escaping
- Add to project
- Set all fields atomically (with retry)
- Return issue number and status

**Input Parameters**:
```json
{
  "title": "Issue title (any characters)",
  "labels": ["pwk:capture", "energy:quick"],
  "body": "Issue body markdown",
  "project_fields": {
    "status": "inbox" | "done" | "inprogress",
    "type": "capture" | "task" | "ai-task" | "work-item",
    "priority": "high" | "medium" | "low" | null,
    "energy": "deep" | "shallow" | "quick" | null
  },
  "should_close": false
}
```

**Output**:
```json
{
  "success": true,
  "issue_number": 45,
  "issue_url": "https://github.com/...",
  "project_item_id": "PVTI_...",
  "fields_set": ["status", "type", "energy"]
}
```

**Error Handling**:
- Retry up to 5 times with exponential backoff
- Validate GitHub CLI is authenticated
- Check repo/project exists
- Graceful degradation (issue created but fields not set)

#### `update_project_status()`
- Move issues between columns
- Bulk update support

#### `close_completed_issue()`
- Close issue
- Set status to Done
- Add completion comment

---

### 2. Skill: `gpwk.log-ops`

**File**: `.claude/skills/gpwk.log-ops.md`

**Purpose**: Manage daily log files

**Functions**:

#### `append_to_activity_stream()`
```json
{
  "date": "2025-12-20",
  "entry": {
    "time": "09:00-10:00",
    "issue_number": 45,
    "title": "Took Mr. Noodles for a walk",
    "tags": ["quick", "completed"]
  }
}
```

#### `create_daily_log()`
- Create log from template
- Populate with GitHub data
- Apply principles for scheduling

#### `update_log_section()`
- Update specific section (Activity Stream, Blockers, etc.)
- Preserve formatting

---

### 3. Skill: `gpwk.parser`

**File**: `.claude/skills/gpwk.parser.md`

**Purpose**: Parse GPWK notation and natural language

**Functions**:

#### `parse_capture_notation()`
**Input**: `"fix login bug [P] !high ~deep"`

**Output**:
```json
{
  "title": "fix login bug",
  "type": "task",
  "labels": ["pwk:personal", "priority:high", "energy:deep"],
  "project_fields": {
    "type": "task",
    "priority": "high",
    "energy": "deep"
  }
}
```

#### `detect_completion_status()`
**Input**: `"I took Mr. Noodles for a walk between 9-10 AM. This is complete."`

**Output**:
```json
{
  "is_completed": true,
  "title": "Took Mr. Noodles for a walk (9:00 AM - 10:00 AM)",
  "time_range": "09:00-10:00",
  "markers": ["past_tense", "explicit_complete", "time_range"]
}
```

**Detection Logic**:
- Past tense verbs: took, did, completed, finished, attended
- Explicit markers: "this is complete", "already done", "finished"
- Time ranges: "between X-Y", "from X to Y", "at X"

---

### 4. Helper Library: `gpwk/lib/github-helpers.sh`

**File**: `gpwk/lib/github-helpers.sh`

**Purpose**: Bash utilities for all GPWK commands

**Key Functions**:

```bash
#!/bin/bash

# Load configuration
gpwk_load_config() {
    # Parse gpwk/memory/github-config.md
    # Export environment variables
    export GPWK_REPO="clostaunau/personal-work"
    export GPWK_PROJECT="1"
    export GPWK_PROJECT_ID="PVT_..."
    # ... etc
}

# Retry with exponential backoff
gpwk_retry() {
    local max_attempts=$1
    shift
    local command="$@"
    local attempt=1
    local wait=1

    while [ $attempt -le $max_attempts ]; do
        if eval "$command"; then
            return 0
        fi

        if [ $attempt -lt $max_attempts ]; then
            sleep $wait
            wait=$((wait * 2))
        fi
        attempt=$((attempt + 1))
    done

    return 1
}

# Get project item ID with retry
gpwk_get_item_id() {
    local issue_number=$1

    gpwk_retry 5 \
        "gh project item-list \"$GPWK_PROJECT\" --owner @me --format json | \
         jq -r \".items[] | select(.content.number == $issue_number) | .id\" | \
         grep -q ."

    gh project item-list "$GPWK_PROJECT" --owner @me --format json | \
        jq -r ".items[] | select(.content.number == $issue_number) | .id"
}

# Safe issue creation (handles special characters)
gpwk_create_issue() {
    local title="$1"
    local labels="$2"
    local body="$3"

    # Create temporary file for body to avoid escaping issues
    local temp_body=$(mktemp)
    echo "$body" > "$temp_body"

    local url
    url=$(gh issue create \
        --repo "$GPWK_REPO" \
        --title "$title" \
        --label "$labels" \
        --body-file "$temp_body")

    rm "$temp_body"
    echo "$url"
}

# Set project field by name
gpwk_set_field() {
    local item_id="$1"
    local field_name="$2"
    local field_value="$3"

    # Map field names to IDs and values to option IDs
    # ... implementation
}
```

---

## Implementation Examples

### Example 1: Improved `/gpwk.capture`

**Before** (current):
```markdown
1. Parse input manually
2. Run gh issue create with inline bash
3. Try to get item ID (fails with special chars)
4. Try to set fields (timing issues)
5. Update log manually
```

**After** (with infrastructure):
```markdown
1. Call gpwk.parser skill to parse input
2. Call gpwk.github-ops skill to create and setup issue
3. Call gpwk.log-ops skill to update daily log
4. Display confirmation
```

**New Command**:
```markdown
### Instructions

1. Parse the capture input:
   - Use gpwk.parser skill: parse_capture_notation($ARGUMENTS)
   - Detect if completed: detect_completion_status($ARGUMENTS)

2. Create issue and setup project:
   - Use gpwk.github-ops skill: create_issue_and_setup_project()
   - Pass parsed metadata
   - If completed, set should_close=true

3. Update local log:
   - Use gpwk.log-ops skill: append_to_activity_stream()
   - Include issue number and metadata

4. Display confirmation with issue details
```

### Example 2: New `/gpwk.sync`

**Purpose**: Sync GitHub project state with local logs

```markdown
# GPWK Sync

Synchronize GitHub project data with local logs.

## Instructions

1. Use gpwk.github-ops skill to fetch all project items
2. Use gpwk.log-ops skill to parse today's log
3. Identify discrepancies:
   - Issues marked done in GitHub but not in log
   - Activities in log not in GitHub
4. Offer to sync both directions
```

---

## Benefits

### For Users
- ✅ **More reliable**: Retry logic handles API timing issues
- ✅ **Better errors**: Clear messages when things fail
- ✅ **Faster**: No debugging bash escaping issues
- ✅ **Richer features**: Can build more complex workflows

### For Developers
- ✅ **DRY**: No duplicate code across commands
- ✅ **Testable**: Skills can be tested independently
- ✅ **Maintainable**: Changes in one place affect all commands
- ✅ **Extensible**: Easy to add new commands

---

## Migration Path

### Phase 1: Build Foundation (Week 1)
- [ ] Create `gpwk/lib/github-helpers.sh`
- [ ] Test retry logic and escaping
- [ ] Create `gpwk.github-ops` skill
- [ ] Create `gpwk.parser` skill

### Phase 2: Migrate Commands (Week 2)
- [ ] Update `/gpwk.capture` to use new infrastructure
- [ ] Update `/gpwk.plan` to use log-ops skill
- [ ] Update `/gpwk.triage` to use github-ops skill
- [ ] Test all commands with edge cases

### Phase 3: New Features (Week 3+)
- [ ] Build `/gpwk.sync` command
- [ ] Add GraphQL support for atomic operations
- [ ] Create automated tests
- [ ] Performance monitoring

---

## Open Questions

1. **Should skills be blocking or async?**
   - Blocking: Wait for GitHub API
   - Async: Queue operations, confirm later

2. **Error recovery strategy?**
   - Rollback on failure?
   - Partial completion with manual fix?
   - Retry indefinitely with user prompt?

3. **Offline support?**
   - Queue captures when offline?
   - Sync when back online?

4. **Testing approach?**
   - Mock GitHub API?
   - Use test repository?
   - Automated integration tests?

---

## Recommendation

**Start with**:
1. Build `gpwk.github-ops` skill first (solves immediate pain)
2. Migrate `/gpwk.capture` as proof of concept
3. Validate with real usage for 1 week
4. Then build remaining skills and migrate other commands

This allows for iterative improvement and validates the architecture early.

---
*Proposal created: 2025-12-20*
