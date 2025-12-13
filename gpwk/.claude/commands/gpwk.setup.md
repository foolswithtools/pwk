# GPWK Setup

One-time setup to configure GitHub integration for Personal Work Kit.

## Arguments
- `$ARGUMENTS` - Optional: repository name (default: `personal-work`)

## Instructions

You are setting up GitHub-integrated Personal Work Kit (GPWK). This creates the necessary GitHub infrastructure.

### Step 1: Determine Repository

Parse `$ARGUMENTS` for repository name. Default to `personal-work` if not provided.

```bash
# Check if repo exists
gh repo view <repo-name> --json name 2>/dev/null
```

If repo doesn't exist, ask user if they want to create it:
- If yes: `gh repo create <repo-name> --private --description "Personal Work Kit - Activity-driven productivity system"`
- If no: Ask for alternative repo name

### Step 2: Create Labels

Create these labels in the repository (skip if they exist):

```bash
# Task type labels
gh label create "pwk:task" --color "0366d6" --description "Standard task" --force
gh label create "pwk:ai" --color "7057ff" --description "AI-delegatable task" --force
gh label create "pwk:personal" --color "d73a4a" --description "Personal task (human only)" --force
gh label create "pwk:work-item" --color "0e8a16" --description "Multi-day work item" --force
gh label create "pwk:capture" --color "fbca04" --description "Quick capture, needs triage" --force

# Priority labels
gh label create "priority:high" --color "b60205" --description "High priority" --force
gh label create "priority:medium" --color "d93f0b" --description "Medium priority" --force
gh label create "priority:low" --color "fef2c0" --description "Low priority" --force

# Energy labels
gh label create "energy:deep" --color "1d76db" --description "Requires deep focus" --force
gh label create "energy:shallow" --color "c2e0c6" --description "Shallow work, low cognitive load" --force
gh label create "energy:quick" --color "bfdadc" --description "Quick win, under 15 minutes" --force

# Carryover tracking labels
gh label create "pwk:c1" --color "ffefc6" --description "Carried over 1 day" --force
gh label create "pwk:c2" --color "ffdfb6" --description "Carried over 2 days" --force
gh label create "pwk:c3" --color "ffcfa6" --description "Carried over 3+ days - needs breakdown" --force

# Status labels (for non-project tracking)
gh label create "status:blocked" --color "d93f0b" --description "Blocked by dependency" --force
gh label create "status:waiting" --color "fef2c0" --description "Waiting on external" --force
```

### Step 3: Create GitHub Project

Create a project for task management:

```bash
# Create the project
gh project create --owner @me --title "Personal Work Kit" --format json
```

Capture the project number from the output.

### Step 4: Add Project Fields

Add custom fields to the project. Note: `gh project field-create` requires the project number.

```bash
PROJECT_NUM=<number from step 3>

# Status field (single select) - this is usually created by default
# If not, create it with options: Inbox, Today, This Week, Backlog, Done

# Type field
gh project field-create $PROJECT_NUM --owner @me --name "Type" --data-type "SINGLE_SELECT" --single-select-options "task,ai-task,work-item,capture"

# Priority field
gh project field-create $PROJECT_NUM --owner @me --name "Priority" --data-type "SINGLE_SELECT" --single-select-options "high,medium,low"

# Energy field
gh project field-create $PROJECT_NUM --owner @me --name "Energy" --data-type "SINGLE_SELECT" --single-select-options "deep,shallow,quick"

# Due Date field
gh project field-create $PROJECT_NUM --owner @me --name "Due" --data-type "DATE"
```

### Step 5: Get Field IDs

Query the project to get field IDs for later use:

```bash
gh project field-list $PROJECT_NUM --owner @me --format json
```

### Step 6: Save Configuration

Save the configuration to `memory/github-config.md`:

```markdown
# GitHub Configuration

## Repository
- **Name**: <repo-name>
- **Owner**: <owner>
- **URL**: https://github.com/<owner>/<repo-name>

## Project
- **Number**: <project-number>
- **URL**: https://github.com/users/<owner>/projects/<project-number>

## Field IDs
- **Status**: <field-id>
- **Type**: <field-id>
- **Priority**: <field-id>
- **Energy**: <field-id>
- **Due**: <field-id>

## Labels
All labels created with `pwk:*`, `priority:*`, `energy:*`, `status:*` prefixes.

## Setup Date
<current-date>
```

### Step 7: Create .gitkeep files

```bash
touch logs/.gitkeep
```

### Step 8: Confirm Setup

Display a summary:

```
✓ GPWK Setup Complete

Repository: <repo-name>
Project: Personal Work Kit (#<number>)
Labels: 15 created
Fields: 4 custom fields added

Next steps:
1. Run /gpwk.principles to set your work preferences
2. Run /gpwk.capture to start logging activities
3. Run /gpwk.plan today to create your first daily plan
```

## Error Handling

- If `gh` is not installed: Prompt user to install GitHub CLI
- If not authenticated: Run `gh auth login`
- If repo creation fails: Check permissions and suggest alternatives
- If project creation fails: Check if user has Projects enabled

## Notes

- All commands use `--force` for labels to make setup idempotent
- Project field IDs are required for gpwk.triage and other commands
- Configuration is stored locally in memory/github-config.md
