#!/usr/bin/env python3
"""Run one command with a bounded timeout and process-group cleanup."""
from __future__ import annotations

import argparse
import os
import signal
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Mapping, Optional, Sequence, Union

TIMEOUT_EXIT_CODE = 124
EXECUTION_ERROR_EXIT_CODE = 125
GRACE_SECONDS = 2
POLL_SECONDS = 0.2


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: bytes
    stderr: bytes
    timed_out: bool


def _bytes(value: Optional[bytes]) -> bytes:
    return value or b""


def _signal_group(process: subprocess.Popen, signum: int) -> None:
    try:
        os.killpg(process.pid, signum)
    except ProcessLookupError:
        pass


def _finish_group(process: subprocess.Popen, signum: int):
    _signal_group(process, signum)
    try:
        return process.communicate(timeout=GRACE_SECONDS)
    except subprocess.TimeoutExpired as first:
        _signal_group(process, signal.SIGKILL)
        try:
            return process.communicate(timeout=GRACE_SECONDS)
        except subprocess.TimeoutExpired as second:
            return second.output or first.output, second.stderr or first.stderr


def run_process(
    command: Union[str, Sequence[str]], *, cwd: Path, timeout: int,
    shell: bool = False, stdout: Union[int, IO[bytes]] = subprocess.PIPE,
    stderr: Union[int, IO[bytes]] = subprocess.PIPE,
    env: Optional[Mapping[str, str]] = None,
) -> ProcessResult:
    """Run in a new session; forward parent signals and kill descendants on timeout."""
    if timeout <= 0:
        raise ValueError("timeout must be a positive integer")
    try:
        process = subprocess.Popen(
            command, cwd=str(cwd), shell=shell, stdin=subprocess.DEVNULL,
            stdout=stdout, stderr=stderr, start_new_session=True, env=env,
        )
    except OSError as exc:
        return ProcessResult(EXECUTION_ERROR_EXIT_CODE, b"", str(exc).encode(), False)

    previous = {}
    forwarded_signal = None
    if threading.current_thread() is threading.main_thread():
        def forward(signum, _frame):
            nonlocal forwarded_signal
            forwarded_signal = signum
            _signal_group(process, signum)
        for signum in (signal.SIGINT, signal.SIGTERM):
            previous[signum] = signal.signal(signum, forward)
    try:
        deadline = time.monotonic() + timeout
        remaining = deadline - time.monotonic()
        while remaining > 0:
            try:
                captured = process.communicate(timeout=min(POLL_SECONDS, remaining))
                returncode = (128 + forwarded_signal
                              if forwarded_signal is not None else process.returncode)
                return ProcessResult(returncode, _bytes(captured[0]),
                                     _bytes(captured[1]), False)
            except subprocess.TimeoutExpired:
                if forwarded_signal is not None:
                    captured = _finish_group(process, forwarded_signal)
                    return ProcessResult(128 + forwarded_signal, _bytes(captured[0]),
                                         _bytes(captured[1]), False)
                remaining = deadline - time.monotonic()
        captured = _finish_group(process, signal.SIGTERM)
        return ProcessResult(TIMEOUT_EXIT_CODE, _bytes(captured[0]),
                             _bytes(captured[1]), True)
    finally:
        for signum, handler in previous.items():
            signal.signal(signum, handler)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", required=True, type=int)
    parser.add_argument("--cwd", default=".", type=Path)
    parser.add_argument("--stdout", type=Path)
    parser.add_argument("--stderr", type=Path)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("a command is required after --")
    if args.timeout <= 0:
        parser.error("--timeout must be a positive integer")

    stdout_handle = args.stdout.open("wb") if args.stdout else None
    stderr_handle = args.stderr.open("wb") if args.stderr else None
    try:
        result = run_process(
            command, cwd=args.cwd.resolve(), timeout=args.timeout,
            stdout=stdout_handle or subprocess.PIPE,
            stderr=stderr_handle or subprocess.PIPE,
        )
        if stdout_handle is None and result.stdout:
            sys.stdout.buffer.write(result.stdout)
        if stderr_handle is None and result.stderr:
            sys.stderr.buffer.write(result.stderr)
        if result.timed_out:
            message = (f"ERROR: command timed out after {args.timeout}s; "
                       "its process group was terminated.\n").encode()
            target = stderr_handle or sys.stderr.buffer
            target.write(message)
            target.flush()
        return result.returncode
    finally:
        if stdout_handle:
            stdout_handle.close()
        if stderr_handle:
            stderr_handle.close()


if __name__ == "__main__":
    raise SystemExit(main())
