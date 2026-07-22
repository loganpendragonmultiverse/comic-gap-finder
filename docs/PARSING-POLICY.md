# Parsing policy

1. Explicit issue markers win.
2. Years and explicit volume tokens are excluded from fallback candidates.
3. The fallback parser accepts exactly one remaining numeric token.
4. Multiple candidates are reported as ambiguous.
5. Decimal issues are listed but do not fill integer gaps.
6. Duplicate numbers are surfaced without declaring files duplicate in content.
