#!/usr/bin/env bash
# Idempotent label setup for /spec -i
# Creates priority, complexity, and type labels. --force updates color/description if label exists.

set -euo pipefail

gh label create "P0" --color "d73a4a" --description "Must have — blocks the feature" --force
gh label create "P1" --color "e99695" --description "Should have — ship in same release" --force
gh label create "P2" --color "f9d0c4" --description "Nice to have — can defer" --force

gh label create "size:S" --color "c2e0c6" --description "Small — under 1 hour" --force
gh label create "size:M" --color "bfd4f2" --description "Medium — 1-4 hours" --force
gh label create "size:L" --color "d4c5f9" --description "Large — 4-8 hours" --force
gh label create "size:XL" --color "e6ccb3" --description "Extra large — over 1 day" --force

gh label create "spec" --color "0e8a16" --description "Spec-generated workstream" --force
