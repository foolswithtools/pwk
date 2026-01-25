# GPWK Optimize

Analyze your work patterns from daily logs and suggest data-driven optimizations to your work principles.

## Arguments
- `$ARGUMENTS` - Optional: `--weeks N` (default: 2), `--dry-run` (preview only), `--apply` (auto-apply approved changes)

## Instructions

**IMPORTANT**: This command now uses the Python backend with OpenTelemetry instrumentation.

### How It Works

Simply call the Python executable to analyze your work patterns. The Python backend handles:
- ✅ Parsing daily logs from `gpwk/logs/`
- ✅ Calculating completion rates, carryover patterns, and trends
- ✅ Identifying optimization opportunities
- ✅ Generating detailed markdown reports
- ✅ Applying approved changes to principles.md
- ✅ Full OpenTelemetry instrumentation (traces, metrics, logs)

### Execute Command

```bash
# Call Python backend from workspace root
gpwk/bin/gpwk-optimize $ARGUMENTS
```

That's it! The Python backend performs all analysis and provides recommendations.

---

## What the Analysis Does

You are analyzing historical work data to optimize the user's productivity system.

### Step 1: Read Configuration

Read `gpwk/memory/principles.md` to understand current settings:
- Daily task limits
- Deep work windows
- Energy management rules
- Carryover thresholds
- Meeting boundaries
- Break schedules

### Step 2: Collect Historical Data

Read logs from `gpwk/logs/` for the specified time period (default: 2 weeks):

```bash
# Get list of recent logs
ls -1 gpwk/logs/*.md | tail -n 14  # Last 2 weeks
```

For each log file, extract:

**Completion Metrics**:
- Planned tasks count
- Completed tasks count
- Completion rate (%)
- Carryover count (c1, c2, c3)

**Time Patterns**:
- Activity stream timestamps
- Deep work block durations
- Meeting times and durations
- When tasks are actually completed

**Energy Patterns**:
- Which energy-labeled tasks (~deep, ~shallow, ~quick) get completed
- Which get carried over
- Time of day correlation

**Task Types**:
- Personal vs AI-delegatable
- Which types have highest completion rates
- Which types always carry over

**Reflections Analysis**:
- Parse "What went well" / "Could improve" / "Learned"
- Look for recurring themes
- Identify self-reported blockers

### Step 3: Calculate Key Metrics

Aggregate data across all days:

**Completion Analysis**:
```
Average daily completion rate: X%
Best day of week for completion: [day]
Worst day of week for completion: [day]
Tasks planned per day (avg): X
Tasks completed per day (avg): X
Recommended daily limit: [based on 80% success rate]
```

**Carryover Patterns**:
```
Average carryover per day: X
Most carried over task types: [list]
Tasks that hit c3: [specific patterns]
Carryover rate by day of week: [chart]
```

**Energy Matching**:
```
Deep work completion rate: X%
Shallow work completion rate: X%
Quick wins completion rate: X%
Deep work best time: [time range based on completion data]
```

**Time Analysis**:
```
Actual deep work duration (avg): X hours
Planned vs actual meeting time: X hrs planned, Y hrs actual
Most productive hours: [based on activity timestamps]
```

### Step 4: Identify Optimization Opportunities

Compare actual patterns against current principles:

**Daily Task Limits**:
```
Current setting: "Maximum significant tasks: 4-6"
Your data: Average planned: 3.5, Average completed: 2.8 (80% rate)
Recommendation: Reduce max to 3-4 to increase success rate
Rationale: You complete 2.8/day with 80% success. Lowering limit to 3
          would give 93% success rate and build momentum.
```

**Deep Work Windows**:
```
Current setting: "Preferred time: Morning (9:00-12:00)"
Your data: Actual deep work happens 14:00-16:00 (70% of deep work)
Recommendation: Shift deep work window to 14:00-16:00
Rationale: Your activity data shows afternoon is when you actually
          complete deep work tasks most consistently.
```

**Carryover Rules**:
```
Current setting: "c3 threshold: Mandatory action"
Your data: 3 tasks hit c3 in last 2 weeks, 0 were broken down
Recommendation: Add automated breakdown trigger at c2
Rationale: Tasks that hit c2 have 80% chance of hitting c3.
          Earlier intervention prevents chronic carryover.
```

**Meeting Boundaries**:
```
Current setting: "No meetings before 10:00 AM"
Your data: 40% of activities logged before 10:00 AM are family/personal
Recommendation: Protect 7:00-9:00 AM as family time, allow meetings 9:00+
Rationale: Your mornings are naturally family-focused. Acknowledge this
          and optimize around it rather than fighting it.
```

