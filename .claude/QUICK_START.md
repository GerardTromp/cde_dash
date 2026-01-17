# Checkpoint System Quick Start Guide

Get your checkpoint system up and running in 15 minutes.

---

## Prerequisites

- Claude Code installed and working
- Git repository initialized
- Claude Pro/Max subscription (for Claude Code)

---

## Step 1: Setup (5 minutes)

### 1.1 Create Directory Structure

In Claude Code, run:

```
Create the checkpoint system directory structure:

1. Create directories:
   - .claude/checkpoints/
   - .claude/context/
   - .claude/sessions/
   - .claude/memory-bank/

2. Create .gitignore additions:
   Add these lines to .gitignore:
   .claude/sessions/
   .claude/checkpoints/

3. Commit the structure:
   git add .claude/
   git commit -m "Add checkpoint system structure"

Confirm when complete.
```

### 1.2 Copy System Documentation

Copy these files to your project:

- `CHECKPOINT_SYSTEM.md` → `.claude/CHECKPOINT_SYSTEM.md`
- `CHECKPOINT_PROMPTS.md` → `.claude/CHECKPOINT_PROMPTS.md`
- `QUICK_START.md` (this file) → `.claude/QUICK_START.md`

```bash
# In Claude Code:
git add .claude/*.md
git commit -m "Add checkpoint system documentation"
```

---

## Step 2: Initial Setup (10 minutes)

### 2.1 Initialize Context Files

In Claude Code, paste this prompt:

```
Initialize the checkpoint system context files by analyzing the current codebase:

For each file, analyze the codebase and create initial content:

1. .claude/context/01-architecture.md
   - Identify the architectural style
   - Map out major components
   - Document the technology stack
   - Describe component communication
   - Identify data flow patterns

2. .claude/context/02-codebase-map.md
   - Generate directory tree with annotations
   - Identify entry points
   - Map module dependencies
   - List hot files based on git log
   - List stable files

3. .claude/context/03-data-models.md
   - Document database schemas if applicable
   - Document key data structures
   - Identify data validation patterns

4. .claude/context/04-patterns.md
   - Identify design patterns in use
   - Document coding conventions
   - Document testing patterns

5. .claude/context/05-decisions.md
   - Review git log for decision context
   - Review README/docs for decisions
   - Create initial ADRs for major architectural choices

6. .claude/context/06-dependencies.md
   - List external dependencies from package manifests
   - Document their purposes
   - Identify internal module dependencies
   - Document third-party integrations

7. .claude/context/07-gotchas.md
   - Review TODO comments for warnings
   - Check for workarounds in code
   - Leave template for future issues

8. .claude/context/08-progress.md
   - Review git log for recent work
   - Check for open branches
   - Document current state

Use git log extensively:
- git log --oneline --since="30 days ago"
- git log --stat --since="30 days ago"
- git shortlog -sn --since="90 days ago"

Read any existing documentation:
- README.md, docs/, CONTRIBUTING.md, any CLAUDE.md files

After creating each file, show me a brief summary.
```

Wait for completion. Review the summaries to ensure accuracy.

### 2.2 Create Initial Checkpoint

```
Create the initial full checkpoint:

1. Read all files in .claude/context/
2. Run git log analysis:
   - Last 10 commits: git log --oneline -10
   - Branch structure: git branch -a
   - Uncommitted changes: git status
   - Recent activity: git log --stat --since="7 days ago"

3. If SESSION_NOTES*.md files exist, read and summarize them

4. Create .claude/checkpoints/checkpoint-[YYYYMMDD-HHMM].md using the template from CHECKPOINT_SYSTEM.md

Focus on:
- Executive summary capturing project essence
- Current implementation state
- Known issues and gotchas
- Clear recovery instructions

Show me the Executive Summary and Current State Assessment sections.
```

### 2.3 Update CLAUDE.md

Add to your root `CLAUDE.md`:

```markdown
## Checkpoint System

This project uses a structured checkpoint system for context preservation.

### Quick Commands
- **Create checkpoint**: See `.claude/CHECKPOINT_PROMPTS.md` → "Incremental Checkpoint: End of Session"
- **Recover context**: See `.claude/CHECKPOINT_PROMPTS.md` → "Recovery: Full Context Restoration"
- **Update progress**: See `.claude/CHECKPOINT_PROMPTS.md` → "Update: 08-progress.md"

### Context Files Location
All context in `.claude/context/`:
- 01-architecture.md - System architecture
- 02-codebase-map.md - Code organization
- 03-data-models.md - Data structures
- 04-patterns.md - Design patterns
- 05-decisions.md - Architecture decisions (ADRs)
- 06-dependencies.md - Dependencies
- 07-gotchas.md - Known issues
- 08-progress.md - Current work status

### Checkpoints Location
- `.claude/checkpoints/` - Full and incremental snapshots
- `.claude/sessions/` - Session notes
- `.claude/memory-bank/` - Lessons learned

### Recovery After Interruption
1. Read most recent `.claude/checkpoints/checkpoint-*.md`
2. Read incremental checkpoints since then
3. Check `.claude/context/08-progress.md`
4. Check `git status`

See `.claude/CHECKPOINT_SYSTEM.md` for complete documentation.
```

