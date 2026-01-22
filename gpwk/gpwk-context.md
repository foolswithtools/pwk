# GitHub Personal Work Kit (GPWK) Context Reference

> A GitHub-integrated framework for personal productivity, combining GitHub Issues and Projects for task management with local logs for reflection.

## What is GitHub Personal Work Kit?

GitHub Personal Work Kit (GPWK) is a **hybrid productivity system** that extends the Activity-Driven Development (ADD) methodology by using GitHub as the backend for tasks while maintaining local files for personal reflection. It leverages the `gh` CLI to bridge Claude Code commands with GitHub Issues, Projects, and Labels.

**Key Innovation**: Tasks live in GitHub (accessible anywhere, persistent, collaborative-ready), while daily reflections and work principles stay local (private, personal).

## Core Philosophy

- **Capture to GitHub**: Activities become issues instantly, not markdown files
- **Carryover via Labels**: `pwk:c1`, `pwk:c2`, `pwk:c3` labels track incomplete duration automatically
- **Triage Before Plan**: Inbox processing is a distinct step from daily planning
- **Hybrid Reflection**: Local logs reference GitHub issues for private journaling
- **Sub-Issues for Breakdown**: Complex work becomes parent issue + linked child issues
- **AI Results as Comments**: Delegated task outputs are posted directly to issues

## Directory Structure

```
gpwk/
├── .claude/commands/           # Slash commands for Claude Code
│   ├── gpwk.setup.md           # One-time GitHub setup
│   ├── gpwk.capture.md         # Create issue from task/activity
│   ├── gpwk.plan.md            # Generate daily plan from project
│   ├── gpwk.triage.md          # Move issues between columns
│   ├── gpwk.breakdown.md       # Create work item with sub-issues
│   ├── gpwk.delegate.md        # Execute AI tasks, post results
│   ├── gpwk.review.md          # End-of-day reflection and metrics
│   ├── gpwk.carryover.md       # Update carryover labels
│   └── gpwk.principles.md      # View/update work principles
├── memory/
│   ├── github-config.md        # Project IDs, field IDs, repo info
│   ├── principles.md           # Personal work style rules
│   └── goals.md                # Long-term goals
├── templates/
│   ├── daily-log.md            # Template for local reflection logs
│   └── issue-body.md           # Templates for GitHub issue bodies
├── logs/
│   └── YYYY-MM-DD.md           # Local daily reflection logs
└── README.md
```

## GitHub Structure

### Repository

Default: `my-work` (private repository)
- Contains: Nothing but issues and project
- Can be customized via `/gpwk.setup [repo-name]`

### Project: Personal Work Kit

A GitHub Project (v2) with these columns:

| Column | Purpose |
|--------|---------|
| Inbox | New captures awaiting triage |
| Today | Tasks scheduled for today |
| This Week | Tasks planned for this week |
| Backlog | Future tasks, low priority |
| Done | Completed tasks |

### Custom Fields

| Field | Type | Options |
|-------|------|---------|
| Type | Single Select | task, ai-task, work-item, capture |
| Priority | Single Select | high, medium, low |
| Energy | Single Select | deep, shallow, quick |
| Due | Date | Target completion date |

### Labels

```
# Task Types
pwk:task          # Standard task
pwk:ai            # AI-delegatable task
pwk:personal      # Human-only task
pwk:work-item     # Multi-day work item (parent)
pwk:capture       # Quick capture, needs triage

# Priority
priority:high     # Urgent/important
priority:medium   # Normal priority
priority:low      # Can wait

# Energy Required
energy:deep       # Requires focused time
energy:shallow    # Low cognitive load
energy:quick      # Under 15 minutes

# Carryover Tracking
pwk:c1            # Carried over 1 day
pwk:c2            # Carried over 2 days
pwk:c3            # Carried over 3+ days (needs breakdown)

# Status
status:blocked    # Waiting on dependency
status:waiting    # Waiting on external
status:ai-complete # AI work done, needs review
```

## Slash Commands

### Setup Command

| Command | Purpose |
|---------|---------|
| `/gpwk.setup [repo]` | Create GitHub repo, project, labels, fields |

### Daily Workflow Commands

