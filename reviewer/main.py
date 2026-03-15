import os
import sys

# Load .env file when running locally (ignored in GitHub Actions)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from github_client import get_pr_diff
from llm_client import review_file
from comment_poster import post_review_comments, post_summary_comment


def main():
    # --- Read environment variables ---
    repo = os.environ.get("REPO_NAME")
    pr_num_str = os.environ.get("PR_NUMBER")

    if not repo or not pr_num_str:
        print("ERROR: REPO_NAME and PR_NUMBER environment variables must be set.")
        sys.exit(1)

    try:
        pr_num = int(pr_num_str)
    except ValueError:
        print(f"ERROR: PR_NUMBER must be an integer, got: {pr_num_str}")
        sys.exit(1)

    print(f"\n🤖 AI Code Reviewer starting...")
    print(f"   Repo: {repo}")
    print(f"   PR:   #{pr_num}\n")

    # --- Fetch the PR diff ---
    print("📥 Fetching PR diff...")
    files = get_pr_diff(repo, pr_num)

    if not files:
        print("No reviewable files found in this PR (only supported: .py .js .ts .jsx .tsx)")
        sys.exit(0)

    print(f"   Found {len(files)} file(s) to review\n")

    # --- Review each file ---
    all_comments: dict[str, list[dict]] = {}

    for file in files:
        filename = file["filename"]
        language = file["language"]
        print(f"🔍 Reviewing {filename} ({language})...")

        comments = review_file(filename, file["patch"], language)
        all_comments[filename] = comments

        if not comments:
            print(f"   ✅ No issues found")
            continue

        print(f"   Found {len(comments)} comment(s) — posting...")
        posted = post_review_comments(repo, pr_num, filename, comments)
        print(f"   ✅ Posted {posted} inline comment(s)")

    # --- Post the summary ---
    print("\n📊 Posting summary comment...")
    post_summary_comment(repo, pr_num, all_comments)

    print("\n✅ Review complete!\n")


if __name__ == "__main__":
    main()
