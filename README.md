# 🤖 AI Code Reviewer

A GitHub Action that automatically reviews every pull request using Claude AI.
It flags bugs, security issues, and style problems — posting inline comments just like a human reviewer would.

## Features

- 🔴 **Error detection** — security vulnerabilities, crashes, logic bugs
- 🟡 **Warnings** — performance issues, bad patterns, missing error handling
- 🔵 **Suggestions** — style improvements, maintainability tips
- 📊 **Summary comment** — severity breakdown table on every PR
- 🌐 **Multi-language** — Python, JavaScript, TypeScript, JSX, TSX

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
cp .env.example .env
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
