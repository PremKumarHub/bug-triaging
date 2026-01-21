import requests
import os
import json

# ---------------- CONFIG ----------------
GITHUB_TOKEN = os.getenv("GITHUB_PAT")

REPOSITORIES = [
    ("microsoft", "vscode"),
    ("microsoft", "vscode-python"),
    ("microsoft", "vscode-eslint"),
    ("microsoft", "vscode-jupyter"),
    ("microsoft", "vscode-cpptools")
]

PER_PAGE = 100
START_YEAR = 2022
MAX_TOTAL_ISSUES = 9000   # overall limit
# ----------------------------------------

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}


def fetch_repo_issues(owner, repo, remaining_limit):
    collected = []
    page = 1
    base_url = f"https://api.github.com/repos/{owner}/{repo}/issues"

    while len(collected) < remaining_limit:
        params = {
            "state": "closed",
            "per_page": PER_PAGE,
            "page": page
        }

        response = requests.get(base_url, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"❌ API error in {repo}: {response.status_code}")
            break

        issues = response.json()
        if not issues:
            break

        for issue in issues:
            # Ignore pull requests
            if "pull_request" in issue:
                continue

            # Must have assignee
            if issue["assignee"] is None:
                continue

            # Filter by closed year
            closed_year = int(issue["closed_at"][:4])
            if closed_year < START_YEAR:
                continue

            collected.append({
                "repository": f"{owner}/{repo}",
                "issue_id": issue["id"],
                "issue_number": issue["number"],
                "title": issue["title"],
                "body": issue["body"],
                "assignee": issue["assignee"]["login"],
                "state": issue["state"],
                "created_at": issue["created_at"],
                "closed_at": issue["closed_at"]
            })

            if len(collected) >= remaining_limit:
                break

        print(f"📦 {repo}: collected {len(collected)}")
        page += 1

    return collected


if __name__ == "__main__":
    if not GITHUB_TOKEN:
        raise RuntimeError("❌ GITHUB_PAT not set")

    all_issues = []

    for owner, repo in REPOSITORIES:
        remaining = MAX_TOTAL_ISSUES - len(all_issues)
        if remaining <= 0:
            break

        print(f"\n⏳ Collecting from {owner}/{repo}")
        repo_issues = fetch_repo_issues(owner, repo, remaining)
        all_issues.extend(repo_issues)

    os.makedirs("data/raw", exist_ok=True)

    with open("data/raw/github_issues_raw.json", "w", encoding="utf-8") as f:
        json.dump(all_issues, f, indent=4)

    print(f"\n✅ DONE: Total collected bugs = {len(all_issues)}")
