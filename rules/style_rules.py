import re

STYLE_RULES = [
    (
        r'^\s*#\s*TODO|^\s*#\s*FIXME|^\s*#\s*HACK|^\s*#\s*XXX',
        "TODO/FIXME comment left in code. Resolve this before merging or create a tracked issue instead.",
        "style",
        "warning",
    ),
    (
        r'print\s*\(',
        "print() statement found. Use a proper logger (logging module) instead of print for production code.",
        "style",
        "suggestion",
    ),
    (
        r'except\s*:',
        "Bare except: catches everything including KeyboardInterrupt and SystemExit. Always catch specific exceptions.",
        "style",
        "warning",
    ),
    (
        r'except\s+Exception\s*:',
        "Catching bare Exception is too broad. Catch the specific exception types you expect.",
        "style",
        "suggestion",
    ),
    (
        r'^\s{0,}(\w+)\s*=\s*\1\s*$',
        "Self-assignment detected (x = x). This line does nothing and should be removed.",
        "style",
        "warning",
    ),
    (
        r'pass\s*$',
        "Empty block with pass. Add a comment explaining why this is intentionally empty, or implement the logic.",
        "style",
        "suggestion",
    ),
    (
        r'lambda\s+\w+.*:\s*\w+\s*\(',
        "Consider replacing this lambda with a named function for better readability and debuggability.",
        "style",
        "suggestion",
    ),
    (
        r'if\s+\w+\s*==\s*True|if\s+\w+\s*==\s*False',
        "Don't compare to True/False explicitly. Use 'if x:' or 'if not x:' instead.",
        "style",
        "suggestion",
    ),
    (
        r'^\s*import\s+\*',
        "Wildcard imports pollute the namespace and make it hard to know where names come from. Import explicitly.",
        "style",
        "warning",
    ),
]


def run(filename: str, patch: str) -> list[dict]:
    """Run all style rules against the added lines in a diff patch."""
    # Only run style rules on Python files
    if not filename.endswith(".py"):
        return []

    comments = []
    for i, line in enumerate(_added_lines(patch), start=1):
        for pattern, message, category, severity in STYLE_RULES:
            if re.search(pattern, line):
                comments.append({
                    "line": i,
                    "severity": severity,
                    "category": category,
                    "comment": message,
                    "source": "rules:style",
                })
                break
    return comments


def _added_lines(patch: str) -> list[str]:
    return [
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
