# /pwk.plan - Plan Your Day or Week

Create a plan for today or the week based on carryover items, calendar, and priorities.

## Usage
```
/pwk.plan [today | week | tomorrow]
```

## Behavior

1. **Gather inputs**:
   - Load carryover items from previous day(s)
   - Check `work/` for active work items and their next tasks
   - Load `memory/principles.md` for time-blocking preferences
   - Reference calendar commitments if mentioned

2. **Prioritize**:
   - Carryover items that have been delayed 2+ times get priority
   - Work items with deadlines get priority
   - Balance personal [P] and AI-delegatable [AI] tasks

3. **Time-block** (if principles specify):
   - Deep work windows for complex tasks
   - Meeting buffers
   - Admin/email time
   - Review/shutdown time

4. **Create daily log**:
   - Generate `logs/YYYY-MM-DD.md` from template
   - Populate Carryover section
   - Add Today's Plan section
   - Leave Activity Stream empty for capture

5. **Output the plan**:
   - Summary of the day/week
   - First actions to take
   - AI tasks ready for delegation

## Plan Output Format

### Today's Plan
```markdown
## Plan: 2024-01-15 (Monday)

### Time Blocks
- 08:00-08:30 | Morning routine, /pwk.carryover
- 08:30-10:30 | Deep Work: API documentation [T003, T004]
- 10:30-11:00 | Break + email
- 11:00-12:00 | Meeting: Sprint planning
- 12:00-13:00 | Lunch
- 13:00-15:00 | Deep Work: Performance review [T005]
- 15:00-15:30 | AI delegation check + admin
- 15:30-17:00 | Meetings + collaboration
- 17:00-17:30 | /pwk.review + shutdown

### Priority Tasks (Must Complete)
- [ ] [T003] [P] Finish API v2 docs (deadline today)
- [ ] [T005] [P] Submit performance review

### If Time Allows
- [ ] [T006] [P] Start quarterly planning
- [ ] [T007] [AI] Research new testing framework

### AI Delegation Queue
- [ ] [T008] [AI] Summarize meeting notes from last week
- [ ] [T009] [AI] Draft email template for client outreach

### Carried Over (Address or Breakdown)
- [ ] [T004] [C] Expense report (day 3 - needs breakdown?)
```

### Week Plan
```markdown
## Week Plan: Jan 15-19, 2024

### Weekly Goals
1. Ship API v2 documentation
2. Complete performance review cycle
3. Start Q1 planning

### Day-by-Day
| Day | Focus | Key Tasks |
|-----|-------|-----------|
| Mon | Documentation | API docs, PR reviews |
| Tue | Reviews | Performance reviews, 1:1s |
| Wed | Deep Work | Q1 planning draft |
| Thu | Collaboration | Team planning session |
| Fri | Wrap-up | Finalize, retrospective |

### Deadlines This Week
- Tue: Performance reviews due
- Thu: API v2 launch
- Fri: Q1 OKRs first draft

### AI Batch Tasks (Run Anytime)
- Research competitor features
- Summarize Q4 metrics
- Draft weekly update email
```

## Examples

```
/pwk.plan
→ Creates plan for today

/pwk.plan tomorrow
→ Creates preliminary plan for tomorrow

/pwk.plan week
→ Creates weekly overview
```

## Integration with Principles

References `memory/principles.md` for:
- Deep work window preferences
- Meeting-free time blocks
- Maximum tasks per day
- AI delegation criteria
