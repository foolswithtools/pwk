# GitHub API Error Analysis & GPWK Improvement Proposals

**Date**: 2025-12-20
**Context**: Analysis of errors during `/gpwk.capture` execution

## Errors Encountered

### 1. Shell Parse Error with Parentheses in Issue Title
```bash
ITEM_ID=$(gh project item-list 1 --owner @me --format json | jq -r '.items[] | select(.content.url == "https://github.com/clostaunau/personal-work/issues/45") | .id')
```
**Error**: `(eval):1: parse error near '('`

**Root Cause**: Issue title contained parentheses: "Took Mr. Noodles (My Dog) for a walk..."
- When the URL is used in complex bash commands with command substitution, special characters can break shell parsing
- The parentheses in the title text confused the shell parser despite being inside a string

**Impact**: Failed to retrieve project item ID, preventing field updates

### 2. Timing/Synchronization Issues
Multiple attempts to find issue #45 in project returned empty results:
```bash
gh project item-list 1 --owner @me --format json | jq -r '.items[] | select(.content.number == 45) | .id'
# Output: (empty)
```

**Root Cause**:
- GitHub's `gh project item-add` command may complete before the item is fully synced/indexed
- The project item list API might have eventual consistency
- No retry logic to wait for synchronization

**Impact**: Unable to set project fields (Status, Type, Energy)

### 3. Lack of Completed Activity Workflow
The current `/gpwk.capture` flow assumes all captures are future tasks going to "Inbox":
- No support for "this is already done" captures
- Workaround: Created issue, then manually closed it
- Fields never got set properly (Status=Done, Type=capture, Energy=quick)

**Root Cause**: Command design didn't account for logging completed activities

**Impact**: Completed activities don't get proper metadata, inconsistent project state

### 4. Multi-Step Workflow Fragility
Current flow requires 4+ separate API calls:
1. Create issue
2. Add issue to project
3. Get project item ID
4. Set Status field
5. Set Type field
6. Set Priority field (if applicable)
7. Set Energy field (if applicable)

**Impact**: Any failure in the chain breaks the whole workflow, partial state updates

## Proposed Solutions

### Solution 1: GPWK Core Agent (Recommended)
**Create**: `.claude/skills/gpwk-core-agent.md`

**Purpose**: Specialized Claude Code agent that handles all GitHub operations with:
- Robust error handling and retry logic
- Proper shell escaping for special characters
- Synchronization handling (polling with backoff)
- Support for completed activities
- Atomic-like operations with rollback on failure

**Capabilities**:
```markdown
- create_issue(title, labels, body, status="inbox"|"done")
- add_to_project_with_fields(issue_url, fields_dict)
- update_project_item(item_id, fields_dict)
- find_project_item_with_retry(issue_number, max_retries=5)
- parse_capture_notation(text) → {title, labels, fields, is_completed}
- log_to_daily_file(date, activity_entry)
```

**Benefits**:
- Encapsulates all GitHub complexity
- Reusable across all GPWK commands
- Better error messages and debugging
- Consistent behavior

### Solution 2: GitHub Helper Library
**Create**: `gpwk/lib/github-helpers.sh`

**Purpose**: Bash functions with built-in retry logic and error handling

**Example Functions**:
```bash
#!/bin/bash

# Create issue and add to project with fields in one call
gpwk_create_and_setup() {
    local title="$1"
    local labels="$2"
    local body="$3"
    local status="${4:-inbox}"
    local type="${5:-capture}"
    local priority="$6"
    local energy="$7"

    # Create issue with proper escaping
    local issue_url
    issue_url=$(gh issue create \
        --repo "$GPWK_REPO" \
        --title "$title" \
        --label "$labels" \
        --body "$body")

    local issue_number
    issue_number=$(echo "$issue_url" | grep -oE '[0-9]+$')

    # Add to project
    gh project item-add "$GPWK_PROJECT" --owner @me --url "$issue_url"

    # Wait and retry to get item ID
    local item_id
    item_id=$(gpwk_get_item_id_with_retry "$issue_number" 5)

    if [ -z "$item_id" ]; then
        echo "Warning: Could not set project fields for issue #$issue_number"
        return 1
    fi

    # Set fields
    gpwk_set_project_fields "$item_id" "$status" "$type" "$priority" "$energy"

    echo "$issue_url"
}

# Get item ID with exponential backoff retry
gpwk_get_item_id_with_retry() {
    local issue_number="$1"
    local max_retries="${2:-5}"
    local retry=0
    local wait=1

    while [ $retry -lt $max_retries ]; do
        local item_id
        item_id=$(gh project item-list "$GPWK_PROJECT" --owner @me --format json | \
            jq -r ".items[] | select(.content.number == $issue_number) | .id")

        if [ -n "$item_id" ]; then
            echo "$item_id"
            return 0
        fi

        sleep "$wait"
        retry=$((retry + 1))
        wait=$((wait * 2))
    done

    return 1
}

# Set multiple project fields
gpwk_set_project_fields() {
    local item_id="$1"
    local status="$2"
    local type="$3"
    local priority="$4"
    local energy="$5"

    # Set status
    if [ -n "$status" ]; then
        local status_option_id
        case "$status" in
            inbox) status_option_id="f75ad846" ;;
            inprogress) status_option_id="47fc9ee4" ;;
            done) status_option_id="98236657" ;;
        esac

        gh project item-edit \
            --project-id "$GPWK_PROJECT_ID" \
            --id "$item_id" \
            --field-id "$GPWK_STATUS_FIELD_ID" \
            --single-select-option-id "$status_option_id"
    fi

    # Set type
    if [ -n "$type" ]; then
        local type_option_id
        case "$type" in
            task) type_option_id="d7fb4fc4" ;;
            ai-task) type_option_id="24aa72b8" ;;
            work-item) type_option_id="be8fd513" ;;
            capture) type_option_id="6d17e1d4" ;;
        esac

        gh project item-edit \
            --project-id "$GPWK_PROJECT_ID" \
            --id "$item_id" \
            --field-id "$GPWK_TYPE_FIELD_ID" \
            --single-select-option-id "$type_option_id"
    fi

    # Set priority if provided
    # Set energy if provided
    # ... similar pattern
}
```