### Step 5: Generate Optimization Report

Create a detailed report with recommendations:

````markdown
# GPWK Optimization Report
**Generated**: YYYY-MM-DD HH:MM
**Data Period**: YYYY-MM-DD to YYYY-MM-DD (N days)
**Logs Analyzed**: N files

## Executive Summary

Based on N days of work data, your system is performing at X% completion rate.
Key findings:
- [Top 3 insights]

## Recommended Changes

### HIGH PRIORITY ⚠️

#### 1. Adjust Daily Task Limit
**Current**: Maximum significant tasks: 4-6
**Recommended**: Maximum significant tasks: 3
**Data**:
- Average planned: 3.5 tasks/day
- Average completed: 2.8 tasks/day
- Current success rate: 80%
- Projected success rate with new limit: 93%

**Rationale**:
You consistently plan 3-4 tasks and complete ~3. Lowering the maximum
to 3 would give you a 93% daily success rate, building confidence and
momentum. Better to complete 3/3 than 4/6.

**Impact**: High - Improves daily satisfaction and reduces carryover

---

#### 2. Shift Deep Work Window
**Current**: Preferred time: Morning (9:00-12:00)
**Recommended**: Preferred time: Afternoon (14:00-16:00)
**Data**:
- Morning deep work completion: 30%
- Afternoon deep work completion: 70%
- Morning activities: 40% family/personal commitments

**Rationale**:
Your activity logs show that 70% of completed deep work happens in the
afternoon. Mornings are naturally filled with family commitments. Work
with your natural rhythm, not against it.

**Impact**: Very High - Aligns planning with actual behavior

---

### MEDIUM PRIORITY

#### 3. Add c2 Breakdown Trigger
**Current**: c3 threshold: Mandatory action
**Recommended**: c2 threshold: Suggest breakdown
**Data**:
- Tasks at c2: 5 in last 2 weeks
- Of those, 3 (60%) progressed to c3
- Tasks broken down at c3: 0

**Rationale**:
Tasks that hit c2 are likely to become chronic carryovers. Earlier
intervention prevents this pattern. Suggest breakdown at c2, mandate at c3.

**Impact**: Medium - Reduces chronic carryover

---

### LOW PRIORITY

#### 4. Increase Quick Win Buffer
**Current**: No specific quick win time allocation
**Recommended**: Reserve 15 min/day for quick wins
**Data**:
- Quick wins planned: 1.5/day
- Quick wins completed: 1.3/day (87% success)
- High satisfaction noted in reflections when quick wins done

**Rationale**:
Quick wins have high completion rate and generate satisfaction.
Explicitly scheduling 15 min increases likelihood of daily quick win.

**Impact**: Low - Minor morale boost

---

## Patterns Identified

### Strengths
- Excellent end-of-day review consistency (100% of days)
- High quick win completion rate (87%)
- Strong evening productivity for deep work
- Good activity tracking discipline

### Growth Areas
- Morning planning often doesn't match afternoon reality
- Complex tasks rarely get broken down proactively
- Meeting time estimates often short by 20-30%
- Personal health tasks mentioned in reflections but rarely scheduled

## Reflection Themes

From "Could improve" sections across N days:
1. "Could have started earlier" (4 mentions)
2. "More tasks from backlog vs new issues" (2 mentions)
3. "Include personal health tasks" (3 mentions)
4. "Better time estimates" (2 mentions)

### Suggested Action:
Add health task reminder to morning planning template

## Completion Trends

| Metric | Week 1 | Week 2 | Trend |
|--------|--------|--------|-------|
| Avg Completion Rate | 67% | 87% | ↑ 20% |
| Avg Carryover | 1.2 | 0.3 | ↓ 75% |
| Deep Work Hours | 2.1 | 2.8 | ↑ 33% |

**Analysis**: Strong improvement trajectory. System is working.

## Recommended Principle Updates

If you approve these changes, the following will be updated in `gpwk/memory/principles.md`:

```diff
## Task Management

### Daily Limits
- **Maximum significant tasks**: 4 (scale up to 6 as you build momentum)
+ **Maximum significant tasks**: 3 (proven sustainable with 93% success)
- **Maximum total tasks**: 10
+ **Maximum total tasks**: 8

## Time Management

### Deep Work Windows
- **Preferred time**: Morning (9:00-12:00) - adjust based on your chronotype
+ **Preferred time**: Afternoon (14:00-16:00) - based on your actual completion data
+ **Family time**: Protect 7:00-9:00 AM for family commitments

### Carryover Rules
+ **c2 threshold**: Suggest breakdown, identify blockers
  **c3 threshold**: Mandatory action - either break down OR archive with reason
```

