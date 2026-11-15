#!/usr/bin/env python3
"""Discover and rebuild CAD designs using per-project design.json manifests.

A manifest opts a project in to rebuilding; other designs can still use the
repository-wide committed STL validation workflow without a build manifest.

Builds write exclusively to dist/builds/<project-id>/ and never update the
committed STLs. Generated meshes are validated before the job passes.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]


class ManifestError(ValueError):
    pass


@dataclass(frozen=True)
class Project:
    slug: str
    root: Path
    source: Path
    requirements: Path | None
    outputs: tuple[str, ...]
    name: str


def confined_file(base: Path, relative: str, label: str) -> Path:
    if not isinstance(relative, str) or not relative or '\\' in relative:
        raise ManifestError(f'{label}: expected a nonempty relative POSIX path')
    p = Path(relative)
    if p.is_absolute() or '..' in p.parts or '.' in p.parts or p == Path('.'):
        raise ManifestError(f'{label}: path must remain inside its project: {relative!r}')
    resolved_base = base.resolve()
    resolved_path = (resolved_base / p).resolve()
    if not resolved_path.is_relative_to(resolved_base):
        raise ManifestError(f'{label}: path escapes its project: {relative!r}')
    if not resolved_path.is_file():
        raise ManifestError(f'{label}: file does not exist: {relative!r}')
    return resolved_path


def parse_manifest(manifest: Path, repository: Path = REPO_ROOT) -> Project:
    designs = (repository / 'designs').resolve()
    root = manifest.resolve().parent
    if not root.is_relative_to(designs):
        raise ManifestError(f'Manifest outside designs/: {manifest}')
    slug = root.relative_to(designs).as_posix()
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError) as exc:
        raise ManifestError(f'{manifest}: {exc}') from exc
    if not isinstance(data, dict) or data.get('schema_version') != 1:
        raise ManifestError(f'{slug}: schema_version must be 1')
    if data.get('id') != slug:
        raise ManifestError(f'{slug}: manifest id must match designs/ relative folder ({slug})')
    if not isinstance(data.get('name'), str) or not data['name'].strip():
        raise ManifestError(f'{slug}: name is required')
    build = data.get('build')
    if not isinstance(build, dict):
        raise ManifestError(f'{slug}: build object is required')
    source = confined_file(root, build.get('script'), 'build.script')
    if source.suffix != '.py':
        raise ManifestError(f'{slug}: build.script must be a Python file')
    requirements = build.get('requirements')
    deps = confined_file(root, requirements, 'build.requirements') if requirements is not None else None
    declared = build.get('outputs')
    if not isinstance(declared, list) or not declared:
        raise ManifestError(f'{slug}: build.outputs must be a nonempty list')
    outputs: list[str] = []
    for output in declared:
        if not isinstance(output, str) or not output or '\\' in output:
            raise ManifestError(f'{slug}: output name must be a relative STL path')
        p = Path(output)
        if p.is_absolute() or '..' in p.parts or '.' in p.parts or p.suffix.lower() != '.stl':
            raise ManifestError(f'{slug}: invalid output STL path: {output!r}')
        outputs.append(output)
    if len(outputs) != len(set(outputs)):
        raise ManifestError(f'{slug}: build.outputs contains duplicate names')
    return Project(slug, root, source, deps, tuple(outputs), data['name'])


def discover_projects(repository: Path = REPO_ROOT) -> list[Project]:
    manifests = sorted((repository / 'designs').glob('**/design.json'))
    if not manifests:
        raise ManifestError('No buildable designs found (expected designs/**/design.json)')
    return [parse_manifest(m, repository) for m in manifests]


def select_projects(projects: Sequence[Project], selection: str) -> list[Project]:
    if selection == 'all':
        return list(projects)
    matches = [p for p in projects if p.slug == selection]
    if not matches:
        names = ', '.join(p.slug for p in projects)
        raise ManifestError(f'Unknown design {selection!r}; choose all or one of: {names}')
    return matches


def check_generated(project: Project, out_dir: Path) -> tuple[bool, list[str]]:
    # Delayed import keeps --list and --check usable without CAD/mesh packages.
    try:
        from .validate_stls import check_stl
    except ImportError:  # direct execution: python scripts/build_designs.py
        from validate_stls import check_stl

    errors = []
    for output in project.outputs:
        candidate = (out_dir / output).resolve()
        if not candidate.is_relative_to(out_dir.resolve()) or not candidate.is_file():
            errors.append(f'FAIL `{output}`: missing generated STL')
            continue
        result = check_stl(candidate)
        print(f'{"PASS" if result.ok else "FAIL"} {project.slug}/{output}: {result.details}', flush=True)
        errors.append(f'{"PASS" if result.ok else "FAIL"} `{output}`: {result.details}')
    return all(row.startswith('PASS') for row in errors), errors


def run_builds(projects: Sequence[Project], artifact_root: Path, *, install: bool = True,
               dry_run: bool = False) -> bool:
    report = [
        '# Design build report', '',
        'Generated STL checks are **mesh validation only**; they do not prove printer fit,',
        'support-free slicing, or working sliding/locking features.', '',
    ]
    success = True
    artifact_root.mkdir(parents=True, exist_ok=True)
    try:
        for project in projects:
            out_dir = artifact_root / project.slug
            cmd = [sys.executable, str(project.source)]
            print(f'\n=== {project.slug} ===', flush=True)
            report.extend((f'## {project.name}', '', f'Project: `{project.slug}`', ''))
            if dry_run:
                print(f'Would run: {cmd}', flush=True)
                print(f'Expected: {", ".join(project.outputs)}', flush=True)
                report.append('DRY RUN — no STL generated.\n')
                continue
            try:
                if install and project.requirements is not None:
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', str(project.requirements)],
                                   check=True, cwd=project.root)
                out_dir.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(prefix='cad-build-work-') as work:
                    env = dict(os.environ,
                               DESIGN_BUILD_OUTPUT_DIR=str(out_dir.resolve()),
                               DESIGN_BUILD_WORK_DIR=work)
                    subprocess.run(cmd, check=True, cwd=project.root, env=env)
                passed, findings = check_generated(project, out_dir)
                report.extend(f'- {line}' for line in findings)
                if not passed:
                    success = False
            except Exception as exc:
                # Preserve report even when a builder fails on GitHub's runner.
                success = False
                report.append(f'- **FAIL:** build/validation error: `{type(exc).__name__}: {exc}`')
                print(f'FAIL {project.slug}: {type(exc).__name__}: {exc}', file=sys.stderr)
            report.append('')
    finally:
        report.append(f'**Overall: {"PASS" if success else "FAIL"}**\n')
        (artifact_root / 'BUILD-REPORT.md').write_text('\n'.join(report), encoding='utf-8')
    return success


def main(argv: Sequence[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--list', action='store_true', help='Show available buildable designs')
    group.add_argument('--check', action='store_true', help='Validate every design manifest without building')
    ap.add_argument('--design', default='all', help='Build all designs, or one designs/relative/path')
    ap.add_argument('--artifact-root', type=Path, default=REPO_ROOT / 'dist' / 'builds')
    ap.add_argument('--no-install', action='store_true', help='Skip installing project CAD dependencies')
    ap.add_argument('--dry-run', action='store_true', help='Print selected builds without executing')
    args = ap.parse_args(argv)
    try:
        projects = discover_projects()
        if args.list:
            for project in projects:
                print(f'{project.slug} — {project.name}')
            return 0
        if args.check:
            for project in projects:
                print(f'PASS manifest: {project.slug}')
            return 0
        selected = select_projects(projects, args.design)
        return 0 if run_builds(selected, args.artifact_root,
                              install=not args.no_install, dry_run=args.dry_run) else 1
    except ManifestError as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
