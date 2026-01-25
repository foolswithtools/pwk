# GPWK AI/LLM Technical Reference

**Version**: 1.0
**Purpose**: AI/LLM consumption and integration
**Format**: Structured data, schemas, examples

---

## System Architecture

```json
{
  "system_name": "GitHub Personal Work Kit (GPWK)",
  "version": "1.0",
  "type": "hybrid_productivity_system",
  "components": {
    "backend": "Python 3.8+",
    "cli_integration": "GitHub CLI (gh)",
    "ui_integration": "Claude Code Slash Commands",
    "storage": {
      "persistent": "GitHub Issues + Projects",
      "local": "Markdown files in gpwk/logs/"
    },
    "telemetry": "OpenTelemetry (traces, metrics, logs)"
  }
}
```

---

## Command Reference

### Command Schema

```json
{
  "command_name": "/gpwk.{action}",
  "executable": "gpwk/bin/gpwk-{action}",
  "backend": "Python",
  "arguments": "string or flags",
  "output": {
    "stdout": "human-readable status",
    "github": "issue/project updates",
    "filesystem": "log file updates (optional)",
    "telemetry": "OTel span"
  },
  "typical_duration_ms": "200-2000",
  "error_handling": "retry with exponential backoff"
}
```

### Command Catalog

```json
{
  "commands": [
    {
      "name": "/gpwk.setup",
      "purpose": "One-time GitHub infrastructure setup",
      "arguments": "[repo-name]",
      "required_auth": "GitHub CLI authenticated",
      "creates": ["GitHub repo", "GitHub project", "labels", "config file"],
      "idempotent": true,
      "typical_duration_seconds": 5
    },
    {
      "name": "/gpwk.capture",
      "purpose": "Create GitHub issue from natural language",
      "arguments": "task description with optional markers",
      "markers": {
        "type": ["[AI]", "[P]"],
        "priority": ["!high", "!medium", "!low"],
        "energy": ["~deep", "~shallow", "~quick"]
      },
      "completion_detection": {
        "past_tense": ["took", "completed", "finished"],
        "time_ranges": ["between X-Y", "from X to Y"],
        "explicit": ["done", "complete"]
      },
      "typical_duration_seconds": 1,
      "outputs": ["GitHub issue", "daily log append"]
    },
    {
      "name": "/gpwk.plan",
      "purpose": "Generate daily or weekly plan",
      "arguments": {
        "modes": ["today", "tomorrow", "YYYY-MM-DD", "week"],
        "default": "today"
      },
      "inputs": ["GitHub project issues", "principles.md", "goals.md"],
      "outputs": ["daily log file", "task categorization", "scheduling suggestions"],
      "typical_duration_seconds": 3
    },
    {
      "name": "/gpwk.triage",
      "purpose": "Move issues between project columns",
      "arguments": "none (interactive)",
      "operations": ["list Inbox issues", "select destination", "update status"],
      "destinations": ["Today", "This Week", "Backlog"],
      "typical_duration_seconds": 2
    },
    {
      "name": "/gpwk.breakdown",
      "purpose": "Decompose complex work into parent + sub-issues",
      "arguments": "work description",
      "creates": {
        "parent_issue": {
          "label": "pwk:work-item",
          "sections": ["Overview", "Scope", "Success Criteria", "Phases", "Progress"]
        },
        "sub_issues": {
          "count": "3-10 typical",
          "types": ["pwk:ai or pwk:personal"],
          "linking": "bidirectional references"
        }
      },
      "typical_duration_seconds": 5
    },
    {
      "name": "/gpwk.delegate",
      "purpose": "Execute AI-delegatable tasks",
      "subcommands": {
        "--list": "Show AI task queue",
        "--execute [#num]": "Prepare task for execution",
        "--post-result": "Post AI result (GitHub Action use)",
        "--mark-complete": "Add ai-complete label (GitHub Action use)",
        "--sync-status": "Move ai-complete tasks to Review"
      },
      "execution_model": "GitHub Actions (claude-gpwk.yml workflow)",
      "typical_duration_seconds": 1
    },
    {
      "name": "/gpwk.complete",
      "purpose": "Mark task complete with optional time tracking",
      "arguments": {
        "required": "issue_number",
        "optional": ["--from TIME", "--to TIME", "--comment TEXT"]
      },
      "time_formats": ["HH:MM", "HH:MM AM/PM"],
      "updates": ["close issue", "project status → Done", "daily log append"],
      "typical_duration_seconds": 1
    },
    {
      "name": "/gpwk.search",
      "purpose": "Query issues by text, status, labels",
      "arguments": {
        "query": "free text (optional)",
        "filters": ["--status", "--label", "--priority", "--energy"]
      },
      "search_scope": "title and body",
      "sort_by": "relevance",
      "typical_duration_seconds": 2
    },
    {
      "name": "/gpwk.review",
      "purpose": "End-of-day reflection and metrics",
      "arguments": "none",
      "generates": {
        "completion_summary": "tasks completed today",
        "metrics": ["completion rate", "time spent", "energy match"],
        "reflection_prompts": ["wins", "challenges", "learnings", "tomorrow priority"]
      },
      "updates": "daily log End of Day section",
      "typical_duration_seconds": 2
    },
    {
      "name": "/gpwk.carryover",
      "purpose": "Update carryover labels for incomplete tasks",
      "arguments": "none",
      "logic": {
        "day_2": "add pwk:c1",
        "day_3": "upgrade to pwk:c2",
        "day_4_plus": "upgrade to pwk:c3 (suggest breakdown)"
      },
      "scope": "tasks in Today column with state=open",
      "typical_duration_seconds": 2
    },
    {
      "name": "/gpwk.principles",
      "purpose": "View or edit work principles",
      "arguments": {
        "default": "view",
        "--edit": "open in editor"
      },
      "file": "gpwk/memory/principles.md",
      "typical_duration_seconds": 1
    },
    {
      "name": "/gpwk.optimize",
      "purpose": "Optimize task schedule (if implemented)",
      "status": "discovered but not fully documented",
      "typical_duration_seconds": "unknown"
    }
  ]
}
```

