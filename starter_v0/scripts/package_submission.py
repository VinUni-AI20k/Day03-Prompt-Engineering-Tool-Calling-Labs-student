"""Build a reproducible submission without environment files or installed dependencies."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIRS = {'artifacts', 'analysis', 'data', 'tools', 'providers', 'scripts', 'tests', 'company_policy', 'samples', 'runs', 'transcripts', '.streamlit'}
EXCLUDED_DIRS = {'.venv', '__pycache__', '.pytest_cache', '.git', 'arxiv_papers', 'node_modules'}


def package() -> Path:
    destination = ROOT.parent / 'NoName_Lab_Submission.zip'
    paths = []
    for path in sorted(ROOT.rglob('*')):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT)
        if any(part in EXCLUDED_DIRS for part in rel.parts):
            continue
        if path.name.startswith('.env') and path.name != '.env.example':
            continue
        if path.name == 'secrets.toml' or path.suffix in {'.pyc', '.zip', '.log'}:
            continue
        if len(rel.parts) > 1 and rel.parts[0] not in ALLOWED_DIRS:
            continue
        paths.append((path, rel))
    manifest = {str(rel): hashlib.sha256(path.read_bytes()).hexdigest() for path, rel in paths}
    # Check against locally configured secrets without copying or printing them.
    secrets: list[str] = []
    env_path = ROOT / '.env'
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            if not line.strip() or line.lstrip().startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            value = value.strip().strip("\"'")
            if ('KEY' in key.upper() or 'TOKEN' in key.upper()) and len(value) >= 12:
                secrets.append(value)
    for path, rel in paths:
        data = path.read_bytes()
        if any(secret.encode() in data for secret in secrets):
            raise ValueError(f'Configured secret found in submission file: {rel}')
    with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path, rel in paths:
            archive.write(path, Path('starter_v0') / rel)
        archive.writestr('submission_manifest.json', json.dumps(manifest, indent=2))
    print(f'Created {destination.name}: {len(paths)} files, {destination.stat().st_size} bytes')
    return destination


if __name__ == '__main__':
    package()
