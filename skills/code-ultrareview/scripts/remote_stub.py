#!/usr/bin/env python3
"""`--remote` flag stub.

Phase-2 escalation to Anthropic's Code Sandbox is reserved. At MVP the
flag accepts cleanly, prints the documented redirect, and exits 0. Users
discover the flag from `argument-hint`, hit this message, and learn
about the phase-2 plan via `references/remote-escalation-design.md`.

The exit-zero (no-op) shape lets the orchestrator chain the call
without special-casing: `python3 remote_stub.py && python3 run.py ...`
falls through to the regular in-session flow.
"""

import sys

MESSAGE = (
    "--remote is reserved for phase-2 escalation. In-session execution "
    "is the current MVP. See references/remote-escalation-design.md "
    "for the planned remote-sandbox flow."
)


def main() -> int:
    print(MESSAGE)
    return 0


if __name__ == "__main__":
    sys.exit(main())
