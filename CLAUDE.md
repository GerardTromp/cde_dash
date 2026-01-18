# Clust_app 

## Primary principles  
- Code must be separate from data  
  - only demonstration data or test data should exist in the code base  
  - user data shall not comingle with the code
  - utilities shall respect separation of data from code 
  - if there are base (default) configurations
    - they shall be read-only  
    - user-space configuration shall override base configurations
    - order of action for config files
      - read base
      - read user (if multiple in defined order -- see Nextflow model)
        - replace any value that occurs in subsequent configuration files
        - last file read trumps any prior config
        - cli or application config parameter value trumps all prior
- design should assume and accommodate intent to containerize

## Python environment

## Session Initialization Guidelines 
When starting a new session or executing commands, assume:

1. **Environment Activation Required**: Most non-standard Linux commands and all Python packages require venv activation
   - Always: `source /home/<user>/venv/<placeholder>/bin/activate`
   - Dependencies requiring venv: <placenholder>
   - **IMPORTANT**: After `/compact` or any session reset, venv must be reactivated

2. **Use Code Path Variable**: Reference scripts via `${DASH_CLUST}` for portability
   - Enables running from any directory
   - Example: `python ${DASH_CLUST}/utils/dash_app.py ...`
   - Usually set in `init_session.sh`


## Post-Compact Recovery (IMPORTANT)

When the user says any of these phrases (or semantic equivalents):
- "back from compacting"
- "just compacted"
- "context was reset"
- "environment lost"
- "session restarted"

**Immediately run:**
```bash
source .claude/init_session.sh
```

This restores the Python environment that is lost during `/compact`. Without this, Python commands will fail.

**After Session Compaction**: Run the initialization script to set up the environment:
```bash
source .claude/init_session.sh
```

This script (not tracked by git) performs all initialization steps:
1. Activates Python virtual environment
2. Loads any spack modules (<none currently>)
3. Verifies all required tools and variables are available

**VS Code Remote Development**: When using VS Code with remote SSH connection:
- Ensure terminal is connected to remote server (not local host)
- Look for indicator showing remote connection in terminal
- If commands fail, verify you're on the server: `hostname` should show server name


**See** `.claude/context/04-patterns.md` → "Session Setup Patterns" for detailed examples and troubleshooting.

## Large Task Execution Protocol

For extensive multi-phase work that may exceed chat attention limits:

### Phased Execution Rules
1. **Pause after each phase** - Do not auto-continue to the next phase
2. **Create per-phase TODOs** - If a phase has many steps, break it into a sub-TODO list
3. **Provide continuation prompt** - After completing a phase, provide the exact prompt to continue seamlessly after `/compact`

### Continuation Prompt Format
After completing a phase, provide a prompt block like:
```
--- CONTINUATION PROMPT ---
Back from compacting. Continue with [Phase X: Description].
Read `.claude/context/[relevant-plan].md` for context.
Last completed: [specific task]
Next step: [specific next action]
--- END PROMPT ---
```

### Why Manual Compacting
- Auto-compact works but loses nuanced context
- Manual compacting at phase boundaries preserves work quality
- Explicit continuation prompts ensure seamless resumption

### Phase Checkpoint Requirements
At each phase completion:
1. Update the plan file with completion status
2. Update the most recent checkpoint file
3. Commit if there are stable, working changes
4. Provide the continuation prompt

## Current status




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