---

## Data Schemas

### GitHub Issue Schema

```json
{
  "issue": {
    "number": "integer (GitHub-assigned)",
    "title": "string (max 256 chars)",
    "body": "markdown string",
    "state": "enum: ['open', 'closed']",
    "labels": [
      {
        "name": "string",
        "color": "hex color",
        "description": "string"
      }
    ],
    "created_at": "ISO8601 datetime",
    "closed_at": "ISO8601 datetime or null",
    "comments": [
      {
        "author": "string",
        "body": "markdown",
        "created_at": "ISO8601"
      }
    ]
  },
  "project_item": {
    "id": "GraphQL ID",
    "issue_id": "integer (GitHub issue number)",
    "fields": {
      "Type": "enum: ['task', 'ai-task', 'work-item', 'capture']",
      "Priority": "enum: ['high', 'medium', 'low']",
      "Energy": "enum: ['deep', 'shallow', 'quick']",
      "Status": "enum: ['Inbox', 'Today', 'This Week', 'Backlog', 'Done']"
    }
  }
}
```

### Label Taxonomy

```json
{
  "label_categories": {
    "type": {
      "prefix": "pwk:",
      "values": ["task", "ai", "personal", "work-item", "capture", "knowledge"],
      "mutually_exclusive": false,
      "colors": {
        "pwk:task": "0366d6",
        "pwk:ai": "7057ff",
        "pwk:personal": "d73a4a",
        "pwk:work-item": "fbca04",
        "pwk:capture": "cfd3d7",
        "pwk:knowledge": "0e8a16"
      }
    },
    "priority": {
      "prefix": "priority:",
      "values": ["high", "medium", "low"],
      "mutually_exclusive": true,
      "colors": {
        "priority:high": "d73a4a",
        "priority:medium": "fbca04",
        "priority:low": "0e8a16"
      }
    },
    "energy": {
      "prefix": "energy:",
      "values": ["deep", "shallow", "quick"],
      "mutually_exclusive": true,
      "colors": {
        "energy:deep": "5319e7",
        "energy:shallow": "0075ca",
        "energy:quick": "bfdadc"
      }
    },
    "carryover": {
      "prefix": "pwk:c",
      "values": ["c1", "c2", "c3"],
      "mutually_exclusive": true,
      "semantics": {
        "c1": "1 day carryover",
        "c2": "2 days carryover (warning)",
        "c3": "3+ days carryover (needs breakdown)"
      },
      "colors": {
        "pwk:c1": "f9d0c4",
        "pwk:c2": "f4a460",
        "pwk:c3": "d73a4a"
      }
    },
    "status": {
      "prefix": "status:",
      "values": ["blocked", "waiting", "ai-complete"],
      "mutually_exclusive": false,
      "colors": {
        "status:blocked": "d73a4a",
        "status:waiting": "fbca04",
        "status:ai-complete": "0e8a16"
      }
    }
  }
}
```

