#!/usr/bin/env python3
"""Run optional per-design scripts/check_meshes.py checks for every project.

The global STL validator is always required separately. Per-project checks
are opt-in, so future designs can supply project-specific assertions.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]


def discover_checks(repository: Path = REPO_ROOT) -> list[Path]:
    return sorted((repository / 'designs').glob('**/scripts/check_meshes.py'))


def run_checks(repository: Path = REPO_ROOT) -> bool:
    checks = discover_checks(repository)
    if not checks:
        print('No additional per-design mesh check scripts found; global STL validation still applies.')
        return True
    passed = True
    for script in checks:
        name = script.relative_to(repository).as_posix()
        print(f'\nRunning {name}', flush=True)
        result = subprocess.run([sys.executable, str(script)], cwd=repository)
        if result.returncode != 0:
            print(f'FAIL additional design checks: {name}', flush=True)
            passed = False
        else:
            print(f'PASS additional design checks: {name}', flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if run_checks() else 1)
