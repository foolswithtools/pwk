# /pwk.breakdown - Decompose Complex Work

Take complex work and break it down into actionable tasks. Creates a work item folder if the work spans multiple days.

## Usage
```
/pwk.breakdown [work item name or description]
```

## Behavior

1. **Assess the work**:
   - Is this a single-day task or multi-day effort?
   - Single-day: Add decomposed tasks directly to today's log
   - Multi-day: Create a work item folder in `work/`

2. **Gather context** (if complex):
   - What is the goal/outcome?
   - What are the constraints (time, dependencies)?
   - Who are stakeholders?
   - What's the deadline?

3. **Decompose using principles**:
   - Load `memory/principles.md` for personal work style
   - Apply two-hour rule: no task should take >2 hours
   - Identify AI-delegatable sub-tasks
   - Mark dependencies between tasks

4. **Generate breakdown**:
   - Phase 1: Research/Context gathering
   - Phase 2: Core work
   - Phase 3: Review/Polish
   - Each task marked [P] or [AI]

5. **Create artifacts**:
   - For work items: `work/[name]/context.md`, `breakdown.md`, `progress.md`
   - For simple breakdown: Add tasks to today's log

## Task Breakdown Format

```markdown
## Breakdown: [Work Item Name]

### Phase 1: Setup & Research
- [ ] [T001] [AI] Research existing solutions
- [ ] [T002] [P] Review requirements with stakeholder

### Phase 2: Core Work
- [ ] [T003] [P] Create initial draft
- [ ] [T004] [P] Implement main functionality
- [ ] [T005] [AI] Generate test cases

### Phase 3: Review & Complete
- [ ] [T006] [P] Self-review
- [ ] [T007] [P] Submit for feedback
- [ ] [T008] [P] Address feedback

### Dependencies
- T003 depends on T001, T002
- T006 depends on T003, T004, T005
```

## Examples

**Simple breakdown (same-day):**
```
/pwk.breakdown write quarterly report

→ Added to today's log:
- [ ] [T010] [AI] Gather metrics from dashboard
- [ ] [T011] [AI] Draft executive summary outline
- [ ] [T012] [P] Write narrative sections
- [ ] [T013] [P] Review and finalize
```

**Complex breakdown (multi-day):**
```
/pwk.breakdown API v3 migration

→ Created work item: work/api-v3-migration/
  - context.md: Goals, stakeholders, deadline
  - breakdown.md: 15 tasks across 4 phases
  - progress.md: Empty, ready for updates

→ Added Phase 1 tasks to today's log
```

## Carryover Detection

If a task has been carried over 3+ times, automatically suggest:
```
Task [T004] "Expense report" has been carried over 3 times.
This suggests it may need breakdown.

Would you like to decompose this task?
→ /pwk.breakdown expense report
```

## Output

```
## Breakdown Complete: [Work Item Name]

Created: [N] tasks
- Personal [P]: [X] tasks
- AI-delegatable [AI]: [Y] tasks
- Estimated effort: [Z] hours

Added to today's log: [First phase tasks]
Work item folder: work/[name]/ (if multi-day)

Next action: [T001] [Description]
```
