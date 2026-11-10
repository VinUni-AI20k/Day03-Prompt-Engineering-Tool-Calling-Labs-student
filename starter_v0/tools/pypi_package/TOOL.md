---
name: pypi_package
track: bonus
kind: live_api
provider: PyPI JSON API
requires_env: []
inputs: [package_name, include_releases]
outputs: [items]
side_effect: false
---
# pypi_package

Fetches Python package metadata from `https://pypi.org/pypi/<package_name>/json`
including latest version, summary, license, `requires_python`, release timestamp, and project URLs.

