import re

# Each rule is: (pattern, line_message, category, severity)
SECURITY_RULES = [
    (
        r'(?i)(password|passwd|pwd|secret|api_key|apikey|token|auth_key)\s*=\s*["\'][^"\']{4,}["\']',
        "Hardcoded secret detected. Never store credentials in source code — use environment variables instead.",
        "security",
        "error",
    ),
    (
        r'eval\s*\(',
        "Use of eval() is dangerous — it can execute arbitrary code. Avoid it entirely or use safer alternatives like ast.literal_eval().",
        "security",
        "error",
    ),
    (
        r'exec\s*\(',
        "Use of exec() allows arbitrary code execution. This is a critical security risk.",
        "security",
        "error",
    ),
    (
        r'os\.system\s*\(',
        "os.system() is vulnerable to command injection. Use subprocess.run() with a list of arguments instead.",
        "security",
        "error",
    ),
    (
        r'subprocess\.call\s*\(.*shell\s*=\s*True',
        "shell=True in subprocess is vulnerable to shell injection. Pass arguments as a list instead.",
        "security",
        "error",
    ),
    (
        r'(?i)SELECT\s+.*\+\s*|WHERE\s+.*\+\s*',
        "Possible SQL injection — string concatenation in SQL queries is dangerous. Use parameterized queries instead.",
        "security",
        "error",
    ),
    (
        r'pickle\.loads?\s*\(',
        "pickle.load() can execute arbitrary code when deserializing untrusted data. Use JSON or another safe format.",
        "security",
        "warning",
    ),
    (
        r'md5\s*\(|hashlib\.md5',
        "MD5 is cryptographically broken. Use hashlib.sha256() or better for security-sensitive hashing.",
        "security",
        "warning",
    ),
    (
        r'http://(?!localhost|127\.0\.0\.1)',
        "Using plain HTTP sends data unencrypted. Use HTTPS instead.",
        "security",
        "warning",
    ),
]


def run(filename: str, patch: str) -> list[dict]:
    """Run all security rules against the added lines in a diff patch."""
    comments = []
    for i, line in enumerate(_added_lines(patch), start=1):
        for pattern, message, category, severity in SECURITY_RULES:
            if re.search(pattern, line):
                comments.append({
                    "line": i,
                    "severity": severity,
                    "category": category,
                    "comment": message,
                    "source": "rules:security",
                })
                break  # one finding per line max
    return comments


def _added_lines(patch: str) -> list[str]:
    """Extract only the lines added in a diff (lines starting with +)."""
    return [
        line[1:]  # strip the leading +
        for line in patch.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]
