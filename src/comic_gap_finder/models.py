from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ParsedComic:
    path: Path
    series: str
    issue: Decimal
    method: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path.as_posix(),
            "series": self.series,
            "issue": format(self.issue, "f"),
            "method": self.method,
        }


@dataclass
class SeriesReport:
    name: str
    comics: list[ParsedComic] = field(default_factory=list)
    missing: list[int] = field(default_factory=list)
    duplicates: dict[str, list[str]] = field(default_factory=dict)
    non_integer_issues: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "issues": [comic.to_dict() for comic in self.comics],
            "missing": self.missing,
            "duplicates": self.duplicates,
            "nonIntegerIssues": self.non_integer_issues,
        }


@dataclass
class ScanReport:
    root: Path
    series: list[SeriesReport]
    ambiguous: list[str]
    ignored: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schemaVersion": 1,
            "root": str(self.root),
            "summary": {
                "series": len(self.series),
                "parsedFiles": sum(len(item.comics) for item in self.series),
                "missingIssues": sum(len(item.missing) for item in self.series),
                "duplicateNumbers": sum(len(item.duplicates) for item in self.series),
                "ambiguousFiles": len(self.ambiguous),
                "ignoredFiles": len(self.ignored),
            },
            "series": [item.to_dict() for item in self.series],
            "ambiguous": self.ambiguous,
            "ignored": self.ignored,
        }
