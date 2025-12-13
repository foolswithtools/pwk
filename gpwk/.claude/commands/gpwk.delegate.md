# GPWK Delegate

Execute AI-delegatable tasks from GitHub Issues.

## Arguments
- `$ARGUMENTS` - Optional: `--list`, `--execute`, `--execute #123`, or specific issue number

## Instructions

You are managing and executing AI-delegatable tasks. These are issues labeled `pwk:ai` that Claude can work on autonomously.

### Step 1: Read Configuration

Read `memory/github-config.md` for repository details.
Read `memory/principles.md` for delegation criteria.

### Step 2: Parse Arguments

- `--list` or empty → List all AI-delegatable tasks
- `--execute` → Execute all pending AI tasks
- `--execute #123` → Execute specific issue
- `#123` → Execute specific issue

### Step 3: List AI Tasks (if --list or no args)

```bash
gh issue list \
  --repo <owner>/<repo> \
  --label "pwk:ai" \
  --state open \
  --json number,title,labels,body,createdAt \
  --limit 50
```

Display:

```
🤖 AI-Delegatable Tasks

Ready to Execute:
  #127 - Research caching strategies
  #129 - Generate API documentation
  #205 - Research existing auth solutions

In Progress (has comments):
  #131 - Summarize meeting notes (partial results posted)

Blocked:
  #133 - Generate test cases (waiting on #132 to complete first)

Run /gpwk.delegate --execute to run all ready tasks
Run /gpwk.delegate #127 to run a specific task
```

### Step 4: Execute AI Task(s)

For each task to execute:

#### 4a. Read the Issue

```bash
gh issue view <number> --repo <owner>/<repo> --json title,body,labels,comments
```

Extract:
- What needs to be done (from title and body)
- Any context from comments
- Parent work item if this is a sub-issue

#### 4b. Validate Delegation

Check against principles in `memory/principles.md`:

**Safe to delegate:**
- Research and information gathering
- Summarization and synthesis
- Drafting initial content
- Generating boilerplate code
- Creating documentation
- Writing tests from specifications

**Do NOT delegate (flag for human):**
- Decisions with significant impact
- Relationship-dependent tasks
- Creative direction choices
- Anything requiring human judgment

If task appears to need human judgment, warn and skip unless forced.

#### 4c. Execute the Task

Based on task type, execute appropriate actions:

**Research tasks:**
- Use web search to gather information
- Synthesize findings into structured notes
- Include sources and references

**Documentation tasks:**
- Read relevant code files
- Generate documentation following project conventions
- Include examples where appropriate

**Code generation tasks:**
- Understand requirements from issue
- Generate code following project patterns
- Include tests if appropriate

**Summarization tasks:**
- Read source material
- Create concise, actionable summary
- Highlight key points and decisions needed

#### 4d. Post Results as Comment

```bash
gh issue comment <number> --repo <owner>/<repo> --body "$(cat <<'EOF'
## AI Execution Results

**Executed by**: Claude (via GPWK)
**Date**: <timestamp>

### Summary
<brief summary of what was done>

### Results

<detailed results, findings, generated content>

### Sources/References
<if applicable>

### Suggested Next Steps
- <what should happen next>

---
*This task was executed by AI delegation. Review results and close if satisfactory.*
EOF
)"
```

#### 4e. Update Issue Status

If results are complete:
```bash
# Add label indicating AI work is done
gh issue edit <number> --add-label "status:ai-complete"

# Optionally move to a review column in project
```

If results are partial or need human review:
```bash
gh issue edit <number> --add-label "status:needs-review"
```

### Step 5: Update Local Log

Append to today's log:

```markdown
## AI Delegation Log
- HH:MM - Executed #127: Research caching strategies ✓
- HH:MM - Executed #129: Generate API documentation ✓
- HH:MM - Skipped #133: Waiting on dependency
```

### Step 6: Summary

After execution, display:

```
🤖 AI Delegation Complete

Executed:
  ✓ #127 - Research caching strategies (results posted)
  ✓ #129 - Generate API documentation (results posted)

Skipped:
  ⏭ #133 - Waiting on #132 (dependency)

Needs Human Review:
  ⚠ #131 - Results posted, needs your review

Next steps:
  • Review results: gh issue view 127
  • Close completed: gh issue close 127
  • Or run /gpwk.review to see today's summary
```

## Execution Modes

### Batch Mode (--execute)
Executes all ready AI tasks sequentially. Good for:
- Morning AI task processing
- Clearing the AI queue before end of day

### Single Task Mode (#123)
Executes one specific task. Good for:
- Urgent research needs
- Re-running a task with updated context

### Interactive Mode
If a task is ambiguous, ask clarifying questions before executing.

## Error Handling

- If issue not found: Report and continue with others
- If execution fails: Post error as comment, flag for human
- If rate limited: Pause and retry, or report partial completion
- Network issues: Save partial results locally, retry later

## Safety Guards

1. Never execute tasks that modify external systems
2. Never execute tasks that require credentials
3. Never post to issues in repositories you don't own
4. Always include "AI-generated" disclosure in comments
5. Flag tasks that seem to require human judgment
