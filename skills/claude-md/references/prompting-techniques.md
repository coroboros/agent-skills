<prompting_techniques>
Master guide for writing effective instructions in CLAUDE.md files. These techniques ensure Claude follows your guidance reliably.

<core_principle>
Show your CLAUDE.md to someone with minimal project context. If they're confused about what to do, Claude will be too.
</core_principle>

<contents>
- Emphasis strategies — keyword, visual, formatting, placement, repetition
- Clarity techniques — be specific, show don't tell, edge cases, ambiguity, sequential steps
- Instruction structure — obligation levels, decision criteria, success criteria
- Context provision — purpose, examples, file links
- Constraint techniques — hard, conditional, escape hatches
- Testing your instructions — clarity test, effectiveness test, common issues
</contents>

<emphasis_strategies>
Reserve emphasis for genuine constraints. Current models follow instructions literally — stacking CRITICAL/NEVER/ALWAYS on ordinary guidance dilutes the rules that matter and can cause overtriggering. Lead with clear, specific directives; add a single emphatic marker only where a rule is truly non-negotiable (secrets, data loss, breaking changes).

<keyword_emphasis>
**CRITICAL / NEVER** — reserve for genuine stakes where a breach is costly (secrets, data loss, breaking changes):
```markdown
**CRITICAL**: Never commit secrets or `.env` files
NEVER commit API keys or credentials
NEVER push directly to `main`
```

**ALWAYS / IMPORTANT / YOU MUST** — available for mandatory behaviors, but most "always do X" guidance lands better as a plain, specific directive than as a stacked keyword:
```markdown
❌ ALWAYS: Run linter before committing
✅ Run `pnpm lint` before committing
```

One keyword per rule, and only where the rule is genuinely non-negotiable — most guidance needs none. Pick the keyword that fits and stop there; stacking three on one line trains the model to discount all of them.
</keyword_emphasis>

<visual_markers>
Use symbols for visual emphasis (sparingly):

```markdown
⚠️ WARNING: This affects production data
🔒 SECURITY: Never commit secrets to git
❌ FORBIDDEN: Do not use interactive test commands
✅ REQUIRED: All PRs must pass CI checks
```

Reserve visual markers for the most critical items only.
</visual_markers>

<formatting_emphasis>
**Bold for critical terms:**
```markdown
Use **TanStack Form** for all forms (not React Hook Form)
```

**Strikethrough for forbidden options:**
```markdown
Commands:
- `pnpm test:ci` - Run tests
- ~~`pnpm test`~~ - NEVER use (interactive mode)
```

**Code blocks for exact commands:**
```markdown
Before pushing, run:
```bash
pnpm lint && pnpm test:ci && pnpm build
```
```
</formatting_emphasis>

<placement_strategy>
Order matters. Claude pays more attention to:

1. **First items** in each section
2. **Repeated items** across sections
3. **Emphasized items** — but sparingly; placement and specificity carry more weight than keywords on current models

Structure your CLAUDE.md with critical rules first:

```markdown
## Code Conventions

### Critical Rules (Follow These First)
- **Never commit `.env` files** — leaks secrets
- Run `pnpm test:ci` before pushing

### General Guidelines
- Use TanStack Form for all forms (not native form/useState)
- Prefer Server Components
- Keep components under 300 lines
- Use TypeScript strict mode
```
</placement_strategy>

<repetition_technique>
For a genuinely load-bearing rule, restate it where it actually applies (the Forms section AND the review checklist). Repeat the rule, not the emphasis — re-stacking CRITICAL in every mention trains the model to discount it:

```markdown
## Forms
Use TanStack Form for all forms — import from `@/features/form/tanstack-form`.

## Before Editing Files
- Read similar files for patterns
- Forms use TanStack Form (see Forms section)

## Code Review Checklist
- [ ] Tests passing
- [ ] Forms use TanStack Form
```
</repetition_technique>
</emphasis_strategies>

<clarity_techniques>
<be_specific>
Vague instructions cause inconsistent behavior. Be explicit:

```markdown
❌ VAGUE:
- Format code properly
- Write good tests
- Follow best practices

✅ SPECIFIC:
- Use 2-space indentation (Prettier configured)
- Write tests in `__tests__/` using Vitest
- Use TanStack Form for all forms
```
</be_specific>

<show_dont_tell>
When format matters, show examples rather than describing:

```markdown
❌ TELLING:
Use conventional commits with type, scope, and description.

✅ SHOWING:
## Commit Format
```
feat(auth): implement JWT authentication

Add login endpoint and token validation middleware
```

Types: feat, fix, refactor, docs, test, chore
```
</show_dont_tell>

<define_edge_cases>
Anticipate questions and answer them:

```markdown
❌ INCOMPLETE:
Run tests before pushing.

✅ COMPLETE:
## Testing
- Run `pnpm test:ci` before pushing
- If tests fail, fix before committing
- For new features, add tests in `__tests__/`
- Minimum 80% coverage for new code
```
</define_edge_cases>

<eliminate_ambiguity>
Replace ambiguous phrases with clear directives:

```markdown
❌ AMBIGUOUS PHRASES:
- "Try to..." → Implies optional
- "Should probably..." → Unclear obligation
- "Generally..." → When are exceptions allowed?
- "Consider..." → Do it or not?

✅ CLEAR PHRASES:
- "Always..." or "Never..." → Clear requirement
- "Must..." or "May optionally..." → Clear obligation
- "Always... except when [condition]" → Rule with exception
- "If [condition], then [action]" → Clear conditional
```
</eliminate_ambiguity>

