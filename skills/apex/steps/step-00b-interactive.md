---
name: step-00b-interactive
description: Interactively configure APEX workflow flags
returns_to: step-00-init.md
---

# Step 0b: Interactive Configuration

## MANDATORY EXECUTION RULES (READ FIRST):

- 🛑 NEVER skip the interactive menu
- 🛑 NEVER assume user preferences
- ✅ ALWAYS use AskUserQuestion for flag selection
- ✅ ALWAYS update all flag variables before returning
- 📋 YOU ARE A CONFIGURATOR, not an implementer
- 💬 FOCUS on flag configuration only
- 🚫 FORBIDDEN to start any workflow steps

## CONTEXT BOUNDARIES:

- Variables available: All current flag values from step-00-init
- This sub-step updates: All flag variables based on user selection
- Return to step-00-init.md after completion

## YOUR TASK:

Present an interactive menu for the user to enable/disable workflow flags.

---

## EXECUTION SEQUENCE:

### 1. Display Current Configuration

Show current flag values:
```
**Current APEX Configuration:**

| Flag | Status | Description |
|------|--------|-------------|
| Auto (`-a`) | {auto_mode ? "✓ ON" : "✗ OFF"} | Skip confirmations |
| Save (`-s`) | {save_mode ? "✓ ON" : "✗ OFF"} | Save outputs to files |
| Economy (`-e`) | {economy_mode ? "✓ ON" : "✗ OFF"} | No subagents, save tokens |
| Branch (`-b`) | {branch_mode ? "✓ ON" : "✗ OFF"} | Verify/create branch |
```

### 2. Ask for Flag Changes

Use AskUserQuestion with multiSelect:
```yaml
questions:
  - header: "Configure"
    question: "Select flags to TOGGLE (current state will flip):"
    options:
      - label: "Auto mode"
        description: "{auto_mode ? 'Disable' : 'Enable'} - skip confirmations"
      - label: "Save mode"
        description: "{save_mode ? 'Disable' : 'Enable'} - save outputs to .claude/output/"
      - label: "Economy mode"
        description: "{economy_mode ? 'Disable' : 'Enable'} - no subagents, save tokens"
      - label: "Branch mode"
        description: "{branch_mode ? 'Disable' : 'Enable'} - verify/create git branch"
      - label: "Done — keep current"
        description: "No more changes, proceed with workflow"
    multiSelect: true
```

### 3. Apply Changes

For each selected flag, toggle its value:
```
IF "Auto mode" selected → {auto_mode} = !{auto_mode}
IF "Save mode" selected → {save_mode} = !{save_mode}
IF "Economy mode" selected → {economy_mode} = !{economy_mode}
IF "Branch mode" selected → {branch_mode} = !{branch_mode}
```

### 4. Show Final Configuration

Display updated configuration:
```
**Updated APEX Configuration:**

| Flag | Status |
|------|--------|
| Auto | {auto_mode ? "✓ ON" : "✗ OFF"} |
| Save | {save_mode ? "✓ ON" : "✗ OFF"} |
| Economy | {economy_mode ? "✓ ON" : "✗ OFF"} |
| Branch | {branch_mode ? "✓ ON" : "✗ OFF"} |
```

### 5. Return

→ Return to step-00-init.md with all flags updated

---

## SUCCESS METRICS:

✅ Current configuration displayed
✅ User able to toggle any flag
✅ All selected flags properly toggled
✅ Final configuration shown

## FAILURE MODES:

❌ Not showing current flag states
❌ Forgetting to toggle selected flags
❌ Starting workflow instead of returning
❌ **CRITICAL**: Using plain text prompts instead of AskUserQuestion

---

## RETURN:

After configuration complete, return to `./step-00-init.md` to continue initialization.

<critical>
Remember: This sub-step ONLY handles flag configuration. Return immediately after updating flags.
</critical>
