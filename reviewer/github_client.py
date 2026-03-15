from github import Github
import os

SUPPORTED_EXTENSIONS = ('.py', '.js', '.ts', '.jsx', '.tsx')


def get_pr_diff(repo_name: str, pr_number: int) -> list[dict]:
    """Fetch the list of changed files and their diffs from a pull request."""
    g = Github(os.environ["GITHUB_TOKEN"])
    repo = g.get_repo(repo_name)
    # pr = repo.get_pull(pr_number)

    files_to_review = []

    for file in pr.get_files():
        if not file.patch:
            # Binary files or files with no diff (e.g. renamed with no changes)
            continue
        if not file.filename.endswith(SUPPORTED_EXTENSIONS):
            continue

        files_to_review.append({
            "filename": file.filename,
            "patch": file.patch,
            "additions": file.additions,
            "deletions": file.deletions,
            "status": file.status,           # added / modified / removed
            "language": detect_language(file.filename),
        })

    return files_to_review


def detect_language(filename: str) -> str:
    """Return a human-readable language name based on file extension."""
    ext = filename.rsplit('.', 1)[-1].lower()
    mapping = {
        "py": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "jsx": "React JSX",
        "tsx": "React TSX",
    }
    return mapping.get(ext, "Unknown")

