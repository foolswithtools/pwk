# /pwk.capture - Quick Activity Capture

Quickly capture an activity, thought, task, or note into today's log or inbox.

## Usage
```
/pwk.capture [activity description]
```

## Behavior

1. **Determine destination**:
   - If activity is actionable → add to today's log as a task
   - If activity is a note/thought → add to inbox for later processing
   - If activity is a time entry → add to Activity Stream with timestamp

2. **Check for today's log**:
   - Look for `logs/YYYY-MM-DD.md` (today's date)
   - If it doesn't exist, create from `templates/daily-log.md`

3. **Parse the input**:
   - Starts with "working on" / "started" / "doing" → Activity Stream entry
   - Starts with "todo" / "need to" / "must" → Task entry
   - Starts with "idea" / "thought" / "note" → Inbox entry
   - Contains "[AI]" → Mark as AI-delegatable task
   - Contains "[W]" or "waiting" → Mark as waiting/blocked

4. **Add entry with context**:
   - Timestamp: Current time (HH:MM)
   - Auto-increment task IDs if adding tasks
   - Preserve any tags or markers from input

5. **Confirm capture**:
   - Show where the entry was added
   - Show the formatted entry

## Examples

**Activity logging:**
```
/pwk.capture working on API documentation
→ Adds to Activity Stream: "10:30 | Working on API documentation"
```

**Task capture:**
```
/pwk.capture todo: finish expense report
→ Adds to Today's Plan: "- [ ] [T001] [P] Finish expense report"
```

**AI-delegatable task:**
```
/pwk.capture [AI] research React testing best practices
→ Adds: "- [ ] [T002] [AI] Research React testing best practices"
```

**Quick thought:**
```
/pwk.capture idea: maybe we should refactor the auth module
→ Adds to inbox/quick-capture.md with timestamp
```

## Output Format

```
Captured to [logs/2024-01-15.md | inbox/quick-capture.md]:

[The formatted entry]

Today's log now has [N] tasks, [M] activities logged.
```
