from google import genai
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from chunk_processor import split_patch_into_chunks, adjust_line_numbers

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

SYSTEM_PROMPT = """You are a senior software engineer performing a thorough code review.

Analyze the provided git diff and return a JSON array of review comments.
Each comment MUST have exactly these fields:
- "line": the line number in the diff where the issue is (integer). Use the last line of the relevant hunk if unsure.
- "severity": one of "error" | "warning" | "suggestion"
- "category": one of "security" | "bug" | "performance" | "style" | "logic" | "maintainability"
- "comment": your review comment. Be specific and actionable. Max 3 sentences.
- "suggestion": an optional improved code snippet (string). Omit this key if you have no fix to offer.

Rules:
- ALWAYS flag hardcoded passwords, credentials, secrets, or sensitive data — this is your #1 priority and overrides all other limits
- The 5 issue limit does NOT apply to security findings
- Only comment on lines that were ADDED (lines starting with +). Do not comment on removed lines (-).
- Be precise. If a line has no real issue, do not comment on it.
- For security issues, always set severity to "error".
- Return ONLY valid JSON array. No markdown fences, no explanation, no preamble.
- If there are no issues at all, return an empty array: []
- Do NOT suggest suggestions unless they are genuinely impactful
- Only comment on a maximum of 5 issues per file
- Ignore minor style preferences — focus on real bugs, security, and performance
- Do NOT comment on missing docstrings or minor naming issues"""


def _call_llm(prompt: str) -> list[dict]:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    raw = response.text.strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    comments = json.loads(raw)

    valid = []
    for c in comments:
        if all(k in c for k in ("line", "severity", "category", "comment")):
            valid.append(c)
        else:
            print(f"  Skipping malformed comment: {c}")

    return valid


def review_file(filename: str, patch: str, language: str) -> list[dict]:
    chunks = split_patch_into_chunks(patch)

    if len(chunks) > 1:
        print(f"  Large diff — split into {len(chunks)} chunks")

    all_comments = []

    for chunk_index, chunk in enumerate(chunks):
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"Please review this {language} diff for `{filename}`"
            + (f" (chunk {chunk_index + 1}/{len(chunks)})" if len(chunks) > 1 else "")
            + f":\n\n```diff\n{chunk}\n```"
        )

        try:
            comments = _call_llm(prompt)
            if chunk_index > 0:
                comments = adjust_line_numbers(comments, chunk_index, 100)
            all_comments.extend(comments)
        except json.JSONDecodeError as e:
            print(f"  JSON parse error in chunk {chunk_index + 1} of {filename}: {e}")
        except Exception as e:
            print(f"  Unexpected error in chunk {chunk_index + 1} of {filename}: {e}")

    return all_comments