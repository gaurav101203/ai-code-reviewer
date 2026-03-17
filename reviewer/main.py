import os
import sys

# Load .env file when running locally (ignored in GitHub Actions)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Allow imports from both reviewer/ and rules/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_client import get_pr_diff
from llm_client import review_file
from comment_poster import post_review_comments, post_summary_comment
from rules import run_all_rules


def merge_comments(rule_comments: list[dict], llm_comments: list[dict]) -> list[dict]:
    """
    Merge rule-based findings with LLM findings.
    Rules take priority — if a rule already flagged a line, skip the LLM comment for that line
    to avoid duplicate feedback on the same issue.
    """
    rule_lines = {c["line"] for c in rule_comments}
    filtered_llm = [c for c in llm_comments if c["line"] not in rule_lines]
    return rule_comments + filtered_llm


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

        # Step 1: fast static rule checks (no API call needed)
        print(f"   Running rule checks...")
        rule_comments = run_all_rules(filename, file["patch"])
        if rule_comments:
            print(f"   Rules found {len(rule_comments)} issue(s)")

        # Step 2: LLM review (catches logic bugs, complex issues rules can't see)
        print(f"   Running AI review...")
        llm_comments = review_file(filename, file["patch"], language)
        if llm_comments:
            print(f"   AI found {len(llm_comments)} issue(s)")

        # Step 3: merge, rules take priority on same lines
        comments = merge_comments(rule_comments, llm_comments)
        all_comments[filename] = comments

        if not comments:
            print(f"   ✅ No issues found")
            continue

        print(f"   Posting {len(comments)} comment(s)...")
        posted = post_review_comments(repo, pr_num, filename, comments)
        print(f"   ✅ Posted {posted} inline comment(s)")

    # --- Post the summary ---
    print("\n📊 Posting summary comment...")
    post_summary_comment(repo, pr_num, all_comments)

    print("\n✅ Review complete!\n")


if __name__ == "__main__":
    main()