---

## Next Steps

1. **Review Recommendations**: Read each recommendation and rationale
2. **Approve/Reject**: Decide which changes to implement
3. **Apply Changes**: Update principles.md with approved changes
4. **Monitor**: Track impact over next 2 weeks
5. **Iterate**: Run /gpwk.optimize again in 2 weeks

Would you like to:
- [A] Apply all HIGH PRIORITY changes
- [B] Apply all recommendations (high + medium + low)
- [C] Review each recommendation individually
- [D] Export report and make manual changes
- [E] Cancel - no changes

Enter your choice:
````

### Step 6: Interactive Approval

Based on user choice:

**Option A**: Apply high priority changes only
**Option B**: Apply all recommended changes
**Option C**: Go through each recommendation with yes/no prompts
**Option D**: Save report to `ideas/optimization-report-YYYY-MM-DD.md`
**Option E**: Exit without changes

### Step 7: Apply Approved Changes

For each approved recommendation:

1. Read current `gpwk/memory/principles.md`
2. Make specific edits using exact diff patterns
3. Add comment noting: "Updated by /gpwk.optimize on YYYY-MM-DD based on N days of data"
4. Save updated principles

### Step 8: Create Tracking Issue

Create GitHub issue to track the experiment:

```bash
gh issue create \
  --repo <owner>/<repo> \
  --title "Optimization Experiment: [changes applied]" \
  --label "pwk:task,priority:medium" \
  --body "$(cat <<'EOF'
## Optimization Applied
- **Date**: YYYY-MM-DD
- **Data Period**: N days (YYYY-MM-DD to YYYY-MM-DD)
- **Source**: /gpwk.optimize

## Changes Made
1. [Change 1]
2. [Change 2]
...

## Expected Impact
- [Impact 1]
- [Impact 2]

## Monitoring Plan
- Track same metrics for next 2 weeks
- Compare completion rates before/after
- Re-run /gpwk.optimize on YYYY-MM-DD
- Decide: keep, revert, or refine

## Success Criteria
- Completion rate: Target X% (current Y%)
- Carryover rate: Target <0.5/day (current Z/day)
- Self-reported satisfaction: Improved

## Notes
(Track observations during the experiment)
EOF
)"
```

### Step 9: Confirmation

```
✓ Optimization Complete

Applied Changes:
  • Updated daily task limit: 6 → 3
  • Shifted deep work window: 9:00-12:00 → 14:00-16:00
  • Added c2 breakdown trigger

Updated File:
  gpwk/memory/principles.md

Tracking Issue:
  #XX - Optimization Experiment: Task Limits & Deep Work Timing

Next Steps:
  1. Use updated principles for next 2 weeks
  2. Continue daily logging as normal
  3. Run /gpwk.optimize again on YYYY-MM-DD
  4. Compare results and iterate

Optimization report saved:
  ideas/optimization-report-YYYY-MM-DD.md
```

## Error Handling

- If insufficient data (< 7 days): Suggest running after more data collection
- If no clear patterns: Report "System appears well-tuned, no changes recommended"
- If principles.md not found: Error and suggest /gpwk.setup
- If logs directory empty: Error and explain need for daily logging

## Advanced Features

### Pattern Recognition

Look for:
- **Weekend effect**: Different patterns Sat/Sun
- **Week start**: Monday vs other days
- **Energy crashes**: Days with 0% completion following high-output days
- **Meeting clustering**: Days with >3 hours meetings → low task completion
- **Burnout indicators**: Multiple days of "could improve: start earlier"

### Predictive Recommendations

```
⚠️ Burnout Risk Detected
Pattern: Last 3 "could improve" mentioned starting earlier
Recommendation: You may be over-planning. Reduce daily limit by 1.
```

### Celebration of Wins

```
🎉 Improvement Detected!
Week-over-week completion rate: +20%
Carryover reduction: -75%
Keep doing what you're doing!
```

## Integration Points

- Runs standalone: `/gpwk.optimize`
- Suggested frequency: Every 2 weeks
- Creates tracking issue for A/B testing
- Exports report to ideas/ for review
- Updates principles.md with data-driven changes

---

## Example Usage

```bash
# Basic run - analyze last 2 weeks, interactive approval
/gpwk.optimize

# Analyze last 4 weeks
/gpwk.optimize --weeks 4

# Preview only, no changes
/gpwk.optimize --dry-run

# Auto-apply all recommendations (use with caution)
/gpwk.optimize --apply
```

---

*This is a meta-system: it observes your work patterns and suggests improvements to the system itself.*
