#!/usr/bin/env python3
"""Hold nonblocking Darwin leases for every shared Echo narration resource."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import os
import signal
import stat
import subprocess
import sys
from pathlib import Path


TEMPORARY_FAILURE = 75


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-root", type=Path, required=True)
    parser.add_argument("--resource", action="append", required=True)
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args(arguments)
    if options.command and options.command[0] == "--":
        options.command = options.command[1:]
    if not options.command:
        parser.error("a command is required after --")
    return options


def canonical_resource(resource: str) -> str:
    return str(Path(resource).resolve())


def lock_path(lock_root: Path, resource: str) -> Path:
    digest = hashlib.sha256(canonical_resource(resource).encode("utf-8")).hexdigest()
    return lock_root / f"{digest}.lock"


def open_lock(path: Path) -> int:
    flags = os.O_RDWR | os.O_CREAT
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    lock_fd = os.open(path, flags, 0o600)
    if not stat.S_ISREG(os.fstat(lock_fd).st_mode):
        os.close(lock_fd)
        raise OSError(f"lease is not a regular file: {path}")
    return lock_fd


def run(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    options.lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if options.lock_root.is_symlink() or not options.lock_root.is_dir():
        print(f"malformed narration lease root: {options.lock_root}", file=sys.stderr)
        return TEMPORARY_FAILURE

    resources = sorted({canonical_resource(resource) for resource in options.resource})
    lock_fds: list[int] = []
    process: subprocess.Popen[bytes] | None = None
    try:
        for resource in resources:
            path = lock_path(options.lock_root, resource)
            lock_fd = open_lock(path)
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                os.close(lock_fd)
                print(
                    f"active narration lease owns shared resource: {resource}",
                    file=sys.stderr,
                )
                return TEMPORARY_FAILURE
            lock_fds.append(lock_fd)

        process = subprocess.Popen(
            options.command,
            close_fds=True,
            pass_fds=tuple(lock_fds),
        )

        def forward_signal(signal_number: int, _frame: object) -> None:
            if process is not None and process.poll() is None:
                process.send_signal(signal_number)

        for signal_number in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM):
            signal.signal(signal_number, forward_signal)

        return_code = process.wait()
        if return_code < 0:
            return 128 - return_code
        return return_code
    except OSError as error:
        print(f"malformed narration lease: {error}", file=sys.stderr)
        return TEMPORARY_FAILURE
    finally:
        for lock_fd in lock_fds:
            os.close(lock_fd)


if __name__ == "__main__":
    raise SystemExit(run(sys.argv[1:]))
