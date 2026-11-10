---
name: pypi_package
track: bonus
kind: live_api
provider: PyPI JSON API
requires_env: []
inputs: [package, version]
outputs: [package, version, summary, license, requires_python, release_date, home_page, project_urls, install]
side_effect: false
---
# pypi_package

Lấy thông tin một package Python trên PyPI qua `GET https://pypi.org/pypi/{package}/json` (hoặc `{package}/{version}/json`).
Không cần API key.