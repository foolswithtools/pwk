# /pwk.delegate - Delegate Tasks to AI

Mark tasks for AI execution or execute AI-delegatable tasks.

## Usage
```
/pwk.delegate [--queue | --execute | --list]
```

## Behavior

### List Mode (default)
1. **Scan for AI tasks**:
   - Check today's log for `[AI]` marked tasks
   - Check `pwk/work/*/breakdown.md` for AI tasks
   - Check inbox for delegatable items

2. **Display delegation queue**:
   - Show all AI-ready tasks
   - Show status (pending, in-progress, completed)

### Queue Mode
1. **Mark tasks for AI**:
   - Convert `[P]` task to `[AI]` task
   - Add context needed for AI execution
   - Set priority/order

### Execute Mode
1. **Execute AI tasks**:
   - Take next AI task from queue
   - Execute using Claude's capabilities
   - Report results back to log
   - Mark task complete

## Delegation Criteria

Reference `pwk/memory/principles.md` for what to delegate:

**Good for AI delegation:**
- Research tasks ("find out about X")
- Draft creation ("write first draft of X")
- Summarization ("summarize meeting notes")
- Data gathering ("collect metrics from X")
- Boilerplate ("create template for X")
- Code generation ("write function to do X")
- Analysis ("analyze trends in X")

**Keep personal:**
- Relationship tasks (1:1s, difficult conversations)
- Strategic decisions
- Creative direction
- Physical tasks
- Tasks requiring your unique context

## Output Formats

### List View
```
/pwk.delegate --list

## AI Delegation Queue

### Ready to Execute
- [ ] [T005] [AI] Research React testing best practices
  Context: For new project, need comparison of Jest vs Vitest

- [ ] [T008] [AI] Summarize Q4 metrics report
  Context: 20-page report at docs/q4-metrics.pdf

- [ ] [T010] [AI] Draft weekly update email
  Context: Based on this week's completed tasks

### In Progress
- [~] [T003] [AI] Generate API documentation
  Status: 60% complete, working on endpoints section

### Completed Today
- [x] [T001] [AI] Research competitor pricing
  Result: Summary saved to pwk/work/pricing-research/findings.md

---
3 tasks ready | 1 in progress | 1 completed

Run `/pwk.delegate --execute` to work on next task.
```

### Queue Mode
```
/pwk.delegate --queue

Which task would you like to delegate to AI?

Current personal tasks:
1. [ ] [T006] [P] Research database options
2. [ ] [T007] [P] Write meeting agenda
3. [ ] [T009] [P] Collect team feedback

Select task number (or describe new task): 1

Converting [T006] to AI task...

Please provide context for AI execution:
> Compare PostgreSQL vs MySQL vs MongoDB for our use case.
> We need: scalability, JSON support, and easy backup.

Task queued:
- [ ] [T006] [AI] Research database options
  Context: Compare PostgreSQL vs MySQL vs MongoDB.
           Requirements: scalability, JSON support, easy backup.

Ready to execute? [Y/n]
```

### Execute Mode
```
/pwk.delegate --execute

## Executing: [T005] Research React testing best practices

Context: For new project, need comparison of Jest vs Vitest

Working...

---

### Result: React Testing Framework Comparison

| Feature | Jest | Vitest |
|---------|------|--------|
| Speed | Moderate | Fast (Vite-native) |
| Config | Complex | Simple |
| ESM Support | Partial | Native |
| Watch Mode | Yes | Yes (faster) |
| Community | Larger | Growing |

**Recommendation**: Vitest for new Vite projects, Jest for existing CRA projects.

**Detailed findings saved to**: pwk/work/testing-research/comparison.md

---

Task completed: [T005]
Updated: pwk/logs/2024-01-15.md

Next AI task: [T008] Summarize Q4 metrics report
Execute next? [Y/n]
```

## Batch Execution

For multiple AI tasks:
```
/pwk.delegate --execute --all

Executing 3 AI tasks in sequence...

1/3 [T005] Research React testing... ✓ (2 min)
2/3 [T008] Summarize Q4 metrics... ✓ (3 min)
3/3 [T010] Draft weekly email... ✓ (1 min)

All AI tasks completed.
Results logged to today's activity stream.
```

## Result Handling

AI task results are:
1. Saved to appropriate location (work folder, log, or new file)
2. Task marked `[x]` in the log
3. Activity stream updated with completion
4. Summary shown to user for review
