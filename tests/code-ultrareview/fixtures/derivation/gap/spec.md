# Spec — gap fixture

A spec with an AC that the diff (out of band) does not implement.
The derivation lens should surface the AC as an UNCLASSIFIED finding;
a downstream subagent classifies it as GAP after comparing to the diff.

## Acceptance criteria

- [ ] AC1: the system shall validate IPv6 zone-id per RFC 6874
- [ ] AC2: a `--strict` flag enables full validation
- [ ] AC3: errors emit `RESULT: error=...` lines on stderr
