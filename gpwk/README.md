# GitHub Personal Work Kit (GPWK)

A GitHub-integrated personal productivity system for [Claude Code](https://claude.ai/claude-code). GPWK uses GitHub Issues and Projects as the backend while maintaining local daily logs for reflection.

## How It Works

GPWK is a **hybrid system**:
- **GitHub Issues** = Your tasks, work items, and AI-delegatable work
- **GitHub Projects** = Kanban-style view with Today/This Week/Backlog columns
- **Local Logs** = Daily reflection, activity stream, and metrics

The `gh` CLI bridges Claude Code commands to your GitHub repository.

## Installation

1. **Copy GPWK to your project:**
   ```bash
   cp -r gpwk /path/to/your/project/
   ```

2. **Ensure GitHub CLI is installed and authenticated:**
   ```bash
   gh auth status
   # If not authenticated: gh auth login
   ```

3. **Run setup:**
   ```
   /gpwk.setup
   # Or specify a custom repo:
   /gpwk.setup my-personal-tasks
   ```

   This creates:
   - A `personal-work` repository (or uses existing)
   - A GitHub Project with status columns
   - Labels for task types, priority, energy, and carryover

4. **Customize your principles:**
   ```
   /gpwk.principles --edit
   ```

## Commands

| Command | Purpose |
|---------|---------|
| `/gpwk.setup [repo]` | One-time GitHub setup |
| `/gpwk.capture [task]` | Create issue from activity/task |
| `/gpwk.plan [today\|week]` | Generate daily plan from GitHub |
| `/gpwk.triage` | Move issues between columns |
| `/gpwk.breakdown [work]` | Create work item with sub-issues |
| `/gpwk.delegate` | Execute AI-delegatable tasks |
| `/gpwk.review` | End-of-day reflection and metrics |
| `/gpwk.carryover` | Update carryover labels |
| `/gpwk.principles` | View/edit work principles |

## Daily Workflow

```
Morning:
  /gpwk.triage          → Process inbox, schedule today
  /gpwk.plan today      → Generate daily plan

Throughout Day:
  /gpwk.capture [task]  → Quick capture to GitHub
  /gpwk.delegate        → Execute AI tasks
  /gpwk.breakdown       → Break down complex work

Evening:
  /gpwk.review          → Reflect, capture metrics
  /gpwk.carryover       → Update carryover labels
```

## Task Notation

When capturing tasks, use these markers:

```
/gpwk.capture fix login bug [P] !high ~deep
```

- `[AI]` - AI-delegatable task
- `[P]` - Personal task (human only)
- `!high` / `!medium` / `!low` - Priority
- `~deep` / `~shallow` / `~quick` - Energy level

## GitHub Structure

### Labels Created
```
pwk:task        - Standard task
pwk:ai          - AI-delegatable
pwk:personal    - Human-only task
pwk:work-item   - Multi-day work item
pwk:capture     - Needs triage
pwk:c1/c2/c3    - Carryover count
priority:*      - Priority levels
energy:*        - Energy requirements
```

### Project Columns
```
Inbox      → Uncategorized captures
Today      → Scheduled for today
This Week  → Planned for this week
Backlog    → Future work
Done       → Completed
```

## Carryover Tracking

Issues track how many days they've been carried over:
- `pwk:c1` - First carryover (normal)
- `pwk:c2` - Second carryover (warning)
- `pwk:c3` - Third+ carryover (needs breakdown)

When an issue reaches `c3`, GPWK suggests running `/gpwk.breakdown` to decompose it.

## AI Delegation

Tasks marked `[AI]` can be executed by Claude:

```
/gpwk.capture research React 19 features [AI]
/gpwk.delegate --execute
```

Results are posted as comments on the issue.

**Safe to delegate:**
- Research and information gathering
- Summarization and drafts
- Documentation generation
- Test case creation

**Keep personal:**
- Decisions with impact
- Relationship-based tasks
- Creative direction

## Directory Structure

```
gpwk/
├── .claude/commands/     # Slash command definitions
│   ├── gpwk.setup.md
│   ├── gpwk.capture.md
│   ├── gpwk.plan.md
│   ├── gpwk.triage.md
│   ├── gpwk.breakdown.md
│   ├── gpwk.delegate.md
│   ├── gpwk.review.md
│   ├── gpwk.carryover.md
│   └── gpwk.principles.md
├── memory/
│   ├── github-config.md  # GitHub project/field IDs
│   ├── principles.md     # Your work preferences
│   └── goals.md          # Long-term goals
├── templates/
│   ├── daily-log.md      # Local log template
│   └── issue-body.md     # Issue templates
├── logs/                 # Local daily logs (gitignored)
└── README.md
```

## Hybrid Approach Benefits

**From GitHub:**
- Tasks persist automatically (no carryover command needed for basic tracking)
- Access from any device
- Full history and audit trail
- Link tasks to code, PRs, commits
- Share with collaborators if needed

**From Local Logs:**
- Private reflection space
- Activity stream throughout day
- Metrics and patterns
- No clutter in GitHub

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI or VS Code extension
- [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated
- A GitHub account

## Customization

Edit `memory/principles.md` to adjust:
- Daily task limits
- Deep work preferences
- Carryover thresholds
- Delegation criteria
- Energy matching rules

## Comparison with PWK

| Feature | PWK (Original) | GPWK (This) |
|---------|----------------|-------------|
| Task storage | Local markdown | GitHub Issues |
| Project view | None | GitHub Projects |
| Multi-device | No | Yes |
| Collaboration | No | Yes |
| Daily logs | Local | Local (hybrid) |
| AI delegation | Local execution | Posts to GitHub |
| Carryover | Manual | Label-based |

## License

MIT
