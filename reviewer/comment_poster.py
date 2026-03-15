from github import Github
import os

# Emoji icons for severity levels
SEVERITY_ICON = {
    "error": "🔴",
    "warning": "🟡",
    "suggestion": "🔵",
}

CATEGORY_LABEL = {
    "security": "SECURITY",
    "bug": "BUG",
    "performance": "PERFORMANCE",
    "style": "STYLE",
    "logic": "LOGIC",
    "maintainability": "MAINTAINABILITY",
}


def post_review_comments(
    repo_name: str,
    pr_number: int,
    filename: str,
    comments: list[dict],
) -> int:
    """
    Post inline review comments on a PR for a single file.
    Returns the number of comments successfully posted.
    """
    if not comments:
        return 0

    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    commit = list(pr.get_commits())[-1]  # always use the latest commit

    posted = 0
    for c in comments:
        # Only post errors and warnings as inline comments to avoid noise
        if c.get("severity") not in ("error", "warning", "suggestion"):
            continue

        icon = SEVERITY_ICON.get(c["severity"], "⚪")
        label = CATEGORY_LABEL.get(c["category"], c["category"].upper())

        body = f"{icon} **[{label}]** {c['comment']}"

        if c.get("suggestion"):
            body += f"\n\n**Suggested fix:**\n```\n{c['suggestion']}\n```"

        try:
            pr.create_review_comment(
                body=body,
                commit=commit,
                path=filename,
                line=int(c["line"]),
            )
            posted += 1
        except Exception as e:
            # Line number may be wrong (e.g. outside the diff hunk) — skip gracefully
            print(f"  Could not post comment on line {c['line']} of {filename}: {e}")

    return posted


def post_summary_comment(
    repo_name: str,
    pr_number: int,
    all_comments: dict[str, list[dict]],
) -> None:
    """
    Post a single top-level PR comment with a summary table of all findings.
    all_comments is a dict of { filename: [comment, ...] }
    """
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    total_errors = 0
    total_warnings = 0
    total_suggestions = 0
    file_rows = []

    for filename, comments in all_comments.items():
        errors = sum(1 for c in comments if c["severity"] == "error")
        warnings = sum(1 for c in comments if c["severity"] == "warning")
        suggestions = sum(1 for c in comments if c["severity"] == "suggestion")
        total_errors += errors
        total_warnings += warnings
        total_suggestions += suggestions

        if comments:
            file_rows.append(
                f"| `{filename}` | {errors} | {warnings} | {suggestions} |"
            )

    if not file_rows:
        verdict = "✅ **No issues found.** Looks good!"
        body = f"## 🤖 AI Code Review\n\n{verdict}"
    else:
        verdict = (
            "🔴 **Issues found — please review before merging.**"
            if total_errors > 0
            else "🟡 **Warnings found — worth reviewing.**"
            if total_warnings > 0
            else "🔵 **Only suggestions — safe to merge.**"
        )

        table_header = (
            "| File | 🔴 Errors | 🟡 Warnings | 🔵 Suggestions |\n"
            "|------|-----------|-------------|----------------|\n"
        )
        table = table_header + "\n".join(file_rows)
        totals_row = f"\n\n**Totals:** {total_errors} errors · {total_warnings} warnings · {total_suggestions} suggestions"

        body = f"## 🤖 AI Code Review\n\n{verdict}\n\n{table}{totals_row}"

    pr.create_issue_comment(body)
    print(f"Summary posted: {total_errors} errors, {total_warnings} warnings, {total_suggestions} suggestions")