Commit everything:

```bash
git add .claude/
git commit -m "Initialize checkpoint system with context files"
```

---

## Step 3: Daily Usage

### Start of Coding Session

If resuming after interruption:

```
Restore project context:

1. Read most recent full checkpoint: .claude/checkpoints/checkpoint-*.md
2. Read incremental checkpoints since then
3. Read .claude/context/08-progress.md
4. Check: git status

Present:
- What we were working on
- Current state
- Suggested next steps
```

If continuing same day:

```
Quick briefing:

1. Read most recent incremental checkpoint
2. Check .claude/context/08-progress.md
3. Run: git status

Show current in-progress items and suggest next step.
```

### End of Coding Session

For normal sessions:

```
Create incremental checkpoint:

1. Analyze git changes this session:
   git diff --stat HEAD~[n]..HEAD
   git log --oneline HEAD~[n]..HEAD
   git status --short

2. Capture:
   - Session summary
   - Files modified with change descriptions
   - Decisions made with rationale
   - Problems and solutions
   - Context for next session

3. Create: .claude/checkpoints/incremental-[YYYYMMDD-HHMM].md

4. Update: .claude/context/08-progress.md

Show me session summary and next steps.
```

For quick sessions (<30 min):

```
Quick checkpoint:

git diff --stat
Brief summary: [what was accomplished]
Next: [what's next]

Create: .claude/checkpoints/incremental-[YYYYMMDD-HHMM].md
Update: .claude/context/08-progress.md if needed
```

### End of Week

```
Create comprehensive full checkpoint:

Follow "Full Checkpoint: Comprehensive State Capture" from CHECKPOINT_PROMPTS.md

Synthesize:
- All context files
- Git history (last 30 commits)
- All session notes
- All incremental checkpoints

Create: .claude/checkpoints/checkpoint-[YYYYMMDD-HHMM].md

Show Executive Summary and Next Steps.
```

---

## Step 4: Maintenance (Monthly)

### Context File Audit

```
Audit context files:

For each .claude/context/*.md file:
1. Read current content
2. Verify against actual codebase
3. Update outdated information
4. Remove obsolete information
5. Add missing information

Show audit report with files updated.
```

### Checkpoint Rotation

```
Archive old checkpoints:

1. List all checkpoints
2. Identify for archiving:
   - Incremental > 30 days old
   - Full > 90 days old (keep monthly)
3. Create: .claude/checkpoints/archive/YYYY/MM/
4. Move old checkpoints to archive

Show summary of archived checkpoints.
```

---

## Common Workflows

### Workflow: New Feature Development

**Day 1: Start feature**

```
# Morning
"Quick briefing" (if continuing work)

# Work on feature

# Evening
"Create incremental checkpoint" focusing on:
- Design decisions for this feature
- Implementation approach chosen
- Progress made
```

**Day 2-4: Continue feature**

```
# Morning
"Read most recent incremental checkpoint"

# Work continues

# Evening
"Create incremental checkpoint" tracking:
- Progress on feature
- Problems solved
- Tests added
```

**Day 5: Complete feature**

```
# Complete work

# Create final incremental checkpoint with:
- Feature completion summary
- Design decisions recap
- Lessons learned

# Update context files:
"Update 04-patterns.md" - Add any new patterns used
"Update 05-decisions.md" - Add ADR for significant decisions
"Update 08-progress.md" - Move feature to completed
```

**Weekend: Create full checkpoint**

```
"Create comprehensive full checkpoint"
```

### Workflow: Bug Investigation

**Start investigation**

```
"Quick briefing"

# During investigation, take notes mentally

# When bug found:
"Add new gotcha to 07-gotchas.md" with:
- Bug symptoms
- Root cause
- Fix applied
- How to prevent
```

**End investigation**

```
"Create incremental checkpoint" including:
- Bug details
- Investigation path
- Solution
- Lessons learned

"Update memory-bank/lessons-learned.md" with:
- Debugging techniques that worked
- What to watch for in future
```

### Workflow: Major Refactoring

**Before refactoring**

```
"Create full checkpoint" - Safety net

"Update 05-decisions.md" with ADR:
- Why refactoring is needed
- Approach chosen
- Expected benefits
- Risks
```

**During refactoring**

```
Daily:
"Create incremental checkpoint" tracking:
- Files refactored
- Pattern changes
- Tests updated
- Remaining work
```

**After refactoring**

```
"Update 01-architecture.md" - Reflect new structure
"Update 04-patterns.md" - Document new patterns
"Create full checkpoint" - New baseline
"Update memory-bank/lessons-learned.md" - Refactoring insights
```

