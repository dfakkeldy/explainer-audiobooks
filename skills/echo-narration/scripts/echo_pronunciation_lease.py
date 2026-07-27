#!/usr/bin/env python3
"""Hold nonblocking Darwin leases for every shared Echo narration resource."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import stat
import subprocess
import sys
from pathlib import Path


TEMPORARY_FAILURE = 75
CAPABILITY_ENV = "ECHO_PRONUNCIATION_LEASE_CAPABILITY"


def parse_arguments(arguments: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lock-root", type=Path, required=True)
    parser.add_argument("--resource", action="append", required=True)
    parser.add_argument("--assert-held", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    options = parser.parse_args(arguments)
    if options.command and options.command[0] == "--":
        options.command = options.command[1:]
    if not options.assert_held and not options.command:
        parser.error("a command is required after --")
    if options.assert_held and options.command:
        parser.error("--assert-held does not accept a command")
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


def load_capability() -> dict[str, int]:
    raw = os.environ.get(CAPABILITY_ENV)
    if not raw:
        raise OSError("missing inherited FD-backed lease capability")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise OSError("malformed inherited FD-backed lease capability") from error
    if not isinstance(payload, dict) or not payload:
        raise OSError("malformed inherited FD-backed lease capability")
    result: dict[str, int] = {}
    for resource, file_descriptor in payload.items():
        if (
            not isinstance(resource, str)
            or canonical_resource(resource) != resource
            or type(file_descriptor) is not int
            or file_descriptor < 0
        ):
            raise OSError("malformed inherited FD-backed lease capability")
        result[resource] = file_descriptor
    return result


def validate_capability(
    lock_root: Path,
    expected_resources: list[str],
    capability: dict[str, int],
) -> None:
    for resource in expected_resources:
        if resource not in capability:
            raise OSError(
                f"inherited FD-backed lease capability does not cover: {resource}"
            )
        inherited_fd = capability[resource]
        inherited_stat = os.fstat(inherited_fd)
        if not stat.S_ISREG(inherited_stat.st_mode):
            raise OSError(f"inherited lease FD is not regular: {resource}")

        expected_path = lock_path(lock_root, resource)
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        comparison_fd = os.open(expected_path, flags)
        try:
            comparison_stat = os.fstat(comparison_fd)
            if (
                inherited_stat.st_dev != comparison_stat.st_dev
                or inherited_stat.st_ino != comparison_stat.st_ino
            ):
                raise OSError(f"inherited lease FD has the wrong inode: {resource}")
            try:
                fcntl.flock(comparison_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                pass
            else:
                fcntl.flock(comparison_fd, fcntl.LOCK_UN)
                raise OSError(f"inherited lease FD does not hold the lock: {resource}")
        finally:
            os.close(comparison_fd)


def run(arguments: list[str]) -> int:
    options = parse_arguments(arguments)
    options.lock_root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if options.lock_root.is_symlink() or not options.lock_root.is_dir():
        print(f"malformed narration lease root: {options.lock_root}", file=sys.stderr)
        return TEMPORARY_FAILURE

    resources = sorted({canonical_resource(resource) for resource in options.resource})
    if options.assert_held:
        try:
            capability = load_capability()
            validate_capability(options.lock_root, resources, capability)
            return 0
        except (OSError, ValueError) as error:
            print(f"invalid narration lease: {error}", file=sys.stderr)
            return TEMPORARY_FAILURE

    lock_fds: list[int] = []
    capability: dict[str, int] = {}
    process: subprocess.Popen[bytes] | None = None
    try:
        inherited_raw = os.environ.get(CAPABILITY_ENV)
        if inherited_raw:
            capability = load_capability()
            validate_capability(options.lock_root, sorted(capability), capability)
        for resource in resources:
            if resource in capability:
                continue
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
            capability[resource] = lock_fd

        environment = os.environ.copy()
        environment[CAPABILITY_ENV] = json.dumps(
            capability, sort_keys=True, separators=(",", ":")
        )
        process = subprocess.Popen(
            options.command,
            close_fds=True,
            pass_fds=tuple(sorted(set(capability.values()))),
            env=environment,
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
