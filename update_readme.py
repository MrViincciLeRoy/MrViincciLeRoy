import requests
from datetime import datetime, timedelta, timezone
import re

USERNAME = "MrViincciLeRoy"
README_PATH = "README.md"
SINCE = (datetime.now(timezone.utc) - timedelta(days=180)).isoformat()
MIN_COMMITS = 20
MAX_PROJECTS = 5

def get_repos():
    repos = []
    page = 1
    while True:
        r = requests.get(
            f"https://api.github.com/users/{USERNAME}/repos",
            params={"per_page": 100, "page": page, "sort": "pushed"},
            headers={"Accept": "application/vnd.github+json"}
        )
        data = r.json()
        if not data:
            break
        repos.extend(data)
        page += 1
    return repos

def get_commit_count(repo_name):
    r = requests.get(
        f"https://api.github.com/repos/{USERNAME}/{repo_name}/commits",
        params={"since": SINCE, "per_page": 100},
        headers={"Accept": "application/vnd.github+json"}
    )
    if r.status_code != 200:
        return 0
    commits = r.json()
    if isinstance(commits, list):
        return len(commits)
    return 0

def build_section(active_repos):
    lines = ["## 💡 Projects\n"]
    for repo in active_repos:
        name = repo["name"]
        desc = repo.get("description") or "No description provided."
        url = repo["html_url"]
        lang = repo.get("language") or "Unknown"
        lines.append(f"### [{name}]({url})")
        lines.append(f"> {desc}")
        lines.append(f"\n![Lang](https://img.shields.io/badge/{lang}-informational?style=flat)\n")
    return "\n".join(lines)

def update_readme(new_section):
    with open(README_PATH, "r") as f:
        content = f.read()

    updated = re.sub(
        r"## 💡 Projects.*?(?=\n## |\Z)",
        new_section + "\n\n",
        content,
        flags=re.DOTALL
    )

    with open(README_PATH, "w") as f:
        f.write(updated)
    print("README updated.")

def main():
    print("Fetching repos...")
    repos = get_repos()
    active = []

    for repo in repos:
        count = get_commit_count(repo["name"])
        print(f"  {repo['name']}: {count} commits")
        if count >= MIN_COMMITS:
            active.append(repo)

    active = active[:MAX_PROJECTS]
    print(f"\nShowing top {len(active)} active repos.")
    section = build_section(active)
    update_readme(section)

if __name__ == "__main__":
    main()
