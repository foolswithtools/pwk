# Personal Work Kit (PWK) Context Reference

> A Spec-Kit inspired framework for personal information management, daily task tracking, and AI-assisted work breakdown.

## What is Personal Work Kit?

Personal Work Kit (PWK) is a methodology and structure for managing daily activities using **Activity-Driven Development (ADD)**—where your captured activities become the source of truth for planning, task breakdown, and execution. It inverts reactive task management by making activity capture the primary artifact; tasks become expressions of observed work patterns.

## Core Philosophy

- **Capture First**: Log activities as they happen, process later
- **Carryover, Not Carry Burden**: Unfinished work flows to the next day, not your mental load
- **Breakdown for Clarity**: Complex work becomes actionable through decomposition
- **Hybrid Execution**: Tasks are explicitly personal or AI-delegated
- **Principles Over Productivity**: Your work style governs, not productivity dogma

## Directory Structure

```
personalworkkit/
├── .claude/commands/           # Slash commands for Claude Code
│   ├── pwk.capture.md          # Quick activity/thought capture
│   ├── pwk.log.md              # View and manage daily log
│   ├── pwk.breakdown.md        # Decompose work into tasks
│   ├── pwk.plan.md             # Plan day or week
│   ├── pwk.carryover.md        # Move incomplete to next day
│   ├── pwk.review.md           # Review completed work
│   ├── pwk.delegate.md         # Mark tasks for AI execution
│   └── pwk.principles.md       # Update personal work principles
├── memory/
│   └── principles.md           # Personal work style & principles
├── logs/
│   └── YYYY-MM-DD.md           # Daily activity logs
├── work/
│   └── [work-item-name]/       # Work item folders
│       ├── context.md          # What is this work about
│       ├── breakdown.md        # Task breakdown
│       └── progress.md         # Progress tracking
├── templates/
│   ├── daily-log.md            # Template for daily logs
│   ├── work-item.md            # Template for work items
│   ├── breakdown.md            # Template for task breakdown
│   └── principles.md           # Template for principles
└── inbox/
    └── quick-capture.md        # Unprocessed captures
```

## Slash Commands

### Daily Workflow Commands

| Command | Purpose |
|---------|---------|
| `/pwk.capture` | Quick capture an activity, thought, or task |
| `/pwk.log` | View today's log, add entries, see patterns |
| `/pwk.plan` | Plan today or this week based on carryover + new work |
| `/pwk.carryover` | Move incomplete items to next day's log |
| `/pwk.review` | End-of-day review of accomplishments |

### Work Breakdown Commands

| Command | Purpose |
|---------|---------|
| `/pwk.breakdown` | Take complex work and decompose into tasks |
| `/pwk.delegate` | Mark tasks as AI-executable and queue them |

### Meta Commands

| Command | Purpose |
|---------|---------|
| `/pwk.principles` | View or update personal work principles |

## Standard Workflow

### Morning Routine
1. `/pwk.carryover` → Review yesterday, move incomplete items
2. `/pwk.plan` → Plan today based on carryover + calendar + priorities

### Throughout the Day
3. `/pwk.capture "working on X"` → Log activities as they happen
4. `/pwk.breakdown [work-item]` → When work feels complex, break it down
5. `/pwk.delegate` → Identify tasks AI can handle

### End of Day
6. `/pwk.review` → See what was accomplished, reflect

## Activity Log Format

Each daily log (`logs/YYYY-MM-DD.md`) contains:

```markdown
# Daily Log: YYYY-MM-DD

## Carryover from Yesterday
- [ ] [C001] Incomplete task from yesterday

## Today's Plan
- [ ] [P001] Planned task for today

## Activity Stream
- 09:15 | Started working on API documentation
- 10:30 | Meeting: Sprint planning
- 11:00 | [BLOCKED] Waiting for design review

## Completed
- [x] [P001] Finished API documentation
- [x] [AD-HOC] Fixed urgent production bug

## Reflections
What went well? What blocked me? What to change?
```

## Task Notation

```
[ID] [Type] [Executor] Description
```

- **[ID]**: T001, T002, etc. (sequential)
- **[Type]**:
  - `[P]` - Personal (you must do it)
  - `[AI]` - AI-delegated (Claude can execute)
  - `[W]` - Waiting (blocked on someone/something)
  - `[C]` - Carryover (from previous day)
- **[Executor]**: Optional name/system for delegation

### Examples
```
- [ ] [T001] [P] Write performance review self-assessment
- [ ] [T002] [AI] Research best practices for React testing
- [ ] [T003] [W:design-team] Waiting for mockups
- [ ] [T004] [C] [P] Finish expense report from yesterday
```

## Work Item Structure

For complex work that spans multiple days:

```
work/api-documentation/
├── context.md      # Why this work exists, stakeholders, deadline
├── breakdown.md    # Tasks decomposed from this work
└── progress.md     # Daily updates, blockers, decisions
```

## Personal Principles

Your `memory/principles.md` defines how you work. Example articles:

1. **Deep Work Windows**: Protect 2-hour blocks for focused work
2. **Capture Before Process**: Log first, organize later
3. **Two-Minute Rule**: If it takes <2 min, do it now
4. **AI Delegation Criteria**: Delegate research, drafts, and boilerplate
5. **End-of-Day Shutdown**: Always run /pwk.review before stopping

## Comparison to Spec-Kit

| Spec-Kit | Personal Work Kit |
|----------|-------------------|
| Specification → Code | Activity → Tasks |
| Constitution | Principles |
| spec.md | context.md |
| plan.md | breakdown.md |
| tasks.md | daily log tasks |
| /speckit.implement | /pwk.delegate (AI tasks) |
| Feature branches | Work item folders |
| Checklists | Daily review |

## Key Concepts

### Capture vs. Process
- **Capture**: Raw activity logging (`/pwk.capture`)
- **Process**: Organizing captures into tasks (`/pwk.breakdown`)

### Carryover Chain
Incomplete tasks flow forward:
```
Day 1: Created → Day 2: [C] Carryover → Day 3: [C] Carryover → Completed
```

If a task carries over 3+ times, trigger `/pwk.breakdown` to decompose it.

### AI Delegation
Tasks marked `[AI]` can be executed by Claude:
- Research tasks
- Draft writing
- Code generation
- Data processing
- File organization

Personal tasks `[P]` require human judgment, relationships, or physical action.

## Getting Started

1. Copy this structure to your project
2. Run `/pwk.principles` to establish your work style
3. Each morning: `/pwk.carryover` then `/pwk.plan`
4. Throughout day: `/pwk.capture` as you work
5. End of day: `/pwk.review`

## Integration Points

- **Calendar**: Reference for time-blocked activities
- **Git/GitHub**: Work items can map to issues/PRs
- **Note-taking apps**: Inbox can sync from quick capture tools
- **AI Assistants**: Delegate tasks via /pwk.delegate
