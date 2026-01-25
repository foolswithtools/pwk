# GPWK Review

End-of-day reflection and daily shutdown ritual with full telemetry.

## Arguments
- None required - Interactive review session

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable for an end-of-day review. The Python backend handles:
- ✅ Analyzing today's completed tasks
- ✅ Checking for incomplete tasks requiring carryover
- ✅ Prompting for reflections and learnings
- ✅ Updating daily log with metrics and reflections
- ✅ Suggesting tomorrow's top priority
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-review
```

That's it! The Python backend guides you through an interactive review.

## Review Workflow

The end-of-day review follows this structure:

1. **Fetch Today's Data**
   - Issues completed today
   - Issues still in "Today" column
   - Total time on tasks
   - Activity stream entries

2. **Calculate Metrics**
   - Completion rate (completed / planned)
   - Task types (personal, AI, work items)
   - Energy distribution (deep, shallow, quick)
   - Time allocation

3. **Interactive Prompts**
   - "What went well today?"
   - "What could be improved?"
   - "What did you learn?"
   - "What's your top priority for tomorrow?"

4. **Update Daily Log**
   - Write metrics section
   - Add reflections
   - List completed and incomplete items
   - Record review timestamp

5. **Prepare for Tomorrow**
   - Suggest running `/gpwk.carryover` for incomplete tasks
   - Recommend tomorrow's focus

## Daily Shutdown Ritual

From your principles (default: 5:30 PM):

**Purpose**: Clear separation between work and personal time
**Duration**: 10-15 minutes
**Non-negotiable**: Defend this time boundary

### The Ritual

1. **Run `/gpwk.review`** - Reflect on the day
2. **Clear Today column** - Apply carryover labels or close tasks
3. **Set tomorrow's priority** - Pick one task for morning focus
4. **Physical shutdown** - Close laptop, leave desk, change location
5. **NO work after shutdown** - No email, Slack, or code

## Features

### Python Backend Benefits
- **Automated metrics**: Calculates completion rates, time allocation
- **Pattern detection**: Identifies trends over time
- **Guided reflection**: Structured prompts for meaningful insights
- **Log integration**: Updates daily log automatically
- **Full telemetry**: Track review patterns and productivity trends

### Telemetry Collected
- **Traces**: Complete review session flow in Grafana Tempo
- **Metrics**: Completion rates, task counts, review duration
- **Logs**: Structured logs in Grafana Loki
- **Attributes**: Reflections, learnings, completion patterns

### Productivity Metrics

Automatically calculated:
- **Completion rate**: Percentage of planned tasks completed
- **Task distribution**: Personal vs AI vs work items
- **Energy usage**: Deep vs shallow vs quick work
- **Carryover count**: Tasks needing continuation
- **Streak data**: Consecutive days of good completion

## Example Session

```bash
/gpwk.review
```

Output:
```
📊 Daily Review: 2025-12-21

=== Today's Metrics ===
Planned: 6 tasks
Completed: 5 (83%)
In Progress: 1

Task Types:
  • Personal: 4
  • AI delegated: 1
  • Work items: 0

Energy Distribution:
  • Deep work: 2 hours
  • Shallow work: 1 hour
  • Quick wins: 3

=== Reflection Prompts ===

What went well today?
> Got the PowerPoint done early and had good deep work session

What could be improved?
> Started a bit late, could wake up 30 min earlier

What did you learn?
> Grafana telemetry setup is easier than expected

What's your top priority for tomorrow?
> Review and send PowerPoint to vendor

=== Summary ===

Completed Issues (5):
  ✓ #27 - PowerPoint with Grafana details
  ✓ #45 - Took Mr. Noodles for walk
  ✓ #39 - Giulianna's piano recital
  ✓ #46 - Test Python telemetry (closed during triage)
  ✓ #47 - Test special characters (closed during triage)

Incomplete (1):
  → #42 - Run /gpwk.optimize (scheduled for 12/27)

Daily log updated: logs/2025-12-21.md
Review completed at: 17:30

Next Steps:
  • Run /gpwk.carryover to update incomplete task labels
  • Shutdown ritual: Close laptop, leave desk
  • Tomorrow priority: Review and send PowerPoint
  • NO work after 5:30 PM ✓
```

## Reflection Quality

Good reflections are:
- **Specific**: "Got PowerPoint done early" not "was productive"
- **Actionable**: "Wake up 30 min earlier" not "be better"
- **Honest**: Acknowledge both wins and struggles
- **Learning-focused**: What did you discover?

The Python backend:
- Saves reflections to daily log
- Tracks reflection themes over time
- Feeds data to `/gpwk.optimize` for pattern analysis

## Integration Points

- **Reads**: Today's daily log file
- **Reads**: GitHub issues completed/incomplete today
- **Updates**: Daily log "End of Day" section
- **Triggers**: `/gpwk.carryover` suggestion for incomplete tasks
- **Feeds**: `/gpwk.optimize` for productivity analysis

## Best Practices

### When to Review
- **Consistent time**: Same time every day (default: 5:30 PM)
- **Before shutdown**: Never skip, even if day was "bad"
- **10-15 minutes**: Don't rush, don't overthink

### What Makes a Good Review
- **Celebrate wins**: Even small completions matter
- **Be honest**: Track real patterns, not aspirational ones
- **Focus on learning**: What can tomorrow-you benefit from?
- **Set one priority**: Not three, not five - ONE top task for tomorrow

### Building the Habit
- **Use physical cues**: Set alarm, change location
- **Track streak**: Review completion rate in telemetry
- **Protect the time**: It's as important as a meeting
- **After shutdown = OFF**: Truly disconnect

## Metrics for Optimization

The review collects data for `/gpwk.optimize`:

- **Completion patterns**: Which days are most productive?
- **Task type distribution**: Am I delegating enough to AI?
- **Energy allocation**: Am I matching energy to task type?
- **Reflection themes**: What issues come up repeatedly?
- **Carryover rates**: Which tasks get stuck?

This data enables data-driven productivity improvements.

## Troubleshooting

**Error: Virtual environment not found**
```bash
cd gpwk/lib/python
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Error: Configuration not found**
Run `/gpwk.setup` first to create GitHub configuration.

**Error: No daily log for today**
Run `/gpwk.plan` first to create today's log file.

**Skipped shutdown ritual:**
It happens. Just do it tomorrow. Don't beat yourself up.

**View telemetry:**
- Traces: Grafana Tempo (search for `gpwk_review`)
- Metrics: Grafana Prometheus (`gpwk.review.*`)
- Logs: Grafana Loki (label: `service_name="gpwk"`)
