# Spec: Malformed sample with no workstreams subheader

**Date:** 2026-05-21

This fixture deliberately carries the spec H1 token but is missing the second half of the heuristic gate — there is no workstreams subheader below. A correctly implemented spec-closure detection must NOT activate on this file (inference should still run).

## Overview

Used by `test_ac_template.py::test_malformed_spec_does_not_match_spec_heuristic` to verify the AND-gate's negative case.