| Command | Purpose |
|---------|---------|
| `/gpwk.capture [task]` | Create GitHub issue from activity/task |
| `/gpwk.triage` | Move issues from Inbox to Today/Week/Backlog |
| `/gpwk.plan [today\|week]` | Generate daily plan from GitHub + local log |
| `/gpwk.review` | End-of-day reflection, metrics, close issues |
| `/gpwk.carryover` | Update `pwk:c1/c2/c3` labels on open issues |

### Work Breakdown Commands

| Command | Purpose |
|---------|---------|
| `/gpwk.breakdown [work]` | Create parent issue + sub-issues |
| `/gpwk.delegate` | Execute `pwk:ai` tasks, post results as comments |

### Meta Commands

| Command | Purpose |
|---------|---------|
| `/gpwk.principles` | View or update personal work principles |

## Standard Workflow

### One-Time Setup
```
/gpwk.setup
# Creates: my-work repo, project, labels, fields
# Saves: Project IDs to memory/github-config.md
```

### Morning Routine
```
1. /gpwk.triage           → Process Inbox, move to Today/Week
2. /gpwk.plan today       → Create local log with GitHub issues
```

### Throughout the Day
```
3. /gpwk.capture [task]   → Create issue, add to project Inbox
4. /gpwk.breakdown [work] → Create parent + sub-issues for complex work
5. /gpwk.delegate         → Execute AI tasks, post results to issues
```

### End of Day
```
6. /gpwk.review           → Metrics, reflection, close issues
7. /gpwk.carryover        → Update c1/c2/c3 labels on open issues
```

## Task Notation

When capturing, use markers in the task description:

```
/gpwk.capture fix login bug [P] !high ~deep
```

### Type Markers
- `[AI]` → Creates issue with `pwk:ai` label
- `[P]` → Creates issue with `pwk:personal` label
- (none) → Creates issue with `pwk:capture` label (needs triage)

### Priority Markers
- `!high` or `!urgent` → `priority:high` label
- `!medium` → `priority:medium` label
- `!low` → `priority:low` label

### Energy Markers
- `~deep` → `energy:deep` label
- `~shallow` → `energy:shallow` label
- `~quick` → `energy:quick` label

### Examples
```
/gpwk.capture research React 19 features [AI]
→ Issue: "research React 19 features"
→ Labels: pwk:ai
→ Status: Inbox

/gpwk.capture fix authentication bug [P] !high ~deep
→ Issue: "fix authentication bug"
→ Labels: pwk:personal, priority:high, energy:deep
→ Status: Inbox

/gpwk.capture call John about project timeline
→ Issue: "call John about project timeline"
→ Labels: pwk:capture
→ Status: Inbox (needs triage to set type)
```

## Work Item Structure

For complex work spanning multiple days, `/gpwk.breakdown` creates:

### Parent Issue
```markdown
## [Work Item] API v3 Migration

## Overview
Migration from API v2 to v3...

## Scope
**In Scope:** ...
**Out of Scope:** ...

## Success Criteria
- [ ] All endpoints migrated
- [ ] Tests passing
- [ ] Documentation updated

## Phases
### Phase 1: Research & Discovery
- [ ] #201 - Research existing patterns [AI]
- [ ] #202 - Document current endpoints [AI]
- [ ] #203 - Architectural decision [P]

### Phase 2: Implementation
- [ ] #204 - Implement new endpoints [P]
...

## Progress
- **Started**: 2024-01-15
- **Status**: In Progress
```

### Sub-Issues
Each sub-issue:
- References parent: "Part of #200: API v3 Migration"
- Has appropriate `pwk:ai` or `pwk:personal` label
- Can be independently triaged and tracked

## Carryover Tracking

Unlike original PWK which copies tasks between daily logs, GPWK uses labels:

| Label | Meaning | Action |
|-------|---------|--------|
| (none) | New task | Normal handling |
| `pwk:c1` | Incomplete 1 day | Track |
| `pwk:c2` | Incomplete 2 days | Warning - check blockers |
| `pwk:c3` | Incomplete 3+ days | Breakdown recommended |

### Carryover Flow
```
Day 1: Created (no label)
Day 2: Still open → /gpwk.carryover adds pwk:c1
Day 3: Still open → /gpwk.carryover upgrades to pwk:c2
Day 4: Still open → /gpwk.carryover upgrades to pwk:c3
       → Suggests running /gpwk.breakdown #issue
```

## AI Delegation

Tasks with `pwk:ai` label can be executed by Claude:

