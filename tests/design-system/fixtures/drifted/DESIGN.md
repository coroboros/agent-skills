---
version: alpha
name: Drifted Fixture
description: Carries one of each drift mode — extension-missing-css, extension-orphan-css (warning), extension-broken-ref. audit-extensions exit 1.
colors:
  primary: "#1a1c1e"
  surface: "#f7f5f1"
  on-surface: "#1a1c1e"
typography:
  body-md:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  sm: 2px
  md: 4px
spacing:
  unit: 8px
  md: 16px
components:
  modal:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.md}"
motion:
  duration-reveal-slow: 1200ms
  duration-reveal-extra-slow: 2000ms
shadows:
  lifted: 0 20px 40px -16px rgb(28 26 22 / 0.08)
---

## Overview

Drifted fixture — exercises every audit-extensions rule.

## Layout

Hero uses `{motion.duration-reveal-slow}` and `{motion.duration-undefined-token}`.

## Elevation & Depth

Modal lifts on `{shadows.cinematic}` (not defined in YAML).
