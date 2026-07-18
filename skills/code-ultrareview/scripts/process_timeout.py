#!/usr/bin/env python3
"""Run a command with a bounded timeout and terminate its process group."""

from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Mapping, Sequence

TIMEOUT_EXIT_CODE = 124
EXECUTION_ERROR_EXIT_CODE = 125
TERMINATION_GRACE_SECONDS = 2


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    """Terminate the command and every descendant in its process group."""
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def run_process(
    command: str | Sequence[str],
    *,
    cwd: Path,
    timeout: int,
    shell: bool = False,
    stdout: int | IO[bytes] = subprocess.PIPE,
    stderr: int | IO[bytes] = subprocess.PIPE,
    env: Mapping[str, str] | None = None,
) -> ProcessResult:
    """Run one command in a new session and kill descendants on timeout."""
    if timeout <= 0:
        raise ValueError("timeout must be a positive integer")
    try:
        process = subprocess.Popen(
            command,
            cwd=str(cwd),
            shell=shell,
            stdout=stdout,
            stderr=stderr,
            start_new_session=True,
            env=env,
        )
    except OSError as exc:
        return ProcessResult(
            returncode=EXECUTION_ERROR_EXIT_CODE,
            stdout=b"",
            stderr=str(exc).encode("utf-8", errors="replace"),
            timed_out=False,
        )

    try:
        captured_stdout, captured_stderr = process.communicate(timeout=timeout)
        return ProcessResult(
            returncode=process.returncode,
            stdout=captured_stdout or b"",
            stderr=captured_stderr or b"",
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        _terminate_process_group(process)
        captured_stdout, captured_stderr = process.communicate()
        return ProcessResult(
            returncode=TIMEOUT_EXIT_CODE,
            stdout=captured_stdout or b"",
            stderr=captured_stderr or b"",
            timed_out=True,
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", required=True, type=int)
    parser.add_argument("--cwd", default=".", type=Path)
    parser.add_argument("--stdout", type=Path)
    parser.add_argument("--stderr", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("a command is required after --")
    if args.timeout <= 0:
        parser.error("--timeout must be a positive integer")

    stdout_handle: IO[bytes] | None = None
    stderr_handle: IO[bytes] | None = None
    try:
        if args.stdout:
            args.stdout.parent.mkdir(parents=True, exist_ok=True)
            stdout_handle = args.stdout.open("wb")
        if args.stderr:
            args.stderr.parent.mkdir(parents=True, exist_ok=True)
            stderr_handle = args.stderr.open("wb")
        result = run_process(
            command,
            cwd=args.cwd.resolve(),
            timeout=args.timeout,
            stdout=stdout_handle or subprocess.PIPE,
            stderr=stderr_handle or subprocess.PIPE,
        )
        if stdout_handle is None and result.stdout:
            sys.stdout.buffer.write(result.stdout)
        if stderr_handle is None and result.stderr:
            sys.stderr.buffer.write(result.stderr)
        if result.timed_out:
            message = (
                f"ERROR: command timed out after {args.timeout}s; "
                "its process group was terminated.\n"
            ).encode()
            if stderr_handle is not None:
                stderr_handle.write(message)
                stderr_handle.flush()
            else:
                sys.stderr.buffer.write(message)
        return result.returncode
    finally:
        if stdout_handle is not None:
            stdout_handle.close()
        if stderr_handle is not None:
            stderr_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
