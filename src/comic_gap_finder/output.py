from __future__ import annotations

import os
import sys
from pathlib import Path


def write_stdout(text: str) -> None:
    """Flush within the CLI error boundary, including small buffered reports."""
    try:
        sys.stdout.write(text)
        sys.stdout.flush()
    except OSError:
        # Prevent a second broken-pipe exception during interpreter shutdown.
        try:
            descriptor = sys.stdout.fileno()
            with open(os.devnull, "w", encoding="utf-8") as sink:
                os.dup2(sink.fileno(), descriptor)
        except (AttributeError, OSError, ValueError):
            pass
        raise


def write_report(output: Path | None, text: str) -> None:
    if output is None:
        write_stdout(text)
    else:
        if output.is_symlink():
            raise FileExistsError(f"output must not be a symlink: {output}")
        # Exclusive creation also refuses dangling symlinks and racing writers.
        with output.open("x", encoding="utf-8", newline="") as stream:
            stream.write(text)


def validate_outputs(paths: list[Path]) -> None:
    """Check the whole requested set before writing any report."""
    for path in paths:
        if path.expanduser().is_symlink() or path.expanduser().exists():
            raise FileExistsError(f"output already exists: {path}")
    try:
        resolved = {path.expanduser().resolve() for path in paths}
    except RuntimeError as exc:
        raise ValueError("output path contains a symlink loop") from exc
    if len(resolved) != len(paths):
        raise ValueError("report outputs must be distinct new files")
