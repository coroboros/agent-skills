---
version: alpha
name: Clean Fixture
description: Award-design output shape — canonical 5 + extension namespaces. Every extension token has its globals.css mirror; every prose ref resolves. audit-extensions exit 0.
colors:
  primary: "#1a1c1e"
  surface: "#f7f5f1"
  on-surface: "#1a1c1e"
  tertiary: "#c9a071"
typography:
  display:
    fontFamily: "Editorial Serif, Georgia, serif"
    fontSize: 88px
    fontWeight: 400
    lineHeight: 1
    letterSpacing: -0.02em
  body-md:
    fontFamily: "Inter, system-ui, sans-serif"
    fontSize: 16px
    fontWeight: 400
    lineHeight: 1.6
rounded:
  none: 0px
  sm: 2px
  md: 4px
  lg: 8px
spacing:
  unit: 8px
  sm: 8px
  md: 16px
  lg: 32px
  xl: 64px
components:
  modal:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.on-surface}"
    rounded: "{rounded.md}"
    padding: 32px
  button-primary:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: 14px 24px
motion:
  duration-hover: 200ms
  duration-reveal-slow: 1200ms
  ease-standard: cubic-bezier(0.16, 1, 0.3, 1)
shadows:
  whisper: 0 1px 0 0 rgb(28 26 22 / 0.08)
  lifted: 0 20px 40px -16px rgb(28 26 22 / 0.08)
aspectRatios:
  listing: 3 / 2
heights:
  hero: 100svh
  nav-desktop: 72px
zIndex:
  modal: 80
opacity:
  overlay-modal: 0.70
---

## Overview

Award-design output stub for audit-extensions test fixture. Atmosphere 3/4/3.

## Layout

Hero reveals on scroll using `{motion.duration-reveal-slow}` paced by `{motion.ease-standard}`. Listings sit at `{aspectRatios.listing}`. Hero block holds `{heights.hero}`.

## Elevation & Depth

Modal lifts on `{shadows.lifted}` over `{opacity.overlay-modal}` scrim. Whisper cards use `{shadows.whisper}`.

## Components

Primary buttons hover over `{motion.duration-hover}`.
