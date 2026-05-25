## Summary
- Adds the `prose-hygiene` lens to the code-ultrareview skill.
- Auto-ingests PR body and commits when a PR is open for the current branch.
- Ships a portable baseline; layers project rules via standard discovery.

## Test plan
- [ ] `python3 -m unittest discover tests/code-ultrareview/ -v` green.
- [ ] Manual: run `bash scripts/fetch_pr_meta.sh` in a clone with no `gh` installed; expect `RESULT: pr_found=false` and exit 0.
- [ ] Manual: run `python3 scripts/check_prose_hygiene.py --pr-body-file <this>` on a clean PR body; expect `[]` output.

## Related skills
- See the brand-voice skill for voice management.
- BRAND-VOICE.md is the canonical output format the public skill emits.

## Writing rules notes
- NEVER commit secrets — keys, tokens, and credentials stay out of the diff.
- The lens never aborts the review; degradation always surfaces a row.
- The orchestrator never silent-drops a finding — sub-80 routes to Unverified.
