# 🤖 AI Code Reviewer

AI Code Reviewer is an automated GitHub PR review agent that analyzes pull request diffs
and generates actionable feedback using LLMs.

It helps developers catch bugs, performance issues, and bad patterns before merging code.

## Features

- 🔴 **Error detection** — security vulnerabilities, crashes, logic bugs
- 🟡 **Warnings** — performance issues, bad patterns, missing error handling
- 🔵 **Suggestions** — style improvements, maintainability tips
- 📊 **Summary comment** — severity breakdown table on every PR
- 🌐 **Multi-language** — Python, JavaScript, TypeScript, JSX, TSX

## Demo
<img width="1567" height="838" alt="Screenshot 2026-03-16 194300" src="https://github.com/user-attachments/assets/2887ea5d-4267-4d58-b3c7-86c4eee26146" />
<img width="1225" height="843" alt="image" src="https://github.com/user-attachments/assets/ae016e4e-e47f-49e9-bec0-ec3b71ef9dd2" />


## Setup

### 1. Add your API key to GitHub Secrets

Go to your repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add: `ANTHROPIC_API_KEY` = your key from [console.anthropic.com](https://console.anthropic.com)

### 2. Push this repo

The workflow in `.github/workflows/review.yml` will automatically activate.

### 3. Open a pull request

The bot will trigger on every new PR or pushed commit.

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and fill in your credentials
# Edit .env with your keys

# Run against a real PR
cd reviewer
python main.py
```

## Project Structure

```
ai-code-reviewer/
├── .github/
│   └── workflows/
│       └── review.yml        ← GitHub Actions trigger
├── reviewer/
│   ├── main.py               ← entry point
│   ├── github_client.py      ← fetch PR diff
│   ├── llm_client.py         ← call Claude API
│   └── comment_poster.py     ← post inline comments + summary
├── prompts/
│   └── review_prompt.txt     ← system prompt reference
├── .env.example              ← template for local dev
├── requirements.txt
└── README.md
```

## How It Works

1. A developer opens a pull request
2. GitHub Actions triggers the workflow
3. `github_client.py` fetches the diff of changed files
4. `llm_client.py` sends each diff to Claude and gets back structured JSON comments
5. `comment_poster.py` posts inline comments on the PR + a summary table
