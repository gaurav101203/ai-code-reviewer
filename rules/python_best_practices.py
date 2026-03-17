import re

PYTHON_RULES = [
    (
        r'^\s*def\s+\w+\s*\(.*\)\s*:(?!\s*[\n\r]\s*["\'])',
        "Function is missing a docstring. Add a brief docstring explaining what it does, its parameters, and return value.",
        "maintainability",
        "suggestion",
    ),
    (
        r'\.keys\(\)\s*\)',
        "Iterating over dict.keys() is redundant. Iterating over a dict directly gives you the keys.",
        "maintainability",
        "suggestion",
    ),
    (
        r'if\s+len\s*\(\s*\w+\s*\)\s*[>=!]=?\s*0|if\s+len\s*\(\s*\w+\s*\)\s*:',
        "Use 'if my_list:' or 'if not my_list:' instead of checking len(). It's more Pythonic and handles all sequences.",
        "maintainability",
        "suggestion",
    ),
    (
        r'open\s*\((?!.*with\s)',
        "Use 'with open(...) as f:' instead of open() directly. It guarantees the file is closed even if an error occurs.",
        "maintainability",
        "warning",
    ),
    (
        r'^\s*(\w+)\s*=\s*\[\s*\]\s*\n.*\.append',
        "Consider using a list comprehension instead of initializing an empty list and appending in a loop.",
        "maintainability",
        "suggestion",
    ),
    (
        r'type\s*\(\s*\w+\s*\)\s*==',
        "Use isinstance() instead of type() == for type checking. It handles subclasses correctly.",
        "maintainability",
        "suggestion",
    ),
    (
        r'^\s*raise\s+Exception\s*\(',
        "Raising a generic Exception is too broad. Use or create a specific exception class for better error handling.",
        "maintainability",
        "suggestion",
    ),
    (
        r'mutable.*=\s*\[|mutable.*=\s*\{',
        "Mutable default arguments are shared across all calls. Use None as default and initialize inside the function.",
        "maintainability",
        "warning",
    ),
]


def run(filename: str, patch: str) -> list[dict]:
    """Run Python best practice rules. Only applies to .py files."""
    if not filename.endswith(".py"):
        return []

    comments = []
    for i, line in enumerate(_added_lines(patch), start=1):
        for pattern, message, category, severity in PYTHON_RULES:
            if re.search(pattern, line):
                comments.append({
                    "line": i,
                    "severity": severity,
                    "category": category,
                    "comment": message,
                    "source": "rules:python",
                })
                break
    return comments


def _added_lines(patch: str) -> list[str]:
    return [
        line[1:]
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
