# /pwk.review - End of Day Review

Review today's accomplishments, reflect on the day, and prepare for tomorrow.

## Usage
```
/pwk.review [--quick | --full]
```

## Behavior

1. **Load today's log**:
   - Read `pwk/logs/YYYY-MM-DD.md`
   - Gather all sections: Plan, Activity Stream, Tasks

2. **Calculate metrics**:
   - Tasks completed vs. planned
   - Ad-hoc tasks that emerged
   - Time coverage (first to last entry)
   - AI tasks executed

3. **Generate review**:
   - What was accomplished
   - What wasn't completed (and why)
   - What emerged that wasn't planned
   - Patterns and insights

4. **Prompt reflection**:
   - What went well?
   - What blocked progress?
   - What to do differently tomorrow?

5. **Prepare tomorrow**:
   - Preview carryover items
   - Suggest priority for tomorrow
   - Queue AI tasks for overnight/morning

6. **Update log**:
   - Add Reflections section to today's log
   - Mark the log as reviewed

## Review Output

### Quick Review
```
/pwk.review --quick

## Quick Review: 2024-01-15

Completed: 6/8 tasks (75%)
Highlight: Shipped API v2 documentation
Incomplete: Performance review, expense report
Tomorrow's priority: Performance review (deadline)

Carryover ready. Run /pwk.carryover tomorrow morning.
```

### Full Review
```
/pwk.review --full

## Daily Review: 2024-01-15

### Accomplishments
- [x] [T001] Shipped API v2 documentation
- [x] [T002] Sprint planning meeting
- [x] [T003] Code review for PR #234
- [x] [T004] [AI] Research testing frameworks
- [x] [T005] Fixed production bug (ad-hoc)
- [x] [T006] Updated team wiki

### Metrics
| Metric | Value |
|--------|-------|
| Tasks Completed | 6 |
| Tasks Planned | 8 |
| Completion Rate | 75% |
| Ad-hoc Tasks | 2 |
| AI-Delegated | 1 |
| First Activity | 08:30 |
| Last Activity | 17:45 |
| Active Hours | 9.25 |

### Incomplete
- [ ] [T007] Performance review
  Reason: Meeting ran long, will complete tomorrow

- [ ] [T008] Expense report (carryover x3)
  Reason: Avoiding? Need to breakdown or delegate

### Unplanned Work
- Fixed production bug (2 hours)
- Updated wiki after team questions (30 min)
→ 2.5 hours of unplanned work

### Insights
- Morning deep work block was productive (completed docs)
- Afternoon fragmented by ad-hoc requests
- Consider: Block afternoon time better?

### AI Task Summary
- Executed: 1 task (testing research)
- Queued for tomorrow: 2 tasks
  - Draft meeting notes
  - Summarize Q4 metrics

---

### Reflections
(Fill in below)

**What went well?**
>

**What blocked progress?**
>

**What to change tomorrow?**
>

---

### Tomorrow Preview
Carryover: 2 items
Priority: Performance review (deadline tomorrow)
Suggested first task: Performance review in morning deep work
```

## Patterns Detection

After multiple days of reviews, detect patterns:
```
### Weekly Patterns (based on 5 days)

- Average completion rate: 72%
- Most productive day: Wednesday (85%)
- Least productive: Friday (60%)
- Recurring carryover: Expense report (5 days!)
- Ad-hoc work average: 1.5 hours/day

Recommendations:
1. Address expense report - it's been 5 days
2. Block more time for ad-hoc on Fridays
3. Schedule deep work for Wed when most productive
```

## Integration

- Updates `pwk/logs/YYYY-MM-DD.md` with Reflections section
- Prepares data for `/pwk.carryover` tomorrow
- Can trigger `/pwk.breakdown` for chronic carryover items
