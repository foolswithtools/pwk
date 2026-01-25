# GitHub Personal Work Kit (GPWK) Requirements Specification

**Document Version**: 1.0
**Date**: 2026-01-10
**Status**: Final
**Author**: Requirements Engineering Team

## Table of Contents

1. [Introduction](#1-introduction)
2. [System Overview](#2-system-overview)
3. [Functional Requirements](#3-functional-requirements)
4. [Integration Requirements](#4-integration-requirements)
5. [Workflow Requirements](#5-workflow-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Data Requirements](#7-data-requirements)
8. [Constraints](#8-constraints)
9. [Glossary](#9-glossary)

---

## 1. Introduction

### 1.1 Purpose

This document specifies the complete requirements for the GitHub Personal Work Kit (GPWK), a hybrid productivity system that integrates GitHub Issues and Projects with local daily logs for personal task management and reflection.

### 1.2 Scope

GPWK provides:
- Task capture and management via GitHub Issues
- Kanban-style project management via GitHub Projects
- Local daily logs for reflection and activity streaming
- AI-powered task delegation capabilities
- Comprehensive telemetry and observability
- Integration with Claude Code for AI assistance

### 1.3 Intended Audience

- GPWK end users (knowledge workers using Claude Code)
- System maintainers and developers
- AI/LLM systems integrating with GPWK

### 1.4 Document Conventions

- **FR-XXX**: Functional Requirement
- **IR-XXX**: Integration Requirement
- **WF-XXX**: Workflow Requirement
- **NFR-XXX**: Non-Functional Requirement
- **DR-XXX**: Data Requirement

---

## 2. System Overview

### 2.1 System Description

GPWK is a Claude Code-integrated productivity system that uses GitHub as the backend for persistent task storage while maintaining local logs for private reflection.

### 2.2 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Claude Code Interface                          │
│              (Slash Commands)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         GPWK System (Python Backend)                        │
│  ┌──────────────┬──────────────┬──────────────────────┐    │
│  │   Commands   │  Workflows   │    Telemetry         │    │
│  └──────────────┴──────────────┴──────────────────────┘    │
└────┬──────────────────┬──────────────────┬─────────────────┘
     │                  │                  │
     ▼                  ▼                  ▼
┌──────────┐   ┌────────────────┐   ┌────────────┐
│ GitHub   │   │  Local Files   │   │ Grafana    │
│ (Issues, │   │  (Daily Logs)  │   │ (Metrics)  │
│ Projects)│   │                │   │            │
└──────────┘   └────────────────┘   └────────────┘
```

### 2.3 Key Innovations

1. **Hybrid Storage**: GitHub for persistence, local files for privacy
2. **Label-based Carryover**: Automatic tracking of incomplete tasks
3. **AI Delegation**: Autonomous execution of delegatable tasks
4. **Full Observability**: OpenTelemetry instrumentation throughout
5. **Python Backend**: Reliable implementation with retry logic

---

## 3. Functional Requirements

### 3.1 Task Capture (FR-CAP-XXX)

#### FR-CAP-001: Basic Task Capture
**Description**: System shall allow users to create GitHub issues from natural language text input.

**Acceptance Criteria**:
- User provides task description as text
- System creates GitHub issue with description as title
- Issue is added to project Inbox column
- Issue receives default `pwk:capture` label
- Operation completes in <2 seconds (p95)

**Priority**: CRITICAL
**Traceability**: `/gpwk.capture` command

#### FR-CAP-002: Task Type Notation Parsing
**Description**: System shall parse task type markers [AI], [P] from input text.

**Acceptance Criteria**:
- `[AI]` marker assigns `pwk:ai` label and sets Type field to "ai-task"
- `[P]` marker assigns `pwk:personal` label and sets Type field to "task"
- No marker assigns `pwk:capture` label and sets Type field to "capture"
- Markers are case-insensitive
- Markers can appear anywhere in input text

**Priority**: HIGH
**Traceability**: `/gpwk.capture` notation parsing

#### FR-CAP-003: Priority Notation Parsing
**Description**: System shall parse priority markers (!high, !medium, !low) from input text.

**Acceptance Criteria**:
- `!high` or `!urgent` assigns `priority:high` label and sets Priority field to "high"
- `!medium` assigns `priority:medium` label and sets Priority field to "medium"
- `!low` assigns `priority:low` label and sets Priority field to "low"
- Priority markers are case-insensitive
- If no priority specified, no priority label is assigned

**Priority**: MEDIUM
**Traceability**: `/gpwk.capture` notation parsing

#### FR-CAP-004: Energy Level Notation Parsing
**Description**: System shall parse energy level markers (~deep, ~shallow, ~quick) from input text.

**Acceptance Criteria**:
- `~deep` assigns `energy:deep` label and sets Energy field to "deep"
- `~shallow` assigns `energy:shallow` label and sets Energy field to "shallow"
- `~quick` assigns `energy:quick` label and sets Energy field to "quick"
- Energy markers are case-insensitive
- If no energy specified, no energy label is assigned

**Priority**: MEDIUM
**Traceability**: `/gpwk.capture` notation parsing

#### FR-CAP-005: Automatic Completion Detection
**Description**: System shall automatically detect and close completed activities based on linguistic patterns.

**Acceptance Criteria**:
- Past tense verbs trigger completion detection (e.g., "took", "completed", "finished")
- Time range patterns trigger completion (e.g., "between 9-10 AM", "from 2-3 PM")
- Explicit markers trigger completion (e.g., "done", "complete")
- Completed tasks are immediately closed
- Completed tasks are moved to Done status
- Completion time is recorded in issue comment

**Priority**: HIGH
**Traceability**: `/gpwk.capture` completion detection

#### FR-CAP-006: Activity Stream Logging
**Description**: System shall append all captured tasks to daily log activity stream.

**Acceptance Criteria**:
- Each capture is appended to `gpwk/logs/YYYY-MM-DD.md`
- Entry includes timestamp, issue number, and title
- Completed activities are marked with ✓
- If daily log doesn't exist, warning is displayed but capture succeeds
- Log entries are in chronological order

**Priority**: MEDIUM
**Traceability**: `/gpwk.capture` daily log integration

#### FR-CAP-007: Special Character Handling
**Description**: System shall handle special characters in task descriptions without escaping issues.

**Acceptance Criteria**:
- Parentheses, quotes, brackets are preserved
- Newlines are preserved or converted to appropriate GitHub markdown
- Unicode characters are supported
- No shell escaping errors occur
- Input is sanitized for GitHub API compatibility

**Priority**: HIGH
**Traceability**: Python backend implementation

### 3.2 Task Planning (FR-PLN-XXX)

#### FR-PLN-001: Daily Plan Generation
**Description**: System shall generate daily plans from GitHub project data.

**Acceptance Criteria**:
- Command accepts `today`, `tomorrow`, `YYYY-MM-DD` as arguments
- System fetches issues from "Today" project column
- System categorizes issues by priority, energy, carryover status
- Daily log file is created at `gpwk/logs/YYYY-MM-DD.md`
- Log follows template structure from `gpwk/templates/daily-log.md`

**Priority**: CRITICAL
**Traceability**: `/gpwk.plan` command

#### FR-PLN-002: Weekly Plan Generation
**Description**: System shall generate weekly overview plans.

**Acceptance Criteria**:
- Command accepts `week` argument
- System fetches issues from "Today" and "This Week" columns
- Weekly log file is created at `gpwk/logs/YYYY-WXX-week.md`
- Plan shows distribution across 7 days
- Overdue items are highlighted

**Priority**: MEDIUM
**Traceability**: `/gpwk.plan week` command

#### FR-PLN-003: Carryover Task Identification
**Description**: System shall identify and highlight tasks with carryover labels.

**Acceptance Criteria**:
- Tasks with `pwk:c1`, `pwk:c2`, `pwk:c3` labels are identified
- Carryover tasks are displayed in dedicated section
- c2 and c3 tasks are flagged for attention
- c3 tasks trigger `/gpwk.breakdown` suggestion

**Priority**: HIGH
**Traceability**: `/gpwk.plan` carryover section

#### FR-PLN-004: Work Principles Application
**Description**: System shall apply user work principles from `gpwk/memory/principles.md` to planning.

**Acceptance Criteria**:
- Daily task limit (default 4-6) is respected
- Deep work windows are suggested (default: morning)
- Energy matching is performed (deep tasks → high energy periods)
- Context switch limits are enforced
- Principles file is read and parsed correctly

**Priority**: MEDIUM
**Traceability**: `gpwk/memory/principles.md` integration

#### FR-PLN-005: AI Delegation Queue Display
**Description**: System shall display AI-delegatable tasks in plan.

**Acceptance Criteria**:
- Issues with `pwk:ai` label and state=open are listed
- AI queue is displayed in dedicated section
- Suggestion to run `/gpwk.delegate` is provided
- Task count is shown

**Priority**: MEDIUM
**Traceability**: `/gpwk.plan` AI delegation section

### 3.3 Task Triage (FR-TRG-XXX)

#### FR-TRG-001: Interactive Column Movement
**Description**: System shall allow users to move issues between project columns interactively.

**Acceptance Criteria**:
- System displays issues in Inbox column
- User can select issues to move
- Destination columns: Today, This Week, Backlog
- GitHub project status field is updated
- Confirmation is displayed after move

**Priority**: HIGH
**Traceability**: `/gpwk.triage` command

#### FR-TRG-002: Batch Triage Operations
**Description**: System shall support batch operations for multiple issues.

**Acceptance Criteria**:
- User can select multiple issues at once
- All selected issues move to same destination
- Operation is atomic (all or none)
- Progress is displayed for batch operations
- Errors don't halt entire batch

**Priority**: MEDIUM
**Traceability**: `/gpwk.triage` batch operations

### 3.4 Work Breakdown (FR-BRK-XXX)

#### FR-BRK-001: Parent Issue Creation
**Description**: System shall create parent work item issues for complex work.

**Acceptance Criteria**:
- Parent issue is created with `pwk:work-item` label
- Parent issue includes:
  - Overview section
  - Scope (in/out)
  - Success criteria
  - Phases section (for sub-issues)
  - Progress tracking section
- Parent Type field set to "work-item"

**Priority**: HIGH
**Traceability**: `/gpwk.breakdown` parent creation

#### FR-BRK-002: Sub-Issue Generation
**Description**: System shall generate sub-issues linked to parent work item.

**Acceptance Criteria**:
- Each sub-issue references parent by number
- Sub-issues are listed in parent issue body
- Sub-issues can be AI or Personal tasks
- Sub-issues can be independently triaged
- Parent-child relationship is bidirectional

**Priority**: HIGH
**Traceability**: `/gpwk.breakdown` sub-issue generation

#### FR-BRK-003: Automatic Breakdown Suggestions
**Description**: System shall suggest breakdown for tasks with `pwk:c3` label.

**Acceptance Criteria**:
- During `/gpwk.plan`, c3 tasks trigger suggestion
- Suggestion includes rationale (task stuck 3+ days)
- User can accept or dismiss suggestion
- If accepted, `/gpwk.breakdown` is invoked automatically

**Priority**: MEDIUM
**Traceability**: `/gpwk.plan` c3 detection and suggestion

### 3.5 AI Delegation (FR-DEL-XXX)

#### FR-DEL-001: AI Task Listing
**Description**: System shall list all AI-delegatable tasks.

**Acceptance Criteria**:
- Command `--list` flag displays all issues with `pwk:ai` label and state=open
- Display includes: issue number, title, priority, energy
- Tasks are sorted by priority (high → medium → low)
- Task count is displayed

**Priority**: HIGH
**Traceability**: `/gpwk.delegate --list`

#### FR-DEL-002: Task Execution Preparation
**Description**: System shall prepare infrastructure for AI task execution.

**Acceptance Criteria**:
- Issue validation (has `pwk:ai` label)
- Issue status moved from Inbox to Today
- Confirmation message displayed
- Duration is logged

**Priority**: CRITICAL
**Traceability**: `/gpwk.delegate #123`

#### FR-DEL-003: Result Posting
**Description**: System shall post AI execution results as issue comments.

**Acceptance Criteria**:
- Result posted as markdown comment
- Comment includes: task name, execution time, model used, duration
- Comment structure: Summary, Key Points, Detailed Analysis, Resources, Recommendations
- Comment is linked to trace/telemetry
- `status:ai-complete` label is added

**Priority**: CRITICAL
**Traceability**: `/gpwk.delegate --post-result`

#### FR-DEL-004: Status Synchronization
**Description**: System shall synchronize AI-complete tasks to Review status.

**Acceptance Criteria**:
- Command `--sync-status` finds all issues with `status:ai-complete` label
- Issues are moved to "Review" status in project
- Count of synced tasks is displayed
- Failed syncs are reported separately

**Priority**: HIGH
**Traceability**: `/gpwk.delegate --sync-status`

#### FR-DEL-005: Delegation Safety Checks
**Description**: System shall validate tasks are safe to delegate before execution.

**Acceptance Criteria**:
- Warning if task appears to require human judgment
- Warning if task involves customer communication
- Warning if task requires institutional knowledge
- User can override warnings
- Unsafe delegation patterns are logged

**Priority**: MEDIUM
**Traceability**: `/gpwk.delegate` safety validation

### 3.6 Task Completion (FR-CMP-XXX)

#### FR-CMP-001: Issue Closure
**Description**: System shall close GitHub issues and update project status.

**Acceptance Criteria**:
- GitHub issue state changed to "closed"
- Project status field set to "Done"
- Completion comment added to issue
- Timestamp of completion recorded

**Priority**: CRITICAL
**Traceability**: `/gpwk.complete #123`

#### FR-CMP-002: Time Tracking
**Description**: System shall support time range tracking for completed tasks.

**Acceptance Criteria**:
- `--from TIME` and `--to TIME` flags accepted
- Time formats supported: 12-hour (HH:MM AM/PM), 24-hour (HH:MM)
- Time range is included in completion comment
- Time range is appended to daily log
- Duration is calculated and recorded

**Priority**: HIGH
**Traceability**: `/gpwk.complete #123 --from --to`

#### FR-CMP-003: Completion Comments
**Description**: System shall support custom completion comments.

**Acceptance Criteria**:
- `--comment TEXT` flag accepted
- Comment is added to issue closure comment
- Comment is included in daily log entry
- Special characters in comment are handled correctly

**Priority**: MEDIUM
**Traceability**: `/gpwk.complete #123 --comment`

#### FR-CMP-004: Daily Log Activity Entry
**Description**: System shall append completion to daily log activity stream.

**Acceptance Criteria**:
- Entry format: `HH:MM-HH:MM - Completed #NUM: Title ✓`
- If no time range: `Completed #NUM: Title ✓`
- Custom comment is included as sub-item
- Entry is appended in chronological order
- If log missing, warning displayed but operation succeeds

**Priority**: HIGH
**Traceability**: `/gpwk.complete` daily log integration

### 3.7 End-of-Day Review (FR-REV-XXX)

#### FR-REV-001: Completion Summary Generation
**Description**: System shall generate summary of completed tasks for the day.

**Acceptance Criteria**:
- All issues closed today are listed
- Total count of completed tasks displayed
- Time spent (if tracked) is summed
- Completion rate (planned vs actual) is calculated

**Priority**: MEDIUM
**Traceability**: `/gpwk.review` completion summary

#### FR-REV-002: Reflection Prompts
**Description**: System shall provide reflection prompts based on daily activity.

**Acceptance Criteria**:
- Prompts for: wins, challenges, learnings, tomorrow's priority
- Prompts are personalized based on completion patterns
- User responses are saved to daily log
- Reflection section is timestamped

**Priority**: LOW
**Traceability**: `/gpwk.review` reflection section

#### FR-REV-003: Metrics Calculation
**Description**: System shall calculate and display daily productivity metrics.

**Acceptance Criteria**:
- Metrics: tasks completed, time spent, completion rate, energy match rate
- Metrics are compared to historical averages
- Trends are identified (improving/declining)
- Metrics are appended to daily log

**Priority**: MEDIUM
**Traceability**: `/gpwk.review` metrics section

### 3.8 Carryover Management (FR-CRY-XXX)

#### FR-CRY-001: Carryover Label Assignment
**Description**: System shall assign and update carryover labels based on task age.

**Acceptance Criteria**:
- Day 1: No carryover label
- Day 2: Assign `pwk:c1` label
- Day 3: Upgrade to `pwk:c2` label
- Day 4+: Upgrade to `pwk:c3` label
- Previous carryover labels are removed during upgrade

**Priority**: HIGH
**Traceability**: `/gpwk.carryover` label management

#### FR-CRY-002: Carryover Detection Logic
**Description**: System shall determine which tasks are carried over.

**Acceptance Criteria**:
- Task is carried over if: created before today AND state=open AND in Today column
- Completed tasks are excluded
- Tasks in Inbox are excluded (not yet scheduled)
- Accuracy: 100% for simple cases

**Priority**: HIGH
**Traceability**: `/gpwk.carryover` detection logic

#### FR-CRY-003: Breakdown Recommendations
**Description**: System shall recommend breakdown for c3 tasks.

**Acceptance Criteria**:
- Tasks with `pwk:c3` label trigger recommendation
- Recommendation message includes: task number, title, days carried over
- User can invoke `/gpwk.breakdown #123` directly from recommendation
- Recommendations are displayed in `/gpwk.plan` and `/gpwk.carryover`

**Priority**: MEDIUM
**Traceability**: `/gpwk.carryover` c3 recommendations

### 3.9 Task Search (FR-SRH-XXX)

#### FR-SRH-001: Basic Search
**Description**: System shall support searching issues by text query.

**Acceptance Criteria**:
- Free-text search across issue title and body
- Case-insensitive matching
- Results sorted by relevance
- Search results display: number, title, status, labels

**Priority**: MEDIUM
**Traceability**: `/gpwk.search [query]`

#### FR-SRH-002: Filter by Status
**Description**: System shall support filtering by issue state and project status.

**Acceptance Criteria**:
- `--status` flag accepts: open, closed, inbox, today, week, backlog, done
- Multiple statuses can be combined (OR logic)
- Filtering is case-insensitive

**Priority**: MEDIUM
**Traceability**: `/gpwk.search --status`

#### FR-SRH-003: Filter by Labels
**Description**: System shall support filtering by labels.

**Acceptance Criteria**:
- `--label` flag accepts label names
- Multiple labels can be specified (AND logic by default)
- Partial label matching supported
- Special filters: `--ai`, `--personal`, `--high-priority`

**Priority**: MEDIUM
**Traceability**: `/gpwk.search --label`

#### FR-SRH-004: Filter by Priority and Energy
**Description**: System shall support filtering by priority and energy levels.

**Acceptance Criteria**:
- `--priority` flag accepts: high, medium, low
- `--energy` flag accepts: deep, shallow, quick
- Filters can be combined

**Priority**: LOW
**Traceability**: `/gpwk.search --priority --energy`

### 3.10 Principles Management (FR-PRC-XXX)

#### FR-PRC-001: View Principles
**Description**: System shall display current work principles.

**Acceptance Criteria**:
- Principles from `gpwk/memory/principles.md` are displayed
- Display is formatted and readable
- All principle categories are shown

**Priority**: LOW
**Traceability**: `/gpwk.principles`

#### FR-PRC-002: Edit Principles
**Description**: System shall allow editing work principles.

**Acceptance Criteria**:
- `--edit` flag opens principles file in default editor
- File is saved after editing
- Validation is performed on save (valid markdown)
- Changes take effect immediately for next command

**Priority**: LOW
**Traceability**: `/gpwk.principles --edit`

### 3.11 System Setup (FR-STP-XXX)

#### FR-STP-001: GitHub Repository Creation
**Description**: System shall create GitHub repository if it doesn't exist.

**Acceptance Criteria**:
- Repository name defaults to "my-work" or uses user-provided name
- Repository is private by default
- Repository is created in authenticated user's account
- If repository exists, setup continues without error

**Priority**: CRITICAL
**Traceability**: `/gpwk.setup`

#### FR-STP-002: GitHub Project Creation
**Description**: System shall create GitHub Project (v2) with required structure.

**Acceptance Criteria**:
- Project named "Personal Work Kit"
- Project columns: Inbox, Today, This Week, Backlog, Done
- Status field created with column values
- Project is linked to repository
- Project ID saved to `gpwk/memory/github-config.md`

**Priority**: CRITICAL
**Traceability**: `/gpwk.setup` project creation

#### FR-STP-003: Label Creation
**Description**: System shall create all required labels in repository.

**Acceptance Criteria**:
- Type labels: pwk:task, pwk:ai, pwk:personal, pwk:work-item, pwk:capture, pwk:knowledge
- Priority labels: priority:high, priority:medium, priority:low
- Energy labels: energy:deep, energy:shallow, energy:quick
- Carryover labels: pwk:c1, pwk:c2, pwk:c3
- Status labels: status:blocked, status:waiting, status:ai-complete
- Labels have appropriate colors
- Existing labels are not duplicated

**Priority**: CRITICAL
**Traceability**: `/gpwk.setup` label creation

#### FR-STP-004: Configuration Persistence
**Description**: System shall save GitHub configuration for future commands.

**Acceptance Criteria**:
- Configuration saved to `gpwk/memory/github-config.md`
- Configuration includes: repo name, owner, project ID, field IDs
- Configuration is validated before saving
- Configuration is readable by all GPWK commands

**Priority**: CRITICAL
**Traceability**: `/gpwk.setup` config persistence

### 3.12 Knowledge Capture (FR-KNW-XXX)

#### FR-KNW-001: Knowledge Task Identification
**Description**: System shall identify knowledge capture tasks requiring automated research.

**Acceptance Criteria**:
- Tasks must have both `pwk:ai` AND `pwk:knowledge` labels
- System detects these tasks during delegation
- Knowledge tasks trigger specialized workflow

**Priority**: MEDIUM
**Traceability**: GitHub Actions workflow `gpwk-knowledge-capture.yml`

#### FR-KNW-002: Automated Research Execution
**Description**: System shall perform internet research for knowledge tasks.

**Acceptance Criteria**:
- WebSearch tool used for information gathering
- WebFetch tool used for content retrieval
- Multiple sources are consulted
- Research depth is appropriate to task complexity

**Priority**: MEDIUM
**Traceability**: Knowledge capture workflow

#### FR-KNW-003: Documentation Generation
**Description**: System shall generate three-part documentation for knowledge tasks.

**Acceptance Criteria**:
- README.md: Human-readable guide
- technical-reference.md: AI/LLM optimized reference
- sources.md: Research metadata and citations
- All files created in `knowledge/{topic}/` directory
- Files follow consistent format

**Priority**: MEDIUM
**Traceability**: Knowledge capture workflow output

#### FR-KNW-004: Knowledge Commit and Notification
**Description**: System shall commit knowledge documentation and notify user.

**Acceptance Criteria**:
- Documentation committed directly to repository
- Commit message includes issue number and topic
- Issue comment posted with link to documentation
- `status:ai-complete` label added to issue

**Priority**: MEDIUM
**Traceability**: Knowledge capture workflow finalization

---

## 4. Integration Requirements

### 4.1 GitHub Integration (IR-GH-XXX)

#### IR-GH-001: GitHub CLI Dependency
**Description**: System shall use GitHub CLI (`gh`) for all GitHub operations.

**Acceptance Criteria**:
- `gh` version 2.0+ is required
- Authentication state is checked before operations
- `gh auth status` command succeeds
- If not authenticated, clear error message with remediation steps

**Priority**: CRITICAL
**Traceability**: All GPWK commands

#### IR-GH-002: GitHub API Integration
**Description**: System shall use GitHub API for issue and project management.

**Acceptance Criteria**:
- Issues API: create, update, close, comment
- Projects API: add items, update fields, move items
- Search API: query issues
- API rate limits are respected
- Retry logic for transient failures (max 3 retries with exponential backoff)

**Priority**: CRITICAL
**Traceability**: Python backend GitHub client

#### IR-GH-003: GraphQL API for Projects
**Description**: System shall use GitHub GraphQL API for Projects v2 operations.

**Acceptance Criteria**:
- Project field updates via GraphQL mutations
- Project item queries via GraphQL
- Error handling for GraphQL-specific errors
- Field IDs are cached after first lookup

**Priority**: HIGH
**Traceability**: Project field management

### 4.2 Claude Code Integration (IR-CC-XXX)

#### IR-CC-001: Slash Command Interface
**Description**: System shall integrate with Claude Code slash command system.

**Acceptance Criteria**:
- All commands defined in `.claude/commands/` directory
- Command metadata follows Claude Code conventions
- Commands are discoverable via autocomplete
- Help text is displayed for each command

**Priority**: CRITICAL
**Traceability**: `.claude/commands/gpwk.*.md`

#### IR-CC-002: GitHub Actions Integration
**Description**: System shall use GitHub Actions for AI task execution.

**Acceptance Criteria**:
- Workflow defined at `.github/workflows/claude-gpwk.yml`
- Claude Code environment available in actions
- ANTHROPIC_API_KEY secret configured
- Manual trigger and scheduled trigger supported
- Workflow execution logs available

**Priority**: HIGH
**Traceability**: AI delegation workflow

### 4.3 Filesystem Integration (IR-FS-XXX)

#### IR-FS-001: Local Log Storage
**Description**: System shall store daily logs in local filesystem.

**Acceptance Criteria**:
- Logs stored in `gpwk/logs/` directory
- Log naming: `YYYY-MM-DD.md` for daily, `YYYY-WXX-week.md` for weekly
- Logs are gitignored by default
- Logs directory is created if it doesn't exist
- File permissions are user-writable

**Priority**: HIGH
**Traceability**: Daily log management

#### IR-FS-002: Configuration File Storage
**Description**: System shall store configuration in version-controlled files.

**Acceptance Criteria**:
- Configuration in `gpwk/memory/` directory
- Files: `github-config.md`, `principles.md`, `goals.md`
- Files are tracked in Git
- Files are in markdown format for human readability

**Priority**: HIGH
**Traceability**: Configuration management

#### IR-FS-003: Template Management
**Description**: System shall use templates for consistent document generation.

**Acceptance Criteria**:
- Templates stored in `gpwk/templates/` directory
- Templates: `daily-log.md`, `issue-body.md`
- Templates use placeholder syntax for variable substitution
- Templates are version-controlled

**Priority**: MEDIUM
**Traceability**: Document generation

### 4.4 Telemetry Integration (IR-TEL-XXX)

#### IR-TEL-001: OpenTelemetry Export
**Description**: System shall export telemetry using OpenTelemetry standard.

**Acceptance Criteria**:
- OTLP protocol used for export
- Traces, metrics, logs exported
- Grafana Stack compatible (Tempo, Prometheus, Loki)
- Telemetry endpoint configurable via environment variables

**Priority**: MEDIUM
**Traceability**: Python backend telemetry

#### IR-TEL-002: Trace Context Propagation
**Description**: System shall propagate trace context across operations.

**Acceptance Criteria**:
- Each command execution is a trace
- Spans created for major operations (API calls, file I/O)
- Parent-child span relationships preserved
- Trace IDs are unique and globally distributed

**Priority**: MEDIUM
**Traceability**: OpenTelemetry instrumentation

#### IR-TEL-003: Metrics Export
**Description**: System shall export operational metrics.

**Acceptance Criteria**:
- Counter metrics: command executions, task completions, errors
- Gauge metrics: active tasks, carryover counts
- Histogram metrics: operation durations
- Metrics namespaced under `gpwk.*`
- Prometheus scrape endpoint available (optional)

**Priority**: LOW
**Traceability**: Metrics instrumentation

---

## 5. Workflow Requirements

### 5.1 Daily Workflow (WF-DAY-XXX)

#### WF-DAY-001: Morning Workflow
**Description**: System shall support morning planning workflow.

**Workflow**:
1. User runs `/gpwk.triage` to process inbox
2. User runs `/gpwk.plan today` to generate daily plan
3. Daily log is created with scheduled tasks

**Acceptance Criteria**:
- Workflow completes in <10 seconds
- All tasks in Today column are included in plan
- Carryover tasks are highlighted
- Plan respects daily task limits

**Priority**: HIGH
**Traceability**: Morning workflow documentation

#### WF-DAY-002: Throughout Day Workflow
**Description**: System shall support continuous task management during the day.

**Workflow**:
1. User runs `/gpwk.capture [task]` to add new tasks
2. User runs `/gpwk.complete #123` to mark tasks done
3. User runs `/gpwk.delegate` to execute AI tasks
4. Daily log is updated continuously

**Acceptance Criteria**:
- Captures are near-instant (<2s)
- Completions update log automatically
- AI tasks execute autonomously
- Activity stream remains chronological

**Priority**: HIGH
**Traceability**: Day workflow documentation

#### WF-DAY-003: Evening Workflow
**Description**: System shall support end-of-day reflection workflow.

**Workflow**:
1. User runs `/gpwk.review` for daily reflection
2. User runs `/gpwk.carryover` to update task labels
3. Daily log is finalized with metrics

**Acceptance Criteria**:
- Review generates completion summary
- Carryover labels are updated accurately
- Metrics are calculated and displayed
- Tomorrow's priority is identified

**Priority**: MEDIUM
**Traceability**: Evening workflow documentation

### 5.2 Weekly Workflow (WF-WK-XXX)

#### WF-WK-001: Weekly Planning
**Description**: System shall support weekly planning workflow.

**Workflow**:
1. User runs `/gpwk.plan week`
2. System shows all tasks across 7 days
3. User distributes tasks across days via triage

**Acceptance Criteria**:
- Weekly plan shows balanced distribution
- Overcommitment warnings are displayed
- High-priority tasks are highlighted
- Weekly log is created

**Priority**: MEDIUM
**Traceability**: Weekly planning

### 5.3 AI Delegation Workflow (WF-AI-XXX)

#### WF-AI-001: Delegation Workflow
**Description**: System shall support end-to-end AI delegation workflow.

**Workflow**:
1. User creates task with `[AI]` marker
2. Task appears in AI queue during planning
3. GitHub Action executes task automatically (scheduled or manual)
4. Result is posted as issue comment
5. User reviews result and closes or iterates

**Acceptance Criteria**:
- Workflow is autonomous after task creation
- Results are comprehensive and actionable
- Human review is explicit step
- Quality is trackable

**Priority**: HIGH
**Traceability**: AI delegation architecture

### 5.4 Work Breakdown Workflow (WF-BRK-XXX)

#### WF-BRK-001: Complex Work Decomposition
**Description**: System shall support breaking complex work into manageable tasks.

**Workflow**:
1. User identifies task as too large (c3 label or manual)
2. User runs `/gpwk.breakdown [description]`
3. Parent work item is created
4. Sub-issues are generated
5. Sub-issues are triaged independently

**Acceptance Criteria**:
- Parent-child relationships are clear
- Sub-issues are independently schedulable
- Progress is trackable via parent issue
- Breakdown rationale is documented

**Priority**: MEDIUM
**Traceability**: Work breakdown architecture

---

## 6. Non-Functional Requirements

### 6.1 Performance (NFR-PRF-XXX)

#### NFR-PRF-001: Command Execution Time
**Description**: Commands shall execute within acceptable time limits.

**Acceptance Criteria**:
- `/gpwk.capture`: <2 seconds (p95)
- `/gpwk.plan`: <5 seconds (p95)
- `/gpwk.triage`: <3 seconds (p95)
- `/gpwk.complete`: <2 seconds (p95)
- `/gpwk.delegate --list`: <3 seconds (p95)

**Priority**: MEDIUM
**Measurement**: OpenTelemetry duration metrics

#### NFR-PRF-002: GitHub API Efficiency
**Description**: System shall minimize GitHub API calls.

**Acceptance Criteria**:
- Batch operations where possible
- Field IDs cached after first lookup
- Redundant queries avoided
- API rate limit headroom >20%

**Priority**: MEDIUM
**Measurement**: API call counts, rate limit usage

### 6.2 Reliability (NFR-REL-XXX)

#### NFR-REL-001: Retry Logic
**Description**: System shall implement retry logic for transient failures.

**Acceptance Criteria**:
- Max 3 retries for GitHub API calls
- Exponential backoff (1s, 2s, 4s)
- Only retry on transient errors (5xx, timeout)
- Log all retry attempts

**Priority**: HIGH
**Traceability**: Python backend error handling

#### NFR-REL-002: Error Handling
**Description**: System shall handle errors gracefully without data loss.

**Acceptance Criteria**:
- All errors are logged with context
- User-facing errors include remediation steps
- Partial failures are clearly communicated
- No silent failures

**Priority**: HIGH
**Traceability**: Error handling throughout

#### NFR-REL-003: Data Consistency
**Description**: System shall maintain consistency between GitHub and local data.

**Acceptance Criteria**:
- GitHub is source of truth for tasks
- Local logs are eventually consistent
- Conflicts are detected and reported
- Manual reconciliation path exists

**Priority**: MEDIUM
**Traceability**: Data synchronization logic

### 6.3 Usability (NFR-USE-XXX)

#### NFR-USE-001: Error Messages
**Description**: Error messages shall be actionable and helpful.

**Acceptance Criteria**:
- Errors explain what went wrong
- Errors suggest how to fix
- Errors include relevant context (task ID, etc.)
- Errors distinguish user errors from system errors

**Priority**: MEDIUM
**Traceability**: Error message design

#### NFR-USE-002: Documentation
**Description**: System shall provide comprehensive user documentation.

**Acceptance Criteria**:
- Each command has help text
- README provides quickstart guide
- Context document explains architecture
- Examples are provided for common scenarios

**Priority**: MEDIUM
**Traceability**: Documentation files

### 6.4 Security and Privacy (NFR-SEC-XXX)

#### NFR-SEC-001: GitHub Authentication
**Description**: System shall use secure GitHub authentication.

**Acceptance Criteria**:
- GitHub CLI authentication used (OAuth)
- No API tokens stored in files
- Credentials managed by `gh` CLI
- User consent required for GitHub access

**Priority**: HIGH
**Traceability**: GitHub CLI integration

#### NFR-SEC-002: Local Log Privacy
**Description**: Local logs shall remain private and not synced to GitHub.

**Acceptance Criteria**:
- Logs directory is gitignored
- No automatic upload of logs
- Logs contain private reflection content
- File permissions are restrictive (user-only)

**Priority**: HIGH
**Traceability**: `.gitignore` configuration

#### NFR-SEC-003: API Key Management
**Description**: Claude API key shall be securely managed.

**Acceptance Criteria**:
- API key stored in GitHub Secrets
- Key not exposed in logs or output
- Key rotation supported
- Key access limited to GitHub Actions

**Priority**: CRITICAL
**Traceability**: GitHub Actions secrets management

### 6.5 Observability (NFR-OBS-XXX)

#### NFR-OBS-001: Full Instrumentation
**Description**: All operations shall be instrumented with telemetry.

**Acceptance Criteria**:
- Every command creates a trace
- Key operations are timed
- Errors are logged with full context
- Telemetry overhead <5% of execution time

**Priority**: MEDIUM
**Traceability**: OpenTelemetry instrumentation

#### NFR-OBS-002: Metrics Availability
**Description**: Operational metrics shall be available for analysis.

**Acceptance Criteria**:
- Metrics exported to Prometheus
- Traces exported to Tempo
- Logs exported to Loki
- Dashboards available in Grafana

**Priority**: LOW
**Traceability**: Grafana Stack integration

---

## 7. Data Requirements

### 7.1 GitHub Issue Schema (DR-ISS-XXX)

#### DR-ISS-001: Issue Fields
**Description**: GitHub issues shall contain required fields for GPWK.

**Schema**:
- **Title**: String, required, max 256 chars
- **Body**: Markdown, optional
- **State**: Enum (open, closed)
- **Labels**: Array of strings
- **Project Fields**:
  - Type: Enum (task, ai-task, work-item, capture)
  - Priority: Enum (high, medium, low)
  - Energy: Enum (deep, shallow, quick)
  - Status: Enum (Inbox, Today, This Week, Backlog, Done)

**Priority**: CRITICAL

#### DR-ISS-002: Issue Label Taxonomy
**Description**: Label system shall follow defined taxonomy.

**Taxonomy**:
- **pwk:*** - Type markers (task, ai, personal, work-item, capture, knowledge)
- **priority:*** - Priority markers (high, medium, low)
- **energy:*** - Energy markers (deep, shallow, quick)
- **pwk:c*** - Carryover markers (c1, c2, c3)
- **status:*** - Status markers (blocked, waiting, ai-complete)

**Priority**: HIGH

### 7.2 Daily Log Schema (DR-LOG-XXX)

#### DR-LOG-001: Daily Log Structure
**Description**: Daily logs shall follow consistent markdown structure.

**Structure**:
```markdown
# Daily Log: YYYY-MM-DD

## Carryover from Yesterday
[Carryover tasks]

## Today's Plan
### Deep Work Block
[Deep focus tasks]

### Shallow Work
[Low cognitive load tasks]

### Quick Wins
[Under 15 min tasks]

## AI Delegation Queue
[AI tasks]

## Activity Stream
[Chronological captures and completions]

## Blockers
[Any blockers]

## End of Day
### Completed (X/Y tasks)
[Completion summary]

### Metrics
[Daily metrics]

### Reflection
[User reflection]

### Tomorrow's Priority
[Next day focus]
```

**Priority**: MEDIUM

### 7.3 Configuration Schema (DR-CFG-XXX)

#### DR-CFG-001: GitHub Configuration
**Description**: GitHub configuration shall be stored in structured format.

**Schema**:
```markdown
# GitHub Configuration

## Repository
- Owner: {username}
- Name: {repo-name}

## Project
- ID: {project-id}
- URL: https://github.com/users/{username}/projects/{num}

## Fields
- Type Field ID: {field-id}
- Priority Field ID: {field-id}
- Energy Field ID: {field-id}
- Status Field ID: {field-id}

## Field Values
- Status Values:
  - Inbox: {value-id}
  - Today: {value-id}
  - This Week: {value-id}
  - Backlog: {value-id}
  - Done: {value-id}
```

**Priority**: CRITICAL

#### DR-CFG-002: Work Principles Schema
**Description**: Work principles shall define user preferences.

**Schema**:
```markdown
# Work Principles

## Time Management
- Daily task limit: 4-6 significant tasks
- Deep work windows: Morning 9:00-12:00
- Context switch limit: Max 3 per day

## AI Delegation
- Delegate: Research, drafts, summaries, boilerplate
- Keep: Decisions, relationships, creative direction

## Carryover
- c2 threshold: Check for blockers
- c3 threshold: Mandatory breakdown consideration

## Energy Matching
- Deep work: High energy periods (morning)
- Shallow work: Lower energy periods (afternoon)
- Quick wins: Transition periods
```

**Priority**: MEDIUM

---

## 8. Constraints

### 8.1 Technical Constraints

1. **Python Version**: Requires Python 3.8+
2. **GitHub CLI**: Requires `gh` CLI version 2.0+
3. **GitHub Account**: Requires authenticated GitHub account
4. **Claude Code**: Designed for Claude Code environment
5. **Operating System**: macOS and Linux supported, Windows not tested
6. **Network**: Requires internet connectivity for GitHub API access

### 8.2 Operational Constraints

1. **GitHub API Rate Limits**: Subject to GitHub API rate limits (5000 requests/hour for authenticated)
2. **Claude API Costs**: AI delegation incurs Claude API costs (user responsible)
3. **Storage**: Local logs accumulate over time (user responsible for cleanup)
4. **Project Limit**: One GPWK project per repository

### 8.3 Design Constraints

1. **GitHub as Source of Truth**: All tasks must exist as GitHub issues
2. **Label-Based State**: State management via labels (no custom databases)
3. **Markdown Format**: All documents in markdown for portability
4. **Privacy-First**: No cloud sync of local logs

---

## 9. Glossary

| Term | Definition |
|------|------------|
| **GPWK** | GitHub Personal Work Kit |
| **Carryover** | Task that remains incomplete and is carried forward to next day |
| **c1/c2/c3** | Carryover labels indicating 1st, 2nd, or 3rd day of carryover |
| **AI Task** | Task delegatable to AI for autonomous execution (label: pwk:ai) |
| **Personal Task** | Task requiring human judgment and execution (label: pwk:personal) |
| **Work Item** | Parent issue for complex multi-day work (label: pwk:work-item) |
| **Capture** | Quick task entry needing later triage (label: pwk:capture) |
| **Deep Work** | Tasks requiring focused concentration (label: energy:deep) |
| **Shallow Work** | Tasks with low cognitive load (label: energy:shallow) |
| **Quick Win** | Tasks completable in <15 minutes (label: energy:quick) |
| **Daily Log** | Local markdown file for daily activity and reflection |
| **Activity Stream** | Chronological list of captures and completions in daily log |
| **Telemetry** | OpenTelemetry traces, metrics, and logs for observability |
| **Slash Command** | Claude Code command invoked with `/gpwk.*` syntax |
| **Python Backend** | Python implementation handling GPWK logic and GitHub integration |

---

**End of Requirements Specification**

*This document is maintained in: `gpwk/requirements/gpwk-requirements.md`*
*Last Updated: 2026-01-10*
*Version: 1.0*