**Benefits**:
- Reusable across commands
- Shell-based (no new dependencies)
- Easy to debug and modify
- Can be sourced by all GPWK commands

### Solution 3: Enhanced Capture Command
**Modify**: `.claude/commands/gpwk.capture.md`

**Add support for**:
- **Completion marker**: Detect past tense or "complete" keyword
  - "I took..." → completed activity
  - "...this is complete" → completed activity
  - "...between X-Y" → completed activity with timeframe

- **Better error handling**: Clear messages when things fail
- **Retry logic**: Built into the command instructions
- **Validation**: Verify issue was created and fields were set

**Example Detection**:
```markdown
### Detect Completion Status

Parse the input for completion indicators:
- Past tense verbs: "took", "completed", "finished", "did"
- Explicit markers: "this is complete", "already done"
- Time ranges: "between 9:00-10:00" suggests completed

If completed:
- Create issue and immediately close it
- Set Status = "Done" in project
- Log to Activity Stream section instead of Plan section
```

### Solution 4: GitHub GraphQL API Migration
**Create**: `gpwk/lib/graphql-operations.sh` or agent

**Purpose**: Use GitHub GraphQL API for atomic operations

**Benefits**:
- Can create issue + add to project + set fields in ONE API call
- Better error handling
- Faster (fewer round trips)
- More reliable

**Example GraphQL Mutation**:
```graphql
mutation CreateIssueAndAddToProject {
  createIssue(input: {
    repositoryId: "R_..."
    title: "Task title"
    body: "Task body"
    labelIds: ["LA_...", "LA_..."]
  }) {
    issue {
      id
      number
      url
    }
  }

  addProjectV2ItemById(input: {
    projectId: "PVT_..."
    contentId: $issueId
  }) {
    item {
      id
    }
  }

  updateProjectV2ItemFieldValue(input: {
    projectId: "PVT_..."
    itemId: $itemId
    fieldId: "PVTSSF_..."
    value: { singleSelectOptionId: "..." }
  }) {
    projectV2Item {
      id
    }
  }
}
```

## Recommended Implementation Plan

### Phase 1: Quick Wins (1-2 hours)
1. Create `gpwk/lib/github-helpers.sh` with retry logic
2. Update `/gpwk.capture` to detect completed activities
3. Add proper error messages to all commands

### Phase 2: GPWK Core Agent (2-4 hours)
1. Create `.claude/skills/gpwk-core.md` agent
2. Migrate common operations to the agent
3. Update all GPWK commands to use the agent
4. Add comprehensive error handling

### Phase 3: GraphQL Migration (4-6 hours)
1. Research GitHub GraphQL API for Projects V2
2. Create GraphQL operation templates
3. Implement atomic issue creation + project setup
4. Test and validate

## Testing Checklist

### Test Cases for Improved System
- [ ] Capture with parentheses in title: `Buy food for (Mr. Noodles) the dog`
- [ ] Capture with quotes: `Review "The Pragmatic Programmer" book`
- [ ] Capture with special chars: `Fix bug: login fails with @#$% characters`
- [ ] Completed activity: `I walked the dog between 9-10 AM. This is complete.`
- [ ] Future task: `Schedule dentist appointment next week`
- [ ] AI task with all markers: `Research AWS pricing [AI] !high ~deep`
- [ ] Network failure during project add
- [ ] Rate limiting from GitHub API
- [ ] Concurrent captures (multiple issues at once)

## Metrics to Track

After implementation:
- **Success rate**: % of captures that fully complete vs. partial failures
- **Retry count**: How often retry logic is needed
- **Error types**: Categorize failures (network, timing, parsing, etc.)
- **Performance**: Time to complete capture operation

## Questions for User

1. **Preference**: Would you prefer a Claude Code Agent or shell library approach?
2. **Migration**: Should we migrate all commands at once or incrementally?
3. **GraphQL**: Interested in GraphQL for better atomicity, or stick with `gh` CLI?
4. **Testing**: Want automated tests for GPWK commands?

## Next Steps

Recommend starting with:
1. Build the shell helper library (`gpwk/lib/github-helpers.sh`)
2. Create a GPWK Core Agent for complex operations
3. Update `/gpwk.capture` to use the new infrastructure
4. Test with various edge cases
5. Roll out to other commands

---
*Analysis completed: 2025-12-20*
