# Personal Work Kit (PWK) C4 Architecture Diagrams

> C4 diagrams showing the architecture of Personal Work Kit at Context, Container, and Component levels.

## Table of Contents

1. [System Context Diagram](#1-system-context-diagram)
2. [Container Diagram](#2-container-diagram)
3. [Component Diagrams](#3-component-diagrams)

---

## 1. System Context Diagram

Shows PWK and its interactions with users and external systems.

```mermaid
C4Context
    title C4 System Context Diagram for Personal Work Kit

    Person(user, "Knowledge Worker", "Captures activities, plans days, breaks down complex work into tasks")

    System(pwk, "Personal Work Kit", "Activity-Driven Development toolkit for personal task management and AI-assisted work breakdown")

    System_Ext(aiAssistant, "AI Coding Assistant", "Claude Code, Copilot - executes delegated tasks and provides research")
    System_Ext(calendar, "Calendar", "Google Calendar, Outlook - provides time commitments and meetings")
    System_Ext(ide, "IDE/Editor", "VS Code, terminal - environment for executing commands")
    System_Ext(git, "Git/GitHub", "Version control for work items and logs")

    Rel(user, pwk, "Captures activities, plans days, delegates tasks")
    Rel(pwk, aiAssistant, "Delegates research, drafts, and analysis tasks")
    Rel(pwk, calendar, "References for time blocking")
    Rel(user, ide, "Executes /pwk.* slash commands")
    Rel(ide, pwk, "Triggers command execution")
    Rel(pwk, git, "Versions logs and work items")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Context Elements

| Element | Type | Description |
|---------|------|-------------|
| Knowledge Worker | Person | Primary user managing their daily work and tasks |
| Personal Work Kit | System | Core toolkit for activity capture, planning, and breakdown |
| AI Coding Assistant | External | Executes delegated [AI] tasks |
| Calendar | External | Source of time commitments for planning |
| IDE/Editor | External | Environment where commands are executed |
| Git/GitHub | External | Version control for persistence |

---

## 2. Container Diagram

Shows the internal containers within Personal Work Kit.

```mermaid
C4Container
    title C4 Container Diagram for Personal Work Kit

    Person(user, "Knowledge Worker", "Manages daily activities and tasks")

    System_Boundary(pwk, "Personal Work Kit") {
        Container(slashCmds, "Slash Command Definitions", "Markdown", "Prompt definitions for /pwk.* commands in .claude/commands/")
        Container(templates, "Templates", "Markdown", "Reusable templates for logs, work items, breakdowns")
        ContainerDb(logs, "Activity Logs", "File System", "Daily logs in logs/YYYY-MM-DD.md format")
        ContainerDb(workItems, "Work Items", "File System", "Multi-day work in work/[name]/ folders")
        ContainerDb(memory, "Personal Memory", "File System", "Principles and accumulated context in memory/")
        ContainerDb(inbox, "Capture Inbox", "File System", "Unprocessed captures in inbox/")
    }

    System_Ext(aiAssistant, "AI Coding Assistant", "Claude Code - processes commands and executes AI tasks")
    System_Ext(ide, "IDE/Editor", "VS Code, terminal")

    Rel(user, ide, "Executes /pwk.* commands")
    Rel(ide, slashCmds, "Reads command definitions")
    Rel(slashCmds, aiAssistant, "Provides structured prompts")

    Rel(aiAssistant, logs, "Writes/reads daily entries")
    Rel(aiAssistant, workItems, "Creates/updates work items")
    Rel(aiAssistant, memory, "Reads principles, writes context")
    Rel(aiAssistant, inbox, "Processes captures")

    Rel(slashCmds, templates, "Uses for generation")
    Rel(templates, logs, "Instantiates daily logs")
    Rel(templates, workItems, "Instantiates work items")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Container Descriptions

| Container | Technology | Description |
|-----------|------------|-------------|
| Slash Command Definitions | Markdown | 8 command files defining /pwk.capture, /pwk.log, /pwk.plan, /pwk.breakdown, /pwk.carryover, /pwk.review, /pwk.delegate, /pwk.principles |
| Templates | Markdown | Templates for daily-log.md, work-item.md, breakdown.md, progress.md, principles.md |
| Activity Logs | File System | `logs/YYYY-MM-DD.md` files tracking daily activities, tasks, and reflections |
| Work Items | File System | `work/[name]/` folders containing context.md, breakdown.md, progress.md for multi-day work |
| Personal Memory | File System | `memory/principles.md` storing work style principles referenced by all commands |
| Capture Inbox | File System | `inbox/quick-capture.md` for unprocessed thoughts and captures |

### Data Flow

1. **Capture**: User runs `/pwk.capture` → AI adds to logs/ or inbox/
2. **Plan**: `/pwk.plan` reads memory/principles + previous logs → creates today's log
3. **Breakdown**: `/pwk.breakdown` analyzes work → creates work item or adds tasks to log
4. **Carryover**: `/pwk.carryover` reads yesterday's log → moves incomplete to today
5. **Delegate**: `/pwk.delegate` finds [AI] tasks → AI executes and updates logs
6. **Review**: `/pwk.review` analyzes today's log → adds reflections, prepares carryover

---

## 3. Component Diagrams

### 3.1 Slash Command Components

```mermaid
C4Component
    title Component Diagram for Slash Commands

    Container_Boundary(slashCmds, "Slash Command Definitions") {
        Component(capture, "pwk.capture.md", "Markdown", "Quick activity and task capture")
        Component(log, "pwk.log.md", "Markdown", "View and manage daily log")
        Component(plan, "pwk.plan.md", "Markdown", "Plan day or week")
        Component(breakdown, "pwk.breakdown.md", "Markdown", "Decompose complex work into tasks")
        Component(carryover, "pwk.carryover.md", "Markdown", "Move incomplete items forward")
        Component(review, "pwk.review.md", "Markdown", "End-of-day review and reflection")
        Component(delegate, "pwk.delegate.md", "Markdown", "Mark and execute AI tasks")
        Component(principles, "pwk.principles.md", "Markdown", "View/update work principles")
    }

    Container_Ext(logs, "Activity Logs", "logs/")
    Container_Ext(workItems, "Work Items", "work/")
    Container_Ext(memory, "Personal Memory", "memory/")
    Container_Ext(inbox, "Capture Inbox", "inbox/")
    System_Ext(ai, "AI Assistant", "Claude Code")

    Rel(ai, capture, "Executes")
    Rel(ai, log, "Executes")
    Rel(ai, plan, "Executes")
    Rel(ai, breakdown, "Executes")
    Rel(ai, carryover, "Executes")
    Rel(ai, review, "Executes")
    Rel(ai, delegate, "Executes")
    Rel(ai, principles, "Executes")

    Rel(capture, logs, "Writes entries")
    Rel(capture, inbox, "Writes captures")
    Rel(log, logs, "Reads/displays")
    Rel(plan, logs, "Creates daily log")
    Rel(plan, memory, "Reads principles")
    Rel(breakdown, workItems, "Creates work items")
    Rel(breakdown, logs, "Adds tasks")
    Rel(carryover, logs, "Reads yesterday, writes today")
    Rel(review, logs, "Analyzes and updates")
    Rel(delegate, logs, "Finds/executes AI tasks")
    Rel(principles, memory, "Reads/writes principles")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

### Command Workflow

| Phase | Commands | Purpose |
|-------|----------|---------|
| Morning | carryover → plan | Start the day |
| Throughout Day | capture, breakdown, delegate | Work execution |
| End of Day | review | Close the day |
| Meta | log, principles | View and configure |

---

### 3.2 Activity Logs Components

```mermaid
C4Component
    title Component Diagram for Activity Logs

    Container_Boundary(logs, "Activity Logs") {
        Component(dailyLog, "Daily Log", "YYYY-MM-DD.md", "Single day's activities, tasks, and reflections")
        Component(carryoverSection, "Carryover Section", "Markdown", "Tasks brought forward from yesterday")
        Component(planSection, "Today's Plan", "Markdown", "Planned tasks for the day")
        Component(streamSection, "Activity Stream", "Markdown", "Timestamped activity entries")
        Component(completedSection, "Completed", "Markdown", "Finished tasks moved here")
        Component(reflectionSection, "Reflections", "Markdown", "End-of-day insights")
    }

    Container_Ext(slashCmds, "Slash Commands", "Command definitions")
    System_Ext(ai, "AI Assistant", "Claude Code")

    Rel(ai, dailyLog, "Creates via /pwk.plan")
    Rel(ai, carryoverSection, "Populates via /pwk.carryover")
    Rel(ai, planSection, "Populates via /pwk.plan")
    Rel(ai, streamSection, "Appends via /pwk.capture")
    Rel(ai, completedSection, "Moves tasks when done")
    Rel(ai, reflectionSection, "Fills via /pwk.review")

    Rel(carryoverSection, dailyLog, "Part of")
    Rel(planSection, dailyLog, "Part of")
    Rel(streamSection, dailyLog, "Part of")
    Rel(completedSection, dailyLog, "Part of")
    Rel(reflectionSection, dailyLog, "Part of")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Daily Log Structure

```
logs/2024-01-15.md
├── Carryover from Yesterday (populated by /pwk.carryover)
├── Today's Plan (populated by /pwk.plan)
├── Activity Stream (appended by /pwk.capture)
├── Completed (tasks moved here when done)
├── Blockers (waiting items)
└── Reflections (filled by /pwk.review)
```

---

### 3.3 Work Items Components

```mermaid
C4Component
    title Component Diagram for Work Items

    Container_Boundary(workItems, "Work Items") {
        Component(workFolder, "Work Folder", "Directory", "work/[work-item-name]/ container")
        Component(contextDoc, "Context Document", "context.md", "What, why, who, deadline, success criteria")
        Component(breakdownDoc, "Breakdown Document", "breakdown.md", "Phased task list with [P] and [AI] markers")
        Component(progressDoc, "Progress Document", "progress.md", "Daily updates, blockers, decisions")
    }

    Container_Ext(slashCmds, "Slash Commands", "Command definitions")
    Container_Ext(logs, "Activity Logs", "Daily logs")
    System_Ext(ai, "AI Assistant", "Claude Code")

    Rel(ai, workFolder, "Creates via /pwk.breakdown")
    Rel(ai, contextDoc, "Writes context")
    Rel(ai, breakdownDoc, "Generates task phases")
    Rel(ai, progressDoc, "Updates daily")

    Rel(breakdownDoc, logs, "Tasks added to daily log")
    Rel(progressDoc, logs, "References daily completions")

    Rel(contextDoc, workFolder, "Part of")
    Rel(breakdownDoc, workFolder, "Part of")
    Rel(progressDoc, workFolder, "Part of")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Work Item Lifecycle

```
1. Created: /pwk.breakdown creates work/[name]/
2. Planned: context.md filled with scope and criteria
3. Broken Down: breakdown.md has phased tasks
4. Executed: Tasks flow to daily logs
5. Tracked: progress.md updated daily
6. Completed: All tasks done, work item archived
```

---

### 3.4 Personal Memory Components

```mermaid
C4Component
    title Component Diagram for Personal Memory

    Container_Boundary(memory, "Personal Memory") {
        Component(principlesDoc, "Principles Document", "principles.md", "Work style rules and preferences")
        Component(timeRules, "Time Management", "Section", "Deep work, two-minute rule, meeting boundaries")
        Component(taskRules, "Task Management", "Section", "Daily limits, carryover threshold")
        Component(aiRules, "AI Delegation", "Section", "What to delegate, review requirements")
        Component(ritualRules, "Rituals", "Section", "Daily review, weekly review")
    }

    Container_Ext(slashCmds, "Slash Commands", "Command definitions")
    System_Ext(ai, "AI Assistant", "Claude Code")

    Rel(ai, principlesDoc, "Reads for all commands")
    Rel(ai, principlesDoc, "Updates via /pwk.principles")

    Rel(timeRules, principlesDoc, "Part of")
    Rel(taskRules, principlesDoc, "Part of")
    Rel(aiRules, principlesDoc, "Part of")
    Rel(ritualRules, principlesDoc, "Part of")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

### Principles Application

| Principle Category | Used By |
|--------------------|---------|
| Time Management | /pwk.plan (time blocking) |
| Task Management | /pwk.plan (limits), /pwk.carryover (threshold) |
| AI Delegation | /pwk.delegate (criteria) |
| Rituals | /pwk.review (shutdown) |

---

## Comparison: PWK vs Spec-Kit Architecture

| Aspect | Spec-Kit | Personal Work Kit |
|--------|----------|-------------------|
| **Primary Artifact** | Specification (spec.md) | Activity Log (YYYY-MM-DD.md) |
| **Governance** | Constitution | Principles |
| **Decomposition** | Plan → Tasks | Breakdown → Tasks |
| **Execution** | /speckit.implement | /pwk.delegate (AI) + manual |
| **Quality Check** | /speckit.analyze | /pwk.review |
| **Carryover** | Feature branches | Daily log chain |
| **AI Role** | Code generation | Task delegation |
| **Time Scope** | Feature lifecycle | Daily cycle |

---

## References

- [Personal Work Kit Context](./pwk-context.md)
- [Spec-Kit C4 Diagrams](../speckit-c4-context.md)
- [C4 Model](https://c4model.com/)
