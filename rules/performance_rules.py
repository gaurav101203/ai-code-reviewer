import re

PERFORMANCE_RULES = [
    (
        r'for\s+\w+\s+in\s+range\s*\(\s*len\s*\(',
        "Using range(len(x)) is inefficient. Iterate directly over the collection or use enumerate() if you need the index.",
        "performance",
        "warning",
    ),
    (
        r'\+\=\s*["\']|["\'].join\s*\(\s*\[',
        "String concatenation in a loop is O(n²). Build a list and use ''.join() at the end for better performance.",
        "performance",
        "warning",
    ),
    (
        r'\.append\s*\(.*\)\s*$',
        "If building a list via append in a loop, consider a list comprehension — it's faster and more readable.",
        "performance",
        "suggestion",
    ),
    (
        r'time\.sleep\s*\(\s*[5-9]\d*|time\.sleep\s*\(\s*[1-9]\d+',
        "Long sleep() calls block the thread entirely. Consider asyncio.sleep() or a task queue for long waits.",
        "performance",
        "warning",
    ),
    (
        r'SELECT\s+\*\s+FROM',
        "SELECT * fetches all columns including ones you don't need. Specify only the columns you require.",
        "performance",
        "warning",
    ),
    (
        r'\.objects\.all\(\)',
        "Fetching all objects can load thousands of rows into memory. Add .filter(), .limit(), or pagination.",
        "performance",
        "warning",
    ),
    (
        r'global\s+\w+',
        "Global variables can cause unexpected state and make code harder to optimize. Prefer passing values as parameters.",
        "performance",
        "suggestion",
    ),
]


def run(filename: str, patch: str) -> list[dict]:
    """Run all performance rules against the added lines in a diff patch."""
    comments = []
    for i, line in enumerate(_added_lines(patch), start=1):
        for pattern, message, category, severity in PERFORMANCE_RULES:
            if re.search(pattern, line):
                comments.append({
                    "line": i,
                    "severity": severity,
                    "category": category,
                    "comment": message,
                    "source": "rules:performance",
                })
                break
    return comments


def _added_lines(patch: str) -> list[str]:
    return [
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
