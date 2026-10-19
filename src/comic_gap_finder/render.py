from __future__ import annotations

import json

from .markdown import literal
from .models import ScanReport


def render_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_markdown(report: ScanReport) -> str:
    summary = report.to_dict()["summary"]
    lines = [
        "# Comic gap report",
        "",
        f"Scanned: {literal(str(report.root))}",
        "",
        (
            f"Parsed {summary['parsedFiles']} files across {summary['series']} series; "
            f"found {summary['missingIssues']} missing issue numbers, "
            f"{summary['duplicateNumbers']} duplicated numbers, and "
            f"{summary['ambiguousFiles']} filenames requiring review."
        ),
        "",
    ]
    for series in report.series:
        lines.extend(
            [
                f"## {literal(series.name)}",
                "",
                "Issues: " + ", ".join(format(comic.issue, "f") for comic in series.comics),
                "",
                "Missing: " + (", ".join(map(str, series.missing)) or "none"),
                "",
                "Duplicate numbers: " + (", ".join(series.duplicates) or "none"),
                "",
                "Non-integer issues: " + (", ".join(series.non_integer_issues) or "none"),
                "",
            ]
        )
        if series.intentional_omissions:
            lines.extend(["Intentional omissions:", ""])
            lines.extend(
                f"- #{n}: {literal(reason)}"
                for n, reason in sorted(series.intentional_omissions.items())
            )
            lines.append("")
    if report.ambiguous:
        lines.extend(
            ["## Ambiguous filenames", "", *[f"- {literal(item)}" for item in report.ambiguous], ""]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "Results come only from filenames. Specials, intentionally skipped numbers, renumbering, and alternate editions require human review.",
            "",
        ]
    )
    return "\n".join(lines)
