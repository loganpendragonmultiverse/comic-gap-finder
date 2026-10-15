# Development scope

Version 1 performs a read-only, metadata-free filename audit. Ambiguous filenames remain unresolved rather than guessed. Missing numbers are computed only within observed or explicitly requested integer ranges.

Archive contents, external databases, rename operations, and editorial claims about true completeness are outside this release.


## 1.1.0 candidate

Use `--expectations expectations.json` to apply a separate integer range to each named series:

```json
{"North Signal":{"start":1,"end":12,"omissions":{"7":"Number intentionally not collected"}}}
```

Series names use the existing normalized filename grouping. Duplicate normalized names are rejected. Each rule requires both bounds; it overrides the global range for that series. Configured series with no files are still reported. Omission reasons appear in JSON and Markdown and suppress only those missing integer numbers. They do not hide present files, duplicates, decimals, annuals, or ambiguous filenames. Global options and scans without a configuration keep their existing behavior. Bounds are limited to -1000 through 100000 (at most 101001 integer numbers per series). Decimal issues remain evidence, not integer range members. Annuals remain separate filename-inferred series; ambiguous identities require review.