### Daily Log Schema

```markdown
# Daily Log: YYYY-MM-DD

## Carryover from Yesterday
<!-- Optional: List of tasks with pwk:c1+ labels -->
- #123: Task title (c2 - 2 days old)

## Today's Plan
### Deep Work Block (suggested: HH:MM-HH:MM)
<!-- Tasks with energy:deep label -->
- #456: Deep focus task

### Shallow Work
<!-- Tasks with energy:shallow label -->
- #789: Low cognitive load task

### Quick Wins
<!-- Tasks with energy:quick label -->
- #101: Under 15 min task

## AI Delegation Queue
<!-- Tasks with pwk:ai label and state=open -->
- #112: Research task [AI]

## Activity Stream
<!-- Chronological list of captures and completions -->
- HH:MM - Captured #113: New task idea
- HH:MM-HH:MM - Completed #114: Previous task ✓

## Blockers
<!-- Optional: Note any blockers -->

## End of Day
### Completed (X/Y tasks)
<!-- List of closed issues -->

### Metrics
- Completion rate: X%
- Time spent: X hours
- Energy match: X%

### Reflection
<!-- User reflection content -->

### Tomorrow's Priority
<!-- Focus for next day -->
```

### GitHub Configuration Schema

```json
{
  "github_config": {
    "repository": {
      "owner": "string (GitHub username)",
      "name": "string (repo name)",
      "url": "https://github.com/{owner}/{name}"
    },
    "project": {
      "id": "string (GraphQL ID)",
      "number": "integer",
      "url": "https://github.com/users/{owner}/projects/{number}"
    },
    "fields": {
      "type_field_id": "string (GraphQL ID)",
      "priority_field_id": "string (GraphQL ID)",
      "energy_field_id": "string (GraphQL ID)",
      "status_field_id": "string (GraphQL ID)"
    },
    "field_values": {
      "status_values": {
        "Inbox": "string (option ID)",
        "Today": "string (option ID)",
        "This Week": "string (option ID)",
        "Backlog": "string (option ID)",
        "Done": "string (option ID)"
      }
    }
  }
}
```

---

## State Machines

### Task Lifecycle State Machine

```
┌─────────┐
│ Created │ (via /gpwk.capture)
└────┬────┘
     │
     ▼
┌─────────────┐
│ Inbox       │ (pwk:capture label, Status: Inbox)
└──────┬──────┘
       │ (/gpwk.triage)
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ Today        │     │ This Week    │     │ Backlog      │
│ (Status:     │◄────┤ (Status:     │◄────┤ (Status:     │
│  Today)      │     │  This Week)  │     │  Backlog)    │
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       │ (/gpwk.complete or auto-close)          │
       ├─────────────────────┴────────────────────┘
       │
       ▼
┌─────────────┐
│ Done        │ (state: closed, Status: Done)
│ (archived)  │
└─────────────┘
```

### Carryover State Machine

```
Day 1: Task in "Today" + state=open
       ↓
Day 2: /gpwk.carryover → add pwk:c1 label
       ↓
Day 3: /gpwk.carryover → upgrade to pwk:c2 label (warning)
       ↓
Day 4: /gpwk.carryover → upgrade to pwk:c3 label (suggest breakdown)
       ↓
       Either:
       - Task completed (labels removed)
       - /gpwk.breakdown invoked (parent created, original closed or linked)
```

