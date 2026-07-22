from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__
from .core import scan_directory
from .render import render_json, render_markdown


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        prog="comic-gap-finder",
        description="Find likely issue-number gaps from local comic filenames.",
    )
    result.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    result.add_argument("root", type=Path)
    result.add_argument("--recursive", action="store_true")
    result.add_argument("--expected-start", type=int)
    result.add_argument("--expected-end", type=int)
    result.add_argument("--json", dest="json_path", type=Path)
    result.add_argument("--markdown", type=Path)
    result.add_argument("--fail-on-gaps", action="store_true")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = scan_directory(
            args.root,
            recursive=args.recursive,
            expected_start=args.expected_start,
            expected_end=args.expected_end,
        )
        markdown = render_markdown(report)
        if args.json_path:
            write_new(args.json_path, render_json(report))
        if args.markdown:
            write_new(args.markdown, markdown)
        if not args.json_path and not args.markdown:
            print(markdown)
        has_gaps = any(series.missing for series in report.series)
        return 1 if args.fail_on_gaps and has_gaps else 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def write_new(path: Path, content: str) -> None:
    target = path.expanduser().resolve()
    if target.exists():
        raise ValueError(f"output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")
