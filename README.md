# Personal Work Kit

A collection of productivity systems for [Claude Code](https://claude.ai/claude-code) built on **Activity-Driven Development (ADD)** — where captured activities become the source of truth for planning, task breakdown, and execution.

## Systems

This repository contains two variants:

| System | Description | Best For |
|--------|-------------|----------|
| **[PWK](./pwk/)** | Local markdown-based system | Single device, offline, privacy-focused |
| **[GPWK](./gpwk/)** | GitHub-integrated hybrid system | Multi-device, collaboration, persistent tracking |

### PWK (Personal Work Kit)

The original local-only system using markdown files:
- Tasks stored in `logs/YYYY-MM-DD.md`
- Work items in `work/[name]/` folders
- Manual carryover between days
- Fully offline capable

```bash
# To use PWK, copy to your project:
cp -r pwk /path/to/your/project/
```

[→ PWK Documentation](./pwk/README.md)

### GPWK (GitHub Personal Work Kit)

GitHub-integrated variant using Issues and Projects:
- Tasks as GitHub Issues
- Status via Project columns (Inbox, Today, This Week, Backlog, Done)
- Carryover tracking via labels (`pwk:c1`, `pwk:c2`, `pwk:c3`)
- Local logs for private reflection (hybrid approach)
- Access from any device via github.com

```bash
# To use GPWK, copy to your project:
cp -r gpwk /path/to/your/project/

# Then run setup:
/gpwk.setup
```

[→ GPWK Documentation](./gpwk/README.md)

## Comparison

| Feature | PWK | GPWK |
|---------|-----|------|
| Task storage | Local markdown | GitHub Issues |
| Status tracking | Log sections | Project columns |
| Carryover | Manual copy | Label-based (`c1/c2/c3`) |
| Work items | Local folders | Parent + sub-issues |
| AI results | Written to logs | Issue comments |
| Multi-device | No | Yes |
| Offline | Full | Local logs only |
| Collaboration | No | Possible |

## Core Philosophy

Both systems share the same principles:

- **Capture First**: Log activities as they happen, process later
- **Carryover, Not Carry Burden**: Unfinished work flows forward, not mental load
- **Breakdown for Clarity**: Complex work becomes actionable through decomposition
- **Hybrid Execution**: Tasks are explicitly personal `[P]` or AI-delegatable `[AI]`
- **Principles Over Productivity**: Your work style governs, not external dogma

## Shared Resources

| File | Purpose |
|------|---------|
| [c4-model-context.md](./c4-model-context.md) | C4 architecture model reference |
| [c4-model-prompts.md](./c4-model-prompts.md) | Prompts for creating C4 diagrams |

## Requirements

- [Claude Code](https://claude.ai/claude-code) CLI or VS Code extension
- For GPWK: [GitHub CLI](https://cli.github.com/) (`gh`) installed and authenticated

## License

MIT
