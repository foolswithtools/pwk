# GitHub Personal Work Kit (GPWK) C4 Architecture Diagrams

> C4 diagrams showing the architecture of GitHub Personal Work Kit at Context, Container, and Component levels.

## Table of Contents

1. [System Context Diagram](#1-system-context-diagram)
2. [Container Diagram](#2-container-diagram)
3. [Component Diagrams](#3-component-diagrams)

---

## 1. System Context Diagram

Shows GPWK and its interactions with users and external systems.

```mermaid
C4Context
    title C4 System Context Diagram for GitHub Personal Work Kit

    Person(user, "Knowledge Worker", "Captures activities, plans days, breaks down complex work, delegates to AI")

    System(gpwk, "GitHub Personal Work Kit", "Hybrid productivity system using GitHub Issues/Projects for tasks and local logs for reflection")

    System_Ext(github, "GitHub", "Issues, Projects, Labels - stores tasks and work items")
    System_Ext(aiAssistant, "AI Coding Assistant", "Claude Code - executes commands and AI-delegated tasks")
    System_Ext(ghCli, "GitHub CLI", "gh command - interface between GPWK and GitHub API")
    System_Ext(ide, "IDE/Editor", "VS Code, terminal - environment for executing commands")
    System_Ext(calendar, "Calendar", "Google Calendar, Outlook - provides time commitments")

    Rel(user, gpwk, "Captures, plans, triages, delegates")
    Rel(gpwk, github, "Creates issues, manages project, applies labels")
    Rel(gpwk, ghCli, "Executes gh commands")
    Rel(gpwk, aiAssistant, "Delegates research, drafts, and analysis")
    Rel(aiAssistant, github, "Posts results as issue comments")
    Rel(user, ide, "Executes /gpwk.* slash commands")
    Rel(ide, gpwk, "Triggers command execution")
    Rel(gpwk, calendar, "References for time blocking")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Context Elements

| Element | Type | Description |
|---------|------|-------------|
| Knowledge Worker | Person | Primary user managing their daily work and tasks |
| GitHub Personal Work Kit | System | Hybrid toolkit integrating GitHub for tasks with local reflection |
| GitHub | External | Issues for tasks, Projects for workflow, Labels for metadata |
| GitHub CLI | External | `gh` command for programmatic GitHub access |
| AI Coding Assistant | External | Executes delegated [AI] tasks, posts results |
| IDE/Editor | External | Environment where slash commands are executed |
| Calendar | External | Source of time commitments for planning |

---

## 2. Container Diagram

Shows the internal containers within GitHub Personal Work Kit.

```mermaid
C4Container
    title C4 Container Diagram for GitHub Personal Work Kit

    Person(user, "Knowledge Worker", "Manages daily activities and tasks")

    System_Boundary(gpwk, "GitHub Personal Work Kit") {
        Container(slashCmds, "Slash Command Definitions", "Markdown", "Prompt definitions for /gpwk.* commands in .claude/commands/")
        Container(templates, "Templates", "Markdown", "Templates for issue bodies and local logs")
        ContainerDb(localLogs, "Local Activity Logs", "File System", "Daily reflection logs in logs/YYYY-MM-DD.md")
        ContainerDb(memory, "Personal Memory", "File System", "Principles, goals, and GitHub config in memory/")
    }

    System_Ext(github, "GitHub") {
        ContainerDb(issues, "GitHub Issues", "GitHub API", "Tasks, work items, AI results as issues")
        ContainerDb(project, "GitHub Project", "GitHub API", "Kanban board: Inbox, Today, This Week, Backlog, Done")
        ContainerDb(labels, "GitHub Labels", "GitHub API", "pwk:*, priority:*, energy:*, status:* labels")
    }

    System_Ext(aiAssistant, "AI Coding Assistant", "Claude Code - processes commands")
    System_Ext(ghCli, "GitHub CLI", "gh command")
    System_Ext(ide, "IDE/Editor", "VS Code, terminal")

    Rel(user, ide, "Executes /gpwk.* commands")
    Rel(ide, slashCmds, "Reads command definitions")
    Rel(slashCmds, aiAssistant, "Provides structured prompts")

    Rel(aiAssistant, ghCli, "Executes gh issue/project commands")
    Rel(ghCli, issues, "Creates, updates, closes issues")
    Rel(ghCli, project, "Manages project items and status")
    Rel(ghCli, labels, "Applies and removes labels")

    Rel(aiAssistant, localLogs, "Writes daily reflections")
    Rel(aiAssistant, memory, "Reads principles and config")

    Rel(slashCmds, templates, "Uses for issue bodies")
    Rel(memory, ghCli, "Provides project/field IDs")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Container Descriptions

| Container | Technology | Description |
|-----------|------------|-------------|
| Slash Command Definitions | Markdown | 9 command files: setup, capture, plan, triage, breakdown, delegate, review, carryover, principles |
| Templates | Markdown | Templates for issue bodies, daily logs |
| Local Activity Logs | File System | `logs/YYYY-MM-DD.md` for daily reflection and activity stream |
| Personal Memory | File System | `memory/principles.md`, `memory/goals.md`, `memory/github-config.md` |
| GitHub Issues | GitHub API | Tasks as issues with labels for type, priority, energy, carryover |
| GitHub Project | GitHub API | Kanban board with status columns and custom fields |
| GitHub Labels | GitHub API | Taxonomy: `pwk:task`, `pwk:ai`, `priority:high`, `energy:deep`, `pwk:c1`, etc. |

### Data Flow

1. **Setup**: `/gpwk.setup` → `gh` creates repo, project, labels → saves config to memory/
2. **Capture**: `/gpwk.capture` → `gh issue create` → `gh project item-add` → appends to local log
3. **Triage**: `/gpwk.triage` → reads project Inbox → `gh project item-edit` moves to Today/Week/Backlog
4. **Plan**: `/gpwk.plan` → reads project "Today" column + principles → creates local daily log
5. **Breakdown**: `/gpwk.breakdown` → `gh issue create` parent + sub-issues → adds to project
6. **Delegate**: `/gpwk.delegate` → queries `pwk:ai` issues → AI executes → `gh issue comment` results
7. **Review**: `/gpwk.review` → queries closed issues → generates metrics → updates local log
8. **Carryover**: `/gpwk.carryover` → finds open "Today" issues → updates `pwk:c1/c2/c3` labels

---

## 3. Component Diagrams

### 3.1 Slash Command Components

```mermaid
C4Component
    title Component Diagram for GPWK Slash Commands

    Container_Boundary(slashCmds, "Slash Command Definitions") {
        Component(setup, "gpwk.setup.md", "Markdown", "One-time GitHub repo/project/labels setup")
        Component(capture, "gpwk.capture.md", "Markdown", "Create issue from activity/task")
        Component(triage, "gpwk.triage.md", "Markdown", "Move issues between project columns")
        Component(plan, "gpwk.plan.md", "Markdown", "Generate daily plan from GitHub + local log")
        Component(breakdown, "gpwk.breakdown.md", "Markdown", "Create work item with sub-issues")
        Component(delegate, "gpwk.delegate.md", "Markdown", "Execute AI tasks, post results")
        Component(review, "gpwk.review.md", "Markdown", "End-of-day metrics and reflection")
        Component(carryover, "gpwk.carryover.md", "Markdown", "Update carryover labels")
        Component(principles, "gpwk.principles.md", "Markdown", "View/update work principles")
    }

    Container_Ext(github, "GitHub", "Issues, Projects, Labels")
    Container_Ext(localLogs, "Local Logs", "logs/")
    Container_Ext(memory, "Personal Memory", "memory/")
    System_Ext(ai, "AI Assistant", "Claude Code")
    System_Ext(ghCli, "GitHub CLI", "gh")

    Rel(ai, setup, "Executes")
    Rel(ai, capture, "Executes")
    Rel(ai, triage, "Executes")
    Rel(ai, plan, "Executes")
    Rel(ai, breakdown, "Executes")
    Rel(ai, delegate, "Executes")
    Rel(ai, review, "Executes")
    Rel(ai, carryover, "Executes")
    Rel(ai, principles, "Executes")

    Rel(setup, ghCli, "Creates repo, project, labels")
    Rel(setup, memory, "Saves github-config.md")
    Rel(capture, ghCli, "Creates issue, adds to project")
    Rel(capture, localLogs, "Appends reference")
    Rel(triage, ghCli, "Moves items between columns")
    Rel(plan, ghCli, "Reads Today column")
    Rel(plan, localLogs, "Creates daily log")
    Rel(plan, memory, "Reads principles")
    Rel(breakdown, ghCli, "Creates parent + sub-issues")
    Rel(delegate, ghCli, "Queries AI issues, posts comments")
    Rel(review, ghCli, "Queries closed issues")
    Rel(review, localLogs, "Updates with reflection")
    Rel(carryover, ghCli, "Updates c1/c2/c3 labels")
    Rel(principles, memory, "Reads/writes principles")

    UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="1")
```

### Command Workflow

| Phase | Commands | Purpose |
|-------|----------|---------|
| Setup (once) | setup | Initialize GitHub infrastructure |
| Morning | triage → plan | Process inbox, create daily plan |
| Throughout Day | capture, breakdown, delegate | Work execution |
| End of Day | review → carryover | Reflect, update labels |
| Meta | principles | Configure work style |

---

### 3.2 GitHub Project Components

```mermaid
C4Component
    title Component Diagram for GitHub Project Structure

    Container_Boundary(project, "GitHub Project: Personal Work Kit") {
        Component(inbox, "Inbox Column", "Status", "New captures awaiting triage")
        Component(today, "Today Column", "Status", "Tasks scheduled for today")
        Component(week, "This Week Column", "Status", "Tasks planned for this week")
        Component(backlog, "Backlog Column", "Status", "Future tasks, low priority")
        Component(done, "Done Column", "Status", "Completed tasks")

        Component(typeField, "Type Field", "Single Select", "task, ai-task, work-item, capture")
        Component(priorityField, "Priority Field", "Single Select", "high, medium, low")
        Component(energyField, "Energy Field", "Single Select", "deep, shallow, quick")
        Component(dueField, "Due Field", "Date", "Target completion date")
    }

    Container_Ext(issues, "GitHub Issues", "Task storage")
    Container_Ext(slashCmds, "Slash Commands", "GPWK commands")
    System_Ext(ghCli, "GitHub CLI", "gh project commands")

    Rel(ghCli, inbox, "Adds new captures")
    Rel(ghCli, today, "Moves via /gpwk.triage")
    Rel(ghCli, week, "Moves via /gpwk.triage")
    Rel(ghCli, backlog, "Moves via /gpwk.triage")
    Rel(ghCli, done, "Moves when issue closed")

    Rel(issues, inbox, "Added to project")
    Rel(issues, typeField, "Categorized by type")
    Rel(issues, priorityField, "Prioritized")
    Rel(issues, energyField, "Energy-tagged")

    UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="1")
```

### Project Column Flow

```
New Capture → Inbox → (triage) → Today / This Week / Backlog → (complete) → Done
```

---

### 3.3 GitHub Labels Components

```mermaid
C4Component
    title Component Diagram for GitHub Labels Taxonomy

    Container_Boundary(labels, "GitHub Labels") {
        Component(typeLabels, "Type Labels", "Label Group", "pwk:task, pwk:ai, pwk:personal, pwk:work-item, pwk:capture")
        Component(priorityLabels, "Priority Labels", "Label Group", "priority:high, priority:medium, priority:low")
        Component(energyLabels, "Energy Labels", "Label Group", "energy:deep, energy:shallow, energy:quick")
        Component(carryoverLabels, "Carryover Labels", "Label Group", "pwk:c1, pwk:c2, pwk:c3")
        Component(statusLabels, "Status Labels", "Label Group", "status:blocked, status:waiting, status:ai-complete")
    }

    Container_Ext(issues, "GitHub Issues", "Task storage")
    Container_Ext(slashCmds, "Slash Commands", "GPWK commands")
    System_Ext(ghCli, "GitHub CLI", "gh issue commands")

    Rel(slashCmds, ghCli, "Applies labels")
    Rel(ghCli, typeLabels, "Sets on capture")
    Rel(ghCli, priorityLabels, "Sets on capture/triage")
    Rel(ghCli, energyLabels, "Sets on capture/triage")
    Rel(ghCli, carryoverLabels, "Updates via /gpwk.carryover")
    Rel(ghCli, statusLabels, "Updates based on state")

    Rel(issues, typeLabels, "Filtered by")
    Rel(issues, carryoverLabels, "Tracked by")

    UpdateLayoutConfig($c4ShapeInRow="5", $c4BoundaryInRow="1")
```

### Label Usage

| Label Category | Used By | Purpose |
|----------------|---------|---------|
| Type (`pwk:*`) | capture, delegate | Identify task nature |
| Priority (`priority:*`) | capture, triage, plan | Schedule by importance |
| Energy (`energy:*`) | capture, triage, plan | Match to energy levels |
| Carryover (`pwk:c1/c2/c3`) | carryover | Track incomplete duration |
| Status (`status:*`) | delegate, review | Flag special states |

---

### 3.4 Local Components (Hybrid)

```mermaid
C4Component
    title Component Diagram for Local Storage (Hybrid)

    Container_Boundary(local, "Local File System") {
        Component(dailyLog, "Daily Log", "logs/YYYY-MM-DD.md", "Activity stream, reflections, local metrics")
        Component(principles, "Principles", "memory/principles.md", "Work style rules and preferences")
        Component(goals, "Goals", "memory/goals.md", "Long-term goals and focus areas")
        Component(config, "GitHub Config", "memory/github-config.md", "Project number, field IDs, repo info")
    }

    Container_Ext(github, "GitHub", "Issues and Project")
    Container_Ext(slashCmds, "Slash Commands", "GPWK commands")
    System_Ext(ai, "AI Assistant", "Claude Code")

    Rel(ai, dailyLog, "Creates via /gpwk.plan")
    Rel(ai, dailyLog, "Updates via /gpwk.capture, /gpwk.review")
    Rel(ai, principles, "Reads for all commands")
    Rel(ai, principles, "Updates via /gpwk.principles")
    Rel(ai, goals, "Reads for planning")
    Rel(ai, config, "Reads for GitHub API calls")
    Rel(slashCmds, config, "Uses project/field IDs")

    Rel(dailyLog, github, "References issues by #number")
    Rel(config, github, "Maps to project structure")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

### Local vs GitHub Split

| Local (Private) | GitHub (Shared/Persistent) |
|-----------------|---------------------------|
| Daily reflections | Tasks and work items |
| Activity stream | Status and progress |
| Personal metrics | Carryover tracking |
| Work principles | AI execution results |
| Configuration | Labels and metadata |

---

### 3.5 Work Item (Sub-Issues) Structure

```mermaid
C4Component
    title Component Diagram for Work Item Breakdown

    Container_Boundary(workItem, "Work Item (GitHub Issues)") {
        Component(parent, "Parent Issue", "[Work Item] Title", "Overview, scope, success criteria, sub-issue links")
        Component(phase1, "Phase 1 Sub-Issues", "Issues", "Research and discovery tasks")
        Component(phase2, "Phase 2 Sub-Issues", "Issues", "Implementation tasks")
        Component(phase3, "Phase 3 Sub-Issues", "Issues", "Testing and integration tasks")
        Component(phase4, "Phase 4 Sub-Issues", "Issues", "Documentation and cleanup tasks")
    }

    Container_Ext(project, "GitHub Project", "Kanban board")
    Container_Ext(slashCmds, "Slash Commands", "GPWK commands")
    System_Ext(ghCli, "GitHub CLI", "gh issue commands")

    Rel(slashCmds, ghCli, "Creates via /gpwk.breakdown")
    Rel(ghCli, parent, "Creates parent issue")
    Rel(ghCli, phase1, "Creates sub-issues")
    Rel(ghCli, phase2, "Creates sub-issues")
    Rel(ghCli, phase3, "Creates sub-issues")
    Rel(ghCli, phase4, "Creates sub-issues")

    Rel(phase1, parent, "Part of #parent")
    Rel(phase2, parent, "Part of #parent")
    Rel(phase3, parent, "Part of #parent")
    Rel(phase4, parent, "Part of #parent")

    Rel(parent, project, "Added to Backlog")
    Rel(phase1, project, "Triaged to Today/Week")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

### Work Item Lifecycle

```
1. Created: /gpwk.breakdown creates parent issue + sub-issues
2. Linked: Sub-issues reference parent with "Part of #123"
3. Phased: Sub-issues organized by execution phase
4. Triaged: Phase 1 tasks moved to Today via /gpwk.triage
5. Executed: Mix of [AI] and [P] tasks completed
6. Tracked: Parent issue body updated with progress
7. Completed: Parent closed when all sub-issues done
```

---

## Comparison: PWK vs GPWK Architecture

| Aspect | PWK (Original) | GPWK (GitHub-Integrated) |
|--------|----------------|--------------------------|
| **Task Storage** | Local markdown (`logs/`) | GitHub Issues |
| **Status Tracking** | Manual in log sections | GitHub Project columns |
| **Carryover** | Copy to next day's log | `pwk:c1/c2/c3` labels |
| **Work Items** | `work/[name]/` folders | Parent issue + sub-issues |
| **AI Results** | Written to logs | Posted as issue comments |
| **Daily Logs** | Primary artifact | Supplementary reflection |
| **Triage** | Part of /pwk.plan | Dedicated /gpwk.triage |
| **Multi-device** | No | Yes (via github.com) |
| **Collaboration** | No | Optional (share repo) |
| **Offline** | Full functionality | Local logs only |

---

## Integration Architecture

```mermaid
C4Context
    title GPWK Integration Flow

    Person(user, "Knowledge Worker")

    System(gpwk, "GPWK Commands", "/gpwk.* slash commands")
    System(claude, "Claude Code", "AI Assistant executing commands")
    System_Ext(ghCli, "GitHub CLI", "gh command interface")
    System_Ext(github, "GitHub", "Issues, Projects, Labels")
    System_Ext(local, "Local FS", "logs/, memory/")

    Rel(user, gpwk, "Runs /gpwk.* commands")
    Rel(gpwk, claude, "Interpreted by")
    Rel(claude, ghCli, "Executes gh commands")
    Rel(ghCli, github, "API calls")
    Rel(claude, local, "File operations")
    Rel(local, github, "References by #number")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

---

## References

- [GitHub Personal Work Kit Context](./gpwk-context.md)
- [Original PWK C4 Diagrams](../pwk-c4-diagrams.md)
- [C4 Model](https://c4model.com/)
- [GitHub CLI Documentation](https://cli.github.com/manual/)