```
/gpwk.delegate              # Execute all ready AI tasks
/gpwk.delegate #123         # Execute specific task
/gpwk.delegate --list       # Show AI task queue
```

### Execution Flow
1. Query: `gh issue list --label pwk:ai --state open`
2. Read: Issue body for context and requirements
3. Execute: Research, generate, summarize
4. Post: `gh issue comment #123 --body "## AI Results..."`
5. Label: Add `status:ai-complete` for human review

### Safe to Delegate
- Research and information gathering
- Summarization and synthesis
- First drafts of documentation
- Boilerplate code generation
- Test case generation

### Keep Personal
- Decisions with significant impact
- Relationship-dependent communication
- Creative direction and vision
- Final reviews and approvals

## Local Logs (Hybrid)

Even with GitHub as primary storage, local logs serve purposes:

### What Goes in Local Logs
- Activity stream (timestamped notes)
- Personal reflections
- Metrics and patterns
- Private notes about work

### Daily Log Format
```markdown
# Daily Log: 2024-01-15

## Activity Stream
- 09:15 - Started work, triaged inbox (#201, #202 moved to Today)
- 10:30 - Meeting: Sprint planning (captured #205)
- 11:00 - Executed AI tasks (#201, #202 complete)

## GitHub Summary
- In Today: #203, #204
- Completed: #201, #202
- Carried Over: #199 (now c2)

## Reflections
Good focus this morning. #199 keeps slipping - need to break it down.

## Tomorrow's Priority
#203 - Architectural decision (blocks Phase 2)
```

## Personal Principles

Your `memory/principles.md` defines how you work. Commands reference these.

### Example Principles
```markdown
## Time Management
- Deep Work: 2-hour minimum blocks, mornings preferred
- Daily limit: 6 significant tasks maximum
- Two-minute rule: Do it now if <2 min

## AI Delegation
- Delegate: Research, drafts, summaries, boilerplate
- Keep: Decisions, relationships, creative direction

## Carryover
- c2 threshold: Check for blockers
- c3 threshold: Mandatory breakdown consideration
```

## Comparison: PWK vs GPWK

| Aspect | PWK (Original) | GPWK (GitHub) |
|--------|----------------|---------------|
| Task storage | `logs/YYYY-MM-DD.md` | GitHub Issues |
| Status tracking | Log sections | Project columns |
| Carryover | Manual copy | `pwk:c1/c2/c3` labels |
| Work items | `work/[name]/` folders | Parent + sub-issues |
| AI results | Written to logs | Issue comments |
| Triage | Part of planning | Separate command |
| Multi-device | No | Yes |
| Collaboration | No | Possible |
| Offline | Full | Local logs only |

## Key Concepts

### Capture vs. Triage
- **Capture**: Create issue, add to Inbox (instant, no decisions)
- **Triage**: Move from Inbox to Today/Week/Backlog (deliberate scheduling)

### GitHub as Source of Truth
- All tasks exist as GitHub Issues
- Status = Project column position
- History = Issue timeline and comments
- Carryover = Label tracking

### Local as Reflection Layer
- Private activity stream
- Personal metrics and patterns
- Unshared reflections
- References issues by `#number`

## Getting Started

1. **Install Prerequisites**
   ```bash
   # Ensure GitHub CLI is installed and authenticated
   gh auth status
   ```

2. **Copy GPWK to Your Project**
   ```bash
   cp -r gpwk /path/to/your/project/
   ```

3. **Run Setup**
   ```
   /gpwk.setup
   # Or: /gpwk.setup my-custom-repo
   ```

4. **Configure Principles**
   ```
   /gpwk.principles --edit
   ```

5. **Start Working**
   ```
   /gpwk.capture my first task [P]
   /gpwk.triage
   /gpwk.plan today
   ```

## Integration Points

- **GitHub CLI**: All GitHub operations via `gh` command
- **GitHub.com**: View/edit tasks from any device
- **GitHub Mobile**: Quick capture and triage on the go
- **GitHub Actions**: Potential for automation (scheduled reminders, etc.)
- **Claude Code**: Executes all commands, handles AI delegation
- **Calendar**: Referenced for time blocking in `/gpwk.plan`

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI or VS Code extension
- [GitHub CLI](https://cli.github.com/) installed and authenticated
- GitHub account with Projects access