---

## Troubleshooting

### "Checkpoint creation is slow"

**Solution**: Use incremental checkpoints for daily work, full checkpoints weekly.

### "Context files are getting too large"

**Solution**: 

1. Split into subdirectories: `.claude/context/subsystem/`
2. Use `@import` in CLAUDE.md to load selectively
3. Archive old sections

### "Too many incremental checkpoints"

**Solution**:

1. Run maintenance rotation monthly
2. Archive to `.claude/checkpoints/archive/`
3. Keep only last 30 days active

### "Can't remember checkpoint syntax"

**Solution**:

1. Keep `CHECKPOINT_PROMPTS.md` open as reference
2. Create aliases in CLAUDE.md:
   
   ```markdown
   ## Quick Commands
   - End session: "Create incremental checkpoint (see CHECKPOINT_PROMPTS.md)"
   - Recover context: "Full context restoration (see CHECKPOINT_PROMPTS.md)"
   ```
3. Create slash commands in `.claude/commands/`:
   - `checkpoint.md` - Incremental checkpoint
   - `recover.md` - Context recovery

---

## Customization

### For Your Tech Stack

Update file patterns in prompts:

**Python project**: Use `*.py` for file tracking
**JavaScript project**: Use `*.js`, `*.jsx`, `*.ts`, `*.tsx`
**Go project**: Use `*.go`
**Multi-language**: List all extensions

### For Your Team Size

**Solo developer**: 

- Skip contributor analysis
- Focus on time-based patterns

**Small team (2-5)**:

- Add contributor sections
- Track collaboration patterns

**Larger team**:

- Add team-specific context files
- Track component ownership

### For Your Domain

Add domain-specific context files:

**Web app**: Add `09-api-routes.md`, `10-frontend-components.md`
**Data pipeline**: Add `09-data-sources.md`, `10-transformations.md`
**ML project**: Add `09-models.md`, `10-training-runs.md`

---

## Integration with Tools

### VS Code Integration

Create tasks in `.vscode/tasks.json`:

```json
{
  "label": "Create Checkpoint",
  "type": "shell",
  "command": "claude",
  "args": ["-f", ".claude/CHECKPOINT_PROMPTS.md#incremental"]
}
```

### Git Hooks

See "Advanced: Automated Checkpoint on Git Hooks" in CHECKPOINT_PROMPTS.md

### CI/CD Integration

Generate checkpoint as build artifact:

```yaml
# .github/workflows/checkpoint.yml
name: Weekly Checkpoint
on:
  schedule:
    - cron: '0 0 * * 0'  # Sunday midnight
jobs:
  checkpoint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Create checkpoint
        run: |
          # Use Claude API to generate checkpoint
          # Commit to repository
```

---

## Best Practices

### DO:

✅ Create incremental checkpoints after every significant session
✅ Create full checkpoints weekly
✅ Update progress.md daily
✅ Add gotchas as soon as discovered
✅ Document decisions when made
✅ Review checkpoints when resuming
✅ Maintain context files regularly

### DON'T:

❌ Skip checkpoints for small sessions (they add up)
❌ Let context files go stale
❌ Forget to commit context files to git
❌ Put sensitive data in checkpoints
❌ Create manual checkpoints (use prompts)
❌ Ignore checkpoint file size (archive old ones)

---

## Success Metrics

You'll know the checkpoint system is working when:

1. **Recovery time < 5 minutes**: After interruption, you're productive in 5 minutes
2. **No repeated explanations**: Claude doesn't need re-briefing on project
3. **Decision history clear**: Can trace why choices were made
4. **Onboarding easier**: New team members get up to speed faster
5. **Less context loss**: Long breaks don't reset understanding
6. **Better continuity**: Sessions build on each other

---

## Next Steps

1. ✅ Complete setup (Steps 1-2)
2. ✅ Use for 1 week (Step 3 daily workflows)
3. ✅ Review effectiveness
4. ✅ Customize for your needs
5. ✅ Share with team
6. ✅ Integrate with tools

---

## Getting Help

- Read full documentation: `.claude/CHECKPOINT_SYSTEM.md`
- Browse all prompts: `.claude/CHECKPOINT_PROMPTS.md`
- Check examples: `.claude/checkpoints/` (after first week)

---

## Advanced Topics

Once comfortable with basics, explore:

- Cross-project pattern mining
- Checkpoint-driven onboarding docs
- Automated checkpoint triggers
- Custom context files for your domain
- Integration with project management tools
- Checkpoint-based retrospectives

See "Advanced Prompts" section in CHECKPOINT_PROMPTS.md

---

*You're now ready to never lose context again!*

**Time invested**: 15 minutes setup  
**Time saved**: Hours per week in context rebuilding  
**ROI**: Immediate and compounding
