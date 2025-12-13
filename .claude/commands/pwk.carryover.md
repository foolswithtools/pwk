# /pwk.carryover - Move Incomplete Items Forward

Review yesterday's incomplete items and carry them to today's log.

## Usage
```
/pwk.carryover [--auto | --interactive]
```

## Behavior

1. **Load yesterday's log**:
   - Find most recent `logs/YYYY-MM-DD.md` before today
   - Extract all incomplete tasks (unchecked `- [ ]`)
   - Note any blocked items `[W]`

2. **Analyze carryover**:
   - Count how many times each task has been carried over
   - Flag tasks carried over 3+ times for breakdown
   - Identify if any blockers have been resolved

3. **Present for review** (interactive mode):
   - Show each incomplete task
   - Options: Carry forward / Drop / Breakdown / Delegate to AI

4. **Create today's log**:
   - Generate from template if doesn't exist
   - Add carryover items to Carryover section
   - Mark items with `[C]` and increment carryover count

5. **Update yesterday's log**:
   - Mark carried items as "→ Carried to [date]"
   - Add end-of-day reflection if not present

## Carryover Modes

### Interactive (default)
```
/pwk.carryover

## Carryover Review: 2024-01-14 → 2024-01-15

### Incomplete from yesterday:

1. [ ] [T003] [P] Write performance review
   Status: First carryover
   → [C]arry / [D]rop / [B]reakdown / [A]I delegate?

2. [ ] [T004] [P] Expense report
   Status: Carried over 3 times!
   → Recommend: Breakdown
   → [C]arry / [D]rop / [B]reakdown / [A]I delegate?

3. [ ] [T005] [W:design] Waiting for mockups
   Status: Still blocked
   → [C]arry / [D]rop / [F]ollow up?
```

### Auto Mode
```
/pwk.carryover --auto

→ Automatically carries all incomplete items
→ Flags items needing attention
→ Creates today's log with carryover section
```

## Carryover Notation

Tasks gain carryover markers:
```
First carryover:  [C]
Second carryover: [C2]
Third carryover:  [C3] ← Triggers breakdown suggestion
```

## Output Format

```
## Carryover Complete

From: 2024-01-14
To:   2024-01-15

### Carried Forward (3)
- [ ] [T003] [C] [P] Write performance review
- [ ] [T004] [C3] [P] Expense report ← NEEDS BREAKDOWN
- [ ] [T005] [C] [W:design] Waiting for mockups

### Dropped (1)
- [~] [T006] [P] Optional cleanup task (deprioritized)

### Converted to AI (1)
- [ ] [T007] [AI] Research meeting → was [P], now delegated

### Blockers to Follow Up
- [T005] waiting on design team - Day 2

---
Today's log created: logs/2024-01-15.md
Run /pwk.plan to plan your day.
```

## Carryover Chain Detection

When a task reaches 3 carryovers:
```
[T004] "Expense report" has been carried over 3 times.

This pattern suggests:
1. Task is too vague → needs clearer definition
2. Task is too large → needs breakdown
3. Task is being avoided → needs motivation strategy
4. Task has hidden blockers → needs investigation

Recommended action: /pwk.breakdown expense report

Or mark as:
- [D]rop: Remove from active list
- [S]omeday: Move to someday/maybe list
- [D]elegate: Assign to someone else
```
