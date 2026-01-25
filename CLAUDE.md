# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains **GitHub Personal Work Kit (GPWK)**, a Claude Code productivity system that uses GitHub Issues and Projects as the backend for task management while maintaining local daily logs for reflection.

GPWK is a **hybrid system**:
- **GitHub Issues** = Tasks, work items, and AI-delegatable work
- **GitHub Projects** = Kanban board with Inbox/Today/This Week/Backlog/Done columns
- **Local Logs** = Daily reflection, activity stream, and metrics in `gpwk/logs/`

## Commands

All commands require GitHub CLI (`gh`) to be installed and authenticated.

| Command | Purpose |
|---------|---------|
| `/gpwk.setup [repo]` | One-time setup: creates GitHub repo, project, labels, fields |
| `/gpwk.capture [task]` | Create GitHub issue from activity/task |
| `/gpwk.plan [today\|week]` | Generate daily plan from GitHub project |
| `/gpwk.triage` | Move issues between project columns |
| `/gpwk.breakdown [work]` | Create work item with parent + sub-issues |
| `/gpwk.delegate` | Execute AI-delegatable tasks, post results as comments |
| `/gpwk.complete ISSUE [--from TIME] [--to TIME]` | Mark task complete with time tracking and log updates |
| `/gpwk.search [QUERY] [--status\|--label\|--priority...]` | Search and query tasks with flexible filters |
| `/gpwk.review` | End-of-day reflection and metrics |
| `/gpwk.carryover` | Update carryover labels (pwk:c1/c2/c3) |
| `/gpwk.principles` | View/edit work principles |

## Task Notation

When capturing tasks, use markers:

```
/gpwk.capture fix login bug [P] !high ~deep
```

- `[AI]` - AI-delegatable task → `pwk:ai` label
- `[P]` - Personal/human-only task → `pwk:personal` label
- `!high` / `!medium` / `!low` - Priority
- `~deep` / `~shallow` / `~quick` - Energy level

## Key Files

| Path | Purpose |
|------|---------|
| `gpwk/memory/github-config.md` | GitHub project/field IDs (populated by setup) |
| `gpwk/memory/principles.md` | User's work style rules (daily limits, delegation criteria, etc.) |
| `gpwk/memory/goals.md` | Long-term goals referenced during planning |
| `gpwk/templates/` | Templates for issue bodies and daily logs |
| `gpwk/logs/` | Local daily reflection logs (gitignored) |
| `.claude/commands/gpwk.*.md` | Slash command definitions |

## GitHub Structure

### Labels
- Type: `pwk:task`, `pwk:ai`, `pwk:personal`, `pwk:work-item`, `pwk:capture`, `pwk:knowledge`
- Priority: `priority:high`, `priority:medium`, `priority:low`
- Energy: `energy:deep`, `energy:shallow`, `energy:quick`
- Carryover: `pwk:c1`, `pwk:c2`, `pwk:c3` (tracks incomplete task duration)
- Status: `status:blocked`, `status:waiting`, `status:ai-complete`

### Project Columns
Inbox → Today → This Week → Backlog → Done

## Daily Workflow

```
Morning:   /gpwk.triage → /gpwk.plan today
Day:       /gpwk.capture, /gpwk.search, /gpwk.complete, /gpwk.delegate, /gpwk.breakdown
Evening:   /gpwk.review → /gpwk.carryover
```

## AI Delegation

Tasks with `pwk:ai` label can be executed by Claude via `/gpwk.delegate`. Results are posted as issue comments with `status:ai-complete` label added for human review.

Safe to delegate: research, summarization, drafts, boilerplate, test generation.
Keep personal: decisions with impact, relationship tasks, creative direction, final approvals.

## Knowledge Capture

Tasks with both `pwk:ai` AND `pwk:knowledge` labels trigger automated research and documentation:

**Workflow**: `gpwk-knowledge-capture.yml`
- Performs internet research using WebSearch/WebFetch
- Creates documentation in `knowledge/{topic}/` directory
- Generates 3 files: README.md (human guide), technical-reference.md (AI/LLM), sources.md (research metadata)
- Commits directly to repository
- Posts results to issue with `status:ai-complete` label

**Usage**:
```bash
/gpwk.capture "Research {topic} patterns and best practices [AI]"
gh issue edit {ISSUE} --add-label "pwk:knowledge"
```

**Output**: Comprehensive documentation committed to `knowledge/{topic-name}/`
