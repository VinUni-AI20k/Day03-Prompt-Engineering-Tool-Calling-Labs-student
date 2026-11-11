---
name: github_repo
track: bonus
kind: live_api
provider: GitHub REST API
requires_env: []
inputs: [repo, include_readme]
outputs: [repo, description, stars, forks, open_issues, language, license, archived, pushed_at, url]
side_effect: false
---
# github_repo

Lấy thông tin một repo GitHub cụ thể qua `GET https://api.github.com/repos/{owner}/{repo}`.
Không cần key; tuỳ chọn `GITHUB_TOKEN` để tăng rate limit.