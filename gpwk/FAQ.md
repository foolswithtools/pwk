# GPWK Frequently Asked Questions

## Table of Contents

- [System Architecture](#system-architecture)
- [GitHub Integration](#github-integration)
- [Daily Workflow](#daily-workflow)
- [AI Delegation](#ai-delegation)
- [Comparison with PWK](#comparison-with-pwk)

---

## System Architecture

### What is the effective book of record - Daily Log files or GitHub Issues?

**Both, with different roles:**

GPWK uses a **dual book of record** system where GitHub and local logs serve complementary purposes:

#### GitHub Issues = Primary/Canonical Record

**What it tracks:**
- Tasks, work items, and AI-delegatable work
- Formal status (Open/Closed)
- Labels (type, priority, energy, carryover)
- Project board position (Inbox/Todo/In Progress/Done)
- Comments and completion timestamps

**Why it's primary:**
- Persistent and version-controlled
- Structured and queryable
- Accessible from anywhere
- Survives across devices
- Can generate reports and metrics

#### Local Logs = Activity Stream & Reflection

**What it tracks:**
- Chronological activity timeline
- Informal captures and notes
- Time-based context (e.g., "cooking bacon for Mr. Noodles")
- End-of-day reflections
- Estimated vs actual durations
- Personal insights and learnings

**Why it's supplemental:**
- Rich narrative context
- Quick time-stamped journaling
- Human-readable daily view
- Private reflections
- Energy/mood tracking

#### How They Work Together

```
Activity Flow:
1. Capture → Creates GitHub issue (#5)
2. Log → References issue in daily log with timestamp
3. Work → Updates both (issue status + activity notes)
4. Complete → Closes issue + logs completion time
5. Review → Metrics from GitHub + reflections in log
```

#### Role Comparison

| Aspect | GitHub Issues | Local Logs |
|--------|--------------|------------|
| **Tasks & Work Items** | ✓ Primary | Reference only |
| **Status Tracking** | ✓ Primary | Snapshot |
| **Activity Timeline** | Comments | ✓ Primary |
| **Reflections** | - | ✓ Primary |
| **Metrics Source** | ✓ Primary | Derived |
| **Search/Query** | ✓ Primary | Text search |

#### In Practice

- **For "What did I complete?"** → Check GitHub Issues (structured data)
- **For "How did my day go?"** → Read daily log (narrative + context)
- **For "What's next?"** → GitHub Project board (workflow state)
- **For "What was I thinking?"** → Daily log reflections
- **For reporting/analysis** → GitHub Issues (queryable, filterable)
- **For daily journaling** → Local logs (chronological, contextual)

#### Key Design Principle

**GitHub is the system of record** (authoritative data).
**Local logs are the system of insight** (context and meaning).

The daily log file should always reference GitHub issue numbers (like #2, #3, #5) to create a link back to the canonical record. This gives you both structure and narrative.

---

### Why use GitHub instead of just local files?

**Persistence and Accessibility:**
- Tasks survive device changes
- Access from phone, web, or any machine
- Never lose data if laptop fails
- Cloud-synced automatically

**Structure:**
- Native project management (Kanban boards)
- Built-in labels and custom fields
- Issue linking and cross-references
- Full search and filtering

**Integration:**
- Link tasks to PRs and commits
- Reference issues in code
- GitHub Actions for automation
- Mobile app for on-the-go capture

**Collaboration (optional):**
- Share specific tasks if needed
- Maintain mostly private workflow
- Can invite collaborators later

---

### What if I don't want my tasks on GitHub?

Then GPWK might not be the right fit. Consider:

- **Original PWK** - Fully local, markdown-based
- **Other local systems** - Obsidian, Notion, plain markdown

GPWK's core value is the hybrid approach. Using GitHub enables:
- Multi-device access
- Persistent history
- Structured querying
- Integration with code workflow

If privacy is the concern:
- All repos are **private by default**
- Only you can see your issues
- Local logs never leave your machine
- You control all data

---

### Can I use GPWK offline?

**Partially:**

**Offline Capabilities:**
- Read existing daily logs
- Write in local log files
- Plan work based on cached data

**Requires Connection:**
- `/gpwk.capture` (creates GitHub issues)
- `/gpwk.triage` (updates project)
- `/gpwk.delegate` (posts AI results)
- Syncing status changes

**Best Practice:**
- Work offline in daily log
- Reference issue numbers manually
- Run `/gpwk.capture` and `/gpwk.triage` when back online
- System syncs automatically

---

## GitHub Integration

### Do I need a GitHub account?

**Yes.** GPWK requires:
- A GitHub account (free tier works fine)
- GitHub CLI (`gh`) installed and authenticated
- Permissions to create private repos and projects

**Setup:**
```bash
# Install GitHub CLI
brew install gh  # macOS
# or download from https://cli.github.com/

# Authenticate
gh auth login
```

---

### Will my tasks be public?

**No.** All repositories created by `/gpwk.setup` are **private by default**.

Only you can see:
- Your issues
- Your project board
- Your labels and fields

You can optionally share specific issues with collaborators, but the default is completely private.

---

### What happens if I delete a GitHub issue?

**Permanent deletion from GitHub:**
- Issue removed from project board
- Comments and history lost
- Cannot be recovered

**Local logs preserve context:**
- Activity stream entries remain
- References to `#123` stay in daily logs
- Narrative context preserved

**Best Practice:**
- Don't delete - close instead
- Use labels like `status:cancelled` or `status:obsolete`
- Add a closing comment explaining why
- Preserve history for future reference

---

### Can I use an existing GitHub repo?

**Yes!** When running `/gpwk.setup`, you can:

```
/gpwk.setup my-existing-repo
```

GPWK will:
- Use the existing repo
- Create the project
- Add labels
- Configure fields

**Note:** GPWK works best with a dedicated repo to avoid clutter in code repositories.

---

## Daily Workflow

### How does carryover tracking work?

**Label-based, not manual copying:**

Unlike original PWK (which copies tasks to the next day's log), GPWK uses labels:

| Day | Status | Label | Action |
|-----|--------|-------|--------|
| 1 | Created | (none) | Normal |
| 2 | Still open | `pwk:c1` | Track |
| 3 | Still open | `pwk:c2` | Warning - check blockers |
| 4+ | Still open | `pwk:c3` | Consider breakdown |

**How it works:**
```
Evening routine:
/gpwk.review    → Close completed tasks
/gpwk.carryover → Auto-labels remaining open tasks

Next morning:
/gpwk.plan today → Shows carryover tasks in daily log
```

**Benefits:**
- No manual copying
- Automatic tracking
- Visual warning system
- Forces decision at c3 threshold

---

### When should I run each command?

**Recommended Daily Rhythm:**

```
Morning (9:00 AM):
  /gpwk.triage          → Process inbox, schedule today
  /gpwk.plan today      → Generate daily plan

Throughout Day:
  /gpwk.capture [task]  → Quick capture as needed
  /gpwk.breakdown       → Break down complex work
  /gpwk.delegate        → Execute AI tasks

Evening (5:30 PM):
  /gpwk.review          → Reflect, capture metrics
  /gpwk.carryover       → Label incomplete tasks
```

**Flexible:**
- Not all commands needed daily
- Use what serves your workflow
- Adjust timing to your schedule

---

### What's the difference between /gpwk.capture and /gpwk.plan?

**`/gpwk.capture`** - Create new tasks
- Converts activity/thought → GitHub issue
- Adds to Inbox for later triage
- Quick, no decisions required
- Use throughout the day

**`/gpwk.plan`** - Schedule existing tasks
- Pulls tasks from GitHub project
- Generates daily log with schedule
- Suggests time blocks
- Use once per day (morning)

**Flow:**
```
Capture → Triage → Plan → Work → Review
   ↓         ↓       ↓      ↓       ↓
  Issue   Inbox→   Daily  Execute  Close
          Today     Log
```

---

### Do I have to use all the commands?

**No.** GPWK is modular. Use what helps:

**Minimum viable workflow:**
- `/gpwk.capture` - Create tasks
- `/gpwk.plan` - See what's scheduled
- Close issues when done

**Full workflow:**
- All commands for maximum productivity
- Carryover tracking
- AI delegation
- Work breakdown
- Daily reflection

**Customize:**
- Edit `memory/principles.md` to adjust behavior
- Skip commands that don't fit your style
- Mix with other tools as needed

---

## AI Delegation

### When should I delegate a task to AI?

**Safe to delegate:**
- Research and information gathering
- Summarization and synthesis
- First drafts of documentation
- Boilerplate code generation
- Test case generation
- Data formatting and cleanup
- Bug reproduction steps

**Keep personal:**
- Decisions with significant impact
- Relationship-dependent communication
- Creative direction and vision
- Anything requiring institutional knowledge
- Final reviews and approvals
- Customer-facing communication
- Research requiring judgment calls

**Rule of thumb:**
If the task requires context only you have, or has meaningful consequences, keep it personal.

---

### How does AI delegation work?

**Flow:**

```
1. Capture with [AI] marker:
   /gpwk.capture research React 19 features [AI]
   → Creates issue with pwk:ai label

2. Execute AI task:
   /gpwk.delegate
   → Claude reads issue, researches, posts results as comment

3. Review results:
   → Issue gets status:ai-complete label
   → You review and decide what to do with results

4. Close when satisfied:
   → Close issue or create follow-up tasks
```

**Benefits:**
- Results posted to GitHub (persistent)
- Can re-run if needed
- Full history in issue comments
- Review before acting on results

---

### Can I trust AI delegation results?

**Always review before using.**

AI delegation is for:
- **Draft work** that you'll refine
- **Research** that you'll verify
- **Boilerplate** that you'll customize

**Not for:**
- Final decisions
- Production code without review
- Critical communications
- Anything you wouldn't double-check

**Best practice:**
- Start with 20-30% delegation
- Review all AI outputs
- Build trust gradually
- Know what AI is good/bad at

---

## Comparison with PWK

### How is GPWK different from original PWK?

| Feature | PWK (Original) | GPWK (This) |
|---------|----------------|-------------|
| **Task storage** | Local markdown files | GitHub Issues |
| **Project view** | None | GitHub Projects (Kanban) |
| **Multi-device** | No | Yes |
| **Collaboration** | No | Optional |
| **Daily logs** | Local only | Local (hybrid) |
| **Carryover** | Manual copy | Automatic labels |
| **AI delegation** | Local execution | Posts to GitHub |
| **Work items** | Folders | Parent + sub-issues |
| **Triage** | Part of planning | Separate step |
| **Offline** | Full | Partial |

---

### Can I migrate from PWK to GPWK?

**Yes, but manual process:**

1. **Set up GPWK:**
   ```
   /gpwk.setup
   ```

2. **Convert existing tasks:**
   - Read through recent PWK logs
   - Capture open tasks: `/gpwk.capture [task]`
   - Triage to appropriate columns

3. **Preserve history:**
   - Keep old PWK logs as archive
   - Don't delete - reference as needed
   - Link to historical context in new issues

4. **Gradual transition:**
   - Run both systems for a week
   - Phase out PWK as you trust GPWK
   - Keep PWK logs for historical reference

---

### Should I use PWK or GPWK?

**Use GPWK if:**
- You want multi-device access
- You work with GitHub regularly
- You want structured task management
- You're comfortable with cloud storage

**Use PWK if:**
- You need fully offline workflow
- You prefer 100% local control
- You don't want GitHub dependency
- You like pure markdown simplicity

**Both are valid.** Choose based on your needs and preferences.

---

## Troubleshooting

### GitHub CLI not authenticated

**Error:** `gh: authentication required`

**Fix:**
```bash
gh auth login
# Follow prompts to authenticate with GitHub
```

---

### Project field IDs not found

**Error:** `field ID invalid` when running commands

**Fix:**
```bash
# Re-run setup to refresh field IDs
/gpwk.setup

# Or manually check:
gh project field-list 1 --owner @me
```

---

### Daily log file not updating

**Possible causes:**
- File permissions issue
- Directory doesn't exist
- Gitignored by mistake

**Fix:**
```bash
# Ensure directory exists
mkdir -p gpwk/logs

# Check .gitignore
cat .gitignore | grep logs

# Should see: gpwk/logs/
# (logs are intentionally gitignored)
```

---

### Issue not appearing in project

**Possible causes:**
- Issue created but not added to project
- Project filter hiding it
- Status field not set

**Fix:**
```bash
# Manually add issue to project
gh project item-add 1 --owner @me --url <issue-url>

# Or re-capture the task
/gpwk.capture [task]
```

---

## Getting Help

### Where can I get support?

- **Documentation:** `gpwk/README.md` and `gpwk/gpwk-context.md`
- **This FAQ:** `gpwk/FAQ.md`
- **Command help:** Read `.claude/commands/gpwk.*.md` files
- **Issues:** File issues in the GPWK repository (if public version exists)

### How do I customize GPWK?

**Edit your principles:**
```
/gpwk.principles --edit
```

Customize:
- Daily task limits
- Deep work preferences
- Carryover thresholds
- Delegation criteria
- Energy matching rules

**Edit command templates:**
- Modify `.claude/commands/gpwk.*.md` files
- Adjust workflow to your needs
- Change default behaviors

---

## Advanced Topics

### Can I use GPWK with a team?

**Partially supported:**

**What works:**
- Share specific issues with collaborators
- Collaborative project boards
- Team can comment on issues
- Link tasks to shared code repos

**What's personal:**
- Local daily logs (never shared)
- Personal principles and goals
- Private reflections
- Individual carryover tracking

**Best for:**
- Personal productivity (primary use case)
- Individual contributors
- Solo developers

**Not ideal for:**
- Full team task management
- Complex project planning
- Multi-person dependencies

---

### Can I integrate with calendar apps?

**Manual integration currently:**

GPWK doesn't auto-sync with Google Calendar, etc., but you can:

1. **Reference calendar in planning:**
   - `/gpwk.plan today` suggests time blocks
   - Manually check calendar
   - Adjust plan based on meetings

2. **Use Due dates:**
   - Set Due field on GitHub issues
   - View upcoming deadlines
   - Sort by due date

3. **Future possibility:**
   - GitHub Actions could create calendar events
   - API integration with calendar apps
   - Would require custom setup

---

### How do I backup my GPWK data?

**GitHub handles most backups automatically:**

- Issues backed up by GitHub
- Project boards synced
- Full history preserved

**Local logs need manual backup:**

```bash
# Backup local logs
cp -r gpwk/logs ~/Dropbox/gpwk-backup/

# Or use git (if you want to version control reflections)
# Remove gpwk/logs from .gitignore
git add gpwk/logs
git commit -m "Backup daily logs"
```

**Recommendation:**
- Let GitHub handle issue backups
- Periodically backup local logs separately
- Consider version controlling logs if comfortable

---

*Last updated: 2025-12-13*
