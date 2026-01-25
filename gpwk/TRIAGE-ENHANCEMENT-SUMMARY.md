# GPWK Triage Enhancement - Bulk Issue Review & Close

**Date**: 2025-12-21
**Enhancement**: Added bulk issue review and closure with telemetry

---

## What Was Added

### New Functionality

**Bulk Issue Review & Close**
- Close multiple issues at once
- Automatic test issue detection
- Smart closure comments based on issue type
- Full OpenTelemetry instrumentation

### Command Syntax

```bash
# Close a range of issues
gpwk/bin/gpwk-triage --close 49-54

# Close specific issues (comma-separated)
gpwk/bin/gpwk-triage --close 49,50,51,52,53,54

# Close specific issues (space-separated)
gpwk/bin/gpwk-triage --close 49 50 51 52 53 54
```

---

## Files Modified

### 1. `gpwk/lib/python/gpwk_core/commands/triage.py`

**Added Methods:**
- `review_and_close_issues()` - Main method for bulk closure with telemetry
- `_get_issue_details()` - Fetch issue details from GitHub
- `_build_closure_comment()` - Generate smart closure comments
- `_close_issue_with_comment()` - Close issue with comment

**Lines Added**: ~185 lines

### 2. `gpwk/lib/python/gpwk_core/models.py`

**Updated Model:**
- `TriageResult` - Added `closed_issues` and `failed_issues` fields

**Lines Changed**: 2 lines

### 3. `gpwk/bin/gpwk-triage`

**Added Features:**
- Argument parsing for `--close` flag
- Support for ranges (49-54)
- Support for comma-separated lists (49,50,51)
- Support for space-separated lists (49 50 51)
- Display formatting for closure results

**Lines Added**: ~60 lines

---

## Features

### 1. Smart Closure Comments

The system automatically generates appropriate comments based on issue type:

**Test Issues** (contains "test", "testing", "final test", "success"):
```
Test completed. Telemetry test completed successfully.
Closing test capture.

🤖 Closed via GPWK Python triage with telemetry
```

**Capture Issues** (has `pwk:capture` label):
```
Test completed. Activity/capture completed.
Closing issue.

🤖 Closed via GPWK Python triage with telemetry
```

**Regular Tasks**:
```
Test completed.

🤖 Closed via GPWK Python triage with telemetry
```

### 2. Full Telemetry

Every bulk close operation emits:

**Traces**:
```
trace: review_and_close
  ├─ get_issue_details (for each issue)
  ├─ build_closure_comment
  └─ close_issue_with_comment
```

**Metrics**:
- `gpwk.triage.items_moved.total{from="open", to="closed"}`
- `gpwk.triage.duration{status="success"}`

**Logs** (structured):
```json
{
  "event": "review_and_close_started",
  "issue_count": 6,
  "reason": "Test completed",
  "trace_id": "..."
}
```

**Span Attributes**:
- `review.issue_count` - Number of issues to close
- `review.reason` - Closure reason
- `review.closed_count` - Successfully closed
- `review.failed_count` - Failed to close

### 3. Error Handling

- Continues processing if individual issues fail
- Reports failed issues separately
- Full error context in telemetry
- Graceful degradation

---

## Usage Examples

### Example 1: Close Test Issues from Telemetry Setup

```bash
# Close issues #49-54 (telemetry test captures)
gpwk/bin/gpwk-triage --close 49-54
```

**Output**:
```
✓ Issue Review & Closure Complete

Closed 6 issues:
────────────────────────────────────────────────────────────
  ✓ #49 - SUCCESS - Full telemetry stack working end-to-end!
  ✓ #50 - Testing TLS configuration for Grafana Cloud OTLP export
  ✓ #51 - FINAL TEST - OTLP over HTTP to Grafana Cloud!
  ✓ #52 - Testing CUMULATIVE temporality - correct imports!
  ✓ #53 - Testing OTLP log export to Grafana Cloud Loki!
  ✓ #54 - FINAL TEST - Logs should reach Loki now!
────────────────────────────────────────────────────────────

Duration: 3542ms
Trace ID in telemetry for observability

All closures include comments and full telemetry 🎯
```

### Example 2: Close Specific Issues

```bash
# Close only specific test issues
gpwk/bin/gpwk-triage --close 49,52,54
```

### Example 3: With Error Handling

If issue #50 doesn't exist:

```
✓ Issue Review & Closure Complete

Closed 5 issues:
────────────────────────────────────────────────────────────
  ✓ #49 - SUCCESS - Full telemetry stack working end-to-end!
  ✓ #51 - FINAL TEST - OTLP over HTTP to Grafana Cloud!
  ✓ #52 - Testing CUMULATIVE temporality - correct imports!
  ✓ #53 - Testing OTLP log export to Grafana Cloud Loki!
  ✓ #54 - FINAL TEST - Logs should reach Loki now!
────────────────────────────────────────────────────────────

⚠️  Failed to close 1 issue:
  ✗ #50 - Not found

Duration: 3123ms
```

---

## Integration with Existing Commands

### Still Supported (Unchanged)

```bash
# Show inbox
gpwk/bin/gpwk-triage

# Move specific issue
gpwk/bin/gpwk-triage #123 today

# Auto-triage
gpwk/bin/gpwk-triage --auto
```

### New Addition

```bash
# Bulk close with review
gpwk/bin/gpwk-triage --close 49-54
```

---

## Telemetry in Grafana

After running bulk close, you can view in Grafana:

**Tempo (Traces)**:
Search for: `review_and_close`
- See all 6 issues processed
- View individual get/close operations
- Identify any failures

**Prometheus (Metrics)**:
```promql
# Count of issues closed
gpwk_triage_items_moved_total{to="closed"}

# Duration of bulk close operations
histogram_quantile(0.95, gpwk_triage_duration_bucket)
```

**Loki (Logs)**:
```logql
{service_name="gpwk"} |= "review_and_close"
```

---

## Benefits

1. **Consistency**: All closures use Python backend (no more bash bypassing)
2. **Observability**: Full telemetry for every closure
3. **Efficiency**: Close multiple issues in one command
4. **Intelligence**: Smart comments based on issue type
5. **Reliability**: Error handling and retry logic
6. **Auditability**: Complete trace of all closures

---

## Migration Path

**Old Way** (bash bypass):
```bash
gh issue close 49 --comment "..."
gh issue close 50 --comment "..."
# ... no telemetry, no structured data
```

**New Way** (Python with telemetry):
```bash
gpwk/bin/gpwk-triage --close 49-54
# ✅ Full telemetry
# ✅ Smart comments
# ✅ Bulk operation
# ✅ Error handling
```

---

## Testing

To test the enhancement, you can:

1. Create test captures:
   ```bash
   /gpwk.capture "Test issue 1"
   /gpwk.capture "Test issue 2"
   /gpwk.capture "Test issue 3"
   ```

2. Note the issue numbers (e.g., #60, #61, #62)

3. Close them with telemetry:
   ```bash
   gpwk/bin/gpwk-triage --close 60-62
   ```

4. Verify in Grafana:
   - Traces in Tempo
   - Metrics in Prometheus
   - Logs in Loki

---

**Enhancement Complete!** ✅

All `/gpwk.triage` operations now use Python backend with full telemetry, including the new bulk close functionality.
