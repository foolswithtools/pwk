# Issue Body Templates

> Templates used by GPWK commands when creating GitHub Issues.

## Standard Task

```markdown
## Captured
- **Date**: {{DATE_TIME}}
- **Source**: GPWK Capture

## Context
{{CONTEXT}}

## Acceptance Criteria
- [ ] {{CRITERION}}

## Notes
(Add notes as you work)
```

## Work Item (Parent)

```markdown
## Overview
{{DESCRIPTION}}

## Scope
**In Scope:**
- {{IN_SCOPE_ITEM}}

**Out of Scope:**
- {{OUT_OF_SCOPE_ITEM}}

## Success Criteria
- [ ] {{SUCCESS_CRITERION}}

## Phases
<!-- Sub-issues linked below -->

### Phase 1: {{PHASE_NAME}}
- [ ] #{{ISSUE}} - {{TASK}} [{{TYPE}}]

## Progress
- **Started**: {{DATE}}
- **Target**: {{TARGET_DATE}}
- **Status**: Not Started | In Progress | Blocked | Complete

## Related
- {{RELATED_LINKS}}
```

## Sub-Issue (Child of Work Item)

```markdown
## Parent Work Item
Part of #{{PARENT_NUMBER}}: {{PARENT_TITLE}}

## Task
{{DESCRIPTION}}

## Phase
{{PHASE_NAME}} ({{N}} of {{TOTAL}} tasks in this phase)

## Acceptance Criteria
- [ ] {{CRITERION}}

## Notes
(Add notes as you work)
```

## AI Task Result

```markdown
## AI Execution Results

**Executed by**: Claude (via GPWK)
**Date**: {{DATE_TIME}}

### Summary
{{BRIEF_SUMMARY}}

### Results
{{DETAILED_RESULTS}}

### Sources/References
{{SOURCES}}

### Suggested Next Steps
- {{NEXT_STEP}}

---
*This task was executed by AI delegation. Review results and close if satisfactory.*
```

## Carryover Notice

```markdown
📅 **Carryover Notice**

This task was carried over from {{PREVIOUS_DATE}}.
Current carryover count: **{{CARRYOVER_LEVEL}}**

If this task continues to be carried over, consider:
- Breaking it into smaller subtasks
- Identifying blockers
- Re-evaluating priority

*Logged by GPWK at {{TIME}}*
```
