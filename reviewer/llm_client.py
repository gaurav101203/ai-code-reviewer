from google import genai
import json
import os

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
- Only comment on lines that were ADDED (lines starting with +). Do not comment on removed lines (-).
- Be precise. If a line has no real issue, do not comment on it.
- For security issues, always set severity to "error".
- Return ONLY valid JSON array. No markdown fences, no explanation, no preamble.
- If there are no issues at all, return an empty array: []

Example output:
[
  {
    "line": 12,
    "severity": "error",
    "category": "security",
    "comment": "Hardcoded credentials are a critical security risk. Anyone with access to this file can steal these credentials.",
    "suggestion": "password = os.environ['DB_PASSWORD']"
  },
  {
    "line": 27,
    "severity": "warning",
    "category": "bug",
    "comment": "This will throw a KeyError if 'user' is not in the dict. Use .get() instead.",
    "suggestion": "user = data.get('user', {})"
  }
]"""


def review_file(filename: str, patch: str, language: str) -> list[dict]:
    """Send a file diff to Gemini and get back a list of structured review comments."""
    full_prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Please review this {language} diff for `{filename}`:\n\n"
        f"```diff\n{patch}\n```"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=full_prompt,
        )
        raw = response.text.strip()

        # Strip markdown fences if the model wrapped the JSON anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        comments = json.loads(raw)

        # Validate the shape — drop malformed entries
        valid = []
        for c in comments:
            if all(k in c for k in ("line", "severity", "category", "comment")):
                valid.append(c)
            else:
                print(f"  Skipping malformed comment: {c}")

        return valid

    except json.JSONDecodeError as e:
        print(f"  JSON parse error for {filename}: {e}")
        print(f"  Raw response: {raw[:300]}")
        return []
    except Exception as e:
        print(f"  Unexpected error reviewing {filename}: {e}")
        return []
