# GPWK Feedback

Feedback from a first-time user walkthrough on 2026-01-24.

---

## Setup

### 1. Auto-detect current repo
**Issue:** When running `/gpwk.setup` from inside an existing git repo, it defaults to creating a new `personal-work` repo instead of offering to use the current repo.

**Suggestion:** Detect if user is in a git repo and offer that as the default option. Reduces friction for users who already have a project in mind.

---

## Capture & Triage

### 2. Energy and priority should be optional
**Issue:** The current notation (`!high`, `~deep`) requires upfront judgment about priority and energy levels for every task.

**Suggestion:** Make these optional with smart defaults:
- Infer from keywords ("research" = shallow, "build" = deep)
- Let users skip and triage later
- Learn from patterns over time

### 3. [P] vs [AI] notation is unclear
**Issue:** New users don't know what `[P]` and `[AI]` mean without reading documentation.

**Suggestion:** Clearer onboarding explanation. Consider more intuitive markers or inline help during first captures.

### 4. Auto-suggest [P] vs [AI] based on keywords
**Issue:** Users have to manually decide if a task is personal or AI-delegatable.

**Suggestion:** Infer from task language:
- "fix", "build", "decide", "meet" → likely `[P]`
- "research", "summarize", "draft", "find" → likely `[AI]`

Offer as a suggestion, not a requirement.

### 5. Triage asks too many questions
**Issue:** Converting a single capture requires answering: type, priority, and energy level. That's three separate prompts.

**Suggestion:** Streamline into fewer prompts:
- Single prompt: "High priority, deep work? [Y/n]"
- Smart defaults with "press enter to accept"
- Batch similar decisions together

### 6. Energy level is hard to predict upfront
**Issue:** Users often don't know how much energy a task requires until they're doing it. A "quick fix" can become a rabbit hole.

**Suggestion:**
- Skip energy during capture/triage entirely
- Allow tagging *after* completion ("that was deeper than expected")
- Use energy only for scheduling suggestions, not as required metadata

---

## Delegation

### 7. Show assignment in GitHub Issues
**Issue:** When Claude completes an AI task, there's no indication in the GitHub Issue that it was handled by automation.

**Suggestion:** Assign the issue to "Personal Work Kit" or add a label/comment indicating automated execution. Makes the audit trail clearer in GitHub's UI.

### 8. Save delegation results locally
**Issue:** Delegation results are posted as GitHub Issue comments only. User expected a local document to review.

**Suggestion:** Also save results to a local file like `gpwk/outputs/2026-01-24-api-rate-limiting.md`. Benefits:
- Easier to review and reference
- Works offline
- Keeps a local copy independent of GitHub

---

## Breakdown

### 9. Don't tie breakdown suggestions to priority
**Issue:** The system suggested breakdown because a task was "high priority." But priority and complexity are different things.

**Rationale:** A high-priority task can be simple ("fix critical typo"). A low-priority task can be complex ("someday refactor auth").

**Suggestion:** Base breakdown suggestions on complexity signals:
- Keywords like "build", "system", "implement", "feature"
- Estimated scope, not urgency

### 10. Offer breakdown inline during capture
**Issue:** Current flow: capture a task, then separately run `/gpwk.breakdown`. User has to remember to do this.

**Suggestion:** When capturing a task that looks complex, immediately ask: "This looks like a multi-step effort. Want me to break it down now?"

Keep `/gpwk.breakdown` as a fallback for later decisions, but handle the common case inline.

---

## Learning & Memory

### 11. Build a user profile over time
**Issue:** Each interaction starts fresh. When breaking down "build auth system," it asked what type of auth from scratch.

**Suggestion:** Accumulate preferences in `gpwk/memory/`:
- Tech stack (e.g., "Node.js + JWT")
- Common patterns
- Past decisions

Future prompts should default to known preferences: "Assuming JWT + Node like before?" rather than open-ended questions.

---

## What Worked Well

### Clarifying questions during breakdown
The breakdown command asked "what type of authentication system?" before generating sub-tasks. This made the output specific and relevant rather than generic.

**Suggestion:** Apply this pattern to capture — if complexity is detected, ask a quick clarifying question, then offer inline breakdown.

### Delegation to GitHub Issues
The AI task executed and posted results directly to the GitHub Issue. This creates a clear record and integrates well with existing GitHub workflows.

### Capture-first, triage-later flow
Being able to quickly capture without categorizing, then triage later, reduces friction during busy moments.

---

## Summary

The core concept is solid: capture activities, triage into tasks, delegate what you can, break down what's complex. The GitHub integration works well.

Main themes for improvement:
1. **Reduce friction** — fewer required fields, smarter defaults, inline flows
2. **Learn over time** — build user profile, remember preferences
3. **Better signals** — use complexity not priority for breakdown, infer [P]/[AI] from language
4. **Local artifacts** — save delegation results locally, not just to GitHub