### AI Delegation State Machine

```
┌──────────────────────────────────────────────────────────┐
│ Task Created with pwk:ai label                           │
└────────────────────┬─────────────────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Status: Inbox                                            │
│ Available for delegation                                 │
└────────────────────┬─────────────────────────────────────┘
                     │ /gpwk.delegate #123 or GitHub Action
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Status: Today                                            │
│ Execution initiated                                      │
└────────────────────┬─────────────────────────────────────┘
                     │ GitHub Action executes with Claude Code
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Result posted as comment                                 │
│ Label: status:ai-complete added                          │
└────────────────────┬─────────────────────────────────────┘
                     │ /gpwk.delegate --sync-status
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Status: Review                                           │
│ Awaiting human review                                    │
└────────────────────┬─────────────────────────────────────┘
                     │ Human review
                     ▼
┌──────────────────────────────────────────────────────────┐
│ Issue closed (if satisfactory)                           │
│ OR                                                        │
│ Follow-up tasks created (if iteration needed)            │
└──────────────────────────────────────────────────────────┘
```

---

## API Integration Patterns

### GitHub REST API Usage

```json
{
  "api_endpoints": {
    "issues": {
      "create": "POST /repos/{owner}/{repo}/issues",
      "update": "PATCH /repos/{owner}/{repo}/issues/{number}",
      "close": "PATCH /repos/{owner}/{repo}/issues/{number} (state: closed)",
      "comment": "POST /repos/{owner}/{repo}/issues/{number}/comments",
      "list": "GET /repos/{owner}/{repo}/issues"
    },
    "labels": {
      "create": "POST /repos/{owner}/{repo}/labels",
      "add_to_issue": "POST /repos/{owner}/{repo}/issues/{number}/labels",
      "remove_from_issue": "DELETE /repos/{owner}/{repo}/issues/{number}/labels/{name}"
    },
    "search": {
      "issues": "GET /search/issues?q={query}"
    }
  },
  "rate_limits": {
    "authenticated": "5000 requests/hour",
    "search": "30 requests/minute"
  }
}
```

### GitHub GraphQL API Usage

