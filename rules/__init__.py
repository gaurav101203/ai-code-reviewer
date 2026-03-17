from rules import security_rules, performance_rules, style_rules, python_best_practices


def run_all_rules(filename: str, patch: str) -> list[dict]:
    """
    Run all static rule engines against a file's diff.
    Returns a combined, deduplicated list of findings.
    """
    all_findings = []

    all_findings += security_rules.run(filename, patch)
    all_findings += performance_rules.run(filename, patch)
    all_findings += style_rules.run(filename, patch)
    all_findings += python_best_practices.run(filename, patch)

    # Deduplicate: if multiple rules fired on the same line, keep the highest severity one
    seen_lines: dict[int, dict] = {}
    severity_rank = {"error": 3, "warning": 2, "suggestion": 1}

    for finding in all_findings:
        line = finding["line"]
        if line not in seen_lines:
            seen_lines[line] = finding
        else:
            existing = seen_lines[line]
            if severity_rank.get(finding["severity"], 0) > severity_rank.get(existing["severity"], 0):
                seen_lines[line] = finding

    return list(seen_lines.values())
