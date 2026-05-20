"""`--apply-safe` writers (opt-in).

Three writers, each gated by per-file confirmation:
    version_sync         — align version artifacts to most-recently-touched.
    description_sync     — align structured descriptions (full-agreement guard).
    failing_test_writer  — additive failing test per confirmed bug.

Shared confirmation gate lives in `_common.confirm_write`.
"""
