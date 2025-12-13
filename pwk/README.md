# Personal Work Kit (PWK)

A markdown-based personal productivity system designed for [Claude Code](https://claude.ai/claude-code). PWK uses slash commands to capture activities, plan your day, and delegate tasks to AI.

## Philosophy

PWK is built on **Activity-Driven Development (ADD)**:

- **Capture First**: Log activities as they happen, process later
- **Carryover, Not Carry Burden**: Unfinished work flows to the next day
- **Breakdown for Clarity**: Complex work becomes actionable through decomposition
- **Hybrid Execution**: Tasks are either Personal `[P]` or AI-delegatable `[AI]`

## Installation

1. Copy this directory into your project:
   ```bash
   cp -r personalworkkit /path/to/your/project/
   ```

2. Open your project in VS Code with Claude Code extension

3. Start using slash commands (type `/pwk.` to see all commands)

## Commands

| Command | Purpose |
|---------|---------|
| `/pwk.capture [activity]` | Quick capture activity or thought |
| `/pwk.log [date]` | View and manage daily logs |
| `/pwk.plan [today\|week]` | Plan your day or week |
| `/pwk.breakdown [work]` | Decompose complex work into tasks |
| `/pwk.carryover` | Move incomplete tasks to today |
| `/pwk.review [--quick\|--full]` | End-of-day reflection |
| `/pwk.delegate [--list\|--execute]` | Manage AI-delegatable tasks |
| `/pwk.principles` | View/edit your work principles |

## Daily Workflow

```
Morning:
  /pwk.carryover    → Review yesterday's incomplete items
  /pwk.plan today   → Plan today's tasks

Throughout Day:
  /pwk.capture      → Log activities as you work
  /pwk.breakdown    → Break down complex tasks
  /pwk.delegate     → Queue AI tasks

Evening:
  /pwk.review       → Reflect and close out the day
```

## Directory Structure

```
personalworkkit/
├── .claude/commands/    # Slash command definitions
├── memory/              # Personal principles and goals
├── templates/           # Reusable markdown templates
├── logs/                # Daily activity logs (gitignored)
├── work/                # Multi-day work items (gitignored)
├── inbox/               # Quick capture area
└── pwk-context.md       # Comprehensive reference guide
```

## Task Notation

- `[P]` - Personal task (you must do it)
- `[AI]` - AI-delegatable (Claude can help)
- `[W:x]` - Waiting on something/someone
- `[C]` / `[C2]` / `[C3]` - Carryover count (3+ triggers breakdown)

## Getting Started

1. Run `/pwk.principles` to customize your work style
2. Run `/pwk.plan today` to create your first daily log
3. Use `/pwk.capture` throughout your day
4. End with `/pwk.review`

## Customization

Edit `memory/principles.md` to adjust:
- Deep work window duration
- Daily task limits
- Carryover thresholds
- Delegation criteria

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI or VS Code extension
- No other dependencies

## License

MIT