<sequential_steps>
For multi-step processes, use numbered lists:

```markdown
## Before Pushing Code

1. Run linter: `pnpm lint`
2. Run type check: `pnpm ts`
3. Run tests: `pnpm test:ci`
4. Verify build: `pnpm build`
5. If all pass, commit and push
```

Sequential steps create clear expectations and prevent skipping.
</sequential_steps>
</clarity_techniques>

<instruction_structure>
<must_nice_mustnot>
Clearly separate obligation levels:

```markdown
## API Development

### Must Have
- Input validation with Zod
- Error handling for all endpoints
- TypeScript types for request/response

### Nice to Have
- Pagination for list endpoints
- Caching headers
- Rate limiting

### Must Not
- Expose internal errors to clients
- Log sensitive data
- Skip authentication checks
```
</must_nice_mustnot>

<decision_criteria>
When Claude must make choices, provide criteria:

```markdown
## Component Choice

**Use Server Component when:**
- Data fetching only
- No user interaction
- No browser APIs needed

**Use Client Component when:**
- User interaction required (forms, buttons)
- Browser APIs needed (localStorage, window)
- Real-time updates needed
```
</decision_criteria>

<success_criteria>
Define what success looks like:

```markdown
## Definition of Done

A feature is complete when:
- [ ] All tests pass
- [ ] Build succeeds
- [ ] Code reviewed and approved
- [ ] Documentation updated (if applicable)
- [ ] No TypeScript errors
```
</success_criteria>
</instruction_structure>

<context_provision>
<give_purpose>
Explain WHY, not just WHAT:

```markdown
❌ JUST WHAT:
Use TanStack Form for all forms.

✅ WHAT + WHY:
Use TanStack Form for all forms.
- Unified validation with Zod schemas
- Consistent error handling across app
- Server action integration built-in
```
</give_purpose>

<provide_examples>
Input/output examples teach patterns better than descriptions:

```markdown
## File Naming

### Server Actions
```
user.action.ts        ✅ Correct
userActions.ts        ❌ Wrong
actions/user.ts       ❌ Wrong
```

### API Routes
```
app/api/users/route.ts    ✅ Correct
app/api/users.ts          ❌ Wrong
```
```
</provide_examples>

<link_to_files>
Reference actual files for complex patterns:

```markdown
## Patterns

For implementation examples:
- **Forms**: See `src/features/form/tanstack-form.tsx`
- **Server Actions**: See `src/lib/actions/safe-actions.ts`
- **API Routes**: See `src/lib/zod-route.ts`
```
</link_to_files>
</context_provision>

<constraint_techniques>
<hard_constraints>
For absolute limits, use explicit language:

```markdown
## Hard Constraints

- Maximum component size: 300 lines
- Maximum function size: 50 lines
- Maximum file size: 500 lines
- Refactor before exceeding these limits — they keep modules reviewable
```
</hard_constraints>

<conditional_constraints>
For context-dependent rules:

```markdown
## Component Complexity

**Simple components (< 100 lines):**
- Keep in single file
- No need for separate test file if trivial

**Complex components (100-300 lines):**
- Extract hooks to separate files
- Require dedicated test file

**If approaching 300 lines:**
- Split into sub-components
- Extract logic to custom hooks
```
</conditional_constraints>

<escape_hatches>
Provide alternatives for edge cases:

```markdown
## Default Patterns

Use Server Components for data fetching.

**Exception**: Use Client Component with TanStack Query when:
- Real-time updates needed
- Optimistic updates required
- Complex client-side caching needed
```
</escape_hatches>
</constraint_techniques>

<testing_your_instructions>
<clarity_test>
Ask yourself:
1. Could a developer unfamiliar with this project follow these instructions?
2. Are there any ambiguous terms?
3. Is anything left to interpretation that shouldn't be?
4. Are the most critical rules placed first and stated specifically?
</clarity_test>

<effectiveness_test>
After using for a few sessions:
1. Did Claude follow the instructions?
2. Which instructions were ignored?
3. What did Claude do wrong?
4. What additional context would help?

Iterate based on observed behavior, not assumptions.
</effectiveness_test>

<common_issues>
| Problem | Solution |
|---------|----------|
| Claude ignores instruction | Check specificity and placement first; move it to the top of its section. Add one emphatic marker only if it's a genuine constraint — over-emphasis backfires on current models |
| Claude does wrong thing | Be more specific, add examples |
| Claude asks for clarification | Anticipate question, add answer |
| Inconsistent behavior | Add edge case handling, remove ambiguity |
</common_issues>
</testing_your_instructions>
</prompting_techniques>

<writing_checklist>
Before finalizing your CLAUDE.md:

- [ ] Genuine constraints (secrets, data loss) marked once; emphasis not stacked on ordinary guidance
- [ ] Most important items appear first in each section
- [ ] Vague phrases replaced with specific instructions
- [ ] Edge cases addressed
- [ ] Examples provided for complex patterns
- [ ] File references for implementation details
- [ ] Ambiguous phrases eliminated
- [ ] Under 200 lines total
- [ ] Tested with real tasks
</writing_checklist>
