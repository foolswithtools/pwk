# /pwk.principles - View or Update Personal Work Principles

Manage your personal work principles that govern how you work.

## Usage
```
/pwk.principles [--view | --edit | --add "principle"]
```

## Behavior

### View Mode (default)
1. Load `memory/principles.md`
2. Display all principles with descriptions
3. Show how principles are applied in other commands

### Edit Mode
1. Open principles for editing
2. Guide through principle review
3. Validate changes

### Add Mode
1. Add a new principle
2. Define its application
3. Update relevant commands

## Principles Structure

```markdown
# Personal Work Principles

> These principles govern how I work. They are referenced by all /pwk.* commands.

## Time Management

### P1: Deep Work Windows
- Protect 2-hour blocks for focused work
- No meetings before 10 AM
- Applied in: /pwk.plan (time blocking)

### P2: Two-Minute Rule
- If a task takes less than 2 minutes, do it immediately
- Don't add to task list, just execute
- Applied in: /pwk.capture (filters quick tasks)

## Task Management

### P3: Maximum Daily Tasks
- No more than 6 significant tasks per day
- Anything beyond goes to tomorrow
- Applied in: /pwk.plan (task limiting)

### P4: Carryover Limit
- Task carried over 3+ times must be addressed
- Options: breakdown, delegate, drop, or schedule
- Applied in: /pwk.carryover (flagging)

## AI Delegation

### P5: Delegation Criteria
- Delegate: Research, drafts, summaries, boilerplate
- Keep: Relationships, decisions, creative direction
- Applied in: /pwk.delegate (filtering)

### P6: Review AI Output
- Always review AI-generated content before using
- AI drafts are starting points, not final products
- Applied in: /pwk.delegate (workflow)

## Energy Management

### P7: Match Task to Energy
- Creative work in high-energy periods (morning)
- Admin work in low-energy periods (afternoon)
- Applied in: /pwk.plan (scheduling)

### P8: End-of-Day Shutdown
- Always run /pwk.review before stopping
- Clear mental load for next day
- Applied in: /pwk.review (ritual)

## Capture & Process

### P9: Capture Before Process
- Log activities first, organize later
- Don't let capture interrupt flow
- Applied in: /pwk.capture (quick entry)

### P10: Weekly Review
- Sunday evening: review week, plan next week
- Monthly: review principles, adjust as needed
- Applied in: /pwk.plan week
```

## Adding Principles

```
/pwk.principles --add "No meetings on Wednesdays"

## Adding New Principle

Name: No Meetings Wednesday
Category: Time Management

Description:
> Keep Wednesdays meeting-free for deep work

Application:
- [ ] /pwk.plan: Warn if meetings scheduled Wednesday
- [ ] /pwk.review: Track compliance

Added as P11 in memory/principles.md
```

## Principle Templates

Common principles to consider:
- Time blocking preferences
- Meeting-free days/hours
- Task size limits
- Delegation criteria
- Communication windows
- Focus/break ratios
- Weekly review timing

## Validation

When editing principles, validate:
1. No conflicts between principles
2. Clear application to commands
3. Measurable when possible
4. Aligned with goals