```graphql
# Add issue to project
mutation AddProjectItem($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {
    projectId: $projectId
    contentId: $contentId
  }) {
    item {
      id
    }
  }
}

# Update project field
mutation UpdateProjectField($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId
    itemId: $itemId
    fieldId: $fieldId
    value: $value
  }) {
    projectV2Item {
      id
    }
  }
}

# Query project items
query GetProjectItems($projectId: ID!) {
  node(id: $projectId) {
    ... on ProjectV2 {
      items(first: 100) {
        nodes {
          id
          content {
            ... on Issue {
              number
              title
              state
            }
          }
          fieldValues(first: 10) {
            nodes {
              ... on ProjectV2ItemFieldSingleSelectValue {
                name
                field {
                  ... on ProjectV2SingleSelectField {
                    name
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

---

## Error Handling Patterns

### Retry Logic

```python
{
  "retry_strategy": {
    "max_retries": 3,
    "backoff_strategy": "exponential",
    "backoff_base_seconds": 1,
    "backoff_formula": "base * (2 ** retry_count)",
    "retry_schedule": [1, 2, 4],
    "retryable_errors": [
      "HTTP 5xx",
      "Timeout",
      "Connection error",
      "Rate limit (with backoff)"
    ],
    "non_retryable_errors": [
      "HTTP 4xx (except 429)",
      "Authentication error",
      "Validation error"
    ]
  }
}
```

### Error Response Format

```json
{
  "error": {
    "type": "string (error category)",
    "message": "string (user-facing message)",
    "details": "string (technical details)",
    "remediation": "string (suggested fix)",
    "context": {
      "command": "string",
      "arguments": "object",
      "timestamp": "ISO8601"
    },
    "trace_id": "string (OTel trace ID)"
  }
}
```

---

## Telemetry Schema

### Trace Schema

```json
{
  "trace": {
    "trace_id": "hex string (16 bytes)",
    "spans": [
      {
        "span_id": "hex string (8 bytes)",
        "parent_span_id": "hex string or null",
        "name": "string (operation name)",
        "kind": "enum: [INTERNAL, CLIENT, SERVER]",
        "start_time": "nanoseconds since epoch",
        "end_time": "nanoseconds since epoch",
        "attributes": {
          "gpwk.command": "string",
          "gpwk.issue_number": "integer or null",
          "gpwk.operation": "string",
          "http.method": "string",
          "http.url": "string",
          "http.status_code": "integer"
        },
        "events": [
          {
            "name": "string",
            "timestamp": "nanoseconds since epoch",
            "attributes": {}
          }
        ],
        "status": {
          "code": "enum: [OK, ERROR]",
          "message": "string or null"
        }
      }
    ]
  }
}
```

### Metrics Schema

```json
{
  "metrics": {
    "counters": [
      {
        "name": "gpwk.capture.count",
        "description": "Number of tasks captured",
        "unit": "1",
        "attributes": ["type", "priority", "energy", "completion_detected"]
      },
      {
        "name": "gpwk.delegate.count",
        "description": "Number of AI tasks delegated",
        "unit": "1",
        "attributes": ["priority", "success"]
      },
      {
        "name": "gpwk.errors.count",
        "description": "Number of errors",
        "unit": "1",
        "attributes": ["command", "error_type"]
      }
    ],
    "histograms": [
      {
        "name": "gpwk.command.duration",
        "description": "Command execution duration",
        "unit": "ms",
        "attributes": ["command"]
      },
      {
        "name": "gpwk.github_api.duration",
        "description": "GitHub API call duration",
        "unit": "ms",
        "attributes": ["endpoint", "method"]
      }
    ],
    "gauges": [
      {
        "name": "gpwk.tasks.active",
        "description": "Number of active (open) tasks",
        "unit": "1",
        "attributes": ["status_column"]
      },
      {
        "name": "gpwk.tasks.carryover",
        "description": "Number of tasks with carryover labels",
        "unit": "1",
        "attributes": ["carryover_level"]
      }
    ]
  }
}
```

---

## Integration Guidance for AI Systems

### When to Use GPWK

```json
{
  "use_cases": [
    {
      "scenario": "User asks to create a task",
      "action": "invoke /gpwk.capture with user's description",
      "example": "User: 'Remind me to research GraphQL best practices' → /gpwk.capture 'research GraphQL best practices [AI]'"
    },
    {
      "scenario": "User asks about today's tasks",
      "action": "invoke /gpwk.plan today",
      "example": "User: 'What's on my plate today?' → /gpwk.plan today"
    },
    {
      "scenario": "User completes a task",
      "action": "invoke /gpwk.complete with issue number and optional time range",
      "example": "User: 'I finished issue 123 from 2-3 PM' → /gpwk.complete 123 --from '14:00' --to '15:00'"
    },
    {
      "scenario": "User wants to search tasks",
      "action": "invoke /gpwk.search with query and filters",
      "example": "User: 'Show me high priority AI tasks' → /gpwk.search --label pwk:ai --priority high"
    }
  ]
}
```

### Notation Parsing Rules

```json
{
  "parsing_rules": {
    "task_type": {
      "pattern": "\\[AI\\]|\\[P\\]",
      "case_insensitive": true,
      "position": "anywhere in text",
      "extraction": "remove from final title"
    },
    "priority": {
      "pattern": "!high|!urgent|!medium|!low",
      "case_insensitive": true,
      "position": "anywhere in text",
      "extraction": "remove from final title"
    },
    "energy": {
      "pattern": "~deep|~shallow|~quick",
      "case_insensitive": true,
      "position": "anywhere in text",
      "extraction": "remove from final title"
    },
    "completion_detection": {
      "past_tense_verbs": ["took", "completed", "finished", "did", "wrote", "created", "fixed"],
      "time_range_patterns": [
        "between (\\d{1,2})(:\\d{2})? (AM|PM)? and (\\d{1,2})(:\\d{2})? (AM|PM)?",
        "from (\\d{1,2})(:\\d{2})? (AM|PM)? to (\\d{1,2})(:\\d{2})? (AM|PM)?"
      ],
      "explicit_markers": ["done", "complete", "finished"]
    }
  }
}
```

### Command Invocation Examples

```json
{
  "examples": [
    {
      "user_intent": "Create AI research task",
      "command": "/gpwk.capture",
      "full_invocation": "/gpwk.capture \"research LangChain vs LlamaIndex for RAG [AI] !high ~deep\"",
      "expected_outcome": {
        "issue_created": true,
        "labels": ["pwk:ai", "priority:high", "energy:deep"],
        "project_status": "Inbox",
        "daily_log_appended": true
      }
    },
    {
      "user_intent": "Mark task complete with time tracking",
      "command": "/gpwk.complete",
      "full_invocation": "/gpwk.complete 42 --from '10:30 AM' --to '11:45 AM' --comment 'Implemented JWT validation with tests'",
      "expected_outcome": {
        "issue_closed": true,
        "project_status": "Done",
        "daily_log_entry": "10:30-11:45 - Completed #42: Implement JWT validation ✓\\n  - Implemented JWT validation with tests"
      }
    },
    {
      "user_intent": "Search for blocked tasks",
      "command": "/gpwk.search",
      "full_invocation": "/gpwk.search --label status:blocked",
      "expected_outcome": {
        "issues_returned": "all issues with status:blocked label",
        "sorted_by": "relevance"
      }
    }
  ]
}
```

---

## Performance Benchmarks

```json
{
  "performance_targets": {
    "capture": {
      "p50": "500ms",
      "p95": "1500ms",
      "p99": "2000ms"
    },
    "plan": {
      "p50": "2000ms",
      "p95": "4000ms",
      "p99": "5000ms"
    },
    "complete": {
      "p50": "600ms",
      "p95": "1500ms",
      "p99": "2000ms"
    },
    "delegate": {
      "prepare": {
        "p50": "500ms",
        "p95": "1500ms"
      },
      "execute": {
        "note": "Execution happens in GitHub Action, typically 30-90 seconds"
      }
    }
  }
}
```

---

## Common Patterns and Anti-Patterns

### Recommended Patterns

```json
{
  "patterns": [
    {
      "name": "Morning Triage and Planning",
      "sequence": [
        "/gpwk.triage",
        "/gpwk.plan today"
      ],
      "frequency": "daily",
      "timing": "start of workday"
    },
    {
      "name": "Continuous Capture",
      "sequence": [
        "/gpwk.capture [task] [markers]"
      ],
      "frequency": "as needed throughout day",
      "timing": "when task or idea arises"
    },
    {
      "name": "Evening Review and Carryover",
      "sequence": [
        "/gpwk.review",
        "/gpwk.carryover"
      ],
      "frequency": "daily",
      "timing": "end of workday"
    },
    {
      "name": "AI Delegation Batch",
      "sequence": [
        "/gpwk.delegate --list",
        "(review AI tasks)",
        "trigger GitHub Action for execution"
      ],
      "frequency": "1-2 times per day",
      "timing": "mid-morning or early afternoon"
    }
  ]
}
```

### Anti-Patterns to Avoid

```json
{
  "anti_patterns": [
    {
      "name": "Skipping Triage",
      "problem": "Inbox accumulates, planning becomes ineffective",
      "solution": "Run /gpwk.triage at least once per day"
    },
    {
      "name": "Ignoring Carryover Labels",
      "problem": "Tasks get stuck indefinitely without breakdown",
      "solution": "Run /gpwk.carryover daily, act on c2/c3 tasks"
    },
    {
      "name": "Manual GitHub Updates",
      "problem": "Bypasses telemetry, breaks local log sync",
      "solution": "Always use GPWK commands instead of direct GitHub edits"
    },
    {
      "name": "Over-delegation to AI",
      "problem": "Tasks requiring human judgment delegated to AI",
      "solution": "Review AI delegation guidelines, mark personal tasks with [P]"
    }
  ]
}
```

---

**End of AI/LLM Reference**

*This document optimized for: AI agents, LLMs, automated integrations*
*Human-readable version: `gpwk-requirements.md`*
*Last Updated: 2026-01-10*
*Version: 1.0*
