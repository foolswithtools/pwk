# /pwk.log - View and Manage Daily Log

View today's activity log, see patterns, and manage entries.

## Usage
```
/pwk.log [date?] [--summary | --tasks | --stream]
```

## Behavior

1. **Load the log**:
   - Default: today's log (`logs/YYYY-MM-DD.md`)
   - If date provided: load that specific date
   - If log doesn't exist: offer to create from template

2. **Display options**:
   - `--summary`: Overview with counts and highlights
   - `--tasks`: Show only tasks (planned, carryover, ad-hoc)
   - `--stream`: Show only activity stream
   - Default: Show full log

3. **Analyze and highlight**:
   - Count completed vs. incomplete tasks
   - Identify tasks carried over multiple times
   - Flag blocked items
   - Show AI-delegatable tasks ready for execution

4. **Provide insights**:
   - Time gaps (periods with no logged activity)
   - Most productive hours (based on completions)
   - Recurring patterns across recent days

## Output Format

### Summary View
```
## Daily Log Summary: 2024-01-15

### Status
- Completed: 5/8 tasks (62%)
- Carryover from yesterday: 2 items
- Blocked: 1 item (waiting on design)
- AI-delegatable: 2 tasks ready

### Activity Coverage
- First entry: 08:30
- Last entry: 17:45
- Gaps: 12:00-13:30 (lunch?)

### Highlights
- [x] Shipped API v2 documentation
- [!] [T004] carried over 3 times → consider breakdown
```

### Tasks View
```
## Tasks: 2024-01-15

### Incomplete
- [ ] [T003] [P] Write performance review
- [ ] [T004] [C] [P] Expense report (carryover x3)
- [ ] [T005] [W:design] Waiting for mockups

### Completed
- [x] [T001] [P] Morning standup
- [x] [T002] [AI] Research testing frameworks

### AI-Ready
- [ ] [T006] [AI] Draft meeting notes summary
```

## Examples

```
/pwk.log
→ Shows today's full log

/pwk.log 2024-01-10
→ Shows log from January 10th

/pwk.log --tasks
→ Shows only task list from today

/pwk.log --summary
→ Shows summary with insights
```
