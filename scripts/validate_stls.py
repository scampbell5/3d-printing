#!/usr/bin/env python3
"""Check every published STL under designs/**/stl/.

This checks mesh integrity, not manufacturing tolerances, sliding fit, support
requirements, slicer output or physical printability.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class MeshCheck:
    path: Path
    ok: bool
    details: str


def check_stl(path: Path) -> MeshCheck:
    try:
        # A Git LFS pointer is text, NOT the real mesh. Fail informatively.
        with path.open('rb') as stream:
            header = stream.read(150)
        if header.startswith(b'version https://git-lfs.github.com/spec/v1'):
            return MeshCheck(path, False, 'Git LFS pointer: download the actual STL (checkout with lfs: true)')

        mesh = trimesh.load_mesh(path, force='mesh', process=True)
        if not isinstance(mesh, trimesh.Trimesh) or mesh.is_empty:
            return MeshCheck(path, False, 'Empty or unrecognized STL mesh')

        extents = np.asarray(mesh.extents)
        if not np.isfinite(extents).all() or np.any(extents <= 0):
            return MeshCheck(path, False, f'Invalid bounding-box dimensions: {extents.tolist()}')
        if not np.isfinite(mesh.vertices).all():
            return MeshCheck(path, False, 'Non-finite vertex coordinates')

        # Identify disconnected shells rather than silently accepting them.
        components = len(mesh.split(only_watertight=False))
        watertight = bool(mesh.is_watertight)
        winding = bool(mesh.is_winding_consistent)
        volume = float(mesh.volume)
        positive_volume = np.isfinite(volume) and volume > 0
        ok = watertight and components == 1 and winding and positive_volume
        dimensions = ' x '.join(f'{d:.2f}' for d in extents)
        description = (f'watertight={watertight}; shells={components}; '
                       f'winding_consistent={winding}; positive_volume={positive_volume}; '
                       f'dimensions={dimensions} (STL units, expected mm); faces={len(mesh.faces):,}')
        return MeshCheck(path, ok, description)
    except Exception as exc:
        return MeshCheck(path, False, f'{type(exc).__name__}: {exc}')


def render_summary(checks: list[MeshCheck]) -> str:
    rows = [
        '# STL validation', '',
        'Checks apply to committed files in `designs/**/stl/`.',
        'They do **not** prove support-free slicing, baseplate fit, lid clearance, or lock strength.',
        '',
        '| File | Result | Details |',
        '|---|---|---|',
    ]
    for check in checks:
        try:
            name = check.path.relative_to(ROOT).as_posix()
        except ValueError:
            name = check.path.as_posix()
        details = check.details.replace('|', r'\|').replace('\n', ' ')
        rows.append(f'| `{name}` | {"PASS" if check.ok else "FAIL"} | {details} |')
    rows.append('')
    rows.append(f'**Result: {sum(c.ok for c in checks)} passed, {sum(not c.ok for c in checks)} failed.**')
    return '\n'.join(rows) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--summary', type=Path, help='Optional markdown output (for GitHub Actions)')
    args = parser.parse_args()
    files = sorted(ROOT.glob('designs/**/stl/**/*.stl'))
    if not files:
        print('FAIL: No published STL files found under designs/**/stl/', file=sys.stderr)
        return 1
    checks = [check_stl(path) for path in files]
    for item in checks:
        status = 'PASS' if item.ok else 'FAIL'
        print(f'{status} {item.path.relative_to(ROOT)}: {item.details}', flush=True)
    if args.summary:
        args.summary.parent.mkdir(parents=True, exist_ok=True)
        args.summary.write_text(render_summary(checks), encoding='utf-8')
        print(f'Wrote {args.summary}', flush=True)
    print(f'Checked {len(checks)} STL(s): {sum(c.ok for c in checks)} PASS / {sum(not c.ok for c in checks)} FAIL')
    return 0 if all(item.ok for item in checks) else 1


if __name__ == '__main__':
    sys.exit(main())
